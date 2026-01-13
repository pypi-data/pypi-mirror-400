# Insyt Secure (Created & Maintained by Temitope Oguntade | Chanels Innovations)

A proprietary service for securely interacting with databases, APIs, and other services within a secure environment. Contact temitope @ insyt [dot] co or temitope @ chanels [dot] io for more information.

## Quick Start

### Installation

```bash
# Basic installation (core functionality only)
pip install insyt-secure
```

#### Installing on a Fresh Ubuntu Instance

Follow these steps to set up insyt-secure on a fresh Ubuntu installation:

```bash
# Step 1: Install required packages
sudo apt update
sudo apt install python3-pip
sudo apt install python3-venv python3-full

# Step 2: Create a directory for your project (optional)
mkdir myproject
cd myproject

# Step 3: Create the virtual environment
python3 -m venv venv

# Step 4: Activate the virtual environment
source venv/bin/activate
# Your command prompt should change to show the virtual environment name
# Example: (venv) ubuntu@ip-100-1-11-111:~/myproject$

# Step 5: Install insyt-secure with desired extensions
pip install insyt-secure[mysql,postgres]
pip install python-dotenv
```

**Notes:**
1. To run the service, use the following command:
```bash
insyt-secure --projects "your-project-id-123:your-api-key-xyz"
```
or run the service in the background:
```bash
nohup insyt-secure --projects "your-project-id-123:your-api-key-xyz" &
```
or with file logging for production:
```bash
insyt-secure --projects "your-project-id-123:your-api-key-xyz" --log-file "insyt-secure.log"
```

2. Remember to activate the virtual environment each time you want to use this package in a new terminal session.
```bash
source venv/bin/activate
```

3. To deactivate the virtual environment when you're done:
```bash
deactivate
```

4. To stop the service, use the following command:
```bash
pkill -f insyt-secure
```

5. To check the status of the service, use the following command:
```bash
ps aux | grep insyt-secure
```

#### Advanced Installation Options

Insyt Secure provides flexible installation options to include only the dependencies you need:

```bash
# Install with PostgreSQL support
pip install "insyt-secure[postgres]"

# Install with MongoDB support
pip install "insyt-secure[mongodb]"

# Install with multiple database support
pip install "insyt-secure[postgres,mongodb,redis]"

# Install with vector database support
pip install "insyt-secure[pinecone]" # or any other vector DB

# Install with cloud provider support
pip install "insyt-secure[aws]" # or azure

# Install with messaging system support
pip install "insyt-secure[kafka]" # or rabbitmq, pulsar

# Complete installation with all dependencies
pip install "insyt-secure[all]"
```

Available extension categories:
- SQL databases: `postgres`, `mysql`, `mssql`, `oracle`, `clickhouse`, `snowflake`, `duckdb`
- NoSQL databases: `mongodb`, `redis`, `cassandra`, `neo4j`, `elasticsearch`, `couchdb`
- Vector databases: `pinecone`, `qdrant`, `milvus`, `weaviate`, `chroma`, `faiss`
- Cloud services: `aws`, `azure`
- Messaging systems: `kafka`, `pulsar`, `rabbitmq`

Broader categories are also available: `rdbms`, `nosql`, `vector`, `cloud`, `messaging`

### Basic Usage

```bash
# Run with a single project
insyt-secure --projects "your-project-id-123:your-api-key-xyz"
```

### Multi-Project Support

Insyt Secure supports managing one or more projects simultaneously:

```bash
# Run with multiple projects
insyt-secure --projects "project-id-1:api-key-1,project-id-2:api-key-2"
```

Each project connection is managed independently, allowing for simultaneous interactions with multiple Insyt projects, each with its own topic subscriptions and credential management.

### Getting Help

```bash
# View all available options and examples
insyt-secure --help
```

The help command provides detailed information about all parameters, their defaults, and usage examples directly in your terminal.

### Audit Dashboard

Insyt Secure includes a web-based audit dashboard for monitoring code execution history. It automatically logs all execution requests against project databases/workflow with user info, queries, executed code, results, and timestamps.

**Usage:**
```bash
# 1. Start the core service (this enables audit logging automatically)
insyt-secure --projects "your-project-id:your-api-key"

# 2. In a separate terminal, start the web dashboard

# Option A: Foreground mode (for local development or monitoring)
insyt-audit-web

# Option B: Localhost-only access (more secure if not accessing remotely)
insyt-audit-web --host 127.0.0.1

# Option C: Background mode with nohup (recommended for remote servers)
# Process survives terminal disconnect and SSH session closure
nohup insyt-audit-web > audit_web.log 2>&1 &

# Optional: Specify custom host/port
nohup insyt-audit-web --port 8080 > audit_web.log 2>&1 &

# Check processes are running
ps aux | grep insyt

# View logs
tail -f ./logs/insyt_secure.log
```

**Access:** 
- **Local/SSH Tunnel**: http://localhost:8080 or http://127.0.0.1:8080
  - When using VS Code Remote SSH, access via localhost (VS Code may auto-forward the port)
  - Or manually set up SSH port forwarding: `ssh -L 8080:localhost:8080 user@server`
- **Remote/Direct IP**: http://your-server-ip:8080 (default since v0.6.6)
  - Ensure your firewall/security group allows inbound traffic on port 8080
- **Default credentials**: admin/admin (change immediately after first login)

**Network Binding (v0.6.6+):**
- Default: Binds to `0.0.0.0` (all interfaces) for easy remote access
- For localhost-only access: Use `--host 127.0.0.1` flag
- Custom host/port: `insyt-audit-web --host 0.0.0.0 --port 9000`

**Features:**
- View execution logs with filtering by user, status, date range
- Analytics dashboard with success rates and user activity charts
- Automatic data retention (1GB limit, 60-day retention by default)
- Password reset via 6-digit codes sent to registered email
- Configure port and host binding via web UI settings page

**Security:** All passwords are hashed with bcrypt and sessions expire after 24 hours. For production deployments, use a reverse proxy (nginx/Apache) with SSL/TLS for encrypted connections.

### Environment Presets

Securely manage and reuse environment variables for code execution via the Settings page in the audit dashboard.

**Features:**
- **Encrypted Storage**: Values encrypted at rest using Fernet (AES-128)
- **Secure Viewing**: Password re-authentication required; 10-minute view sessions
- **Project Organization**: Categorize presets by project for easy management
- **Full CRUD**: Create, view, edit, and delete presets and individual variables

**Access:** Settings tab → Environment Presets (after logging into the audit dashboard)

**Use Cases:** Database credentials, API keys, service configurations, multi-environment setups

### Advanced Options

```bash
# Run with all options (for a single project)
insyt-secure \
  --projects "your-project-id-123:your-api-key-xyz" \
  --max-workers 10 \
  --timeout 60 \
  --allowed-hosts "192.168.1.1,10.0.0.1:3456"

# Run with file logging for production deployments
insyt-secure \
  --projects "your-project-id-123:your-api-key-xyz" \
  --log-file "/var/log/insyt-secure.log" \
  --log-level info \
  --log-format json
```

### Logging Options

By default, logs are user-friendly and redact sensitive information. You can customize logging behavior:

```bash
# Enable debug level logging (most verbose - shows detailed execution info)
insyt-secure --projects "your-project-id:your-api-key" --log-level debug

# Info level logging (default - shows normal operation messages)
insyt-secure --projects "your-project-id:your-api-key" --log-level info

# Warning level logging (only warnings and errors)
insyt-secure --projects "your-project-id:your-api-key" --log-level warning

# Error level logging (only errors and critical issues)
insyt-secure --projects "your-project-id:your-api-key" --log-level error

# Critical level logging (only critical system failures)
insyt-secure --projects "your-project-id:your-api-key" --log-level critical

# Output logs in JSON format (useful for log processing systems)
insyt-secure --projects "your-project-id:your-api-key" --log-format json

# Use standard logging format (traditional timestamp + level + message)
insyt-secure --projects "your-project-id:your-api-key" --log-format standard

# Enable file logging (logs to both console and file)
insyt-secure --projects "your-project-id:your-api-key" --log-file "/var/log/insyt-secure.log"

# File logging with specific log level and format
insyt-secure --projects "your-project-id:your-api-key" --log-file "insyt-secure.log" --log-level debug --log-format json
```

**Log File Management**: When using `--log-file`, logs are automatically rotated daily at midnight and kept for 7 days. Old log files are automatically deleted to prevent disk space issues.

**Log Output**: By default, logs are output to the console only. For file logging, use the `--log-file` parameter to specify a file path. When file logging is enabled, logs are written to both console and file. Log files are automatically rotated daily and kept for 7 days.

**Log Level Guide**:
- `debug`: Most verbose - shows detailed execution steps, connection details, and internal operations
- `info`: Default level - shows normal operation messages, project starts/stops, and connection status
- `warning`: Shows potential issues and recoverable errors that don't stop the service
- `error`: Shows errors that affect individual requests but don't crash the service
- `critical`: Shows only critical system failures that may require immediate attention

You can also control the log level via environment variables:

```bash
# Set log level using environment variable (all levels available)
INSYT_LOG_LEVEL=debug insyt-secure --projects "your-project-id:your-api-key"
INSYT_LOG_LEVEL=info insyt-secure --projects "your-project-id:your-api-key"
INSYT_LOG_LEVEL=warning insyt-secure --projects "your-project-id:your-api-key"
INSYT_LOG_LEVEL=error insyt-secure --projects "your-project-id:your-api-key"
INSYT_LOG_LEVEL=critical insyt-secure --projects "your-project-id:your-api-key"

# Set log format using environment variable
INSYT_LOG_FORMAT=json insyt-secure --projects "your-project-id:your-api-key"
INSYT_LOG_FORMAT=standard insyt-secure --projects "your-project-id:your-api-key"
INSYT_LOG_FORMAT=user_friendly insyt-secure --projects "your-project-id:your-api-key"

# Configure projects using environment variable (optional alternative to --projects)
INSYT_PROJECTS="project-id-1:api-key-1,project-id-2:api-key-2" insyt-secure

# Enable file logging using environment variable
INSYT_LOG_FILE="/var/log/insyt-secure.log" insyt-secure --projects "your-project-id:your-api-key"

# Combine multiple environment variables for production setup
INSYT_LOG_FILE="insyt-secure.log" INSYT_LOG_LEVEL=info INSYT_LOG_FORMAT=json insyt-secure --projects "proj:key"
```

**Configuration Priority**: Command line parameters always take precedence over environment variables. Environment variables serve as defaults when no command line parameter is provided. For example:

```bash
# Environment variable sets default, but command line parameter overrides it
export INSYT_LOG_LEVEL=warning
insyt-secure --projects "proj:key" --log-level debug  # Uses debug (not warning)

# Environment variable used when no command line parameter provided
export INSYT_LOG_LEVEL=warning  
insyt-secure --projects "proj:key"  # Uses warning from environment
```

## Cross-Platform Compatibility

Insyt Secure is designed to work seamlessly on all major platforms:

- **Windows**: Fully supported natively, no additional configuration needed
- **macOS**: Fully supported
- **Linux**: Fully supported

The service uses paho-mqtt with a platform-agnostic implementation to ensure consistent behavior across all operating systems.

## Command Line Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--projects` | Comma-separated list of project-id:api-key pairs for managing one or more projects | - |
| `--max-workers` | Maximum number of concurrent code executions per project | 20 |
| `--timeout` | Default maximum execution time in seconds per code snippet | 30 |
| `--allowed-hosts` | Comma-separated list of allowed IPs/hostnames | All allowed |
| `--log-level` | Set the logging level (debug, info, warning, error, critical) | info |
| `--log-format` | Set the logging format (user_friendly, json, standard) | user_friendly |
| `--log-file` | Optional log file path for file logging | Console only |

## Environment Variables

All command line parameters can be set via environment variables. Command line parameters take precedence over environment variables.

| Environment Variable | Command Line Equivalent | Description |
|---------------------|-------------------------|-------------|
| `INSYT_PROJECTS` | `--projects` | Project configurations |
| `INSYT_MAX_WORKERS` | `--max-workers` | Maximum concurrent workers per project |
| `INSYT_EXECUTION_TIMEOUT` | `--timeout` | Execution timeout in seconds |
| `INSYT_ALLOWED_HOSTS` | `--allowed-hosts` | Comma-separated list of allowed hosts |
| `INSYT_ALWAYS_ALLOWED_DOMAINS` | `--always-allowed-domains` | Always-allowed domains |
| `INSYT_LOG_LEVEL` | `--log-level` | Logging level |
| `INSYT_LOG_FORMAT` | `--log-format` | Logging format |
| `INSYT_LOG_FILE` | `--log-file` | Optional log file path |
| `INSYT_API_URL` | `--api-url` | API URL for credential acquisition |

## Credentials Management

This service automatically retrieves and manages connection credentials:

1. When the service starts, it gets credentials from the Insyt API for each configured project
2. If the connection drops or credentials expire, it automatically requests new credentials
3. Each project's credentials are managed independently

## Project Management

Insyt Secure supports managing one or more projects simultaneously:

### Configuration Options

You can configure projects in two ways:

1. **Command line parameter**:
   ```bash
   insyt-secure --projects "project-id-1:api-key-1,project-id-2:api-key-2"
   ```

2. **Environment variable**:
   ```bash
   export INSYT_PROJECTS="project-id-1:api-key-1,project-id-2:api-key-2"
   insyt-secure
   ```

### Benefits of Multi-Project Mode

- **Resource Efficiency**: All projects share a single process but maintain independent connections
- **Simplified Management**: Manage multiple projects from a single service instance
- **Independent Reconnection**: Each project can reconnect independently if its connection fails
- **Shared DNS Cache**: All projects benefit from the DNS cache for improved resilience


## Use Cases

### Data Processing Microservice

Perfect for running data transformation code that connects to various data sources:

```bash
insyt-secure --projects "your-project-id:your-api-key" --max-workers 15
```

### Secure Environment for Code Testing

Create a sandboxed environment with restricted network access:

```bash
insyt-secure --projects "your-project-id:your-api-key" \
  --allowed-hosts "10.0.0.1,192.168.1.100" --timeout 30
```

### Multi-Project Service

Run a single service that executes code for multiple projects:

```bash
insyt-secure --projects "PRJ-A235466:api-key-1,PRJ-A235477:api-key-2,ai-models:api-key-3" \
  --max-workers 10 --timeout 60
```

### Containerized Deployment

```bash
docker run -d --name insyt-secure \
  insyt-secure insyt-secure \
  --projects "your-project-id:your-api-key"
```

## System Requirements and Dependencies

Insyt Secure is designed with a modular dependency structure to minimize installation size and resource usage. Below is a breakdown of what's included in each installation option:

### Core Dependencies (included in base install)

The base installation includes:
- HTTP client capabilities via `httpx`
- MQTT connectivity via `paho-mqtt`
- Basic data science libraries: NumPy, Pandas, SciPy
- JSON and date handling utilities

### Optional Dependencies

#### SQL Database Connectors
- `postgres`: High-performance PostgreSQL client (asyncpg)
- `mysql`: MySQL client libraries
- `mssql`: Microsoft SQL Server connectivity
- `oracle`: Oracle database connectivity
- `clickhouse`: ClickHouse analytics database client
- `snowflake`: Snowflake data warehouse client
- `duckdb`: Embedded analytical database

#### NoSQL Database Connectors
- `mongodb`: MongoDB client with async support
- `redis`: Redis client
- `cassandra`: Apache Cassandra and ScyllaDB clients
- `neo4j`: Neo4j graph database client
- `elasticsearch`: Elasticsearch search engine client
- `couchdb`: CouchDB document database client

#### Vector Database Connectors
- `pinecone`: Pinecone vector database client
- `qdrant`: Qdrant vector search engine client
- `milvus`: Milvus vector database client
- `weaviate`: Weaviate vector search engine
- `chroma`: ChromaDB for AI embeddings
- `faiss`: Facebook AI Similarity Search

#### Cloud Services
- `aws`: AWS SDK (boto3) with S3, Dynamo, etc.
- `azure`: Azure clients for Cosmos DB, Blob Storage, etc.

#### Messaging Systems
- `kafka`: Apache Kafka client
- `pulsar`: Apache Pulsar client
- `rabbitmq`: RabbitMQ client

### Performance Considerations

The base installation already includes the core ML libraries (numpy, pandas, etc.). If you're installing on a resource-constrained environment, consider using only the specific connector extensions you need rather than the broader categories.

For production deployments, we recommend specifying exact dependencies rather than using broader categories:

```bash
# Good (minimal dependencies)
pip install "insyt-secure[postgres,redis]"

# Less efficient (pulls in many unused dependencies)
pip install "insyt-secure[rdbms,nosql]"
```

### Platform-Specific Installation

Insyt Secure is designed to work on all major platforms without modification:

#### Windows

```bash
# Install on Windows
pip install insyt-secure

# Run (in PowerShell or Command Prompt)
insyt-secure --projects "your-project-id-123:your-api-key-xyz"
```

#### macOS/Linux

```bash
# Install on macOS/Linux
pip install insyt-secure

# Run
insyt-secure --projects "your-project-id-123:your-api-key-xyz"
```

#### Docker

```bash
# Create a simple Dockerfile
echo 'FROM python:3.10-slim
RUN pip install insyt-secure
ENTRYPOINT ["insyt-secure"]' > Dockerfile

# Build the Docker image
docker build -t insyt-secure .

# Run in Docker
docker run insyt-secure --projects "your-project-id-123:your-api-key-xyz"
```

#### Platform-Specific Considerations

- **Windows**: Works natively without WSL, using a cross-platform MQTT implementation
- **MacOS/Linux**: All features fully supported
- **Docker**: Ideal for deployment in containerized environments


