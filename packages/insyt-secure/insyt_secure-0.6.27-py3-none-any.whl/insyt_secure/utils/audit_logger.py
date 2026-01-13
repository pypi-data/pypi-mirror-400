"""
Audit logging system for tracking code execution requests.
Logs query, code, results, user info, and execution status.
"""
import sqlite3
import zlib
import json
import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AuditLogger:
    """Manages audit logs for code execution with automatic retention policy."""
    
    def __init__(self, db_path: str, max_size_gb: float = 1.0, max_retention_days: int = 60):
        """
        Initialize audit logger.
        
        Args:
            db_path: Path to SQLite database file
            max_size_gb: Maximum database size in GB before auto-purge
            max_retention_days: Maximum age of logs in days before auto-purge
        """
        self.db_path = db_path
        self.max_size_bytes = int(max_size_gb * 1024 * 1024 * 1024)
        self.max_retention_days = max_retention_days
        
        # Performance optimization: Don't check retention after every insert
        self._last_retention_check = time.time()
        self._retention_check_interval = 300  # Check every 5 minutes
        self._inserts_since_check = 0
        self._insert_threshold = 100  # Or after 100 inserts, whichever comes first
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Create tables and indexes if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create main audit log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    request_id TEXT,
                    user TEXT NOT NULL,
                    group_name TEXT,
                    project_id TEXT,
                    query_compressed BLOB,
                    python_code_compressed BLOB,
                    extracted_data_compressed BLOB,
                    status TEXT NOT NULL,
                    error_message TEXT
                )
            """)
            
            # Create indexes for fast filtering
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON execution_logs(timestamp DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user 
                ON execution_logs(user)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_group 
                ON execution_logs(group_name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON execution_logs(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_request_id 
                ON execution_logs(request_id)
            """)
            
            conn.commit()
        
        # Perform migration: Add project_id column if it doesn't exist
        # Note: This also creates the idx_project index
        self._migrate_add_project_id()
        
        # Perform migration: Add request_id column if it doesn't exist
        self._migrate_add_request_id()
        
        logger.info(f"Audit database initialized at {self.db_path}")
    
    def _migrate_add_project_id(self):
        """Add project_id column to existing databases (migration)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if project_id column exists
                cursor.execute("PRAGMA table_info(execution_logs)")
                columns = [row[1] for row in cursor.fetchall()]
                
                if 'project_id' not in columns:
                    logger.info("Migrating database: Adding project_id column to execution_logs")
                    cursor.execute("""
                        ALTER TABLE execution_logs 
                        ADD COLUMN project_id TEXT
                    """)
                    
                    # Create index for the new column
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_project 
                        ON execution_logs(project_id)
                    """)
                    
                    conn.commit()
                    logger.info("Database migration completed: project_id column added")
        except Exception as e:
            logger.error(f"Error during database migration: {str(e)}")
    
    def _migrate_add_request_id(self):
        """Add request_id column to existing databases (migration)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if request_id column exists
                cursor.execute("PRAGMA table_info(execution_logs)")
                columns = [row[1] for row in cursor.fetchall()]
                
                if 'request_id' not in columns:
                    logger.info("Migrating database: Adding request_id column to execution_logs")
                    cursor.execute("""
                        ALTER TABLE execution_logs 
                        ADD COLUMN request_id TEXT
                    """)
                    
                    # Create index for the new column
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_request_id 
                        ON execution_logs(request_id)
                    """)
                    
                    conn.commit()
                    logger.info("Database migration completed: request_id column added")
        except Exception as e:
            logger.error(f"Error during request_id migration: {str(e)}")
    
    @staticmethod
    def _compress(data: Optional[str]) -> Optional[bytes]:
        """Compress string data using zlib."""
        if data is None:
            return None
        return zlib.compress(data.encode('utf-8'), level=9)
    
    @staticmethod
    def _decompress(data: Optional[bytes]) -> Optional[str]:
        """Decompress zlib data to string."""
        if data is None:
            return None
        return zlib.decompress(data).decode('utf-8')
    
    def log_execution(
        self,
        query: str,
        python_code: str,
        user: str,
        status: str,
        group: Optional[str] = None,
        project_id: Optional[str] = None,
        extracted_data: Optional[str] = None,
        error_message: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> int:
        """
        Log a code execution event.
        
        Args:
            query: User's natural language query
            python_code: Generated Python code
            user: Username who executed the query
            status: Execution status ('success' or 'failure')
            group: User's group/team affiliation (optional)
            project_id: Project identifier (optional)
            extracted_data: Data returned from execution (optional)
            error_message: Error message if status is 'failure' (optional)
            request_id: Unique request identifier for tracking retries (optional)
            
        Returns:
            Log entry ID
        """
        # Compress data
        query_compressed = self._compress(query)
        code_compressed = self._compress(python_code)
        data_compressed = self._compress(extracted_data) if extracted_data else None
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO execution_logs 
                (request_id, user, group_name, project_id, query_compressed, python_code_compressed, 
                 extracted_data_compressed, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (request_id, user, group, project_id, query_compressed, code_compressed, 
                  data_compressed, status, error_message))
            
            log_id = cursor.lastrowid
            conn.commit()
        
        # Optimized retention check: Only check periodically, not every time
        self._inserts_since_check += 1
        current_time = time.time()
        
        # Check if we should enforce retention policy
        should_check = (
            self._inserts_since_check >= self._insert_threshold or  # Too many inserts
            current_time - self._last_retention_check >= self._retention_check_interval  # Too much time
        )
        
        if should_check:
            self._enforce_retention_policy()
            self._last_retention_check = current_time
            self._inserts_since_check = 0
        
        logger.info(f"Logged execution for user '{user}' with status '{status}' (ID: {log_id})")
        return log_id
    
    def _enforce_retention_policy(self):
        """Automatically purge old logs based on size and age limits."""
        try:
            # Check database size
            db_size = os.path.getsize(self.db_path)
            
            # Check if we need to purge
            needs_purge = False
            
            if db_size > self.max_size_bytes:
                logger.warning(f"Database size ({db_size / 1024 / 1024 / 1024:.2f} GB) "
                             f"exceeds limit ({self.max_size_bytes / 1024 / 1024 / 1024:.2f} GB)")
                needs_purge = True
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check for old logs
                cutoff_date = datetime.now() - timedelta(days=self.max_retention_days)
                cursor.execute("""
                    SELECT COUNT(*) FROM execution_logs 
                    WHERE timestamp < ?
                """, (cutoff_date,))
                
                old_count = cursor.fetchone()[0]
                if old_count > 0:
                    logger.warning(f"Found {old_count} logs older than {self.max_retention_days} days")
                    needs_purge = True
                
                if needs_purge:
                    # Delete oldest logs
                    deleted = self._purge_old_logs(conn, cursor, cutoff_date, db_size)
                    logger.info(f"Purged {deleted} old log entries")
                    
                    # Vacuum database to reclaim space
                    conn.execute("VACUUM")
                    logger.info("Database vacuumed successfully")
        
        except Exception as e:
            logger.error(f"Error enforcing retention policy: {e}")
    
    def _purge_old_logs(self, conn, cursor, cutoff_date, current_size) -> int:
        """Delete oldest logs to meet retention policy."""
        # First, delete by date
        cursor.execute("""
            DELETE FROM execution_logs 
            WHERE timestamp < ?
        """, (cutoff_date,))
        
        deleted = cursor.rowcount
        
        # If still over size limit, delete oldest entries
        if current_size > self.max_size_bytes:
            # Calculate how many to delete (roughly 10% more than needed)
            cursor.execute("SELECT COUNT(*) FROM execution_logs")
            total_count = cursor.fetchone()[0]
            
            # Estimate entries to delete
            to_delete = int(total_count * 0.2)  # Delete 20% of entries
            
            cursor.execute("""
                DELETE FROM execution_logs 
                WHERE id IN (
                    SELECT id FROM execution_logs 
                    ORDER BY timestamp ASC 
                    LIMIT ?
                )
            """, (to_delete,))
            
            deleted += cursor.rowcount
        
        conn.commit()
        return deleted
    
    def get_logs_summary(
        self,
        limit: int = 50,
        offset: int = 0,
        users: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
        project_ids: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get summary of logs (without full code/data) for dashboard.
        
        Args:
            limit: Maximum number of logs to return
            offset: Offset for pagination
            users: Filter by users (optional)
            groups: Filter by groups (optional)
            project_ids: Filter by project IDs (optional)
            statuses: Filter by statuses (optional)
            date_from: Start date for filtering (optional)
            date_to: End date for filtering (optional)
            users: Filter by users (optional)
            groups: Filter by groups (optional)
            statuses: Filter by statuses (optional)
            date_from: Start date filter (optional)
            date_to: End date filter (optional)
            
        Returns:
            Tuple of (logs list, total count)
        """
        query = """
            SELECT 
                id,
                timestamp,
                user,
                group_name,
                project_id,
                query_compressed,
                status,
                error_message
            FROM execution_logs
            WHERE 1=1
        """
        params = []
        
        # Apply filters
        if users:
            placeholders = ','.join('?' * len(users))
            query += f" AND user IN ({placeholders})"
            params.extend(users)
        
        if groups:
            placeholders = ','.join('?' * len(groups))
            query += f" AND group_name IN ({placeholders})"
            params.extend(groups)
        
        if project_ids:
            placeholders = ','.join('?' * len(project_ids))
            query += f" AND project_id IN ({placeholders})"
            params.extend(project_ids)
        
        if statuses:
            placeholders = ','.join('?' * len(statuses))
            query += f" AND status IN ({placeholders})"
            params.extend(statuses)
        
        if date_from:
            query += " AND timestamp >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND timestamp <= ?"
            params.append(date_to)
        
        # Get total count
        count_query = query.replace(
            "SELECT id, timestamp, user, group_name, project_id, query_compressed, status, error_message",
            "SELECT COUNT(*)"
        )
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute(count_query, params)
            result = cursor.fetchone()
            total = result[0] if result else 0
            
            # Get paginated results
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
        
        # Format results with query preview
        logs = []
        for row in rows:
            # Decompress query and get preview (first 100 chars)
            full_query = self._decompress(row[5])
            query_preview = full_query[:100] + "..." if full_query and len(full_query) > 100 else full_query
            
            logs.append({
                'id': row[0],
                'timestamp': row[1],
                'user': row[2],
                'group': row[3] or '—',
                'project_id': row[4] or '—',
                'query_preview': query_preview or '—',
                'status': row[6],
                'has_error': bool(row[7])
            })
        
        return logs, total
    
    def get_log_detail(self, log_id: int) -> Optional[Dict[str, Any]]:
        """
        Get full details of a specific log entry.
        
        Args:
            log_id: ID of the log entry
            
        Returns:
            Full log details with decompressed data
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    id, timestamp, user, group_name, project_id,
                    query_compressed, python_code_compressed, 
                    extracted_data_compressed, status, error_message
                FROM execution_logs
                WHERE id = ?
            """, (log_id,))
            
            row = cursor.fetchone()
        
        if not row:
            return None
        
        return {
            'id': row[0],
            'timestamp': row[1],
            'user': row[2],
            'group': row[3],
            'project_id': row[4],
            'query': self._decompress(row[5]),
            'python_code': self._decompress(row[6]),
            'extracted_data': self._decompress(row[7]),
            'status': row[8],
            'error_message': row[9]
        }
    
    def get_analytics(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        project_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get analytics data for dashboard.
        
        Args:
            date_from: Start date for analytics
            date_to: End date for analytics
            project_ids: Filter by project IDs (optional)
            
        Returns:
            Analytics data dictionary
        """
        query_base = "SELECT {} FROM execution_logs WHERE 1=1"
        params = []
        
        if date_from:
            query_base += " AND timestamp >= ?"
            params.append(date_from)
        
        if date_to:
            query_base += " AND timestamp <= ?"
            params.append(date_to)
        
        if project_ids:
            placeholders = ','.join('?' * len(project_ids))
            query_base += f" AND project_id IN ({placeholders})"
            params.extend(project_ids)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total unique executions - count unique request_ids (final status only) + legacy entries without request_id
            # This gives us the true count of unique requests, not counting retries multiple times
            cursor.execute(
                query_base.format("COUNT(*)") + 
                " AND (request_id IS NULL OR id IN ("
                "   SELECT MAX(id) FROM execution_logs "
                "   WHERE request_id IS NOT NULL "
                "   GROUP BY request_id"
                "))", 
                params
            )
            total_executions = cursor.fetchone()[0]
            
            # Success/failure rates - count only the FINAL status per unique request_id
            # For requests with a request_id, we take only the latest entry (by id/timestamp)
            # For requests without request_id (legacy), we count each individually
            cursor.execute(
                query_base.format("status, COUNT(*)") + 
                " AND (request_id IS NULL OR id IN ("
                "   SELECT MAX(id) FROM execution_logs "
                "   WHERE request_id IS NOT NULL "
                "   GROUP BY request_id"
                ")) GROUP BY status", 
                params
            )
            status_counts = dict(cursor.fetchall())
            
            success_count = status_counts.get('success', 0)
            failed_count = status_counts.get('failure', 0)
            
            # Most active users
            cursor.execute(
                query_base.format("user, COUNT(*) as count") + " GROUP BY user ORDER BY count DESC LIMIT 10",
                params
            )
            top_users = [{'user': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            # Top groups - use COALESCE to show placeholder for NULL/empty group names
            cursor.execute(
                query_base.format("COALESCE(NULLIF(group_name, ''), 'Ungrouped') as group_display, COUNT(*) as count") + 
                " GROUP BY group_display ORDER BY count DESC LIMIT 10",
                params
            )
            top_groups = [{'group': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            # Execution trends (daily) with success/failure breakdown
            cursor.execute(
                query_base.format("DATE(timestamp) as date, status, COUNT(*) as count") + 
                " GROUP BY DATE(timestamp), status ORDER BY date DESC LIMIT 60",
                params
            )
            trends_raw = cursor.fetchall()
            
            # Organize trends by date with success/failure counts
            trends_by_date = {}
            for row in trends_raw:
                date_str, status, count = row
                if date_str not in trends_by_date:
                    trends_by_date[date_str] = {'date': date_str, 'success': 0, 'failure': 0, 'total': 0}
                trends_by_date[date_str][status] = count
                trends_by_date[date_str]['total'] += count
            
            # Convert to sorted list (oldest to newest)
            trends = sorted(trends_by_date.values(), key=lambda x: x['date'])[-30:]  # Last 30 days
            
            # Debug logging
            logger.debug(f"Analytics query returned {len(trends)} trend data points")
            if len(trends) > 0:
                logger.debug(f"First trend: {trends[0]}, Last trend: {trends[-1]}")
            else:
                logger.warning("No trend data returned from query - checking if data exists")
                cursor.execute("SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM execution_logs WHERE 1=1" + 
                             (" AND timestamp >= ?" if date_from else "") + 
                             (" AND timestamp <= ?" if date_to else ""),
                             [p for p in ([date_from] if date_from else []) + ([date_to] if date_to else [])])
                count, min_ts, max_ts = cursor.fetchone()
                logger.warning(f"Total logs: {count}, Date range: {min_ts} to {max_ts}")
        
        # Calculate trend comparison (current period vs previous period)
        prev_total, prev_success, prev_failed = self._get_previous_period_stats(date_from, date_to, project_ids)
        
        def calc_trend(current, previous):
            if previous == 0:
                return 100.0 if current > 0 else 0.0
            return ((current - previous) / previous) * 100
            
        current_rate = (success_count / total_executions * 100) if total_executions > 0 else 0
        prev_rate = (prev_success / prev_total * 100) if prev_total > 0 else 0
        
        return {
            'total_executions': total_executions,
            'success_count': success_count,
            'failed_count': failed_count,
            'success_rate': current_rate,
            'top_users': top_users,
            'top_groups': top_groups,
            'execution_trends': trends,
            # Trend comparisons vs previous period
            'trends': {
                'total': calc_trend(total_executions, prev_total),
                'success': calc_trend(success_count, prev_success),
                'failed': calc_trend(failed_count, prev_failed),
                'rate': current_rate - prev_rate
            },
            'previous_period': {
                'total': prev_total,
                'success': prev_success,
                'failed': prev_failed,
            }
        }
    
    def _get_previous_period_stats(
        self,
        date_from: Optional[datetime],
        date_to: Optional[datetime],
        project_ids: Optional[List[str]]
    ) -> Tuple[int, int, int]:
        """
        Get stats for the previous equivalent period.
        
        If current period is 7 days, previous period is the 7 days before that.
        
        Returns:
            Tuple of (total, success_count, failed_count)
        """
        if not date_from or not date_to:
            # No date filter, can't calculate previous period
            return 0, 0, 0
        
        # Calculate period duration
        period_duration = date_to - date_from
        
        # Previous period ends where current period starts
        prev_date_to = date_from
        prev_date_from = date_from - period_duration
        
        # Build query
        query_base = "SELECT {} FROM execution_logs WHERE timestamp >= ? AND timestamp < ?"
        params = [prev_date_from, prev_date_to]
        
        if project_ids:
            placeholders = ','.join('?' * len(project_ids))
            query_base += f" AND project_id IN ({placeholders})"
            params.extend(project_ids)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total count (final status only for request_ids)
            cursor.execute(
                query_base.format("COUNT(*)") + 
                " AND (request_id IS NULL OR id IN ("
                "   SELECT MAX(id) FROM execution_logs "
                "   WHERE request_id IS NOT NULL "
                "   GROUP BY request_id"
                "))", 
                params
            )
            total = cursor.fetchone()[0]
            
            # Status breakdown
            cursor.execute(
                query_base.format("status, COUNT(*)") + 
                " AND (request_id IS NULL OR id IN ("
                "   SELECT MAX(id) FROM execution_logs "
                "   WHERE request_id IS NOT NULL "
                "   GROUP BY request_id"
                ")) GROUP BY status", 
                params
            )
            status_counts = dict(cursor.fetchall())
            
            success = status_counts.get('success', 0)
            failed = status_counts.get('failure', 0)
        
        return total, success, failed
    
    def get_distinct_values(self) -> Dict[str, List[str]]:
        """Get distinct users, groups, project IDs, and statuses for filter dropdowns."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get distinct users
            cursor.execute("SELECT DISTINCT user FROM execution_logs ORDER BY user")
            users = [row[0] for row in cursor.fetchall()]
            
            # Get distinct groups (excluding NULL)
            cursor.execute("SELECT DISTINCT group_name FROM execution_logs WHERE group_name IS NOT NULL ORDER BY group_name")
            groups = [row[0] for row in cursor.fetchall()]
            
            # Get distinct project IDs (excluding NULL)
            cursor.execute("SELECT DISTINCT project_id FROM execution_logs WHERE project_id IS NOT NULL ORDER BY project_id")
            project_ids = [row[0] for row in cursor.fetchall()]
            
            # Get distinct statuses
            cursor.execute("SELECT DISTINCT status FROM execution_logs ORDER BY status")
            statuses = [row[0] for row in cursor.fetchall()]
        
        return {
            'users': users,
            'groups': groups,
            'project_ids': project_ids,
            'statuses': statuses
        }
    
    def update_retention_policy(self, max_size_gb: Optional[float] = None, 
                               max_retention_days: Optional[int] = None):
        """Update retention policy settings."""
        if max_size_gb is not None:
            self.max_size_bytes = int(max_size_gb * 1024 * 1024 * 1024)
            logger.info(f"Updated max database size to {max_size_gb} GB")
        
        if max_retention_days is not None:
            self.max_retention_days = max_retention_days
            logger.info(f"Updated max retention to {max_retention_days} days")
        
        # Immediately enforce new policy
        self._enforce_retention_policy()
