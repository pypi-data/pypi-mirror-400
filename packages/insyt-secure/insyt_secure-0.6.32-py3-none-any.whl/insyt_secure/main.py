import os
import sys
import time
import argparse
import asyncio
import socket
import threading
import logging
import logging.config
import signal
import json
import traceback
import atexit
from pathlib import Path
from urllib.parse import urljoin

# Configure NumExpr for thread safety BEFORE any imports that might use NumPy/pandas
# This prevents segmentation faults when multiple concurrent executions use data science libraries
os.environ['NUMEXPR_MAX_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'

import requests
from dotenv import load_dotenv

from insyt_secure.executor.code_executor import CodeExecutor, NetworkRestrictionError, AuthenticationError
from insyt_secure.utils.logging_config import configure_logging, UserFriendlyFormatter, LoggingFormat
from insyt_secure.utils import get_log_level_from_env
from insyt_secure.project_manager import ProjectManager

# Create a logger for this module
logger = logging.getLogger(__name__)

# Constants
MAX_RETRIES = 5  # Maximum number of retry attempts for credential acquisition
RETRY_DELAY = 5  # Delay in seconds between retry attempts
AUTH_ERROR_DELAY = 15  # Delay in seconds after authentication error before requesting new credentials
MAX_AUTH_RETRIES = 20

# PID file for web dashboard
_WEB_PID_FILE = Path('./data/insyt-audit-web.pid')


def _kill_web_dashboard():
    """Kill the web dashboard process if it's running (reads PID from file)."""
    if not _WEB_PID_FILE.exists():
        logger.debug("No web dashboard PID file found, skipping cleanup")
        return
    
    try:
        with open(_WEB_PID_FILE, 'r') as f:
            web_pid = int(f.read().strip())
        
        logger.info(f"Found web dashboard process (PID: {web_pid}), stopping it...")
        
        try:
            # Try to kill the process
            os.kill(web_pid, signal.SIGTERM)
            
            # Wait a moment for graceful shutdown
            time.sleep(1)
            
            # Check if process is still alive
            try:
                os.kill(web_pid, 0)  # Signal 0 just checks if process exists
                # Process still alive, force kill
                logger.warning(f"Web dashboard didn't stop gracefully, force killing...")
                os.kill(web_pid, signal.SIGKILL)
                time.sleep(0.5)
            except ProcessLookupError:
                # Process is already dead, good
                pass
            
            logger.info("Web dashboard stopped successfully")
            
        except ProcessLookupError:
            # Process doesn't exist
            logger.debug(f"Web dashboard process {web_pid} not found (may have already exited)")
        except PermissionError:
            logger.error(f"Permission denied to kill web dashboard process {web_pid}")
        except Exception as e:
            logger.error(f"Error killing web dashboard process: {e}")
        
        # Always try to clean up PID file
        try:
            if _WEB_PID_FILE.exists():
                _WEB_PID_FILE.unlink()
                logger.debug("Web dashboard PID file removed")
        except Exception as e:
            logger.warning(f"Failed to remove PID file: {e}")
        
    except ValueError as e:
        logger.error(f"Invalid PID in file: {e}")
        # Remove corrupted PID file
        try:
            _WEB_PID_FILE.unlink()
        except:
            pass
    except Exception as e:
        logger.warning(f"Failed to stop web dashboard: {e}")


# Register cleanup function to run on exit
atexit.register(_kill_web_dashboard)


# Note: keep this function for backward compatibility. 
# The ProjectManager now has its own implementation to avoid circular imports.
def get_credentials(project_id, api_url, api_key=None):
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
            
            # Check if the request was successful
            if response.status_code == 200:
                api_response = response.json()
                
                # Map the response to the expected format
                credentials = {
                    'username': api_response.get('username'),
                    'password': api_response.get('password'),
                    'broker': 'broker.insyt.co',  # Hard-coded broker address
                    'port': api_response.get('sslPort', 8883),
                    'topic': api_response.get('topic'),
                    'ssl_enabled': api_response.get('sslEnabled', True)
                }
                
                # Validate the required credentials are present
                required_fields = ['username', 'password', 'broker', 'port', 'topic']
                missing_fields = [field for field in required_fields if field not in credentials or not credentials[field]]
                
                if missing_fields:
                    logger.error(f"Missing required credentials: {', '.join(missing_fields)}")
                    raise ValueError(f"Missing required credentials: {', '.join(missing_fields)}")
                
                logger.info(f"Credentials received successfully for project {project_id}")
                return credentials
            else:
                logger.error(f"Failed to get credentials for project {project_id}. Status code: {response.status_code}")
                logger.debug(f"Response: {response.text}")
                
                # Handle auth errors specially
                if response.status_code in (401, 403):
                    raise AuthenticationError(f"Authentication failed for project {project_id}")
                
        except requests.RequestException as e:
            logger.error(f"Request error for project {project_id}: {str(e)}")
        except ValueError as e:
            logger.error(f"Value error for project {project_id}: {str(e)}")
        except AuthenticationError:
            # Re-raise authentication errors without retrying
            raise
        except Exception as e:
            logger.error(f"Unexpected error for project {project_id}: {str(e)}")
        
        # If we've reached the maximum number of retries, raise an exception
        if attempt >= MAX_RETRIES:
            raise Exception(f"Failed to acquire valid credentials for project {project_id} after {MAX_RETRIES} attempts")
        
        # Wait before retrying
        logger.info(f"Retrying in {RETRY_DELAY} seconds...")
        time.sleep(RETRY_DELAY)

def parse_project_config(config_str):
    """
    Parse project configuration string in the format 'project_id:api_key'.
    
    Args:
        config_str: String containing project ID and API key separated by colon
        
    Returns:
        tuple: (project_id, api_key) or None if format is invalid
    """
    if not config_str:
        return None
    
    # Strip various quote types that users might use
    config_str = config_str.strip()
    
    # Check for double backticks first (longer pattern)
    if len(config_str) >= 4 and config_str.startswith('``') and config_str.endswith('``'):
        config_str = config_str[2:-2]
    else:
        # Check for single character quotes
        quote_chars = ['"', "'", '`']
        for quote_char in quote_chars:
            if len(config_str) >= 2 and config_str.startswith(quote_char) and config_str.endswith(quote_char):
                config_str = config_str[1:-1]
                break
    
    # Handle mixed quotes by stripping any remaining quote characters from ends
    config_str = config_str.strip('"\'`')
        
    parts = config_str.split(':', 1)
    if len(parts) != 2:
        logger.warning(f"Invalid project configuration format: {config_str}")
        return None
        
    project_id, api_key = parts
    if not project_id or not api_key:
        logger.warning(f"Project ID or API key is empty in configuration: {config_str}")
        return None
        
    return (project_id.strip(), api_key.strip())

def parse_projects_str(projects_str):
    """
    Parse multiple project configurations from a comma-separated string.
    
    Args:
        projects_str: Comma-separated string of 'project_id:api_key' pairs
        
    Returns:
        list: List of (project_id, api_key) tuples
    """
    if not projects_str:
        return []
    
    # Strip various quote types that users might use around the entire string
    projects_str = projects_str.strip()
    
    # Check for double backticks first (longer pattern)
    if len(projects_str) >= 4 and projects_str.startswith('``') and projects_str.endswith('``'):
        projects_str = projects_str[2:-2]
    else:
        # Check for single character quotes
        quote_chars = ['"', "'", '`']
        for quote_char in quote_chars:
            if len(projects_str) >= 2 and projects_str.startswith(quote_char) and projects_str.endswith(quote_char):
                projects_str = projects_str[1:-1]
                break
    
    # Handle mixed quotes by stripping any remaining quote characters from ends
    projects_str = projects_str.strip('"\'`')
        
    result = []
    for project_config in projects_str.split(','):
        parsed = parse_project_config(project_config.strip())
        if parsed:
            result.append(parsed)
            
    return result

def setup_argparse():
    """Set up and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Insyt Secure Execution Service",
        epilog="The service securely executes code received via the signaling server."
    )
    
    # Project configuration
    project_group = parser.add_argument_group('Project Configuration')
    project_group.add_argument(
        "--projects",
        default=os.getenv("INSYT_PROJECTS"),
        help="Comma-separated list of 'project_id:api_key' pairs (format: 'project1:key1,project2:key2'). At least one project must be specified."
    )
    
    # API configuration
    parser.add_argument(
        "--api-url", 
        default=os.getenv("INSYT_API_URL", "https://api.account.insyt.co/"),
        help="API URL for credential acquisition (default: from INSYT_API_URL env var or https://api.account.insyt.co/)"
    )
    
    # Execution configuration
    parser.add_argument(
        "--max-workers",
        type=int,
        default=int(os.getenv("INSYT_MAX_WORKERS", "5")),
        help="Maximum number of concurrent execution workers per project (default: 5)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.getenv("INSYT_EXECUTION_TIMEOUT", "30")),
        help="Execution timeout in seconds per project (default: 30)"
    )
    
    # Network security
    parser.add_argument(
        "--allowed-hosts",
        type=str,
        default=os.getenv("INSYT_ALLOWED_HOSTS"),
        help="Comma-separated list of allowed hosts (default: from INSYT_ALLOWED_HOSTS env var)"
    )
    parser.add_argument(
        "--always-allowed-domains",
        type=str,
        default=os.getenv("INSYT_ALWAYS_ALLOWED_DOMAINS", "insyt.co,localhost"),
        help="Comma-separated list of always-allowed domains (default: insyt.co,localhost)"
    )
    
    # Logging configuration
    parser.add_argument(
        "--log-level",
        type=str,
        default=os.getenv("INSYT_LOG_LEVEL", "info"),
        choices=["debug", "info", "warning", "error", "critical"],
        help="Set the logging level (default: info)"
    )
    parser.add_argument(
        "--log-format",
        type=str,
        default=os.getenv("INSYT_LOG_FORMAT", "user_friendly"),
        choices=["user_friendly", "json", "standard"],
        help="Set the logging format (default: user_friendly)"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=os.getenv("INSYT_LOG_FILE"),
        help="Optional log file path. If not specified, logs output to console only (default: from INSYT_LOG_FILE env var)"
    )
    
    return parser

async def main():
    """Main entry point for the service."""
    # Declare project_manager here so it's available in the finally block
    project_manager = None
    
    try:
        # Parse command line arguments
        parser = setup_argparse()
        args = parser.parse_args()
        
        # Configure logging based on command line arguments or environment variables
        log_level = get_log_level_from_env(args.log_level)
        log_format = args.log_format
        
        # Map string format to enum
        format_mapping = {
            "user_friendly": LoggingFormat.USER_FRIENDLY,
            "json": LoggingFormat.JSON,
            "standard": LoggingFormat.STANDARD
        }
        logging_format = format_mapping.get(log_format, LoggingFormat.USER_FRIENDLY)
        
        # Apply logging configuration
        configure_logging(level=log_level, format=logging_format, log_file=args.log_file)
        
        # Log startup message
        logger.info("Insyt Secure Execution Service starting up")
        
        # Clean up any stale web dashboard process from previous run
        # This handles cases where the main service crashed and didn't clean up
        if _WEB_PID_FILE.exists():
            logger.info("Found stale web dashboard PID file from previous run, cleaning up...")
            _kill_web_dashboard()
        
        # Parse network security settings
        allowed_hosts = None
        if args.allowed_hosts:
            allowed_hosts = [h.strip() for h in args.allowed_hosts.split(",")]
            logger.debug(f"Using allowed hosts: {allowed_hosts}")
        
        always_allowed_domains = [d.strip() for d in args.always_allowed_domains.split(",")]
        logger.debug(f"Using always allowed domains: {always_allowed_domains}")
        
        # Parse projects from arguments
        projects = []
        
        # Parse the projects format
        if args.projects:
            projects.extend(parse_projects_str(args.projects))
        
        # Check if we have at least one valid project
        if not projects:
            logger.error("No valid project configurations found.")
            logger.error("Please specify at least one project using the --projects argument with format:")
            logger.error("  --projects \"project_id1:api_key1,project_id2:api_key2,...\"")
            logger.error("Or set the INSYT_PROJECTS environment variable with the same format.")
            sys.exit(1)
        
        # Save project config to runtime config (so web UI can access it)
        from insyt_secure.config.runtime_config import _runtime_config
        if projects:
            first_project_id, first_api_key = projects[0]
            _runtime_config.set_project_config(first_project_id, {
                'api_key': first_api_key,
                'api_url': args.api_url
            })
            # Also set as top-level for easy access
            _runtime_config.set('account_service', {
                'url': args.api_url,
                'project_id': first_project_id,
                'api_key': first_api_key
            })
            logger.debug(f"Saved project config to runtime_config.json")
        
        # Log the number of projects
        if len(projects) == 1:
            logger.info(f"Managing 1 project")
        else:
            logger.info(f"Managing {len(projects)} projects")
        
        # Initialize the project manager
        project_manager = ProjectManager()
        
        # Configure shared network options
        project_manager.set_shared_network_options(
            allowed_hosts=allowed_hosts,
            always_allowed_domains=always_allowed_domains
        )
        
        # Add projects to the manager
        for project_id, api_key in projects:
            logger.info(f"Adding project: {project_id}")
            await project_manager.add_project(
                project_id=project_id,
                api_key=api_key,
                api_url=args.api_url,
                max_workers=args.max_workers,
                timeout=args.timeout
            )
        
        # Start the project manager
        logger.info("Starting project manager...")
        try:
            await project_manager.start()
            logger.info("Project manager started successfully")
        except Exception as e:
            logger.error(f"Failed to start project manager: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            sys.exit(1)
        
        # Keep the main task running to allow for Ctrl+C handling
        while True:
            await asyncio.sleep(3600)  # Wait for 1 hour
                
    except KeyboardInterrupt:
        # Handle Ctrl+C or SIGTERM
        logger.info("Shutdown signal received. Exiting...")
        
    except Exception as e:
        # Handle any other exceptions
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
        
    finally:
        # Stop the project manager if it was created and started
        if project_manager is not None:
            try:
                logger.info("Stopping project manager...")
                await project_manager.stop()
                logger.info("Project manager stopped")
            except Exception as e:
                logger.error(f"Error stopping project manager: {str(e)}")

if __name__ == "__main__":
    # Run the main async function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)

def run_main():
    """Entry point for the command-line script."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)