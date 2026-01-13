"""Web interface module for audit dashboard."""
from .app import create_app, run_web_server
from .auth import AuthManager

__all__ = ['create_app', 'run_web_server', 'AuthManager']
