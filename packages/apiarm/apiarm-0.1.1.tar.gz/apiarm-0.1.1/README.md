# API-ARM 🦾

**Application Programming Interface with Automated Request Manipulator**

API-ARM is a powerful Python tool that analyzes APIs, determines their usage patterns, and mimics secure requests to return anticipated results.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **API Analysis** | Auto-discover endpoints, auth methods, and rate limits from OpenAPI/Swagger |
| 🔐 **Multi-Auth Support** | API Key, Bearer Token, Basic Auth, OAuth 2.0 |
| 📡 **Smart Requests** | Make properly authenticated requests with retry logic |
| 📊 **Request Logging** | Track all requests with timing and statistics |
| ⚡ **Response Caching** | LRU cache with TTL for faster repeated requests |
| 🖥️ **Beautiful CLI** | Terminal interface with Rich formatting |

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/apiarm.git
cd apiarm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

## 📖 Quick Start

### Python API

```python
import asyncio
from apiarm import APIArm

async def main():
    async with APIArm("https://api.example.com") as arm:
        # Configure authentication
        arm.set_api_key("your-api-key")
        
        # Enable logging and caching
        arm.enable_logging(console=True)
        arm.enable_caching(max_size=100, default_ttl=300)
        
        # Analyze the API
        analysis = await arm.analyze()
        print(f"Found {analysis.endpoint_count} endpoints")
        
        # Make requests
        response = await arm.get("/users")
        print(response.data)
        
        # Print statistics
        arm.print_stats()

asyncio.run(main())
```

### CLI Commands

```bash
# Analyze an API
apiarm analyze https://api.example.com

# Make a GET request
apiarm request https://api.example.com/users

# Make a POST request with data
apiarm request https://api.example.com/users -m POST -d '{"name": "John"}'

# With authentication
apiarm request https://api.example.com/users -k "your-api-key"
apiarm request https://api.example.com/users -b "your-bearer-token"
```

## 🏗️ Project Structure

```
apiarm/
├── apiarm/                    # Main package
│   ├── __init__.py
│   ├── cli.py                # Command-line interface
│   ├── core/
│   │   ├── analyzer.py       # API analysis engine
│   │   ├── requester.py      # Request handling
│   │   ├── security.py       # Authentication
│   │   ├── logger.py         # Request logging
│   │   ├── cache.py          # Response caching
│   │   └── arm.py            # Main unified interface
│   ├── models/
│   │   ├── endpoint.py       # Endpoint model
│   │   └── response.py       # Response model
│   └── utils/
│       └── helpers.py        # Utility functions
├── examples/
│   └── basic_usage.py
├── tests/
├── requirements.txt
└── pyproject.toml
```

## 🔐 Authentication Methods

```python
from apiarm import APIArm
from apiarm.models import AuthMethod

async with APIArm("https://api.example.com") as arm:
    # API Key
    arm.set_api_key("your-key", header_name="X-API-Key")
    
    # Bearer Token
    arm.set_bearer_token("your-token")
    
    # Or use configure_auth for any method
    arm.configure_auth(
        AuthMethod.BASIC,
        username="user",
        password="pass"
    )
    
    arm.configure_auth(
        AuthMethod.OAUTH2,
        client_id="id",
        client_secret="secret",
        token="access-token"
    )
```

## 📊 Logging & Caching

```python
from pathlib import Path

async with APIArm("https://api.example.com") as arm:
    # Enable console logging
    arm.enable_logging(console=True)
    
    # Log to file (JSON lines format)
    arm.enable_logging(console=True, file_path=Path("requests.log"))
    
    # Enable caching (5 minute TTL by default)
    arm.enable_caching(max_size=100, default_ttl=300)
    
    # Make requests...
    await arm.get("/users")
    await arm.get("/users")  # Cache hit!
    
    # View statistics
    arm.print_stats()
    
    # Access logger directly
    for log in arm.logger.get_logs():
        print(f"{log.method} {log.path} - {log.duration_ms}ms")
```

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=apiarm --cov-report=html
```

## 🛠️ Development

```bash
# Format code
black apiarm/ tests/
isort apiarm/ tests/

# Type checking
mypy apiarm/
```

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 👤 Author

**Rayen Bahroun** - [bahroun.me](https://bahroun.me)

---

<p align="center">Made with 🦾 by API-ARM</p>
