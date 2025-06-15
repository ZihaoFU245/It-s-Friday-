# Skills Module

This is a standalone skills module that provides an MCP (Model Context Protocol) server for the Friday application.

## Overview

The skills module exposes Friday's core functionality as tools that AI assistants can use through the MCP protocol. It provides a clean interface to weather, email, calendar, and drive operations.

## Features

- **Weather Operations**: Get current weather, forecasts, and location-based weather data
- **Email Management**: Send emails and retrieve unread messages via multi-account EmailManager
- **Calendar Integration**: Access and manage Google Calendar events
- **Drive Access**: List and manage Google Drive files

## Usage

### Running the MCP Server

```bash
python skills/server.py
```

The server will start and expose all available tools through the FastMCP framework.

### Available Tools

1. **get_weather(city, mode)** - Get weather information
2. **get_forecast(city)** - Get weather forecast
3. **get_unread_emails_from_account(account, max_results)** - Get unread emails from specific account
4. **get_unread_emails_all_accounts(max_results_per_account)** - Get unread emails from all accounts
5. **send_email_from_account(to, subject, body, account)** - Send emails from specific account
6. **list_email_accounts()** - List configured email accounts
7. **get_calendar_events(max_results)** - Get calendar events
8. **get_drive_files(page_size)** - List drive files

## Architecture

The skills module imports services from the main `app` package:

```python
from app import weather_service, email_manager, calendar_service, drive_service
```

This provides a clean separation where:
- The `app` package contains the core business logic and services
- The `skills` module provides the MCP interface layer
- AI assistants interact only with the skills module
- EmailManager handles multi-account email operations seamlessly

## Configuration

The skills module inherits configuration from the main app package. Make sure the app is properly configured with API keys and credentials before using the skills.

## Dependencies

- FastMCP framework for MCP server functionality
- Main app package for service layer access
- All dependencies from the main app (Google APIs, weather APIs, etc.)
