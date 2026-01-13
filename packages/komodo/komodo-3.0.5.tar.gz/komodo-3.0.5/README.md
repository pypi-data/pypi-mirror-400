# Komodo Connector SDK

The Komodo Connector SDK is a Python library that provides programmatic access to the Komodo Health platform. It includes both a CLI for authentication management and a Python API for interacting with Komodo services and executing Snowflake queries through the Komodo platform.

## Features

- **OAuth 2.0 Device Authorization Flow**: Browser-based authentication for easy credential management
- **CLI Tools**: Simple commands for login, JWT management, and account selection
- **Snowflake Integration**: Execute SQL queries against Komodo's Snowflake data warehouse via proxy
- **Synchronous and Asynchronous Query Execution**: Support for both blocking and async query patterns
- **Automatic Token Refresh**: Credentials are automatically refreshed when they expire
- **Multi-Environment Support**: Switch between integration and production environments

### Prerequisites

- Python 3.11 or higher

## Installation

Install via pip:
```bash
pip install komodo
```

Confirm expected version:
```bash
komodo --version
```

## Usage

See: https://docs.komodohealth.com
