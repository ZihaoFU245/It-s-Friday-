# ITS-FRIDAY MCP Servers

This directory contains the refactored MCP (Model Context Protocol) servers for the ITS-FRIDAY system. The original monolithic `server.py` has been broken down into smaller, specialized servers for better maintainability and organization.

## Server Architecture

### Individual Servers

Each server focuses on a specific domain of functionality:

#### 1. Weather Server (`weather_server.py`)
- **Name**: `ITS-FRIDAY-WEATHER`
- **Purpose**: Weather information and forecasting
- **Tools**: 
  - `get_weather_now` - Current weather conditions
  - `get_weather_forecast` - Multi-day weather forecast
  - `get_weather_at` - Historical weather data

#### 2. Email Server (`email_server.py`)
- **Name**: `ITS-FRIDAY-EMAIL`
- **Purpose**: Email management across multiple accounts
- **Resources**:
  - `mcp://friday/email-accounts` - Account information
  - `mcp://friday/unread-email-counts` - Quick unread counts
- **Tools**: Email reading, sending, draft management, account management

#### 3. Contacts Server (`contacts_server.py`)
- **Name**: `ITS-FRIDAY-CONTACTS`
- **Purpose**: Contact database management
- **Tools**: CRUD operations for contacts with search and pagination

#### 4. Browser Server (`browser_server.py`)
- **Name**: `ITS-FRIDAY-BROWSER`
- **Purpose**: Web browser automation
- **Tools**: Page navigation, element interaction, JavaScript execution, screenshots

#### 5. Google Services Server (`google_server.py`)
- **Name**: `ITS-FRIDAY-GOOGLE`
- **Purpose**: Google services integration
- **Tools**: Calendar events, Google Drive file listing

## Usage

### Running Individual Servers

Each server can be run independently:

```bash
# Weather services
python weather_server.py

# Email management
python email_server.py

# Contact management
python contacts_server.py

# Browser automation
python browser_server.py

# Google services
python google_server.py
```

### Server Registry

The `server_registry.py` file contains metadata about all servers and can be used to:

```python
from server_registry import SERVERS, print_server_info

# Print information about all servers
print_server_info()

# Get specific server info
weather_info = get_server_by_name("weather")
```

## Migration from Original server.py

The original `server.py` contained all functionality in a single file (~800+ lines). The new structure provides:

### Benefits
- **Modularity**: Each server handles one domain
- **Maintainability**: Easier to update individual components
- **Scalability**: Servers can be deployed independently
- **Resource Efficiency**: Only load needed functionality
- **Testing**: Easier to test individual components

### Breaking Points
The original file was split at these logical boundaries:

1. **Weather Tools** → `weather_server.py`
2. **Email Tools + Resources** → `email_server.py`  
3. **Contact Management Tools** → `contacts_server.py`
4. **Browser Automation Tools** → `browser_server.py` (cut-off point as requested)
5. **Google Services Tools** → `google_server.py`

### Preserved Functionality
All original tools and resources are preserved with the same:
- Function signatures
- Parameter types
- Return types
- Documentation
- Error handling

## Configuration

Each server:
- Imports the same configuration system
- Uses the same logging setup
- Maintains the same import patterns
- Handles fallback imports for direct execution

## Development

When adding new functionality:

1. **Identify the appropriate server** based on the feature domain
2. **Add tools to the relevant server file**
3. **Update `server_registry.py`** with new tool names
4. **Test the individual server** independently
5. **Update this README** if adding new servers

## Legacy Support

The original `server.py` file is preserved and can still be used if needed, but the new modular approach is recommended for ongoing development.
