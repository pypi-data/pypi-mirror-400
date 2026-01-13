import os
from .runtime_config import get_secret_key, get_web_config, get_db_paths

# MQTT Settings
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

# Executor Settings
POD_NAME = os.getenv('POD_NAME', 'local-executor')
MAX_WORKERS = int(os.getenv('MAX_WORKERS', '6'))

# Topic Settings
SUBSCRIBE_TOPIC = "$share/code-executors/code.execute"

# Audit Logging Settings
AUDIT_LOGGING_ENABLED = os.getenv('AUDIT_LOGGING_ENABLED', 'true').lower() == 'true'
AUDIT_MAX_SIZE_GB = float(os.getenv('AUDIT_MAX_SIZE_GB', '1.0'))
AUDIT_MAX_RETENTION_DAYS = int(os.getenv('AUDIT_MAX_RETENTION_DAYS', '60'))

# Get database paths from runtime config (persists across restarts)
_db_paths = get_db_paths()
AUDIT_DB_PATH = _db_paths['audit_db']
AUTH_DB_PATH = _db_paths['auth_db']

# Get web configuration from runtime config (persists across restarts)
_web_config = get_web_config()
WEB_INTERFACE_ENABLED = _web_config['enabled']
WEB_INTERFACE_HOST = _web_config['host']
WEB_INTERFACE_PORT = _web_config['port']

# Get secret key from runtime config (auto-generated once, persists forever)
SECRET_KEY = get_secret_key()

# Account Service Settings (for password reset)
# Priority: ENV VAR > Runtime Config > Empty string
from .runtime_config import _runtime_config
_account_service = _runtime_config.get('account_service', {})

ACCOUNT_SERVICE_URL = os.getenv('ACCOUNT_SERVICE_URL') or _account_service.get('url', '')
PROJECT_ID = os.getenv('PROJECT_ID') or _account_service.get('project_id', '')
API_KEY = os.getenv('API_KEY') or _account_service.get('api_key', '')