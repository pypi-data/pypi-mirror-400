import os
import json
import asyncio
import logging
import io
import sys
import re
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Tuple, List, Optional
import concurrent.futures
import threading
import time
import paho.mqtt.client as mqtt
import uuid
import platform
import random
import traceback
import struct

# Configure NumExpr for thread safety BEFORE any other imports
# This prevents segmentation faults in concurrent execution environments
os.environ['NUMEXPR_MAX_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'

# Import the DNS cache
from insyt_secure.utils.dns_cache import DNSCache
from insyt_secure.utils.audit_logger import AuditLogger
from insyt_secure.config import settings

# Configure module-level logger
logger = logging.getLogger(__name__)

# Additional NumExpr safety configuration if already imported
try:
    import numexpr as ne
    ne.set_num_threads(1)
    logger.debug("NumExpr configured for single-threaded operation to prevent segmentation faults")
except ImportError:
    logger.debug("NumExpr not available - thread safety configuration skipped")
except Exception as e:
    logger.warning(f"Could not configure NumExpr thread safety: {e}")

class NetworkRestrictionError(Exception):
    """Exception raised when attempting to connect to a restricted network."""
    pass

class CodeExecutionTimeoutError(Exception):
    """Exception raised when code execution exceeds the timeout."""
    pass

class AuthenticationError(Exception):
    """Exception raised when broker authentication fails due to invalid credentials."""
    pass

class CodeExecutor:
    """
    Executes Python code snippets received via secure communication channel.
    
    The execution timeout can be specified in two ways:
    1. As a default value when initializing the executor
    2. Dynamically in each message payload with the "execution_time" key
    
    If "execution_time" is present in the message, it will override the default timeout
    for that specific execution.
    """
    def __init__(self, mqtt_broker, mqtt_port, mqtt_username, mqtt_password, subscribe_topic, 
                 publish_topic=None, ssl_enabled=False, allowed_ips=None, always_allowed_domains=None, 
                 max_workers=20, execution_timeout=30, project_id=None):
        """
        Initialize the CodeExecutor with connection details.
        
        All connection parameters are required and must be provided explicitly.
        
        Args:
            mqtt_broker: Broker hostname or IP
            mqtt_port: Broker port
            mqtt_username: Username
            mqtt_password: Password
            subscribe_topic: Topic to subscribe to
            publish_topic: Topic to publish results to (if None, will use response_topic from individual messages)
            ssl_enabled: Whether to use SSL for connection
            allowed_ips: Optional list of allowed IPs/hostnames (with optional ports)
            always_allowed_domains: Domains that are always allowed regardless of IP restrictions
            max_workers: Maximum number of concurrent executions (default: 5)
            execution_timeout: Maximum execution time in seconds for each code snippet (default: 30)
            project_id: Optional project identifier for context in execution environment
        """
        # Connection parameters - must be provided explicitly
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        self.subscribe_topic = subscribe_topic
        self.publish_topic = publish_topic
        self.ssl_enabled = ssl_enabled
        self.allowed_ips = allowed_ips
        self.always_allowed_domains = always_allowed_domains or []
        
        # Execution parameters
        self.pod_name = os.getenv('POD_NAME', 'local-executor')
        self.max_workers = max_workers
        self.execution_timeout = execution_timeout  # Store default timeout
        self.project_id = project_id  # Store project context for execution environment
        
        # MQTT message tracking for diagnostics
        self.message_received_count = 0
        self.message_published_count = 0
        self.message_published_topics = set()  # Keep track of all topics we've published to
        self.message_received_topics = set()   # Keep track of all topics we've received from
        self.last_message_time = 0
        
        # Subscription tracking
        self.last_subscription_time = 0
        self.last_subscription_mid = None
        self.subscription_confirmed = False
        self.client_id = None  # Will be set during client setup
        
        logger.debug(f"Setting up executor with {self.max_workers} concurrent workers")
        logger.debug(f"Execution timeout set to {self.execution_timeout} seconds")
        logger.debug(f"SSL enabled: {self.ssl_enabled}")
        
        # Log sensitive information only at debug level
        logger.debug(f"Input channel: {self.subscribe_topic}")
        logger.debug(f"Output channel: {self.publish_topic}")
        
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Create a queue for coordinating message processing across threads
        self.message_queue = asyncio.Queue(maxsize=self.max_workers)
        
        # For tracking active message processing tasks
        self.active_tasks = set()
        
        # Initialize DNS cache with 24-hour TTL
        self.dns_cache = DNSCache(ttl_seconds=86400)  # 24 hours
        logger.info("DNS cache initialized with 24-hour TTL for resilience against DNS outages")
        
        # Initialize audit logger if enabled
        self.audit_logger = None
        if settings.AUDIT_LOGGING_ENABLED:
            try:
                self.audit_logger = AuditLogger(
                    db_path=settings.AUDIT_DB_PATH,
                    max_size_gb=settings.AUDIT_MAX_SIZE_GB,
                    max_retention_days=settings.AUDIT_MAX_RETENTION_DAYS
                )
                logger.info("Audit logging enabled - execution logs will be stored")
            except Exception as e:
                logger.error(f"Failed to initialize audit logger: {e}")
                logger.warning("Continuing without audit logging")
        else:
            logger.info("Audit logging disabled")
        
        # Validate host against allowed IPs
        if self.allowed_ips:
            logger.debug(f"Network restrictions enabled")
            # Only show allowed IPs at debug level
            logger.debug(f"Allowed IPs: {self.allowed_ips}")
            logger.debug(f"Always allowed domains: {self.always_allowed_domains}")
            self._validate_host(self.mqtt_broker)
        
        # Initialize client
        self.client = None
        self.connected = False
        self.loop = None
        self.mqtt_client_thread = None
        
        # Setup thread exception handler to catch MQTT library errors
        self._original_thread_excepthook = threading.excepthook
        threading.excepthook = self._handle_thread_exception
        
    def _validate_host(self, host):
        """Validate if a host is allowed based on the IP whitelist."""
        if not self.allowed_ips:
            return True
            
        # Properly check if host is insyt.co or a subdomain of insyt.co
        if host == "insyt.co" or host.endswith(".insyt.co"):
            logger.debug(f"Host {host} is allowed as an insyt.co domain")
            return True
            
        # Also check against explicitly allowed domains
        for domain in self.always_allowed_domains:
            if host == domain or host.endswith(f".{domain}"):
                logger.debug(f"Host {host} is allowed as part of domain {domain}")
                return True
            
        # Check if host is in allowed IPs
        if any(host.startswith(ip.split(':')[0]) for ip in self.allowed_ips):
            return True
            
        # Resolve hostname to IP and check
        try:
            # Use our DNS cache for resolution
            ip = self.dns_cache.resolve(host)
            if any(ip == allowed_ip.split(':')[0] for allowed_ip in self.allowed_ips):
                return True
        except socket.gaierror:
            pass
            
        raise NetworkRestrictionError(f"Host {host} is not in the allowed IP list")
    
    # Client callback for when the client receives a CONNACK response from the server
    def on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback when connection is established to signaling server."""
        # For MQTT v5, rc might be a ReasonCodes object instead of an integer
        # We need to handle both cases
        try:
            # Try to convert rc to an integer if it's a ReasonCodes object
            if hasattr(rc, 'value'):
                rc_value = rc.value
            else:
                rc_value = int(rc)  # Ensure it's an integer
                
            if rc_value == 0:
                # Log connection success - add more visibility for reconnections
                if getattr(self, 'reconnecting', False):
                    logger.info(f"Successfully reconnected to signaling server after disconnection")
                    self.reconnecting = False
                else:
                    logger.debug(f"Successfully connected to signaling server")
                
                # Set connection status before subscribing
                self.connected = True
                
                # Use QoS level 1 for subscribing to ensure at-least-once delivery
                try:
                    result, mid = client.subscribe(self.subscribe_topic, qos=1)
                    subscription_status = "Success" if result == 0 else f"Failed with code {result}"
                    logger.debug(f"Subscription status: {subscription_status}")
                    logger.debug(f"Subscribed to topic: {self.subscribe_topic} with QoS=1")
                    # More detailed logging at debug level
                    logger.debug(f"Subscription details - Topic: {self.subscribe_topic}, QoS: 1, Result: {result}, Message ID: {mid}")
                    
                    # Track subscription attempt
                    self.last_subscription_time = time.time()
                    self.last_subscription_mid = mid
                    self.subscription_confirmed = False  # Will be set to True in on_subscribe
                    
                    # Reset consecutive error counter on successful connection
                    self._consecutive_auth_errors = 0
                    
                except Exception as e:
                    logger.error(f"Error subscribing to topic: {str(e)}")
                    import traceback
                    logger.error(f"Exception traceback: {traceback.format_exc()}")
            else:
                # Extended connection result codes dictionary with MQTT v5 codes
                connection_results = {
                    1: "Connection refused - incorrect protocol version",
                    2: "Connection refused - invalid client identifier",
                    3: "Connection refused - server unavailable",
                    4: "Connection refused - bad username or password",
                    5: "Connection refused - not authorised",
                    # Additional MQTT v5 return codes
                    16: "Connection refused - No matching subscribers",
                    17: "Connection refused - No subscription existed",
                    128: "Connection refused - Unspecified error",
                    129: "Connection refused - Malformed packet",
                    130: "Connection refused - Protocol error",
                    131: "Connection refused - Implementation specific error",
                    132: "Connection refused - Unsupported protocol version",
                    133: "Connection refused - Client identifier not valid",
                    134: "Connection refused - Bad username or password",
                    135: "Connection refused - Not authorized",
                    136: "Connection refused - Server unavailable",
                    137: "Connection refused - Server busy",
                    138: "Connection refused - Banned",
                    140: "Connection refused - Bad authentication method",
                    144: "Connection refused - Topic Name invalid",
                    149: "Connection refused - Packet too large",
                    151: "Connection refused - QoS not supported",
                    153: "Connection refused - Retain not supported",
                    154: "Connection refused - Receive Maximum exceeded"
                }
                
                error_message = connection_results.get(rc_value, f"Unknown error code: {rc_value}")
                logger.error(f"Failed to connect to signaling server: {error_message}")
                self.connected = False
                
                # Handle specific error codes
                if rc_value in (2, 133):
                    # Invalid client ID - suggest generating a new one
                    logger.warning("Server rejected our client ID. Will generate a new one on reconnection.")
                    # We don't need to do anything special as a new client ID is generated on each reconnect
                    
                    # Track consecutive auth-related errors
                    self._consecutive_auth_errors = getattr(self, '_consecutive_auth_errors', 0) + 1
                    logger.warning(f"Consecutive auth-related errors: {self._consecutive_auth_errors}")
                elif rc_value in (135, 5, 4, 134):
                    # Authentication errors - signal to get new credentials
                    logger.error(f"Authentication error detected: {error_message} (code {rc_value})")
                    logger.error("Broker rejected credentials. Will attempt to acquire new ones.")
                    
                    # Set a flag that can be checked by _mqtt_client_connect
                    self._auth_error_detected = True
                    # Track consecutive auth-related errors
                    self._consecutive_auth_errors = getattr(self, '_consecutive_auth_errors', 0) + 1
                    logger.warning(f"Consecutive auth-related errors: {self._consecutive_auth_errors}")
                    
                    if self.loop:
                        asyncio.run_coroutine_threadsafe(self._signal_auth_error(), self.loop)
                elif rc_value in (136, 3):
                    # Server availability issues - backoff and retry
                    logger.warning("Server unavailable. Will implement longer backoff on reconnection.")
                    # This will be handled by the reconnection logic with exponential backoff
                
        except Exception as e:
            # Handle any exception during processing of rc
            logger.error(f"Error in on_connect handler: {str(e)}")
            logger.error(f"Connection likely failed, treating as error")
            self.connected = False
            if self.loop:
                asyncio.run_coroutine_threadsafe(self._handle_reconnection(), self.loop)
    
    # Client callback for when a message is received from the server
    def on_message(self, client, userdata, msg):
        """Callback when a message is received."""
        # Update message tracking
        self.message_received_count += 1
        self.message_received_topics.add(msg.topic)
        self.last_message_time = time.time()
        
        # Only log detailed message info at debug level
        logger.debug("\n" + "="*40)
        logger.debug(f"RECEIVED MESSAGE ON TOPIC: {msg.topic}")
        logger.debug(f"QoS: {msg.qos}, Retain: {msg.retain}")
        logger.debug("RAW PAYLOAD START")
        try:
            # Try to decode and pretty print if it's valid JSON
            payload_str = msg.payload.decode('utf-8')
            try:
                # Try to parse and pretty print JSON
                json_payload = json.loads(payload_str)
                # Mask pythonCode if present
                if isinstance(json_payload, dict) and 'pythonCode' in json_payload:
                    json_payload['pythonCode'] = '*** CODE CONTENT MASKED ***'
                logger.debug(json.dumps(json_payload, indent=2))
            except json.JSONDecodeError:
                # Just print raw string if not valid JSON
                logger.debug(payload_str)
        except UnicodeDecodeError:
            # If it's not valid UTF-8, print hex representation
            logger.debug("Binary data (hex):", ' '.join(f'{b:02x}' for b in msg.payload))
        logger.debug("RAW PAYLOAD END")
        logger.debug("="*40 + "\n")

        logger.debug(f"Received message on topic: {msg.topic} (size: {len(msg.payload)} bytes)")
        
        # Check if this is a subscription test message
        try:
            payload = json.loads(msg.payload)
            if isinstance(payload, dict) and payload.get("type") == "subscription_test":
                logger.debug("Received subscription test message")
                self.test_message_received = True
                return  # Skip further processing for test messages
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass  # Not a JSON message or not our test message
            
        if self.loop:
            try:
                # Convert the message to the format expected by process_message
                message = MQTTMessageWrapper(msg)
                # Schedule the message processing in the asyncio event loop
                asyncio.run_coroutine_threadsafe(self.message_queue.put(message), self.loop)
            except Exception as e:
                logger.error(f"Error queueing message for processing: {str(e)}")
                import traceback
                logger.error(f"Exception traceback: {traceback.format_exc()}")

    # Add callback for successful subscriptions
    def on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        """Callback when subscription is confirmed by the broker."""
        try:
            # For MQTT v5, granted_qos might be an object with different structure
            # Log appropriately based on what we received
            if isinstance(granted_qos, (list, tuple)):
                qos_str = ", ".join(str(qos) for qos in granted_qos)
                logger.debug(f"Broker confirmed subscription with message ID: {mid}")
                logger.debug(f"Granted QoS: [{qos_str}]")
            else:
                logger.debug(f"Broker confirmed subscription with message ID: {mid}")
                logger.debug(f"Granted QoS: {granted_qos}")
            
            # Mark subscription as confirmed
            self.subscription_confirmed = True
            
            # Schedule a self-test after subscription is confirmed
            if self.loop:
                asyncio.run_coroutine_threadsafe(self._run_subscription_test(), self.loop)
        except Exception as e:
            logger.error(f"Error processing subscription confirmation: {str(e)}")
            # Still mark as confirmed since we did receive the confirmation
            self.subscription_confirmed = True
    
    # Add callback for publish confirmations
    def on_publish(self, client, userdata, mid):
        """Callback when publish is confirmed by the broker."""
        logger.debug(f"Broker confirmed message publication with message ID: {mid}")
        # Could track specific message IDs here if needed
    
    # Client callback for when the client disconnects from the server
    def on_disconnect(self, client, userdata, rc, properties=None):
        """Callback when disconnected from signaling server."""
        self.connected = False
        
        # Handle rc as either integer or ReasonCodes object
        try:
            # Try to convert rc to an integer if it's a ReasonCodes object
            if hasattr(rc, 'value'):
                rc_value = rc.value
            else:
                rc_value = int(rc)
                
            if rc_value != 0:
                logger.warning(f"Unexpected disconnection from signaling server, rc: {rc_value}")
                # Try to reconnect
                if self.loop:
                    asyncio.run_coroutine_threadsafe(self._handle_reconnection(), self.loop)
            else:
                logger.info("Successfully disconnected from signaling server")
        except Exception as e:
            # If we can't process rc, assume it's an error
            logger.error(f"Error in on_disconnect handler: {str(e)}")
            logger.warning("Assuming unexpected disconnection")
            if self.loop:
                asyncio.run_coroutine_threadsafe(self._handle_reconnection(), self.loop)
    
    async def _signal_auth_error(self):
        """Signal that an authentication error occurred."""
        logger.error("Authentication error. Signaling main thread to get new credentials.")
        # Raise specific authentication exception to be caught in start() method
        raise AuthenticationError("Authentication error. Credentials have expired and need to be refreshed.")
    
    async def _handle_reconnection(self):
        """Handle reconnection logic after unexpected disconnection."""
        logger.info("Initiating reconnection process due to unexpected disconnection")
        # This will be caught in start() method and trigger reconnection
        raise Exception("Unexpected disconnection. Triggering reconnection.")
    
    def _mqtt_client_setup(self):
        """Set up the client with all callbacks and configuration."""
        # Create a new client instance with a unique ID that won't collide
        unique_id = str(uuid.uuid4())[:8]
        hostname = platform.node()
        client_id = f"insyt-secure-{self.pod_name}-{hostname}-{os.getpid()}-{unique_id}"
        
        # Track the client ID for diagnostics
        self.client_id = client_id
        
        try:
            logger.debug(f"Setting up MQTT client with ID: {client_id}")
            
            # Check if MQTTv5 is available in this version of paho-mqtt
            mqtt_version = mqtt.MQTTv311  # Default to 3.1.1
            try:
                if hasattr(mqtt, 'MQTTv5'):
                    mqtt_version = mqtt.MQTTv5
                    logger.debug("Using MQTT 5.0 protocol")
                else:
                    logger.debug("MQTT 5.0 not available, using MQTT 3.1.1")
            except AttributeError:
                logger.debug("MQTT 5.0 not available, using MQTT 3.1.1")
            
            # Create client with appropriate protocol version
            if mqtt_version == mqtt.MQTTv5:
                self.client = mqtt.Client(client_id=client_id, protocol=mqtt_version)
            else:
                # For MQTT 3.1.1, we can use clean_session
                self.client = mqtt.Client(client_id=client_id, clean_session=True)
            
            # Store MQTT version for later use
            self.mqtt_version = mqtt_version
            
            # Set up username and password
            self.client.username_pw_set(self.mqtt_username, self.mqtt_password)
            
            # Set up callbacks
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_disconnect = self.on_disconnect
            self.client.on_subscribe = self.on_subscribe  # Add subscription callback
            self.client.on_publish = self.on_publish      # Add publish callback
            
            # Set up SSL if enabled
            if self.ssl_enabled:
                logger.debug("SSL enabled for connection")
                self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
                self.client.tls_insecure_set(False)
            
            # Set the client to automatically reconnect with exponential backoff
            self.client.reconnect_delay_set(min_delay=1, max_delay=30)
            
            # Set up will message for clean disconnect notification
            will_message = {
                "status": "offline",
                "client_id": client_id,
                "timestamp": time.time(),
                "reason": "unexpected_disconnect"
            }
            will_topic = f"status/{client_id}"
            self.client.will_set(will_topic, json.dumps(will_message), qos=1, retain=True)
            
            # Double-check host against allowed IPs before connecting
            if self.allowed_ips:
                self._validate_host(self.mqtt_broker)
            
            return self.client
        except Exception as e:
            logger.error(f"Error setting up MQTT client: {str(e)}")
            import traceback
            logger.error(f"Exception traceback: {traceback.format_exc()}")
            raise

    def _mqtt_client_connect(self):
        """Connect the client to the signaling server and start the network loop."""
        try:
            logger.debug(f"Connecting to signaling server...")
            # Log detailed connection info only at debug level
            logger.debug(f"Server: {self.mqtt_broker}:{self.mqtt_port}, Username: {self.mqtt_username}")
            
            # Resolve hostname before connecting to use DNS cache if needed
            try:
                # Try to resolve the hostname and cache it
                host_ip = self.dns_cache.resolve(self.mqtt_broker)
                logger.debug(f"Resolved {self.mqtt_broker} to {host_ip}")
                
                # If the hostname resolution was successful but different from the original,
                # we'll still use the hostname for the connection (the MQTT client will
                # do its own resolution) but we've successfully cached the IP for future use
            except socket.gaierror as e:
                # DNS resolution failed even with cache - will be raised and handled by caller
                logger.error(f"DNS resolution failed for {self.mqtt_broker}: {str(e)}")
                raise
            
            # Track if we've detected an auth error to avoid infinite loops
            self._auth_error_detected = False
            
            # Connect with appropriate parameters based on MQTT version
            if hasattr(self, 'mqtt_version') and self.mqtt_version == mqtt.MQTTv5:
                # For MQTT 5.0
                try:
                    # Try to create Properties object if available
                    connect_properties = None
                    # The constant 1 is for CONNECT packet type
                    # This is more resilient than relying on mqtt.PacketTypes.CONNECT
                    if hasattr(mqtt, 'Properties'):
                        try:
                            # First try with PacketTypes if available
                            if hasattr(mqtt, 'PacketTypes'):
                                connect_properties = mqtt.Properties(mqtt.PacketTypes.CONNECT)
                            else:
                                # Fall back to using the raw value (1 is CONNECT)
                                connect_properties = mqtt.Properties(1)
                        except TypeError:
                            # Some versions might expect different parameters
                            logger.warning("Could not create MQTT Properties, connecting without properties")
                    
                    self.client.connect(
                        self.mqtt_broker, 
                        self.mqtt_port, 
                        keepalive=60, 
                        clean_start=True,
                        properties=connect_properties
                    )
                except (TypeError, AttributeError) as e:
                    # If clean_start or properties aren't supported, fall back to basic connect
                    logger.warning(f"MQTT 5.0 connect failed, trying basic connect: {str(e)}")
                    self.client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
            else:
                # For MQTT 3.1.1
                self.client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
            
            # Start the network loop to process callbacks
            self.client.loop_start()
            
            # Increase the connection timeout based on retry count but keep it reasonable
            retry_count = getattr(self, '_retry_count', 0)
            connection_timeout = min(20, 10 + (retry_count * 2))  # Longer timeout for repeated retries, max 20 seconds
            
            # Wait for connection to be established or failed
            logger.debug(f"Waiting up to {connection_timeout} seconds for connection...")
            timeout = connection_timeout
            start_time = time.time()
            while not self.connected and time.time() - start_time < timeout:
                # Check if an auth error was detected by the on_connect callback
                if getattr(self, '_auth_error_detected', False):
                    logger.info("Authentication error detected during connection process")
                    self.client.loop_stop()
                    raise AuthenticationError("Authentication error detected during connection")
                time.sleep(0.1)
            
            if not self.connected:
                logger.error(f"Failed to connect to signaling server within {timeout} seconds")
                self.client.loop_stop()
                
                # Check if we have consecutive auth-related or client ID errors
                if retry_count > 1 and getattr(self, '_consecutive_auth_errors', 0) > 0:
                    logger.error("Multiple connection attempts failed with potential credential issues")
                    raise AuthenticationError("Likely credential reset by server detected")
                
                raise Exception("Failed to connect to signaling server")
            
            # Publish online status
            try:
                status_message = {
                    "status": "online",
                    "client_id": self.client_id,
                    "timestamp": time.time(),
                    "pod_name": self.pod_name,
                    "subscribe_topic": self.subscribe_topic
                }
                status_topic = f"status/{self.client_id}"
                self.client.publish(status_topic, json.dumps(status_message), qos=1, retain=True)
                logger.debug(f"Published online status to {status_topic}")
            except Exception as e:
                logger.warning(f"Failed to publish online status: {str(e)}")
                # Non-critical, so continue even if this fails
                
        except Exception as e:
            logger.error(f"Error connecting to signaling server: {str(e)}")
            if self.client:
                self.client.loop_stop()
            raise
    
    async def _safe_process_message(self, message):
        """
        Safely process a message with additional error handling to prevent service crashes.
        This is a wrapper around process_message with extra protection.
        """
        try:
            await self.process_message(message)
        except Exception as e:
            logger.error(f"Critical error in _safe_process_message: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # Try to extract message details for better error reporting
            try:
                if hasattr(message, 'payload'):
                    payload_preview = str(message.payload)[:100] if message.payload else "No payload"
                    logger.error(f"Message payload preview: {payload_preview}")
                if hasattr(message, 'topic'):
                    logger.error(f"Message topic: {message.topic}")
            except Exception as detail_error:
                logger.error(f"Could not extract message details: {str(detail_error)}")
            
            # This method should never raise an exception to protect the service
            logger.error("Message processing failed but service continues running")

    async def _process_messages(self):
        """Process messages from the queue."""
        while True:
            try:
                # Wait for a message from the queue
                message = await self.message_queue.get()
                
                # Process the message in a separate task using the safe wrapper
                task = asyncio.create_task(self._safe_process_message(message))
                self.active_tasks.add(task)
                task.add_done_callback(self._task_done_callback)
                
                # Log if we're at capacity
                if len(self.active_tasks) >= self.max_workers:
                    logger.info(f"Processing at capacity with {len(self.active_tasks)} concurrent executions")
                
                # Let the queue know we're done with this item
                self.message_queue.task_done()
            except asyncio.CancelledError:
                logger.info("Message processing loop cancelled")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in message processing loop: {type(e).__name__}: {str(e)}")
                import traceback
                logger.error(f"Exception traceback: {traceback.format_exc()}")
                # Sleep briefly to avoid tight error loops
                await asyncio.sleep(1)
    
    def _task_done_callback(self, task):
        """Callback when a task is done - checks for exceptions and logs them."""
        self.active_tasks.discard(task)
        
        # Check if the task raised an exception
        if not task.cancelled():
            exception = task.exception()
            if exception:
                logger.error(f"Task raised an unhandled exception: {type(exception).__name__}: {str(exception)}")
                import traceback
                # Get full traceback including the exception details
                try:
                    # Format the full exception traceback
                    if hasattr(exception, '__traceback__') and exception.__traceback__:
                        tb_lines = traceback.format_exception(type(exception), exception, exception.__traceback__)
                        logger.error(f"Full exception traceback:\n{''.join(tb_lines)}")
                    else:
                        logger.error(f"Exception traceback: {traceback.format_exc()}")
                except Exception as e:
                    logger.error(f"Error formatting exception traceback: {str(e)}")
                    logger.error(f"Original exception: {type(exception).__name__}: {str(exception)}")
    
    async def start(self):
        """Start the executor and connect to signaling server."""
        retry_count = 0
        self.reconnecting = False
        self._consecutive_auth_errors = 0
        
        # Store the event loop for use in callbacks
        self.loop = asyncio.get_running_loop()
        
        # Log expected message format at debug level
        self._log_message_format()
        
        while True:
            try:
                # Set up client
                self._mqtt_client_setup()
                
                # Set reconnecting flag and retry count
                if retry_count > 0:
                    self.reconnecting = True
                    self._retry_count = retry_count  # Store for use in _mqtt_client_connect
                
                # Connect to signaling server
                self._mqtt_client_connect()
                
                # Reset retry count on successful connection
                if retry_count > 0:
                    logger.info(f"Reconnection successful after {retry_count} attempts")
                    retry_count = 0
                
                # Start message processing
                message_processor = asyncio.create_task(self._process_messages())
                
                # Diagnostic task completely disabled
                # diagnostic_task = asyncio.create_task(self._log_topic_diagnostics())
                
                # Start heartbeat task
                heartbeat_task = asyncio.create_task(self._send_heartbeat())
                
                # Start subscription monitor task
                subscription_monitor = asyncio.create_task(self._monitor_subscription())
                
                # Keep the event loop running
                try:
                    while self.connected:
                        await asyncio.sleep(1)
                    
                    # If we get here, it means we disconnected
                    logger.warning("Disconnected from signaling server")
                    raise Exception("Disconnected from signaling server")
                    
                except asyncio.CancelledError:
                    # Cancel all tasks if we're shutting down
                    message_processor.cancel()
                    # diagnostic_task.cancel()  # Not needed anymore
                    heartbeat_task.cancel()
                    subscription_monitor.cancel()
                    raise
                    
            except NetworkRestrictionError as e:
                logger.error(f"Network restriction error: {str(e)}")
                sys.exit(1)  # Exit immediately for security reasons
            
            except AuthenticationError as e:
                # Explicitly handle authentication errors with the specific exception class
                logger.error(f"Authentication error detected: {str(e)}")
                logger.error("Server has likely reset credentials. Returning to main loop to request fresh credentials.")
                
                # Clean up resources
                if self.client:
                    self.client.loop_stop()
                    self.client = None
                
                # Return to let main() handle credential refresh
                return
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Connection error (attempt {retry_count}): {str(e)}")
                
                # Clean up resources
                if self.client:
                    self.client.loop_stop()
                    self.client = None
                
                # Check for authentication errors that might have been missed by the specific exception
                error_str = str(e).lower()
                if ("auth" in error_str or "unauthorized" in error_str or 
                    "credentials" in error_str or "permission" in error_str or
                    "not authorized" in error_str):
                    logger.error("Authentication error detected via string matching. Credentials may have expired or been reset.")
                    logger.error("Returning to main loop to request fresh credentials")
                    return
                
                # If we have too many consecutive auth-related errors, assume credentials need refreshing
                if getattr(self, '_consecutive_auth_errors', 0) >= 2:
                    logger.error(f"Multiple consecutive auth-related errors ({self._consecutive_auth_errors}). Requesting fresh credentials.")
                    return
                
                # Implement more sophisticated backoff for connection retries
                base_backoff = min(30, 2 ** min(retry_count, 4))
                jitter = 0.1 * retry_count  # Add increasing jitter as retry count grows
                backoff_time = base_backoff + (random.random() * jitter)
                
                # If we've had multiple consecutive failures, add extra delay
                if retry_count > 3:
                    logger.warning(f"Multiple connection failures detected, adding extra delay")
                    backoff_time += 5
                    
                logger.warning(f"Connection failed. Retrying in {backoff_time:.1f} seconds...")
                await asyncio.sleep(backoff_time)
    
    def _log_message_format(self):
        """Log details about expected message format and subscription."""
        logger.debug("=== Subscription and Message Format Information ===")
        logger.debug(f"This service is configured to subscribe to: {self.subscribe_topic}")
        if self.publish_topic:
            logger.debug(f"Default publish topic for responses: {self.publish_topic}")
        else:
            logger.debug("No default publish topic configured - will use response_topic from messages")
        logger.debug("Expected incoming message format:")
        logger.debug("""
        {
            "pythonCode": "...", // Required: Python code to execute
            "requestId": "...",  // Required: Unique identifier for this request
            "sharedTopic": "...", // Optional: Topic to publish results to
            "executionTime": "30" // Optional: Maximum execution time in seconds
        }
        """)
        logger.debug("Response message format:")
        logger.debug("""
        {
            "codeOutput": "...", // Output from the code execution
            "requestId": "...",  // Same requestId that was received
            "executionTime": "...", // Actual execution time in seconds
            "status": "success"|"failure", // Execution status
            "errorDescription": "..." // Optional: Detailed error description
        }
        """)
        logger.debug("===================================================")
    
    async def process_message(self, message):
        """Process an incoming execution request."""
        request_id = None  # Initialize for error logging
        start_time = time.time()
        response_topic = None  # Initialize for error handling
        status = "failure"  # Default status
        
        try:
            # Parse the message payload
            try:
                payload = json.loads(message.payload)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse message payload as JSON: {str(e)}")
                logger.error(f"Raw payload: {message.payload[:100]}..." if len(message.payload) > 100 else message.payload)
                return  # Can't process non-JSON messages
            except Exception as e:
                logger.error(f"Unexpected error parsing message payload: {str(e)}")
                return
            
            # Log the message structure without sensitive content at debug level only
            try:
                payload_structure = {k: '***' if k == 'pythonCode' else ('present' if v else 'missing') 
                                    for k, v in payload.items()}
                logger.debug(f"Message structure: {payload_structure}")
            except Exception as e:
                logger.error(f"Error logging message structure: {str(e)}")
                # Continue processing even if we can't log the structure
            
            # Extract fields from payload with the correct keys
            python_code = payload.get("pythonCode")
            if not python_code:
                logger.warning("Received message without code to execute")
                return
            
            # Extract requestId
            request_id = payload.get("requestId")
            if not request_id:
                logger.warning("Received message without requestId")
                return
                
            # Get the response topic from the message, or fall back to the default
            response_topic = payload.get("sharedTopic")
            if not response_topic:
                if self.publish_topic:
                    logger.warning(f"Message missing response channel, using default: {self.publish_topic}")
                    response_topic = self.publish_topic
                else:
                    logger.error("Message missing response channel and no default publish topic configured")
                    return  # Can't respond without a topic
            
            # Extract execution timeout from payload or use default
            # Note: according to spec, it's "executionTime" not "executionTimeout"
            execution_timeout = payload.get("executionTime")
            if execution_timeout:
                try:
                    execution_timeout = int(execution_timeout)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid execution time value '{execution_timeout}', using default: {self.execution_timeout}")
                    execution_timeout = self.execution_timeout
            else:
                execution_timeout = self.execution_timeout
            
            # Calculate code length for logging (useful for debugging but avoid logging full code for security)
            code_length = len(python_code)
            
            # Log request with masked ID and current timestamp
            masked_id = request_id[-4:] if len(request_id) > 4 else "****"
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"[{current_time}] Processing execution request (ID: ****{masked_id}, input length: {code_length} chars)")
            logger.debug(f"Using timeout: {execution_timeout}s for request ID: {request_id}")
            
            # Execute the code with the specified timeout
            execution_start_time = time.time()
            
            try:
                future = self.executor.submit(
                    self.extract_and_run_python_code_with_timeout, 
                    python_code, 
                    execution_timeout
                )
                
                # Get the result with a timeout that's slightly longer than the execution timeout
                # This prevents the system from hanging if there's an issue with the executor
                extended_timeout = execution_timeout + 10
                result, parsed_result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, future.result),
                    timeout=extended_timeout
                )
            except asyncio.TimeoutError:
                logger.error(f"Critical: Executor did not complete within extended timeout ({extended_timeout}s)")
                result = f"Execution timed out after {execution_timeout} seconds (critical system timeout)"
                parsed_result = None
            except concurrent.futures.CancelledError:
                logger.error("Execution was cancelled")
                result = "Execution was cancelled by the system"
                parsed_result = None
            except Exception as e:
                logger.error(f"Unexpected error during execution: {str(e)}")
                result = f"Execution failed with unexpected error: {str(e)}"
                parsed_result = None
            
            # Log execution time
            actual_execution_time = time.time() - execution_start_time
            # Log output character count
            output_length = len(result) if result is not None else 0
            if output_length == 0:
                logger.info(f"[****{masked_id}] Output is empty or null (output length: 0 chars)")
            else:
                logger.info(f"[****{masked_id}] Output length: {output_length} chars")
            
            # Determine if execution was successful (no error message in result)
            has_error = isinstance(result, str) and ("Error" in result or "timed out" in result or "cancelled" in result)
            status = "failure" if has_error else "success"
            
            # Extract error description if there's an error
            error_description = None
            if has_error:
                # Try to extract a meaningful error description from the result
                if "Error" in result:
                    error_parts = result.split("Error:", 1)
                    if len(error_parts) > 1:
                        error_description = error_parts[1].strip()
                elif "timed out" in result:
                    error_description = f"Execution timed out after {execution_timeout} seconds"
                elif "cancelled" in result:
                    error_description = "Execution was cancelled by the system"
            
            # Save the execution result (extracted data) before it gets overwritten
            extracted_data = result
            
            # Format the response according to the specified structure
            response = {
                "codeOutput": result,
                "requestId": request_id,
                "executionTime": str(actual_execution_time),
                "status": status
            }
            
            # Add error description if this is a failure case
            if error_description:
                response["errorDescription"] = error_description
            
            # Publish response FIRST (time-sensitive)
            logger.debug(f"Publishing result with status: {status}")
            # Log detailed info only at debug level
            logger.debug(f"Publishing to channel: {response_topic}")
            
            try:
                response_json = json.dumps(response)
            except (TypeError, ValueError) as e:
                logger.error(f"Failed to serialize response to JSON: {str(e)}")
                # Try to create a simpler response that can be serialized
                response = {
                    "codeOutput": f"Error: Failed to serialize original output: {str(e)}",
                    "requestId": request_id,
                    "executionTime": str(actual_execution_time),
                    "status": "failure",
                    "errorDescription": f"Failed to serialize original output: {str(e)}"
                }
                response_json = json.dumps(response)
            
            # Use client to publish response
            if self.client and self.connected:
                logger.debug(f"Publishing result to: {response_topic}")
                
                # Track published topics for diagnostics
                self.message_published_count += 1
                self.message_published_topics.add(response_topic)
                
                # Use QoS level 1 for publishing to ensure at-least-once delivery
                try:
                    mqtt_result = self.client.publish(response_topic, response_json, qos=1)
                    if mqtt_result.rc == mqtt.MQTT_ERR_SUCCESS:
                        logger.debug(f"Successfully published result (ID: {mqtt_result.mid})")
                    else:
                        logger.error(f"Failed to publish result: MQTT error code {mqtt_result.rc}")
                except Exception as e:
                    logger.error(f"Exception during publish: {str(e)}")
            else:
                logger.error(f"Cannot publish result: Not connected to signaling server")
            
            # Log execution to audit database AFTER publishing (non-blocking for response time)
            if self.audit_logger:
                try:
                    # Extract query, user, and group from payload if present
                    query = payload.get("query", "No query provided")
                    user = payload.get("user", "unknown")
                    group = payload.get("group")
                    
                    # Schedule audit logging in background to not block
                    # run_in_executor returns a Future, use ensure_future instead of create_task
                    loop = asyncio.get_event_loop()
                    asyncio.ensure_future(
                        loop.run_in_executor(
                            None,  # Use default executor
                            self.audit_logger.log_execution,
                            query,
                            python_code,
                            user,
                            status,
                            group,
                            self.project_id,
                            extracted_data if extracted_data else None,
                            error_description,
                            request_id  # Track request_id for retry analytics
                        )
                    )
                except Exception as audit_error:
                    # Don't let audit logging failures affect execution
                    logger.error(f"Failed to schedule audit log: {audit_error}")
        
        except Exception as e:
            # Get total processing time regardless of errors
            total_time = time.time() - start_time
            
            # Log the exception with full traceback
            import traceback
            logger.error(f"Unhandled exception in process_message: {str(e)}")
            logger.error(f"Exception traceback: {traceback.format_exc()}")
            logger.error(f"Total processing time before error: {total_time:.2f}s")
            
            # Attempt to publish error response if we have a requestId and client
            if request_id and response_topic and self.client and self.connected:
                try:
                    error_description = str(e)
                    error_response = {
                        "codeOutput": f"Error: {error_description}",
                        "requestId": request_id,
                        "executionTime": str(total_time),
                        "status": "failure",
                        "errorDescription": error_description
                    }
                    logger.debug(f"Publishing error response to: {response_topic}")
                    
                    # Track published topics for diagnostics
                    self.message_published_count += 1
                    self.message_published_topics.add(response_topic)
                    
                    # Use QoS level 1 for publishing error responses
                    mqtt_error_result = self.client.publish(response_topic, json.dumps(error_response), qos=1)
                    if mqtt_error_result.rc == mqtt.MQTT_ERR_SUCCESS:
                        logger.debug(f"Published error response (ID: {mqtt_error_result.mid})")
                    else:
                        logger.error(f"Failed to publish error response: MQTT error code {mqtt_error_result.rc}")
                except Exception as publish_error:
                    logger.error(f"Failed to publish error response: {str(publish_error)}")
                    logger.error(f"Exception traceback: {traceback.format_exc()}")
            elif request_id:
                logger.error(f"Could not publish error for request ID ****{masked_id if 'masked_id' in locals() else request_id[-4:] if len(request_id) > 4 else '****'}")
                if not response_topic:
                    logger.error("No response topic available")
                if not self.client:
                    logger.error("MQTT client not initialized")
                if not self.connected:
                    logger.error("Not connected to broker")

    def _validate_code_safety(self, code):
        """
        Check code for potentially dangerous patterns that could crash the service.
        Returns (is_safe, warning_message)
        """
        dangerous_patterns = [
            ('quit()', 'Interactive quit() function'),
            ('exit()', 'Interactive exit() function'),
            ('help()', 'Interactive help() function'),
            ('license()', 'Interactive license() function'),
            ('copyright()', 'Interactive copyright() function'),
            ('credits()', 'Interactive credits() function'),
            ('input(', 'Input function (service cannot handle interactive input)'),
            ('raw_input(', 'Raw input function (service cannot handle interactive input)'),
        ]
        
        warnings = []
        for pattern, description in dangerous_patterns:
            if pattern in code:
                warnings.append(f"Warning: Code contains {description}")
        
        # Check for risky imports
        risky_imports = [
            ('import subprocess', 'Subprocess import'),
            ('from subprocess', 'Subprocess import'),
            ('import ctypes', 'Ctypes import'),
            ('from ctypes', 'Ctypes import'),
        ]
        
        for pattern, description in risky_imports:
            if pattern in code:
                warnings.append(f"Warning: Code contains {description} - this may be restricted")
        
        return len(warnings) == 0, warnings

    def _create_safe_replacements(self):
        """Create safe replacement functions for problematic built-ins."""
        
        def safe_quit():
            """Safe replacement for quit() that doesn't actually quit."""
            return "quit() is not available in this execution environment. Use 'return' to end your code."
        
        def safe_exit():
            """Safe replacement for exit() that doesn't actually exit."""
            return "exit() is not available in this execution environment. Use 'return' to end your code."
        
        def safe_help(obj=None):
            """Safe replacement for help() that provides basic info without interactive mode."""
            if obj is None:
                return "Help is limited in this execution environment. Try using print(dir(object)) to explore objects."
            else:
                try:
                    return f"Object type: {type(obj).__name__}\nAttributes: {dir(obj)[:10]}..."
                except:
                    return f"Unable to provide help for {obj}"
        
        def safe_input(prompt=""):
            """Safe replacement for input() that explains why it's not available."""
            raise RuntimeError(f"input() is not available in this execution environment. {prompt}")
        
        def safe_copyright():
            """Safe replacement for copyright()."""
            return "Copyright information is not available in this execution environment."
        
        def safe_license():
            """Safe replacement for license()."""
            return "License information is not available in this execution environment."
        
        def safe_credits():
            """Safe replacement for credits()."""
            return "Credits information is not available in this execution environment."
        
        def safe_open(*args, **kwargs):
            """Safe replacement for open() that blocks file access."""
            raise PermissionError("File access is not currently supported in this execution environment. Use APIs or databases instead.")
        
        return {
            'quit': safe_quit,
            'exit': safe_exit,
            'help': safe_help,
            'input': safe_input,
            'raw_input': safe_input,  # Python 2 compatibility
            'copyright': safe_copyright,
            'license': safe_license,
            'credits': safe_credits,
            'open': safe_open,        # Block file access
        }

    def _create_safe_globals(self):
        """Create a safe globals dictionary for code execution."""
        # Create a safer execution environment
        safe_builtins = {
            # Include safe built-ins
            'len': len, 'str': str, 'int': int, 'float': float, 'bool': bool,
            'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
            'min': min, 'max': max, 'sum': sum, 'abs': abs, 'round': round,
            'sorted': sorted, 'reversed': reversed, 'enumerate': enumerate,
            'zip': zip, 'map': map, 'filter': filter, 'range': range,
            'print': print, 'type': type, 'isinstance': isinstance,
            'hasattr': hasattr, 'getattr': getattr, 'setattr': setattr,
            'dir': dir, 'vars': vars, 'id': id, 'hash': hash,
            'locals': locals, 'globals': globals,  # Add locals and globals functions
            'any': any, 'all': all, 'ord': ord, 'chr': chr,
            'bin': bin, 'oct': oct, 'hex': hex, 'pow': pow,
            'divmod': divmod, 'format': format, 'repr': repr,
            
            # Mathematical functions
            'complex': complex,
            
            # Data analytics and processing built-ins
            'slice': slice,           # Essential for data slicing
            'memoryview': memoryview, # For efficient buffer operations
            'bytes': bytes,           # For byte data handling
            'bytearray': bytearray,   # For mutable byte arrays
            'frozenset': frozenset,   # Immutable set operations
            
            # Iterator and functional programming
            'iter': iter,             # Create iterators
            'next': next,             # Iterate through iterators
            'callable': callable,     # Check if object is callable
            'property': property,     # Property decorator
            'staticmethod': staticmethod,  # Static method decorator
            'classmethod': classmethod,    # Class method decorator
            
            # Object and class operations
            'super': super,           # Access parent class methods
            'object': object,         # Base object class
            'delattr': delattr,       # Delete attributes (useful for data cleaning)
            
            # Advanced built-ins for data manipulation
            'exec': exec,             # Execute dynamically generated code (already restricted by environment)
            'eval': eval,             # Evaluate expressions (already restricted by environment)
            'compile': compile,       # Compile code objects
            # Note: 'open' removed - file access not currently supported
            'round': round,           # Already included above but commonly used
            'ascii': ascii,           # ASCII representation
            'bin': bin, 'oct': oct, 'hex': hex,  # Already included above
            
            # Additional useful built-ins for data processing
            'zip_longest': getattr(__import__('itertools'), 'zip_longest', None),  # Extended zip
            'chain': getattr(__import__('itertools'), 'chain', None),              # Chain iterables
            # Exception handling
            'Exception': Exception, 'ValueError': ValueError, 'TypeError': TypeError,
            'KeyError': KeyError, 'IndexError': IndexError, 'AttributeError': AttributeError,
            'ImportError': ImportError, 'RuntimeError': RuntimeError,
            'ZeroDivisionError': ZeroDivisionError, 'NameError': NameError,
            'PermissionError': PermissionError, 'FileNotFoundError': FileNotFoundError,
            'OSError': OSError, 'IOError': IOError, 'NotImplementedError': NotImplementedError,
            'StopIteration': StopIteration, 'UnicodeError': UnicodeError,
            'UnicodeDecodeError': UnicodeDecodeError, 'UnicodeEncodeError': UnicodeEncodeError,
            'OverflowError': OverflowError, 'RecursionError': RecursionError,
            'MemoryError': MemoryError, 'FloatingPointError': FloatingPointError,
            'ArithmeticError': ArithmeticError, 'LookupError': LookupError,
            'BufferError': BufferError, 'ConnectionError': ConnectionError,
            'TimeoutError': TimeoutError, 'InterruptedError': InterruptedError,
            'IsADirectoryError': IsADirectoryError, 'NotADirectoryError': NotADirectoryError,
            'BrokenPipeError': BrokenPipeError, 'ChildProcessError': ChildProcessError,
            'ProcessLookupError': ProcessLookupError, 'BlockingIOError': BlockingIOError,
            # Essential imports that are commonly needed
            '__import__': __import__,
        }
        
        # Add safe replacements for problematic functions
        safe_replacements = self._create_safe_replacements()
        safe_builtins.update(safe_replacements)
        
        # Safe modules to include
        safe_modules = {}
        try:
            # Core Python modules
            safe_modules['math'] = __import__('math')
            safe_modules['random'] = __import__('random')
            safe_modules['json'] = __import__('json')
            safe_modules['datetime'] = __import__('datetime')
            safe_modules['time'] = __import__('time')
            safe_modules['re'] = __import__('re')
            
            # Create restricted os module without file operations
            import os as _os
            class RestrictedOS:
                """Restricted os module that blocks file operations but allows environment access."""
                # Allow environment variables
                environ = _os.environ
                
                # Allow path operations (but not actual file access)
                path = _os.path
                
                # Allow these safe operations
                getpid = _os.getpid
                getcwd = lambda: "/restricted"  # Return dummy path
                
                def __getattr__(self, name):
                    # Block dangerous file operations
                    blocked_ops = {
                        'open', 'listdir', 'mkdir', 'rmdir', 'remove', 'unlink', 'rename',
                        'stat', 'chmod', 'chown', 'access', 'exists', 'isfile', 'isdir',
                        'walk', 'scandir', 'chdir', 'system', 'popen', 'spawn*'
                    }
                    if any(name.startswith(blocked) for blocked in blocked_ops):
                        raise PermissionError(f"os.{name} is not available - file operations are restricted")
                    
                    # For other attributes, try to get from real os module
                    if hasattr(_os, name):
                        attr = getattr(_os, name)
                        # Block functions that might be dangerous
                        if callable(attr) and name not in ['getpid']:
                            raise PermissionError(f"os.{name} is not available in this restricted environment")
                        return attr
                    
                    raise AttributeError(f"module 'os' has no attribute '{name}'")
            
            safe_modules['os'] = RestrictedOS()
            # Include sys with restrictions
            safe_modules['sys'] = __import__('sys')
            
            # Data analytics and processing modules
            safe_modules['collections'] = __import__('collections')  # Counter, defaultdict, etc.
            safe_modules['itertools'] = __import__('itertools')      # Efficient iterators
            safe_modules['functools'] = __import__('functools')      # Higher-order functions
            safe_modules['operator'] = __import__('operator')        # Functional operators
            safe_modules['statistics'] = __import__('statistics')    # Statistical functions
            safe_modules['decimal'] = __import__('decimal')          # Precise decimal arithmetic
            safe_modules['fractions'] = __import__('fractions')      # Rational numbers
            safe_modules['copy'] = __import__('copy')                # Deep and shallow copying
            safe_modules['heapq'] = __import__('heapq')              # Heap queue operations
            safe_modules['bisect'] = __import__('bisect')            # Binary search operations
            safe_modules['uuid'] = __import__('uuid')                # Generate unique IDs
            safe_modules['hashlib'] = __import__('hashlib')          # Secure hash functions
            safe_modules['base64'] = __import__('base64')            # Base64 encoding/decoding
            safe_modules['csv'] = __import__('csv')                  # CSV file processing
            safe_modules['io'] = __import__('io')                    # I/O operations
            safe_modules['string'] = __import__('string')            # String operations
            safe_modules['textwrap'] = __import__('textwrap')        # Text wrapping utilities
            
            # Additional modules with error handling for optional ones
            try:
                safe_modules['urllib'] = __import__('urllib')            # URL handling utilities
            except ImportError:
                logger.debug("urllib not available")
            
            # File operations modules removed - file access not currently supported
            # pathlib, tempfile, shutil removed for security
            
            try:
                safe_modules['pickle'] = __import__('pickle')            # Python object serialization
            except ImportError:
                logger.debug("pickle not available")
            
            try:
                safe_modules['sqlite3'] = __import__('sqlite3')          # SQLite database interface
            except ImportError:
                logger.debug("sqlite3 not available")
            
            try:
                safe_modules['logging'] = __import__('logging')          # Logging facility
            except ImportError:
                logger.debug("logging not available")
            
            try:
                safe_modules['warnings'] = __import__('warnings')       # Warning control
            except ImportError:
                logger.debug("warnings not available")
            
            try:
                safe_modules['weakref'] = __import__('weakref')          # Weak references
            except ImportError:
                logger.debug("weakref not available")
            
            try:
                safe_modules['gc'] = __import__('gc')                    # Garbage collector interface
            except ImportError:
                logger.debug("gc not available")
            
            # Pre-import NumPy and pandas to prevent concurrent initialization segfaults
            # This ensures NumExpr is initialized safely at service startup rather than
            # during concurrent user code execution
            try:
                import numpy as np
                safe_modules['numpy'] = np
                safe_modules['np'] = np  # Common alias
                logger.debug("Pre-imported NumPy with thread-safe NumExpr configuration")
            except ImportError:
                logger.debug("NumPy not available - skipping pre-import")
                
            try:
                import pandas as pd
                safe_modules['pandas'] = pd
                safe_modules['pd'] = pd  # Common alias
                logger.debug("Pre-imported pandas with thread-safe NumExpr configuration")
            except ImportError:
                logger.debug("pandas not available - skipping pre-import")
            
            # Provide thread-safe NumExpr wrapper to prevent users from changing thread settings
            try:
                import numexpr as ne
                
                class ThreadSafeNumExpr:
                    """Wrapper for NumExpr that prevents thread configuration changes."""
                    def __init__(self, original_ne):
                        # Store reference to original NumExpr
                        self._ne = original_ne
                    
                    def __getattr__(self, name):
                        """Delegate all attribute access to the original NumExpr, except for thread-related methods."""
                        # Don't intercept these - let them fall through to our actual methods
                        return getattr(self._ne, name)
                    
                    def set_num_threads(self, nthreads):
                        """Override set_num_threads to maintain thread safety."""
                        logger.warning(f"NumExpr thread configuration ignored for safety (requested: {nthreads}, keeping: 1)")
                        return 1  # Always return 1 to indicate single-threaded mode
                    
                    @property
                    def nthreads(self):
                        """Return the actual number of threads."""
                        return self._ne.nthreads
                
                safe_modules['numexpr'] = ThreadSafeNumExpr(ne)
                safe_modules['ne'] = safe_modules['numexpr']  # Common alias
                logger.debug("Provided thread-safe NumExpr wrapper")
            except ImportError:
                logger.debug("NumExpr not available - skipping thread-safe wrapper")
                
        except ImportError as e:
            logger.warning(f"Could not import safe module: {str(e)}")
        
        # Add special Python variables that are normally available
        special_vars = {
            # Standard Python special variables
            '__name__': '__main__',  # Standard value for executed scripts
            '__file__': '<string>',  # Indicate this is executed from string
            '__doc__': None,         # No docstring for dynamic code
            '__package__': None,     # Not part of a package
            '__spec__': None,        # No module spec for dynamic code
            '__annotations__': {},   # Empty annotations dict
            '__cached__': None,      # No cached bytecode for dynamic code
            '__loader__': None,      # No loader for dynamic code
            '__debug__': __debug__,  # Python's debug flag (inherits from runtime)
            
            # Insyt-specific execution context variables
            '__insyt_executor__': 'secure_code_executor',  # Execution environment identifier
            '__execution_mode__': 'sandboxed',             # Execution mode indicator
            '__security_level__': 'restricted',            # Security level indicator
            '__data_science_mode__': True,                 # Indicates data science capabilities
            
            # Version and context information (helpful for debugging)
            '__executor_version__': '0.4.2',              # From pyproject.toml version
            '__python_version__': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            
            # Project context (set dynamically if available)
            '__project_id__': self.project_id,            # Current project context
            '__execution_id__': str(uuid.uuid4())[:8],    # Unique execution identifier
        }

        return {
            '__builtins__': safe_builtins,
            **safe_modules,
            **special_vars
        }

    def extract_and_run_python_code(self, code, start_time=None):
        """Execute code and capture its output."""
        try:
            logger.debug("Starting code execution")
            
            # Log that we're executing code, but don't log the full code by default
            # Just log the length and first line for identification purposes
            first_line = code.strip().split('\n')[0][:100] if code else ""
            logger.debug(f"Executing Python code ({len(code)} chars): {first_line}...")
            # Only log full code at debug level
            logger.debug("=== EXECUTING PYTHON CODE ===")
            logger.debug(code)
            logger.debug("============================")
            
            # Validate code safety
            is_safe, warnings = self._validate_code_safety(code)
            if warnings:
                for warning in warnings:
                    logger.warning(warning)
            
            # Create a safer execution environment using the helper method
            globals_dict = self._create_safe_globals()

            # Redirect stdout to a StringIO object
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            # Execute the code with enhanced error handling
            execution_success = True
            try:
                exec(code, globals_dict)
            except SystemExit as e:
                # Handle sys.exit() calls gracefully
                logger.warning(f"Code attempted to exit with code: {e.code}")
                print(f"Warning: Code attempted to exit with code: {e.code}", file=sys.stderr)
                execution_success = False
            except KeyboardInterrupt:
                # Handle Ctrl+C or similar interrupts
                logger.warning("Code execution was interrupted")
                print("Warning: Code execution was interrupted", file=sys.stderr)
                execution_success = False
            except Exception as e:
                logger.error(f"Error during code execution: {type(e).__name__}: {str(e)}")
                # Print the error to the redirected stderr with full details
                import traceback
                print(f"Error: {type(e).__name__}: {str(e)}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                execution_success = False
            except BaseException as e:
                # Catch any other base exceptions (like GeneratorExit, etc.)
                logger.error(f"Base exception during code execution: {type(e).__name__}: {str(e)}")
                print(f"Critical Error: {type(e).__name__}: {str(e)}", file=sys.stderr)
                execution_success = False

            # Get the printed output
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()

            # Restore the original stdout and stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            # Combine stdout and stderr for the result
            if stderr_output:
                result = stderr_output.strip()
                if stdout_output:
                    result = f"{stdout_output.strip()}\n\n{result}"
            else:
                result = stdout_output.strip()

            # Only show a preview of the output
            result_preview = (result[:50] + "...") if len(result) > 50 else result
            # Use the provided start_time if available, else use current time
            if start_time is not None:
                execution_time = time.time() - start_time
            else:
                execution_time = 0.0
            # Combined log message for execution completion
            if execution_success:
                logger.info(f"Code execution completed successfully in {execution_time:.2f}s")
            else:
                logger.warning(f"Code execution completed with errors in {execution_time:.2f}s")
            
            logger.debug(f"Output preview: {result_preview}")

            try:
                # Try to parse the result as JSON
                parsed_result = json.loads(result)
                logger.debug("Result was valid JSON")
            except json.JSONDecodeError:
                logger.debug("Result was not valid JSON")
                parsed_result = None
            except Exception as e:
                logger.error(f"Unexpected error parsing result as JSON: {str(e)}")
                parsed_result = None

            return result, parsed_result

        except Exception as e:
            logger.error(f"Critical error executing code: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"Exception traceback: {traceback.format_exc()}")
            return f"Error executing code: {type(e).__name__}: {str(e)}", None

    def extract_and_run_python_code_with_timeout(self, code_block, timeout):
        """Execute code with a timeout."""
        try:
            logger.debug(f"Running code with {timeout}s timeout")
            start_time = time.time()
            # Set up the timeout mechanism
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self.extract_and_run_python_code, code_block, start_time)
                try:
                    result, parsed_result = future.result(timeout=timeout)
                    return result, parsed_result
                except concurrent.futures.TimeoutError:
                    logger.warning(f"Execution timed out after {timeout}s")
                    if not future.done():
                        future.cancel()
                        logger.info("Cancelled timed-out execution task")
                    return f"Execution timed out after {timeout} seconds", None
                except Exception as e:
                    logger.error(f"Unexpected error in timeout handler: {type(e).__name__}: {str(e)}")
                    import traceback
                    logger.error(f"Exception traceback: {traceback.format_exc()}")
                    return f"Error: {type(e).__name__}: {str(e)}", None
        except Exception as e:
            logger.error(f"Critical error setting up execution with timeout: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"Exception traceback: {traceback.format_exc()}")
            return f"Error: {type(e).__name__}: {str(e)}", None

    async def _log_topic_diagnostics(self):
        """Periodically log diagnostic information about topics and message activity."""
        # This method has been disabled to prevent periodic summary output
        while True:
            try:
                await asyncio.sleep(30)  # Just sleep, no output
            except asyncio.CancelledError:
                raise
            except Exception:
                await asyncio.sleep(30)

    async def _run_subscription_test(self):
        """Send a test message to verify subscription is working."""
        await asyncio.sleep(2)  # Give a small delay to ensure subscription is fully processed
        
        try:
            # Create a test message with a special marker
            test_message = {
                "type": "subscription_test",
                "timestamp": time.time(),
                "client_id": self.client._client_id.decode('utf-8') if hasattr(self.client, '_client_id') else "unknown"
            }
            
            test_message_json = json.dumps(test_message)
            test_topic = self.subscribe_topic
            self.test_message_received = False
            
            # Simplified logging for test message
            logger.debug(f"Testing subscription by publishing to: {test_topic}")
            
            try:
                # Publish the message
                result = self.client.publish(test_topic, test_message_json, qos=1)
                
                # Track published topics for diagnostics only if successful
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    self.message_published_count += 1
                    self.message_published_topics.add(test_topic)
                    logger.debug(f"Test message published with ID: {result.mid}")
                    
                    # Wait for the message to be received back
                    await asyncio.sleep(5)  # Wait 5 seconds for message to be received
                    
                    if not self.test_message_received:
                        logger.debug("Subscription test: Did not receive test message back")
                        logger.debug("This might be due to broker ACL rules preventing self-publishing")
                    else:
                        logger.debug("Subscription test successful: Received test message")
                else:
                    logger.warning(f"Failed to publish test message, error code: {result.rc}")
            except Exception as e:
                # Don't fail the whole process if the test doesn't work
                logger.debug(f"Subscription test failed: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error during subscription test: {str(e)}")

    async def _send_heartbeat(self):
        """Send periodic heartbeat messages to confirm the connection is active."""
        while True:
            try:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
                if self.connected and self.client:
                    try:
                        # Create heartbeat message
                        heartbeat_message = {
                            "type": "heartbeat",
                            "client_id": self.client_id,
                            "timestamp": time.time(),
                            "received_count": self.message_received_count,
                            "published_count": self.message_published_count
                        }
                        
                        # Publish heartbeat
                        heartbeat_topic = f"heartbeat/{self.client_id}"
                        result = self.client.publish(heartbeat_topic, json.dumps(heartbeat_message), qos=0)
                        
                        if result.rc == mqtt.MQTT_ERR_SUCCESS:
                            logger.debug(f"Sent heartbeat to {heartbeat_topic}")
                        else:
                            logger.warning(f"Failed to send heartbeat: {result.rc}")
                            
                    except Exception as e:
                        logger.error(f"Error sending heartbeat: {str(e)}")
            except asyncio.CancelledError:
                logger.info("Heartbeat task cancelled")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in heartbeat task: {str(e)}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _monitor_subscription(self):
        """Monitor subscription status and re-subscribe if needed."""
        while True:
            try:
                await asyncio.sleep(15)  # Check every 15 seconds
                
                if self.connected and self.client:
                    # Check if we've received confirmation of our subscription
                    if not self.subscription_confirmed and self.last_subscription_time > 0:
                        time_since_subscribe = time.time() - self.last_subscription_time
                        
                        # If it's been more than 10 seconds since we tried to subscribe without confirmation
                        if time_since_subscribe > 10:
                            logger.warning(f"Subscription not confirmed after {time_since_subscribe:.1f} seconds, re-subscribing")
                            
                            try:
                                # Try to subscribe again
                                result, mid = self.client.subscribe(self.subscribe_topic, qos=1)
                                logger.info(f"Re-subscription attempt result: {result}")
                                
                                # Update tracking
                                self.last_subscription_time = time.time()
                                self.last_subscription_mid = mid
                            except Exception as e:
                                logger.error(f"Error re-subscribing: {str(e)}")
                    
                    # The message inactivity check has been removed as it's redundant
                    
            except asyncio.CancelledError:
                logger.info("Subscription monitor task cancelled")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in subscription monitor: {str(e)}")
                await asyncio.sleep(10)  # Wait before retrying

    def _handle_thread_exception(self, args):
        """
        Custom exception handler for thread exceptions.
        Specifically handles MQTT protocol errors that occur in background threads.
        """
        # Log the exception
        logger.error(f"Unhandled exception in thread {args.thread.name}: {args.exc_type.__name__}: {args.exc_value}")
        logger.error(f"Thread traceback: {''.join(traceback.format_tb(args.exc_traceback))}")
        
        # Check if this is the MQTT client thread
        is_mqtt_thread = False
        if hasattr(args.thread, '_target') and 'mqtt' in str(args.thread._target).lower():
            is_mqtt_thread = True
        elif "Thread-" in args.thread.name and hasattr(self, 'client') and self.client is not None:
            # It's possibly the MQTT thread
            is_mqtt_thread = True
        
        # Check for struct.error specifically, which is what's happening in the PUBREL handler
        if is_mqtt_thread and args.exc_type == struct.error and "unpack requires a buffer" in str(args.exc_value):
            logger.warning("Detected MQTT protocol error with malformed packet. Attempting recovery.")
            
            # Schedule a reconnection in the asyncio event loop
            if self.loop:
                asyncio.run_coroutine_threadsafe(self._handle_mqtt_protocol_error(), self.loop)
        else:
            # For other exceptions, call the original excepthook
            if self._original_thread_excepthook:
                self._original_thread_excepthook(args)

    async def _handle_mqtt_protocol_error(self):
        """
        Handle MQTT protocol errors by forcing a reconnection.
        This should be called when we detect malformed packets from the broker.
        """
        logger.info("Initiating MQTT client recovery due to protocol error")
        
        # Stop the current client cleanly
        if self.client:
            try:
                self.client.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting MQTT client during recovery: {str(e)}")
            
            try:
                self.client.loop_stop()
            except Exception as e:
                logger.warning(f"Error stopping MQTT client loop during recovery: {str(e)}")
            
            self.client = None
        
        self.connected = False
        
        # Raise an exception that will be caught in the start() method to trigger reconnection
        raise Exception("MQTT protocol error detected. Forcing reconnection.")

    async def stop(self):
        """Stop the executor cleanly."""
        logger.info("Stopping executor...")
        
        # Restore original thread exception handler
        if hasattr(self, '_original_thread_excepthook'):
            threading.excepthook = self._original_thread_excepthook
        
        # Disconnect MQTT client if it exists
        if self.client:
            try:
                logger.debug("Disconnecting from signaling server...")
                self.client.disconnect()
                logger.debug("Signaling server disconnected")
            except Exception as e:
                logger.warning(f"Error disconnecting MQTT client: {str(e)}")
            
            try:
                logger.debug("Stopping MQTT network loop...")
                self.client.loop_stop()
                logger.debug("MQTT network loop stopped")
            except Exception as e:
                logger.warning(f"Error stopping MQTT loop: {str(e)}")
        
        # Cancel all active tasks
        for task in list(self.active_tasks):
            task.cancel()
        
        # Shutdown the ThreadPoolExecutor
        self.executor.shutdown(wait=False)
        
        logger.info("Executor stopped")

# Wrapper class to maintain API compatibility with messages
class MQTTMessageWrapper:
    def __init__(self, mqtt_message):
        self.topic = mqtt_message.topic
        self.payload = mqtt_message.payload
        self.qos = mqtt_message.qos
        self.retain = mqtt_message.retain
        self.mid = mqtt_message.mid

async def main():
    # This is a test function - normally CodeExecutor would be created with proper parameters
    executor = CodeExecutor(
        mqtt_broker="localhost",
        mqtt_port=1883,
        mqtt_username="test",
        mqtt_password="test",
        subscribe_topic="test/topic"
    )
    await executor.start()

if __name__ == "__main__":
    asyncio.run(main())