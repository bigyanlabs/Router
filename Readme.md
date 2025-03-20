# Flask Router

A flexible routing framework with integrated real-time logging capabilities.

## Table of Contents
1. Installation
2. Quick Start
3. Project Structure
4. Core Features
   - Router System
   - Session-based Logging
   - Real-time Log Viewer
5. Configuration
6. API Reference
7. Development Guide
8. Troubleshooting

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/bigyanlabs/Router.git
   cd Router
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r Requirements.txt
   ```

## Quick Start

1. **Start the main server**
   ```bash
   python main.py
   ```
   Or use the convenience batch file:
   ```bash
   run.bat
   ```

2. **Start the log viewer** (in a separate terminal)
   ```bash
   python log.py
   ```
   Or use the convenience batch file:
   ```bash
   logger.bat
   ```

3. **Access the applications**
   - Main application: [http://localhost:5000](http://localhost:5000)
   - Log viewer: [http://localhost:9001](http://localhost:9001)

## Project Structure

```
Router/
├── core/                   # Core framework files
│   ├── engine.py           # Main routing engine
│   ├── logger.py           # Session-based logging system
│   └── router.py           # Route registration and handling
├── logs/                   # Log files directory
├── routes/                 # Route definitions
│   └── ...                 # Your route files
├── viewer/                 # Log viewer files
│   ├── page.html           # Log viewer interface
│   ├── scripts.js          # Log viewer JavaScript
│   └── styles.css          # Log viewer CSS
├── .env                    # Environment configuration
├── log.py                  # Real-time log server
├── logger.bat              # Batch file to start log server
├── main.py                 # Main application entry point
├── Readme.md               # This documentation
├── Requirements.txt        # Python dependencies
└── run.bat                 # Batch file to start main server
```

## Core Features

### Router System

The router system allows for dynamic routing with minimal configuration:

1. **Creating a new route**

   Create a new file in the routes directory with appropriate HTML, CSS and JavaScript.
   The system automatically registers routes based on the file structure.

2. **Route naming convention**

   Routes are automatically mapped based on file names:
   - `routes/index.html` → `/`
   - `routes/about.html` → `/about`
   - `routes/user/profile.html` → `/user/profile`

3. **API routes**

   API routes can be defined using Python files in the routes directory:
   ```python
   # routes/api/users.py
   from flask import jsonify

   def get():
       return jsonify({"users": ["user1", "user2"]})

   def post():
       # Handle POST request
       return jsonify({"status": "created"})
   ```

### Session-based Logging

The logging system creates session-specific log files:

1. **Log file naming**

   Log files are named using date and session ID:
   ```
   logs/2025-03-20_20250320_171640.log
   ```

2. **Development mode**

   In development mode, the logger reuses the same session ID for an hour to prevent creating multiple log files during rapid development cycles.

3. **Production mode**

   In production, each server restart creates a new session ID and log file for better isolation and debugging.

4. **Log levels**

   The system supports standard log levels:
   ```python
   from core.logger import log_info, log_error, log_warning, log_debug

   log_info("Server started")
   log_warning("Resource running low")
   log_error("Failed to connect to database")
   log_debug("Variable x = 42")
   ```

### Real-time Log Viewer

A dedicated server for viewing logs in real-time:

1. **Features**
   - Real-time log streaming
   - Filter logs by level (info, warning, error, debug)
   - Search functionality
   - Historical log browsing
   - Download logs
   - Auto-scroll toggle

2. **Interface**
   - Sidebar with list of available log files
   - Main panel showing log entries
   - Toolbar with filters and search
   - Status indicators for connection state

## Configuration

### Environment Variables

Create a .env file in the root directory with the following options:

```
# Server configuration
PORT=5000
DEBUG=True
SECRET_KEY=your_secret_key_here

# Log configuration
FLASK_ENV=development
LOG_LEVEL=DEBUG

# Log viewer configuration
LOG_SERVER_PORT=9001
```

### Development vs Production

To switch between development and production modes:

**Development Mode**
```
FLASK_ENV=development
DEBUG=True
```

**Production Mode**
```
FLASK_ENV=production
DEBUG=False
```

## API Reference

### Main Server

#### Core Logger API

```python
from core.logger import log_info, log_error, log_warning, log_debug, log_request

# Basic logging
log_info("Information message")
log_warning("Warning message")
log_error("Error message")
log_debug("Debug information")

# Request logging
log_request("/path", "GET", 200)
```

#### Router API

```python
from core.router import register_route, get_routes

# Manual route registration
register_route("/custom", view_func, methods=["GET"])

# Get all registered routes
routes = get_routes()
```

### Log Server API

The log server exposes these endpoints:

- `GET /` - Log viewer interface
- `GET /api/logs` - Get all logs or filtered by file
- `GET /api/files` - List available log files
- `GET /api/stream` - Server-sent events stream for real-time logs
- `GET /api/download/<filename>` - Download a specific log file
- `GET /api/search?q=<query>` - Search logs for specific text

## Development Guide

### Adding a New Route

1. **Static route**

   Create an HTML file in the routes directory:
   ```html
   <!-- routes/contact.html -->
   <html>
     <head>
       <title>Contact Us</title>
     </head>
     <body>
       <h1>Contact Us</h1>
       <p>Email: contact@example.com</p>
     </body>
   </html>
   ```

2. **API route**

   Create a Python file in the `routes/api` directory:
   ```python
   # routes/api/status.py
   from flask import jsonify

   def get():
       return jsonify({
           "status": "operational",
           "version": "1.0.0"
       })
   ```

### Extending the Logger

To add custom log handlers:

```python
# custom_logging.py
from core.logger import logger

# Add custom handler
custom_handler = YourCustomHandler()
logger.addHandler(custom_handler)
```

## Troubleshooting

### Common Issues

1. **Multiple log files during development**

   Make sure `FLASK_ENV=development` is set in your environment. The logger uses this to determine whether to reuse session IDs.

2. **Server stops immediately after starting**

   Check for errors in the console or log files. Common causes include port conflicts or missing dependencies.

3. **Missing logs in the log viewer**

   Ensure the log directory (logs) exists and is writable. Check if the correct log file path is configured in both the main server and log server.

4. **Routes not registering**

   Verify file naming and structure in the routes directory. Check the server logs for any route registration errors.

### Debug Mode

To enable verbose debugging:

```bash
# On Windows
set DEBUG=True
python main.py

# On Unix/MacOS
export DEBUG=True
python main.py
```

---
