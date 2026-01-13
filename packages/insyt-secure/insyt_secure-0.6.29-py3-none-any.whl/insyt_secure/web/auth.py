"""
Authentication and password management for the audit web interface.
"""
import sqlite3
import bcrypt
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging
import requests

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages user authentication and password reset functionality."""
    
    # Rate limiting for password reset attempts
    MAX_RESET_ATTEMPTS = 3
    RESET_ATTEMPT_WINDOW_MINUTES = 15
    
    def __init__(self, db_path: str, account_service_url: str, project_id: str, api_key: str, 
                 managed_projects: Optional[List[Dict[str, str]]] = None):
        """
        Initialize authentication manager.
        
        Args:
            db_path: Path to SQLite database for user credentials
            account_service_url: Base URL for account service API
            project_id: Primary project ID for account service
            api_key: API key for primary project
            managed_projects: List of all managed projects (for multi-project password reset)
                             Format: [{'project_id': 'proj1', 'api_key': 'key1'}, ...]
        """
        self.db_path = db_path
        self.account_service_url = account_service_url
        self.project_id = project_id
        self.api_key = api_key
        self.managed_projects = managed_projects or [{'project_id': project_id, 'api_key': api_key}]
        
        self._init_database()
        self._ensure_default_admin()
    
    def _init_database(self):
        """Create authentication tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME
                )
            """)
            
            # Password reset codes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS password_reset_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    code TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    FOREIGN KEY (username) REFERENCES users(username)
                )
            """)
            
            # Reset attempts tracking (for brute-force prevention)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reset_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    attempt_time DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_token TEXT UNIQUE NOT NULL,
                    username TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    FOREIGN KEY (username) REFERENCES users(username)
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_token 
                ON sessions(session_token)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_reset_code 
                ON password_reset_codes(code, username)
            """)
            
            conn.commit()
    
    def _ensure_default_admin(self):
        """Ensure default admin user exists with password 'admin'."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", ('admin',))
            
            if cursor.fetchone()[0] == 0:
                # Create default admin user
                password_hash = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt())
                cursor.execute("""
                    INSERT INTO users (username, password_hash) 
                    VALUES (?, ?)
                """, ('admin', password_hash))
                conn.commit()
                logger.info("Created default admin user (username: admin, password: admin)")
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate user and create session.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Session token if successful, None otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT password_hash FROM users WHERE username = ?
            """, (username,))
            
            row = cursor.fetchone()
            
            if not row:
                logger.warning(f"Login attempt for non-existent user: {username}")
                return None
            
            password_hash = row[0]
            
            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), password_hash):
                # Update last login
                cursor.execute("""
                    UPDATE users SET last_login = CURRENT_TIMESTAMP 
                    WHERE username = ?
                """, (username,))
                
                # Create session token
                session_token = secrets.token_urlsafe(32)
                expires_at = datetime.now() + timedelta(hours=24)
                
                cursor.execute("""
                    INSERT INTO sessions (session_token, username, expires_at)
                    VALUES (?, ?, ?)
                """, (session_token, username, expires_at))
                
                conn.commit()
                logger.info(f"User '{username}' logged in successfully")
                return session_token
            else:
                logger.warning(f"Failed login attempt for user: {username}")
                return None
    
    def validate_session(self, session_token: str) -> Optional[str]:
        """
        Validate session token and return username.
        
        Args:
            session_token: Session token to validate
            
        Returns:
            Username if session is valid, None otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, expires_at FROM sessions 
                WHERE session_token = ?
            """, (session_token,))
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            username, expires_at = row
            expires_at = datetime.fromisoformat(expires_at)
            
            if datetime.now() > expires_at:
                # Session expired
                cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
                conn.commit()
                return None
            
            return username
    
    def verify_password(self, username: str, password: str) -> bool:
        """
        Verify a user's password without creating a session.
        
        Args:
            username: Username
            password: Password to verify
            
        Returns:
            True if password is correct, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT password_hash FROM users WHERE username = ?
            """, (username,))
            
            row = cursor.fetchone()
            
            if not row:
                return False
            
            password_hash = row[0]
            
            # Verify password
            return bcrypt.checkpw(password.encode('utf-8'), password_hash)
    
    def logout(self, session_token: str):
        """
        Logout user by invalidating session.
        
        Args:
            session_token: Session token to invalidate
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
            conn.commit()
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            username: Username
            old_password: Current password
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
            
            row = cursor.fetchone()
            if not row:
                return False
            
            # Verify old password
            if not bcrypt.checkpw(old_password.encode('utf-8'), row[0]):
                logger.warning(f"Failed password change for user '{username}': incorrect old password")
                return False
            
            # Update password
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("""
                UPDATE users SET password_hash = ? WHERE username = ?
            """, (new_hash, username))
            
            # Invalidate all sessions for security
            cursor.execute("DELETE FROM sessions WHERE username = ?", (username,))
            
            conn.commit()
            logger.info(f"Password changed successfully for user '{username}'")
            return True
    
    def initiate_password_reset(self, username: str) -> Optional[str]:
        """
        Generate password reset code and send to account service.
        
        Args:
            username: Username requesting password reset
            
        Returns:
            Reset code if successful, None if rate limited or failed
        """
        # Check rate limiting
        if not self._check_reset_rate_limit(username):
            logger.warning(f"Password reset rate limit exceeded for user '{username}'")
            return None
        
        # Generate 6-digit code
        code = ''.join(secrets.choice(string.digits) for _ in range(6))
        expires_at = datetime.now() + timedelta(minutes=15)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store reset code
            cursor.execute("""
                INSERT INTO password_reset_codes (username, code, expires_at)
                VALUES (?, ?, ?)
            """, (username, code, expires_at))
            
            # Track attempt
            cursor.execute("""
                INSERT INTO reset_attempts (username) VALUES (?)
            """, (username,))
            
            conn.commit()
        
        # Send code to account service for ALL managed projects
        success_count = 0
        failed_projects = []
        
        for project in self.managed_projects:
            try:
                response = requests.post(
                    f"{self.account_service_url}/api/v1/service/broker/send-reset-code",
                    params={
                        'projectId': project['project_id'],
                        'code': code
                    },
                    headers={
                        'X-API-Key': project['api_key']
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    success_count += 1
                    logger.info(f"Password reset code sent for project '{project['project_id']}'")
                else:
                    failed_projects.append(project['project_id'])
                    logger.error(f"Account service error for project '{project['project_id']}': {response.status_code}")
            
            except Exception as e:
                failed_projects.append(project['project_id'])
                logger.error(f"Failed to send reset code to project '{project['project_id']}': {e}")
        
        # Return code if at least one project succeeded
        if success_count > 0:
            if failed_projects:
                logger.warning(f"Reset code sent to {success_count}/{len(self.managed_projects)} projects. Failed: {', '.join(failed_projects)}")
            else:
                logger.info(f"Reset code successfully sent to all {success_count} managed projects")
            return code
        else:
            logger.error("Failed to send reset code to any managed project")
            return None
    
    def _check_reset_rate_limit(self, username: str) -> bool:
        """Check if user has exceeded password reset rate limit."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Clean old attempts
            cutoff = datetime.now() - timedelta(minutes=self.RESET_ATTEMPT_WINDOW_MINUTES)
            cursor.execute("""
                DELETE FROM reset_attempts 
                WHERE attempt_time < ?
            """, (cutoff,))
            
            # Count recent attempts
            cursor.execute("""
                SELECT COUNT(*) FROM reset_attempts 
                WHERE username = ? AND attempt_time >= ?
            """, (username, cutoff))
            
            count = cursor.fetchone()[0]
            conn.commit()
            
            return count < self.MAX_RESET_ATTEMPTS
    
    def complete_password_reset(self, username: str, code: str, new_password: str) -> bool:
        """
        Complete password reset using code.
        
        Args:
            username: Username
            code: 6-digit reset code
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Find valid, unused reset code
            cursor.execute("""
                SELECT id, expires_at FROM password_reset_codes
                WHERE username = ? AND code = ? AND used = 0
                ORDER BY created_at DESC
                LIMIT 1
            """, (username, code))
            
            row = cursor.fetchone()
            
            if not row:
                logger.warning(f"Invalid reset code for user '{username}'")
                return False
            
            reset_id, expires_at = row
            expires_at = datetime.fromisoformat(expires_at)
            
            if datetime.now() > expires_at:
                logger.warning(f"Expired reset code for user '{username}'")
                return False
            
            # Update password
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("""
                UPDATE users SET password_hash = ? WHERE username = ?
            """, (new_hash, username))
            
            # Mark code as used
            cursor.execute("""
                UPDATE password_reset_codes SET used = 1 WHERE id = ?
            """, (reset_id,))
            
            # Invalidate all sessions
            cursor.execute("DELETE FROM sessions WHERE username = ?", (username,))
            
            conn.commit()
            logger.info(f"Password reset completed for user '{username}'")
            return True
    
    def fetch_project_aliases(self, project_ids: List[str]) -> Dict[str, Optional[str]]:
        """
        Fetch project aliases from account service.
        
        Args:
            project_ids: List of project IDs to fetch aliases for
            
        Returns:
            Dictionary mapping project_id -> alias (or None if not found)
            Format: {'PRJ-123': 'Production', 'PRJ-456': 'Staging', 'PRJ-789': None}
        """
        if not project_ids:
            return {}
        
        aliases = {}
        
        # Use first managed project's credentials for the API call
        # (API key only needs to match one project in the array)
        primary_project = self.managed_projects[0] if self.managed_projects else {
            'project_id': self.project_id,
            'api_key': self.api_key
        }
        
        try:
            response = requests.post(
                f"{self.account_service_url}/api/v1/service/broker/project-aliases",
                json={"projectIds": project_ids},
                headers={
                    'X-API-Key': primary_project['api_key'],
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse response: {projects: {projectId: {alias, status}, ...}}
                if 'projects' in data:
                    projects_dict = data['projects']
                    for project_id, project_info in projects_dict.items():
                        status = project_info.get('status')
                        
                        if status == 'found':
                            aliases[project_id] = project_info.get('alias')
                        else:
                            aliases[project_id] = None
                            logger.debug(f"Project '{project_id}' alias not found (status: {status})")
                
                logger.info(f"Fetched aliases for {len(aliases)}/{len(project_ids)} projects")
            else:
                logger.error(f"Failed to fetch project aliases: HTTP {response.status_code}")
                # Return None for all projects on error
                for project_id in project_ids:
                    aliases[project_id] = None
        
        except Exception as e:
            logger.error(f"Error fetching project aliases: {e}")
            # Return None for all projects on exception
            for project_id in project_ids:
                aliases[project_id] = None
        
        return aliases
    
    def cleanup_expired_data(self):
        """Clean up expired sessions and reset codes."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete expired sessions
            cursor.execute("DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP")
            
            # Delete old reset codes (older than 24 hours)
            cutoff = datetime.now() - timedelta(hours=24)
            cursor.execute("DELETE FROM password_reset_codes WHERE created_at < ?", (cutoff,))
            
            # Delete old reset attempts
            cutoff = datetime.now() - timedelta(hours=24)
            cursor.execute("DELETE FROM reset_attempts WHERE attempt_time < ?", (cutoff,))
            
            conn.commit()
