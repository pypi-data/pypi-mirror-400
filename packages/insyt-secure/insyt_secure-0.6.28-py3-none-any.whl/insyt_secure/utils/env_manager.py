"""
Environment Presets Manager - Secure storage and retrieval of environment variables.
Provides encrypted storage with Fernet encryption derived from SECRET_KEY.
"""
import sqlite3
import os
import re
import base64
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import logging

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class EnvPresetManager:
    """Manages environment variable presets with encryption."""
    
    # Reserved environment variable names that shouldn't be overridden
    RESERVED_KEYS = {
        'PATH', 'HOME', 'USER', 'SHELL', 'TERM', 'PWD', 
        'LANG', 'TZ', 'TMPDIR', 'PYTHONPATH', 'PYTHONHOME',
        'LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH', 'SYSTEMROOT'
    }
    
    # Session duration for viewing unmasked values (10 minutes)
    VIEW_SESSION_DURATION_MINUTES = 10
    
    def __init__(self, db_path: str, secret_key: str):
        """
        Initialize environment preset manager.
        
        Args:
            db_path: Path to SQLite database file
            secret_key: Secret key for deriving encryption key
        """
        self.db_path = db_path
        self.secret_key = secret_key
        
        # Derive Fernet encryption key from SECRET_KEY
        self._encryption_key = self._derive_encryption_key(secret_key)
        self._fernet = Fernet(self._encryption_key)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _derive_encryption_key(self, secret_key: str) -> bytes:
        """
        Derive a Fernet-compatible encryption key from SECRET_KEY.
        
        Args:
            secret_key: The application's secret key
            
        Returns:
            Base64-encoded 32-byte key for Fernet
        """
        # SHA256 hash gives us 32 bytes
        key_hash = hashlib.sha256(secret_key.encode()).digest()
        # Base64 encode for Fernet compatibility
        return base64.urlsafe_b64encode(key_hash)
    
    def _init_database(self):
        """Create tables and indexes if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Environment presets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS env_presets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preset_name TEXT UNIQUE NOT NULL,
                    project_id TEXT DEFAULT NULL,
                    description TEXT,
                    created_by TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Environment variables table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS env_variables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preset_id INTEGER NOT NULL,
                    key_name TEXT NOT NULL,
                    encrypted_value BLOB NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (preset_id) REFERENCES env_presets(id) ON DELETE CASCADE,
                    UNIQUE(preset_id, key_name)
                )
            """)
            
            # View sessions table (for time-limited value visibility)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS env_view_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_token TEXT UNIQUE NOT NULL,
                    username TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_preset_project 
                ON env_presets(project_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_variable_preset 
                ON env_variables(preset_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_token 
                ON env_view_sessions(session_token)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_expiry 
                ON env_view_sessions(expires_at)
            """)
            
            conn.commit()
        
        logger.info(f"Environment presets database initialized at {self.db_path}")
    
    @staticmethod
    def validate_key_name(key: str) -> Tuple[bool, str]:
        """
        Validate environment variable key name.
        
        Rules:
        1. Must start with letter or underscore
        2. Can only contain letters, numbers, underscores
        3. Length: 1-255 characters
        4. Cannot be reserved system names
        
        Args:
            key: The environment variable key name
            
        Returns:
            (is_valid, error_message)
        """
        if not key:
            return False, "Key cannot be empty"
        
        if len(key) > 255:
            return False, "Key too long (max 255 characters)"
        
        # Must start with letter or underscore
        if not re.match(r'^[A-Za-z_]', key):
            return False, "Key must start with a letter or underscore"
        
        # Can only contain alphanumeric and underscores
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', key):
            return False, "Key can only contain letters, numbers, and underscores"
        
        # Check reserved names
        if key.upper() in EnvPresetManager.RESERVED_KEYS:
            return False, f"'{key}' is a reserved system variable"
        
        return True, ""
    
    def _encrypt_value(self, value: str) -> bytes:
        """Encrypt a value using Fernet."""
        return self._fernet.encrypt(value.encode('utf-8'))
    
    def _decrypt_value(self, encrypted_value: bytes) -> str:
        """Decrypt a value using Fernet."""
        return self._fernet.decrypt(encrypted_value).decode('utf-8')
    
    def create_preset(
        self, 
        preset_name: str, 
        created_by: str,
        project_id: Optional[str] = None,
        description: Optional[str] = None,
        variables: Optional[List[Dict[str, str]]] = None
    ) -> int:
        """
        Create a new environment preset.
        
        Args:
            preset_name: Unique name for the preset
            created_by: Username creating the preset
            project_id: Optional project ID for UI organization
            description: Optional description
            variables: Optional list of {"key": "KEY_NAME", "value": "value"} dicts
            
        Returns:
            Preset ID
            
        Raises:
            ValueError: If preset name already exists or validation fails
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if preset name already exists
            cursor.execute(
                "SELECT id FROM env_presets WHERE preset_name = ?",
                (preset_name,)
            )
            if cursor.fetchone():
                raise ValueError(f"Preset '{preset_name}' already exists")
            
            # Insert preset
            cursor.execute("""
                INSERT INTO env_presets (preset_name, project_id, description, created_by)
                VALUES (?, ?, ?, ?)
            """, (preset_name, project_id, description, created_by))
            
            preset_id = cursor.lastrowid
            
            # Add variables if provided
            if variables:
                for var in variables:
                    key = var.get('key', '').strip()
                    value = var.get('value', '')
                    
                    if not key:
                        continue  # Skip empty keys
                    
                    # Validate key
                    is_valid, error = self.validate_key_name(key)
                    if not is_valid:
                        raise ValueError(f"Invalid key '{key}': {error}")
                    
                    # Encrypt and store
                    encrypted_value = self._encrypt_value(value)
                    cursor.execute("""
                        INSERT INTO env_variables (preset_id, key_name, encrypted_value)
                        VALUES (?, ?, ?)
                    """, (preset_id, key, encrypted_value))
            
            conn.commit()
        
        logger.info(f"Created preset '{preset_name}' (ID: {preset_id}) by {created_by}")
        return preset_id
    
    def get_presets(self, include_var_count: bool = True) -> List[Dict[str, Any]]:
        """
        Get all environment presets.
        
        Args:
            include_var_count: Whether to include variable count
            
        Returns:
            List of preset dictionaries (values are NOT included, only metadata)
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, preset_name, project_id, description, 
                       created_by, created_at, updated_at
                FROM env_presets
                ORDER BY 
                    CASE WHEN project_id IS NULL THEN 1 ELSE 0 END,
                    project_id,
                    preset_name
            """)
            
            presets = []
            for row in cursor.fetchall():
                preset = dict(row)
                
                # Get variable count if requested
                if include_var_count:
                    cursor.execute(
                        "SELECT COUNT(*) FROM env_variables WHERE preset_id = ?",
                        (preset['id'],)
                    )
                    preset['variable_count'] = cursor.fetchone()[0]
                
                presets.append(preset)
        
        return presets
    
    def get_preset(self, preset_id: int, mask_values: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get a specific preset with its variables.
        
        Args:
            preset_id: The preset ID
            mask_values: Whether to mask values (●●●●●●) or show actual values
            
        Returns:
            Preset dictionary with variables, or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get preset metadata
            cursor.execute("""
                SELECT id, preset_name, project_id, description,
                       created_by, created_at, updated_at
                FROM env_presets
                WHERE id = ?
            """, (preset_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            preset = dict(row)
            
            # Get variables
            cursor.execute("""
                SELECT id, key_name, encrypted_value, created_at, updated_at
                FROM env_variables
                WHERE preset_id = ?
                ORDER BY key_name
            """, (preset_id,))
            
            variables = []
            for var_row in cursor.fetchall():
                var = {
                    'id': var_row['id'],
                    'key': var_row['key_name'],
                    'created_at': var_row['created_at'],
                    'updated_at': var_row['updated_at']
                }
                
                if mask_values:
                    var['value'] = '●' * 8  # Masked
                else:
                    var['value'] = self._decrypt_value(var_row['encrypted_value'])
                
                variables.append(var)
            
            preset['variables'] = variables
        
        return preset
    
    def update_preset(
        self,
        preset_id: int,
        preset_name: Optional[str] = None,
        project_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> bool:
        """
        Update preset metadata (not variables).
        
        Args:
            preset_id: The preset ID
            preset_name: New preset name
            project_id: New project ID for organization
            description: New description
            
        Returns:
            True if updated successfully
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if preset_name is not None:
                # Check for duplicate name
                cursor.execute(
                    "SELECT id FROM env_presets WHERE preset_name = ? AND id != ?",
                    (preset_name, preset_id)
                )
                if cursor.fetchone():
                    raise ValueError(f"Preset '{preset_name}' already exists")
                
                updates.append("preset_name = ?")
                params.append(preset_name)
            
            if project_id is not None:
                updates.append("project_id = ?")
                params.append(project_id)
            
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            
            if not updates:
                return True  # Nothing to update
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(preset_id)
            
            cursor.execute(f"""
                UPDATE env_presets
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            
            conn.commit()
            
            return cursor.rowcount > 0
    
    def update_variables(
        self,
        preset_id: int,
        variables: List[Dict[str, str]]
    ) -> bool:
        """
        Replace all variables in a preset.
        
        Args:
            preset_id: The preset ID
            variables: List of {"key": "KEY_NAME", "value": "value"} dicts
            
        Returns:
            True if updated successfully
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Verify preset exists
            cursor.execute("SELECT id FROM env_presets WHERE id = ?", (preset_id,))
            if not cursor.fetchone():
                raise ValueError(f"Preset ID {preset_id} not found")
            
            # Delete existing variables
            cursor.execute("DELETE FROM env_variables WHERE preset_id = ?", (preset_id,))
            
            # Insert new variables
            for var in variables:
                key = var.get('key', '').strip()
                value = var.get('value', '')
                
                if not key:
                    continue  # Skip empty keys
                
                # Validate key
                is_valid, error = self.validate_key_name(key)
                if not is_valid:
                    raise ValueError(f"Invalid key '{key}': {error}")
                
                # Encrypt and store
                encrypted_value = self._encrypt_value(value)
                cursor.execute("""
                    INSERT INTO env_variables (preset_id, key_name, encrypted_value)
                    VALUES (?, ?, ?)
                """, (preset_id, key, encrypted_value))
            
            # Update preset timestamp
            cursor.execute("""
                UPDATE env_presets
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (preset_id,))
            
            conn.commit()
        
        logger.info(f"Updated variables for preset ID {preset_id}")
        return True
    
    def delete_variable(self, preset_id: int, variable_id: int) -> bool:
        """
        Delete a single variable from a preset.
        
        Args:
            preset_id: The preset ID
            variable_id: The variable ID
            
        Returns:
            True if deleted successfully
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM env_variables
                WHERE id = ? AND preset_id = ?
            """, (variable_id, preset_id))
            
            if cursor.rowcount > 0:
                # Update preset timestamp
                cursor.execute("""
                    UPDATE env_presets
                    SET updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (preset_id,))
            
            conn.commit()
            
            return cursor.rowcount > 0
    
    def delete_preset(self, preset_id: int) -> bool:
        """
        Delete an entire preset (and all its variables via CASCADE).
        
        Args:
            preset_id: The preset ID
            
        Returns:
            True if deleted successfully
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM env_presets WHERE id = ?", (preset_id,))
            conn.commit()
            
            deleted = cursor.rowcount > 0
        
        if deleted:
            logger.info(f"Deleted preset ID {preset_id}")
        
        return deleted
    
    def create_view_session(self, username: str) -> str:
        """
        Create a time-limited session for viewing unmasked values.
        
        Args:
            username: The username requesting access
            
        Returns:
            Session token valid for 10 minutes
        """
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=self.VIEW_SESSION_DURATION_MINUTES)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Clean up expired sessions first
            cursor.execute(
                "DELETE FROM env_view_sessions WHERE expires_at < ?",
                (datetime.utcnow(),)
            )
            
            # Create new session
            cursor.execute("""
                INSERT INTO env_view_sessions (session_token, username, expires_at)
                VALUES (?, ?, ?)
            """, (session_token, username, expires_at))
            
            conn.commit()
        
        logger.info(f"Created view session for {username}, expires at {expires_at}")
        return session_token
    
    def validate_view_session(self, session_token: str) -> Optional[str]:
        """
        Validate a view session token.
        
        Args:
            session_token: The session token
            
        Returns:
            Username if valid, None if expired or invalid
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT username, expires_at
                FROM env_view_sessions
                WHERE session_token = ?
            """, (session_token,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            username, expires_at_str = row
            expires_at = datetime.fromisoformat(expires_at_str)
            
            if datetime.utcnow() > expires_at:
                # Session expired, delete it
                cursor.execute(
                    "DELETE FROM env_view_sessions WHERE session_token = ?",
                    (session_token,)
                )
                conn.commit()
                return None
            
            return username
    
    def get_decrypted_variables(self, preset_id: int) -> Dict[str, str]:
        """
        Get all variables from a preset as a plain dictionary (for code execution).
        
        Args:
            preset_id: The preset ID
            
        Returns:
            Dictionary of key-value pairs (decrypted)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT key_name, encrypted_value
                FROM env_variables
                WHERE preset_id = ?
            """, (preset_id,))
            
            variables = {}
            for key_name, encrypted_value in cursor.fetchall():
                variables[key_name] = self._decrypt_value(encrypted_value)
        
        return variables
    
    def get_preset_by_name(self, preset_name: str) -> Optional[int]:
        """
        Get preset ID by name.
        
        Args:
            preset_name: The preset name
            
        Returns:
            Preset ID or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id FROM env_presets WHERE preset_name = ?",
                (preset_name,)
            )
            
            row = cursor.fetchone()
            return row[0] if row else None
    
    def apply_preset(self, preset_id: int) -> Dict[str, Any]:
        """
        Apply preset variables to current process environment (os.environ).
        
        Variables are set in the current process and will be available to:
        - Code executed by code_executor
        - Child processes spawned by this instance
        - Any code that reads os.environ or os.getenv()
        
        Variables persist only for the lifetime of the current process.
        To survive restarts, use auto_apply_env_preset_id in runtime_config.json.
        
        Args:
            preset_id: The preset ID to apply
            
        Returns:
            dict: Applied variables count, preset name, and variable keys
            
        Raises:
            ValueError: If preset not found
        """
        preset = self.get_preset(preset_id, mask_values=False)
        if not preset:
            raise ValueError(f"Preset {preset_id} not found")
        
        applied_count = 0
        applied_vars = []
        
        for var in preset['variables']:
            key = var['key']
            value = var['value']
            
            # Set in current process environment
            os.environ[key] = value
            applied_count += 1
            applied_vars.append(key)
            
            logger.debug(f"Set environment variable: {key}")
        
        logger.info(
            f"Applied {applied_count} variables from preset "
            f"'{preset['preset_name']}' (ID: {preset_id})"
        )
        
        return {
            'preset_id': preset_id,
            'preset_name': preset['preset_name'],
            'applied_count': applied_count,
            'variables': applied_vars
        }
    
    def remove_preset_variables(self, preset_id: int) -> Dict[str, Any]:
        """
        Remove variables from current process environment (os.environ).
        
        Only removes variables that are currently set and match the preset.
        Reserved system variables are never removed.
        
        Args:
            preset_id: The preset ID whose variables should be removed
            
        Returns:
            dict: Removed variables count and variable keys
            
        Raises:
            ValueError: If preset not found
        """
        preset = self.get_preset(preset_id, mask_values=False)
        if not preset:
            raise ValueError(f"Preset {preset_id} not found")
        
        removed_count = 0
        removed_vars = []
        
        for var in preset['variables']:
            key = var['key']
            
            # Skip reserved keys (safety check)
            if key.upper() in self.RESERVED_KEYS:
                logger.warning(f"Skipped removing reserved variable: {key}")
                continue
            
            # Remove if exists
            if key in os.environ:
                del os.environ[key]
                removed_count += 1
                removed_vars.append(key)
                logger.debug(f"Removed environment variable: {key}")
        
        logger.info(
            f"Removed {removed_count} variables from preset "
            f"'{preset['preset_name']}' (ID: {preset_id})"
        )
        
        return {
            'preset_id': preset_id,
            'preset_name': preset['preset_name'],
            'removed_count': removed_count,
            'variables': removed_vars
        }
    
    def get_active_environment_snapshot(self) -> Dict[str, str]:
        """
        Get a snapshot of current environment variables.
        
        Useful for debugging and verifying which variables are currently set.
        Excludes reserved system variables for security.
        
        Returns:
            dict: Current environment variables (non-reserved only)
        """
        snapshot = {}
        for key, value in os.environ.items():
            # Exclude reserved system variables from snapshot
            if key.upper() not in self.RESERVED_KEYS:
                snapshot[key] = value
        
        return snapshot
