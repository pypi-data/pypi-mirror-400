"""
Daemon mode support for running web server as a background service.
This ensures the process survives terminal disconnection.
"""
import os
import sys
import signal
import atexit
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def daemonize(pid_file: Path, working_dir: Path = None):
    """
    Properly daemonize the current process using double-fork method.
    This ensures the process completely detaches from the terminal.
    
    Args:
        pid_file: Path to store the daemon PID
        working_dir: Working directory for the daemon (default: current dir)
    """
    # Check if already running
    if pid_file.exists():
        try:
            with open(pid_file, 'r') as f:
                old_pid = int(f.read().strip())
            
            # Check if process is still alive
            try:
                os.kill(old_pid, 0)
                print(f"ERROR: Daemon already running with PID {old_pid}")
                print(f"To stop it: kill {old_pid}")
                print(f"Or remove stale PID file: rm {pid_file}")
                sys.exit(1)
            except ProcessLookupError:
                # Process is dead, remove stale PID file
                pid_file.unlink()
        except Exception:
            # Corrupted PID file, remove it
            pid_file.unlink()
    
    # Ensure PID file directory exists
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    
    # First fork - creates child process
    try:
        pid = os.fork()
        if pid > 0:
            # Parent process - exit
            print(f"Starting daemon with PID {pid}...")
            sys.exit(0)
    except OSError as e:
        sys.stderr.write(f"Fork #1 failed: {e}\n")
        sys.exit(1)
    
    # Decouple from parent environment
    # Keep the working directory instead of changing to /
    # This preserves relative paths like ./data/audit_logs.db
    if working_dir:
        os.chdir(str(working_dir))
    # else: stay in current directory
    os.setsid()  # Create new session - becomes session leader
    os.umask(0)
    
    # Second fork - ensures we're not session leader
    # This prevents process from acquiring a controlling terminal
    try:
        pid = os.fork()
        if pid > 0:
            # First child exits
            sys.exit(0)
    except OSError as e:
        sys.stderr.write(f"Fork #2 failed: {e}\n")
        sys.exit(1)
    
    # We're now in the grandchild process - the actual daemon
    
    # Redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    
    # Close stdin
    si = open(os.devnull, 'r')
    os.dup2(si.fileno(), sys.stdin.fileno())
    
    # Redirect stdout and stderr to log files for debugging
    # Create logs directory if it doesn't exist
    log_dir = Path('./logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Redirect stdout and stderr to log file
    log_file = log_dir / 'audit_web_daemon.log'
    so = open(log_file, 'a+')
    se = open(log_file, 'a+')
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
    
    # Write PID file
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))
    
    # Register cleanup function
    def cleanup():
        if pid_file.exists():
            pid_file.unlink()
    
    atexit.register(cleanup)
    
    # Handle termination signals
    def signal_handler(signum, frame):
        cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


def is_daemon_running(pid_file: Path) -> bool:
    """
    Check if daemon is currently running.
    
    Args:
        pid_file: Path to PID file
        
    Returns:
        True if daemon is running, False otherwise
    """
    if not pid_file.exists():
        return False
    
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process exists
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, ValueError, FileNotFoundError):
        # Process doesn't exist or PID file is corrupted
        return False


def stop_daemon(pid_file: Path) -> bool:
    """
    Stop a running daemon.
    
    Args:
        pid_file: Path to PID file
        
    Returns:
        True if daemon was stopped, False if not running
    """
    if not pid_file.exists():
        return False
    
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        # Send SIGTERM
        os.kill(pid, signal.SIGTERM)
        
        # Wait for process to die
        import time
        for _ in range(10):
            try:
                os.kill(pid, 0)
                time.sleep(0.5)
            except ProcessLookupError:
                # Process is dead
                if pid_file.exists():
                    pid_file.unlink()
                return True
        
        # Process didn't die, force kill
        try:
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.5)
        except ProcessLookupError:
            pass
        
        if pid_file.exists():
            pid_file.unlink()
        return True
        
    except (ValueError, FileNotFoundError, ProcessLookupError):
        # PID file corrupted or process already dead
        if pid_file.exists():
            pid_file.unlink()
        return False
