# Changelog

All notable changes to the `insyt-secure` package will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and follows the format from [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [0.6.18] - 2025-10-25

### Added
- **Environment Presets**: New secure environment variable management system
  - Web-based UI for creating and managing environment variable presets
  - Fernet encryption for all variable values (derived from existing SECRET_KEY)
  - Project categorization for UI organization (service-wide scope)
  - 10-minute time-limited view sessions for viewing unmasked values
  - Password re-authentication required to view actual values
  - Real-time validation for environment variable key names
  - Smart placeholder text guides users (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
  - CRUD operations: Create, Read, Update, Delete presets and individual variables
  - New database: `./data/env_presets.db` with encrypted storage
  - 8 new API endpoints for preset management
  - Grouping presets by project in UI for better organization

### Changed
- **Settings Page UI**: Reorganized into tabbed interface to improve navigation
  - Added 4-tab navigation: Retention Policy, Web Server, Environment Presets, Password
  - Eliminates vertical scrolling by organizing content into logical sections
  - Maintains all existing functionality with improved user experience
  - Clean visual design with icons and active state highlighting
  
### Dependencies
- **Added**: `cryptography>=41.0.0` for Fernet encryption

### Security
- Environment variable values encrypted at rest
- Masked values (●●●●●●●●) in all views by default
- Reserved system variable names blocked (PATH, HOME, etc.)
- Session-based value viewing with automatic expiry
- Unique preset names enforced
- CASCADE deletion prevents orphaned variables

### Files Changed
- `pyproject.toml` - Added cryptography dependency
- `src/insyt_secure/utils/env_manager.py` - NEW: EnvPresetManager class
- `src/insyt_secure/web/app.py` - Added 8 API routes and env_manager initialization
- `src/insyt_secure/web/auth.py` - Added verify_password() method
- `src/insyt_secure/web/templates/settings.html` - Added Environment Presets section with full UI

### Documentation
- `ENV_PRESETS_FEATURE.md` - Complete feature documentation

## [0.6.9] - 2025-10-24

### Fixed
- **Host Header Validation**: Fixed web dashboard rejecting valid hostname requests
  - Now accepts EC2 DNS names (e.g., `ec2-3-21-158-178.us-east-2.compute.amazonaws.com`)
  - Now accepts custom domain names and valid hostnames
  - Still blocks malicious host header injection attacks
  - Improved hostname validation regex to be more permissive for legitimate hostnames

## [0.6.8] - 2025-10-24

## [0.6.7] - 2025-10-24

### Fixed
- **Daemon Mode Crash**: Fixed daemon process immediately dying after start
  - Preserved working directory instead of changing to `/` (broke relative paths like `./data/`)
  - Added logging to `./logs/audit_web_daemon.log` for debugging daemon issues
  - Daemon now properly maintains access to configuration and database files

## [0.6.6] - 2025-10-24

### Changed
- **Default Network Binding**: Web dashboard now binds to `0.0.0.0` by default (all network interfaces)
  - **Breaking Change**: Previously defaulted to `127.0.0.1` (localhost only)
  - **Benefit**: Easier remote access for cloud/remote deployments (EC2, DigitalOcean, etc.)
  - **SSH Users**: Still accessible via `localhost:8080` when using VS Code Remote SSH or SSH port forwarding
  - **Security**: For localhost-only access, use `--host 127.0.0.1` flag
  - **Upgrade Note**: Existing `runtime_config.json` files will retain old `127.0.0.1` setting
    - Delete `./data/runtime_config.json` to adopt new default
    - Or manually edit the file to change `"host": "127.0.0.1"` to `"host": "0.0.0.0"`

### Documentation
- **README**: Updated with clearer access instructions for different scenarios
  - SSH tunnel access (VS Code Remote SSH users)
  - Direct IP access (remote deployments)
  - Network binding options and security considerations

## [0.6.5] - 2025-10-24

### Added
- **Daemon Mode**: Web server can now run as a true background daemon
  - New `--daemon` flag to properly detach from terminal
  - Process survives SSH disconnection and terminal closure
  - Uses double-fork method for complete session independence
  - New `--stop` flag to cleanly stop daemon
  - New `--status` flag to check if daemon is running
  
### Fixed
- **Terminal Disconnect Issue**: Web server no longer dies when SSH session ends
  - Previously, even with `nohup`, process could receive SIGHUP and terminate
  - Now properly detaches from controlling terminal
  - Dashboard remains accessible after terminal disconnect
- **Duplicate Table Rows**: Fixed execution logs table showing duplicate entries
  - Removed duplicate `<tbody>` section that was rendering logs twice
  - Table now displays each log entry exactly once

### Enhanced
- **Process Management**: Better daemon lifecycle control
  - Proper PID file management
  - Graceful shutdown on SIGTERM/SIGINT
  - Prevents multiple instances from running
  - Automatic cleanup of stale PID files
- **Dashboard UI**: Smarter column visibility in execution logs table
  - Project column automatically hidden when specific project is selected
  - Reduces redundancy and improves readability when filtering by project
  - Column shows when "All Projects" is selected

## [0.6.2] - 2025-10-23

### Added
- **Project Aliases**: Display friendly project names in audit dashboard
  - Fetches aliases from account service API endpoint `/api/v1/service/broker/project-aliases`
  - Shows format "Alias (Project-ID)" in dropdown and logs table
  - Graceful fallback to project ID if alias not found
  - Caches aliases for performance

### Enhanced
- **Dashboard UI**: Project selector and logs table now show meaningful project names
  - New `/api/project-aliases` endpoint for fetching aliases
  - Automatic alias loading on dashboard init
  - Improved user experience when managing multiple projects
  - Dropdown auto-resizes (200px-450px) to fit longer alias names without text cutoff

## [0.6.1] - 2025-10-23

### Fixed
- **Database Migration**: Fixed initialization error where `project_id` index creation was attempted before column migration
  - Moved index creation to after column migration to prevent "no such column" errors
  - Ensures seamless upgrade from pre-0.6.0 versions

### Changed
- **Data Retention**: Removed automatic deletion of NULL project_id logs during migration
  - Old audit logs are now preserved with NULL project_id values
  - New logs enforce project_id at application level
  - UI filters support viewing logs with or without project_id

## [0.6.0] - 2025-10-23

### Added
- **Multi-Project Support**: Track audit logs per project with project_id column
  - Added project_id to audit log schema with automatic database migration
  - Project selector dropdown in dashboard navigation
  - Filter logs and analytics by one or multiple projects
  - "All Projects" view for combined monitoring
  - Project count badge in UI
  - Runtime config integration (projects visible even with zero logs)

- **Multi-Project Password Reset**: Send same reset code to all managed projects
  - Reads managed projects from runtime_config.json
  - Sends identical 6-digit code to all project endpoints
  - Detailed per-project success/failure logging

### Changed
- **API Endpoints**: Added optional project_ids[] parameter to /api/logs and /api/analytics
- **Settings Page**: Remains global (single settings for all projects)
- **Version**: Bumped to 0.6.0 (minor version for new feature + schema change)

## [0.5.0] - 2025-10-21

### Added
- **Audit Logging System**: Comprehensive logging of all code execution requests
  - Automatic logging of query, Python code, extracted data, status, user, group, and timestamp
  - Data compression for query, code, and results (70-80% storage reduction)
  - SQLite database with optimized indexes for fast queries
  - Configurable retention policy (size and age-based auto-purging)
  - Default limits: 1 GB storage, 60 days retention

- **Web Dashboard**: Modern web interface for viewing audit logs
  - Built with Flask, Tailwind CSS, Alpine.js, and Chart.js
  - Zero build tools required (CDN-based frontend)
  - Responsive, mobile-friendly design
  - Real-time analytics and charts
  - Advanced filtering (users, groups, statuses, date ranges)
  - Pagination support for large datasets
  - Detailed view modal with lazy loading
  - Execution trends visualization

- **Authentication System**: Secure login and password management
  - Bcrypt password hashing
  - Session-based authentication (24-hour expiration)
  - Default credentials: admin/admin
  - In-app password changes
  - Password reset via 6-digit email codes
  - Brute-force protection on reset attempts
  - Session cleanup and security features

- **Analytics Dashboard**: Visual insights into code executions
  - Total executions, success/failure counts and rates
  - Most active users leaderboard
  - Top groups leaderboard
  - Execution trends over time (configurable periods)
  - Filterable analytics by date range

- **Configuration System**: Flexible environment-based configuration
  - Toggle audit logging on/off
  - Toggle web interface on/off
  - Configurable database paths
  - Configurable retention policies
  - Configurable web server host/port
  - Support for password reset via account service integration

- **Command-Line Tools**:
  - `insyt-audit-web`: Start web dashboard server
  - Existing `insyt-secure` command unchanged

- **Documentation**:
  - `AUDIT_LOGGING_README.md`: Complete feature documentation
  - `MIGRATION_GUIDE.md`: Upgrade guide for existing deployments
  - `QUICK_START.md`: 5-minute getting started guide
  - `IMPLEMENTATION_SUMMARY.md`: Technical implementation details
  - `.env.example`: Configuration template
  - `examples/audit_logging_demo.py`: Working demo script

### Changed
- Updated version from 0.4.5 to 0.5.0
- Enhanced `CodeExecutor` to integrate automatic audit logging
- Updated `settings.py` with audit logging and web interface configuration
- Modified MQTT message processing to extract audit fields (query, user, group)

### Added Dependencies
- `flask>=3.0.0`: Web framework for dashboard
- `bcrypt>=4.0.0`: Secure password hashing
- `werkzeug>=3.0.0`: WSGI utilities (bundled with Flask)

### Security
- Secure password storage with bcrypt and salt
- Cryptographically secure session tokens
- Automatic session expiration
- Rate limiting on password reset attempts
- Localhost-only binding by default
- No sensitive data in logs (masked code/queries)

### Performance
- Compressed storage reduces database size by 70-80%
- Indexed database queries for fast filtering
- Pagination for efficient data loading
- Lazy loading of detail views
- Minimal execution overhead (< 5ms per request)
- Non-blocking audit logging

### Backward Compatibility
- ✅ **Fully backward compatible** - no breaking changes
- Existing code executors work without modifications
- MQTT message format unchanged (audit fields optional)
- All existing environment variables still supported
- Audit logging can be completely disabled if not needed

### Notes
- For audit logging to capture full context, MQTT messages should include:
  - `query`: User's natural language question
  - `user`: Username or email
  - `group`: Team/group affiliation (optional)
- If these fields are missing, execution still works (defaults used)
- Web dashboard requires first-time password change from default

## [0.3.7] - 2025-06-27

### Added
- Fixed `locals()` and `globals()` functions now available in secure execution environment
- Enhanced data analytics support with new built-ins: `slice`, `memoryview`, `bytes`, `bytearray`, `frozenset`, `iter`, `next`, `callable`, `super`, `object`, `delattr`
- Added data processing modules: `collections`, `itertools`, `functools`, `operator`, `statistics`, `decimal`, `csv`, `io`, `copy`, `heapq`, `bisect`, `uuid`, `hashlib`, `base64`, `string`, `textwrap`
- Object-oriented programming support with `property`, `staticmethod`, `classmethod` decorators

### Fixed
- Resolved `NameError: name 'locals' is not defined` in code execution environment

## [0.3.0] - 2025-05-14

### Added
- Support for managing one or more projects simultaneously
- Independent connection management for each project (separate credential handling and reconnection)
- Shared DNS cache across all project connections
- Command-line option `--projects` for specifying project configurations
- Support for environment variable `INSYT_PROJECTS` for project configuration

### Changed
- Enhanced project identification in logs
- Improved resource management for multiple concurrent connections

### Removed
- Legacy single-project mode using separate `--project-id` and `--api-key` parameters
- Projects must now be specified using the `--projects` parameter or `INSYT_PROJECTS` environment variable

## [0.2.9] - 2025-05-13

### Added
- DNS caching mechanism to improve resilience against DNS server outages
- Cached DNS resolutions are stored for up to 24 hours and used as fallback
- Initial release of version 0.2.6 