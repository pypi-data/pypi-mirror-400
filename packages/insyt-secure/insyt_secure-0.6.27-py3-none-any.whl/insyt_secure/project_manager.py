"""Project Manager for handling multiple CodeExecutor instances."""

import os
import sys
import asyncio
import logging
import time
import signal
import traceback
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

import requests

from insyt_secure.executor.code_executor import CodeExecutor, AuthenticationError, NetworkRestrictionError
from insyt_secure.utils.dns_cache import DNSCache

logger = logging.getLogger(__name__)

# Constants for credential acquisition
MAX_RETRIES = 5  # Maximum number of retry attempts for credential acquisition
RETRY_DELAY = 5  # Delay in seconds between retry attempts
AUTH_ERROR_DELAY = 15  # Delay in seconds after authentication error
MAX_AUTH_RETRIES = 20  # Maximum number of authentication failures before removing a project

class ProjectManager:
    """
    Manages multiple CodeExecutor instances, one for each project.
    
    This class handles the coordination of multiple independent project connections,
    allowing each to have its own credentials and connection state.
    """
    
    def __init__(self):
        """Initialize the project manager."""
        self.executors = {}  # project_id -> CodeExecutor
        self.credentials = {}  # project_id -> credentials
        self.tasks = {}  # project_id -> asyncio task
        self.running = False
        
        # Shared DNS cache across all executors
        self.dns_cache = DNSCache(ttl_seconds=86400)  # 24 hours
        logger.info("Initialized shared DNS cache with 24-hour TTL")
        
        # Project-specific settings
        self.max_workers = {}  # project_id -> max_workers
        self.timeout = {}  # project_id -> execution_timeout
        
        # Shared settings
        self.allowed_hosts = None
        self.always_allowed_domains = ["insyt.co", "localhost"]
        
    async def add_project(self, project_id: str, api_key: str, api_url: str, 
                         max_workers: int = 5, timeout: int = 30) -> bool:
        """
        Add a new project to be managed.
        
        Args:
            project_id: The project ID
            api_key: API key for authenticating with the credentials API
            api_url: The base URL of the credentials API
            max_workers: Maximum number of concurrent code executions
            timeout: Default execution timeout in seconds
            
        Returns:
            bool: True if project was added successfully, False otherwise
        """
        if project_id in self.executors:
            logger.warning(f"Project {project_id} is already being managed")
            return False
            
        logger.info(f"Adding project {project_id} to manager")
        
        # Store project-specific settings
        self.max_workers[project_id] = max_workers
        self.timeout[project_id] = timeout
        
        # Also store API credentials for later use
        self.credentials[project_id] = {
            'api_key': api_key,
            'api_url': api_url
        }
        
        # Start the project if manager is already running
        if self.running:
            # Create and start a task for this project
            try:
                logger.debug(f"Creating task for project {project_id}")
                task = asyncio.create_task(
                    self._run_project(project_id)
                )
                self.tasks[project_id] = task
                logger.debug(f"Task created for project {project_id}")
            except Exception as e:
                logger.error(f"Failed to create task for project {project_id}: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return False
            
        return True
        
    async def remove_project(self, project_id: str) -> bool:
        """
        Remove a project from management.
        
        Args:
            project_id: The project ID to remove
            
        Returns:
            bool: True if project was removed successfully, False otherwise
        """
        if project_id not in self.executors and project_id not in self.credentials:
            logger.warning(f"Project {project_id} is not being managed")
            return False
            
        logger.info(f"Removing project {project_id} from manager")
        
        # Cancel the project's task if it exists
        if project_id in self.tasks:
            task = self.tasks[project_id]
            if not task.done():
                logger.debug(f"Cancelling task for project {project_id}")
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.debug(f"Task for project {project_id} cancelled successfully")
                except Exception as e:
                    logger.error(f"Error while cancelling task for project {project_id}: {str(e)}")
            
            del self.tasks[project_id]
            logger.debug(f"Task removed for project {project_id}")
            
        # Clean up the executor
        if project_id in self.executors:
            executor = self.executors[project_id]
            # Make sure executor is stopped
            try:
                await executor.stop()
                logger.debug(f"Executor stopped for project {project_id}")
            except Exception as e:
                logger.error(f"Error stopping executor for project {project_id}: {str(e)}")
            
            del self.executors[project_id]
            logger.debug(f"Executor removed for project {project_id}")
            
        # Clean up other project-specific data
        if project_id in self.credentials:
            del self.credentials[project_id]
        if project_id in self.max_workers:
            del self.max_workers[project_id]
        if project_id in self.timeout:
            del self.timeout[project_id]
            
        logger.info(f"Project {project_id} successfully removed")
        return True
    
    def set_shared_network_options(self, allowed_hosts=None, always_allowed_domains=None):
        """Set shared network security options for all projects."""
        if allowed_hosts is not None:
            self.allowed_hosts = allowed_hosts
            
        if always_allowed_domains is not None:
            self.always_allowed_domains = always_allowed_domains
            
        logger.debug(f"Updated shared network options - allowed hosts: {self.allowed_hosts}, allowed domains: {self.always_allowed_domains}")
    
    async def start(self):
        """Start all project executors."""
        try:
            if self.running:
                logger.warning("Project manager is already running")
                return
                
            self.running = True
            logger.info("Starting project manager")
            
            # Skip signal handlers in Windows
            if os.name != 'nt':
                try:
                    self._setup_signal_handlers()
                    logger.debug("Signal handlers set up successfully")
                except Exception as e:
                    logger.warning(f"Failed to set up signal handlers: {str(e)}")
                    logger.debug(f"Signal handler setup error: {traceback.format_exc()}")
            
            # Start a task for each configured project
            project_count = 0
            for project_id in list(self.credentials.keys()):
                # Only start projects that aren't already running
                if project_id not in self.tasks:
                    try:
                        logger.debug(f"Creating task for project {project_id}")
                        task = asyncio.create_task(
                            self._run_project(project_id)
                        )
                        self.tasks[project_id] = task
                        project_count += 1
                        logger.debug(f"Task created for project {project_id}")
                    except Exception as e:
                        logger.error(f"Failed to create task for project {project_id}: {str(e)}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
            
            if project_count == 0:
                logger.warning("No projects were started")
                return
                
            logger.info(f"Started {project_count} project tasks")
            
            # Wait for all tasks to complete (they should run indefinitely)
            running_tasks = list(self.tasks.values())
            if running_tasks:
                try:
                    logger.debug(f"Waiting for {len(running_tasks)} project tasks")
                    done, pending = await asyncio.wait(
                        running_tasks, 
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    # If any task completes, log it
                    for task in done:
                        try:
                            result = task.result()
                            logger.info(f"Project task completed with result: {result}")
                        except asyncio.CancelledError:
                            logger.debug("Project task was cancelled")
                        except Exception as e:
                            logger.error(f"Project task failed with error: {str(e)}")
                            logger.error(f"Traceback: {traceback.format_exc()}")
                    
                    # If we get here, it means a task completed unexpectedly
                    logger.warning("A project task completed unexpectedly")
                    
                except asyncio.CancelledError:
                    logger.info("Project manager tasks cancelled")
                except Exception as e:
                    logger.error(f"Error waiting for project tasks: {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
            else:
                logger.warning("No project tasks to run")
        except Exception as e:
            self.running = False
            logger.error(f"Error in project manager start: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    async def stop(self):
        """Stop all project executors."""
        if not self.running:
            logger.warning("Project manager is not running")
            return
            
        logger.info("Stopping project manager")
        self.running = False
        
        # Cancel all running tasks
        for project_id, task in list(self.tasks.items()):
            if not task.done():
                logger.info(f"Cancelling task for project {project_id}")
                task.cancel()
                
        # Wait for all tasks to be cancelled
        for project_id, task in list(self.tasks.items()):
            try:
                await task
                logger.debug(f"Task for project {project_id} completed")
            except asyncio.CancelledError:
                logger.debug(f"Task for project {project_id} cancelled successfully")
            except Exception as e:
                logger.error(f"Error while cancelling task for project {project_id}: {str(e)}")
        
        # Stop all executors
        for project_id, executor in list(self.executors.items()):
            try:
                logger.debug(f"Stopping executor for project {project_id}")
                await executor.stop()
                logger.debug(f"Executor for project {project_id} stopped")
            except Exception as e:
                logger.error(f"Error stopping executor for project {project_id}: {str(e)}")
                
        # Clear all tasks
        self.tasks.clear()
        
        logger.info("All project executors stopped")
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        # Skip in Windows due to asyncio compatibility issues with signals
        if os.name == 'nt':
            return
            
        try:
            loop = asyncio.get_running_loop()
            
            # Handle SIGTERM (termination) and SIGINT (keyboard interrupt)
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(
                    sig,
                    lambda s=sig: asyncio.create_task(self._handle_signal(s))
                )
            logger.debug("Signal handlers set up successfully")
        except Exception as e:
            logger.error(f"Failed to set up signal handlers: {str(e)}")
            raise
            
    async def _handle_signal(self, sig):
        """Handle shutdown signals."""
        sig_name = signal.Signals(sig).name
        logger.info(f"Received signal {sig_name}, shutting down...")
        
        await self.stop()
        
        # Signal the main loop to exit
        loop = asyncio.get_running_loop()
        loop.stop()
    
    def get_credentials(self, project_id, api_url, api_key=None):
        """
        Get service credentials from the API.
        
        Args:
            project_id: The project ID to get credentials for
            api_url: The base URL of the credentials API
            api_key: Optional API key for authentication
            
        Returns:
            dict: Dictionary containing credentials and connection details
            
        Raises:
            Exception: If unable to get valid credentials after MAX_RETRIES
            AuthenticationError: If authentication fails
        """
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"Attempting to acquire credentials for project {project_id} (attempt {attempt}/{MAX_RETRIES})...")
                
                # Construct the full API URL
                endpoint = f"api/v1/service/broker/proxy-credentials?projectId={project_id}"
                full_url = urljoin(api_url, endpoint)
                
                logger.info(f"Requesting service credentials for project {project_id}")
                logger.debug(f"API URL: {full_url}")
                
                # Set up headers if API key is provided
                headers = {}
                if api_key:
                    headers["X-API-Key"] = api_key
                    
                # Make the API request
                response = requests.post(full_url, headers=headers, json={}, timeout=10)
                
                # Handle authentication errors
                if response.status_code == 401 or response.status_code == 403:
                    error_msg = f"Authentication failed for project {project_id}. Status code: {response.status_code}"
                    logger.error(error_msg)
                    logger.debug(f"Response: {response.text}")
                    raise AuthenticationError(error_msg)
                
                # Check if the request was successful
                if response.status_code == 200:
                    api_response = response.json()
                    
                    # Map the response to the expected format
                    broker_credentials = {
                        'username': api_response.get('username'),
                        'password': api_response.get('password'),
                        'broker': 'broker.insyt.co',  # Hard-coded broker address
                        'port': api_response.get('sslPort', 8883),
                        'topic': api_response.get('topic'),
                        'ssl_enabled': api_response.get('sslEnabled', True)
                    }
                    
                    # Validate the required credentials are present
                    required_fields = ['username', 'password', 'broker', 'port', 'topic']
                    missing_fields = [field for field in required_fields if field not in broker_credentials or not broker_credentials[field]]
                    
                    if missing_fields:
                        error_msg = f"Missing required credentials: {', '.join(missing_fields)}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    
                    logger.info(f"Credentials received successfully for project {project_id}")
                    
                    # For debugging, log parts of the credential info
                    masked_username = broker_credentials['username'][:3] + "..." if broker_credentials['username'] else None
                    masked_password = "***" if broker_credentials['password'] else None
                    logger.debug(f"Broker: {broker_credentials['broker']}:{broker_credentials['port']}")
                    logger.debug(f"Topic: {broker_credentials['topic']}")
                    logger.debug(f"Username: {masked_username}, Password: {masked_password}")
                    
                    return broker_credentials
                else:
                    logger.error(f"Failed to get credentials for project {project_id}. Status code: {response.status_code}")
                    logger.debug(f"Response: {response.text}")
                    
            except AuthenticationError:
                # Re-raise authentication errors to be handled by the caller
                raise
            except requests.RequestException as e:
                logger.error(f"Request error for project {project_id}: {str(e)}")
            except ValueError as e:
                logger.error(f"Value error for project {project_id}: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error for project {project_id}: {str(e)}")
                logger.debug(f"Traceback: {traceback.format_exc()}")
            
            # If we've reached the maximum number of retries, raise an exception
            if attempt >= MAX_RETRIES:
                error_msg = f"Failed to acquire valid credentials for project {project_id} after {MAX_RETRIES} attempts"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Wait before retrying
            logger.info(f"Retrying credential acquisition in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
    
    async def _run_project(self, project_id):
        """
        Run a single project executor.
        
        This method acquires credentials, starts the executor, and handles
        reconnection and credential refreshing as needed.
        
        Args:
            project_id: The project ID
        """
        if project_id not in self.credentials:
            logger.error(f"No credentials found for project {project_id}")
            return
            
        # Get the API credentials for this project
        project_config = self.credentials[project_id]
        api_key = project_config.get('api_key')
        api_url = project_config.get('api_url')
        
        if not api_key or not api_url:
            logger.error(f"Missing API credentials for project {project_id}")
            return
        
        consecutive_auth_errors = 0
        
        logger.debug(f"Starting project loop for {project_id}")
        
        while self.running:
            try:
                # Get credentials for this project
                # We don't import get_credentials from main to avoid circular imports
                logger.info(f"Acquiring credentials for project {project_id}")
                try:
                    broker_credentials = self.get_credentials(project_id, api_url, api_key)
                    logger.info(f"Successfully acquired credentials for project {project_id}")
                except AuthenticationError as e:
                    logger.error(f"Authentication error for project {project_id}: {str(e)}")
                    consecutive_auth_errors += 1
                    if consecutive_auth_errors >= MAX_AUTH_RETRIES:
                        logger.critical(f"Too many consecutive authentication errors ({consecutive_auth_errors}) for project {project_id}")
                        logger.critical(f"Removing project {project_id} from management")
                        await self.remove_project(project_id)
                        return
                    logger.info(f"Waiting {AUTH_ERROR_DELAY} seconds before retrying...")
                    await asyncio.sleep(AUTH_ERROR_DELAY)
                    continue
                except Exception as e:
                    logger.error(f"Error acquiring credentials for project {project_id}: {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    await asyncio.sleep(RETRY_DELAY)
                    continue
                
                # Reset auth error counter if we successfully got credentials
                if consecutive_auth_errors > 0:
                    logger.info(f"Successfully recovered after {consecutive_auth_errors} authentication errors for project {project_id}")
                    consecutive_auth_errors = 0
                
                # Create or get executor
                if project_id not in self.executors:
                    logger.info(f"Creating new executor for project {project_id}")
                    executor = CodeExecutor(
                        mqtt_broker=broker_credentials['broker'],
                        mqtt_port=int(broker_credentials['port']),
                        mqtt_username=broker_credentials['username'],
                        mqtt_password=broker_credentials['password'],
                        subscribe_topic=broker_credentials['topic'],
                        publish_topic=broker_credentials.get('response_topic', f"response/{broker_credentials['topic']}"),
                        ssl_enabled=broker_credentials.get('ssl_enabled', True),
                        allowed_ips=self.allowed_hosts,
                        always_allowed_domains=self.always_allowed_domains,
                        max_workers=self.max_workers.get(project_id, 5),
                        execution_timeout=self.timeout.get(project_id, 30),
                        project_id=project_id
                    )
                    # Use shared DNS cache
                    executor.dns_cache = self.dns_cache
                    self.executors[project_id] = executor
                else:
                    # Update existing executor with new credentials
                    logger.info(f"Updating credentials for existing project {project_id}")
                    executor = self.executors[project_id]
                    executor.mqtt_broker = broker_credentials['broker']
                    executor.mqtt_port = int(broker_credentials['port'])
                    executor.mqtt_username = broker_credentials['username']
                    executor.mqtt_password = broker_credentials['password']
                    executor.subscribe_topic = broker_credentials['topic']
                    executor.publish_topic = broker_credentials.get('response_topic', f"response/{broker_credentials['topic']}")
                    executor.ssl_enabled = broker_credentials.get('ssl_enabled', True)
                
                # Start the executor
                logger.info(f"Starting executor for project {project_id}")
                try:
                    await executor.start()
                    # If we get here, the executor was stopped normally
                    logger.warning(f"Executor for project {project_id} stopped normally")
                except AuthenticationError as e:
                    logger.error(f"Authentication error starting executor for project {project_id}: {str(e)}")
                    consecutive_auth_errors += 1
                    # This is an error that requires new credentials
                except Exception as e:
                    logger.error(f"Error starting executor for project {project_id}: {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                
                # If we reach here, it means start() returned normally or with an exception,
                # which usually indicates credentials have expired or an error occurred
                logger.warning(f"Executor for project {project_id} disconnected. Getting new credentials...")
                
                # Check for too many auth errors
                if consecutive_auth_errors >= MAX_AUTH_RETRIES:
                    logger.critical(f"Too many consecutive auth errors ({consecutive_auth_errors}) for project {project_id}")
                    logger.critical(f"Removing project {project_id} from management")
                    await self.remove_project(project_id)
                    return
                
                # Wait before retry
                logger.info(f"Waiting {AUTH_ERROR_DELAY} seconds before requesting new credentials for project {project_id}")
                await asyncio.sleep(AUTH_ERROR_DELAY)
                
            except NetworkRestrictionError as e:
                logger.critical(f"Network restriction error for project {project_id}: {str(e)}")
                logger.critical(f"Removing project {project_id} due to security concerns")
                await self.remove_project(project_id)
                return
                
            except asyncio.CancelledError:
                logger.info(f"Task for project {project_id} was cancelled")
                # Clean up any resources
                if project_id in self.executors:
                    try:
                        executor = self.executors[project_id]
                        await executor.stop()
                    except Exception as e:
                        logger.error(f"Error stopping executor during cancellation for project {project_id}: {str(e)}")
                return
                
            except Exception as e:
                logger.error(f"Unexpected error for project {project_id}: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                logger.info(f"Retrying in 10 seconds for project {project_id}...")
                await asyncio.sleep(10)
                
                # If we have too many errors, consider removing the project
                consecutive_auth_errors += 1
                if consecutive_auth_errors >= MAX_AUTH_RETRIES:
                    logger.critical(f"Too many errors ({consecutive_auth_errors}) for project {project_id}, removing from management")
                    await self.remove_project(project_id)
                    return 