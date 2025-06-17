# We are making a Agent App which is called <i><b>It's Friday!😆</b></i>

## Application Structure Overview

```mermaid
flowchart TD
    A[It's Friday! App Structure] --> B(frontend/ Electron + React)
    B --> B1(components/)
    B1 --> B1a(Header.jsx - Mode switcher)
    B1 --> B1b(ModulePanel/ - Each module UI)
    B1 --> B1c(ChatInterface.jsx - Voice + text chat)
    B --> B2(services/ - HTTP API calls)
    B --> B3(app.tsx)
    
    A --> C(app/ Python + FastAPI Backend)
    C --> C1(main.py - HTTP server)
    C --> C2(modules/ Independent modules)
    C2 --> C2a(google_clients/ - Gmail, Calendar, Drive)
    C2 --> C2b(weather.py)
    C2 --> C2c(systemInfo.py)
    C2 --> C2d(contact_booklet.py - Contact management with SQLite 🆕)
    C --> C3(services/ Business Logic Layer)
    C3 --> C3a(weather_service.py)
    C3 --> C3b(email_manager.py - Multi-account email 🆕)
    C3 --> C3c(email_service.py - Single account deprecated ⚠️)
    C3 --> C3d(calendar_service.py)
    C3 --> C3e(drive_service.py)
    C --> C4(config.py - Multi-account configuration 🆕)
    C --> C5(secrets/ - Credentials & tokens 🆕)
    C --> C6(email_accounts.json - Account configuration 🆕)
    C --> C7(db/ SQLite Database)
    C7 --> C7a(database.py - SQLAlchemy setup)
    C7 --> C7b(models.py - Contact model)
    C7 --> C7c(app.db - SQLite database file)
    
    A --> S(skills/ Standalone MCP Server)
    S --> S1(server.py - FastMCP server)
    S --> S2(email_skills.py - Multi-account email skills 🆕)
    S --> S3(contact_skills.py - Contact management MCP tools 🆕)
    S --> S4(weather_skills.py - Weather MCP tools)
    S --> S5(README.md - Skills documentation)
    
    A --> D(memory/ ChromaDB + embeddings)
    A --> E(tts_stt/ Whisper + ElevenLabs integration)
    A --> F(automation/ AutoGUI scripts)
    A --> G(README.md)
    
    A --> H(llm_orchestrator/ Agent Engine)
    H --> H1(llm_api_client.py - call OpenAI, DeepSeek, Gemini)
    H --> H2(plan_executor.py - plan steps, invoke MCP skills)
    H --> H3(memory_interface.py - retrieve/store context)
    H --> S(MCP Skill Server - skills/)
    
    %% Smart Automation Flow
    H2 --> AI{AI Request Analysis}
    AI --> AI1["Send email to Sergio about project"]
    AI1 --> S3
    S3 --> C2d
    C2d --> S2
    S2 --> C3b
    AI --> AI2["What's the weather in Paris?"]
    AI2 --> S4
    S4 --> C2b
```

## Email System Architecture 🆕

The application now supports **multi-account email management**:

### New Multi-Account System:
- **EmailManager** - Manages multiple email accounts (personal, work, etc.)
- **Account-specific operations** - Send/receive from specific accounts
- **Unified interface** - Single API for all accounts
- **Secure credential storage** - Credentials stored in `app/secrets/`
- **Flexible configuration** - JSON-based account configuration

### Architecture Components:

```mermaid
flowchart LR
    A[EmailManager] --> B[Personal Gmail]
    A --> C[Work Gmail]
    A --> D[Future: Outlook]
    A --> E[Future: Exchange]
    
    B --> B1[secrets/credentials_personal.json]
    B --> B2[secrets/token_personal.json]
    C --> C1[secrets/credentials_work.json]
    C --> C2[secrets/token_work.json]
    
    F[email_accounts.json] --> A
    G[MCP Tools] --> A
    H[Skills Layer] --> A
```

## Application Workflow

```mermaid
sequenceDiagram
    participant UI as User Interface
    participant LLM as LLM Orchestrator
    participant MCP as Skill Server (MCP)
    participant CM as ContactManager
    participant EM as EmailManager
    participant Gmail as Gmail API

    UI->>LLM: "Send work email to Sergio about project update"
    LLM->>MCP: invoke(skill="find_contact", name="Sergio")
    MCP->>CM: search contact by name
    CM-->>MCP: return contact with email
    MCP-->>LLM: Contact found: sergio@company.com
    LLM->>MCP: invoke(skill="send_email_from_account", to="sergio@company.com", account="work", ...)
    MCP->>EM: send_email(account="work", to="sergio@company.com", ...)
    EM->>Gmail: Gmail API call with work credentials
    Gmail-->>EM: Success / Data
    EM-->>MCP: Return result with account info
    MCP-->>LLM: Return result
    LLM->>UI: "Work email sent to Sergio about project update!"
```

## Codebase Structure 📁

```
its-Friday/
├── 📄 ReadMe.md                     # Project documentation
├── 📄 requirements.txt              # Python dependencies
├── 📄 api.json                      # API configuration
├── 📄 .env.sample                   # Environment template
├── 📄 MULTI_ACCOUNT_FIX_SUMMARY.md  # Multi-account fix documentation
│
├── 📁 app/                          # Main Python application
│   ├── 📄 __init__.py               # App initialization & service instances
│   ├── 📄 main.py                   # FastAPI HTTP server
│   ├── 📄 config.py                 # Multi-account configuration system
│   ├── 📄 dependencies.py           # FastAPI dependencies & auth
│   ├── 📄 utils.py                  # Utility functions & EmailAccountManager
│   ├── 📄 .env                      # Environment variables (local)
│   ├── 📄 email_accounts.json       # Email account configurations
│   ├── 📄 email_accounts.json.example # Email config template
│   │
│   ├── 📁 db/                       # Database layer
│   │   ├── 📄 database.py           # SQLAlchemy database setup
│   │   ├── 📄 models.py             # Database models (Contact, etc.)
│   │   └── 📄 app.db                # SQLite database file
│   │
│   ├── 📁 modules/                  # Core functionality modules
│   │   ├── 📄 __init__.py           # Module imports
│   │   ├── 📄 weather.py            # Weather API client
│   │   ├── 📄 contact_booklet.py    # Contact management
│   │   ├── 📄 systemInfo.py         # System information gathering
│   │   │
│   │   ├── 📁 google_clients/       # Google API clients
│   │   │   ├── 📄 __init__.py       # Google clients exports
│   │   │   ├── 📄 google_base_client.py # OAuth2 base client
│   │   │   ├── 📄 gmail_client.py   # Gmail API wrapper
│   │   │   ├── 📄 calendar_client.py# Calendar API wrapper
│   │   │   └── 📄 drive_client.py   # Drive API wrapper
│   │   │
│   │   └── 📁 email_clients/        # Email provider adapters
│   │       ├── 📄 __init__.py       # Email clients exports
│   │       ├── 📄 base_email_client.py # Abstract email interface
│   │       ├── 📄 gmail_client_adapter.py # Gmail adapter
│   │       ├── 📄 outlook_client_adapter.py # Outlook adapter (placeholder)
│   │       └── 📄 README.md         # Email architecture docs
│   │
│   ├── 📁 services/                 # Business logic layer
│   │   ├── 📄 __init__.py           # Service exports
│   │   ├── 📄 weather_service.py    # Weather operations
│   │   ├── 📄 email_manager.py      # 🆕 Multi-account email manager
│   │   ├── 📄 calendar_service.py   # Calendar operations
│   │   └── 📄 drive_service.py      # Drive operations
│   │
│   ├── 📁 routes/                   # FastAPI route handlers
│   │   ├── 📄 __init__.py           # Routes initialization
│   │   └── 📄 weather_endpoints.py  # Weather HTTP endpoints
│   │
│   ├── 📁 secrets/                  # 🔒 Secure credential storage
│   │   ├── 📄 credentials.json      # Default Gmail credentials
│   │   ├── 📄 token.json           # Default Gmail token
│   │   └── 📄 test_token.json      # Test credentials
│   │
│   └── 📁 logs/                     # Application logs
│
├── 📁 skills/                       # 🤖 MCP Server (Model Context Protocol)
│   ├── 📄 __init__.py               # Skills module exports
│   ├── 📄 server.py                 # FastMCP server with all tools
│   ├── 📄 weather_skills.py         # Weather-related MCP tools
│   ├── 📄 email_skills.py           # 🆕 Multi-account email tools
│   ├── 📄 calendar_skills.py        # Calendar-related MCP tools
│   ├── 📄 drive_skills.py           # Drive-related MCP tools
│   └── 📄 README.md                 # Skills documentation
│
├── 📁 examples/                     # Usage examples
│   └── 📄 email_manager_demo.py     # EmailManager usage examples
│
├── 📁 testing/                      # Test suite
│   ├── 📄 test_auth_system.py       # Google OAuth testing
│   ├── 📄 test_contact.py           # Contact system testing
│   ├── 📄 test_email.py             # Email functionality testing
│   └── 📁 need_verify/              # Integration test results
│       └── 📄 README.MD             # Test verification docs
│
└── 📁 ZZZ_guides/                   # 📚 Comprehensive documentation
    ├── 📄 EMAIL_SYSTEM_ARCHITECTURE.md # Email system detailed docs
    ├── 📄 GMAIL_CLIENT_README.md     # Gmail client documentation
    ├── 📄 INTEGRATION_GUIDE.md       # Integration guide
    ├── 📄 MULTI_ACCOUNT_EMAIL_GUIDE.md # Multi-account setup guide
    ├── 📄 OAUTH_FLOW.md             # OAuth2 authentication flow
    └── 📄 gmail_client_examples.py  # Gmail client code examples
```

## Quick Setup for Multi-Account Email

### 1. Add Email Accounts

```bash
# Add personal Gmail account
python setup_email_accounts.py add personal gmail "path/to/personal_credentials.json" "Personal Gmail"

# Add work Gmail account (set as default)
python setup_email_accounts.py add work gmail "path/to/work_credentials.json" "Work Gmail" --default

# List configured accounts
python setup_email_accounts.py list
```

### 2. Test Your Setup

```bash
python test_multi_email_setup.py
```

### 3. Use in MCP Server

```bash
cd skills && python server.py
```

## New MCP Tools Available 🆕

### Contact Management Tools:
- `list_contacts(offset=0, limit=20)` - List all contacts with pagination
- `find_contact(name="Sergio")` - Search contacts by name (surname/forename)
- `add_contact(contact_data)` - Add new contact to database
- `update_contact(contact_id, updated_data)` - Update existing contact
- `delete_contact(name)` - Delete contacts by name
- `get_contact_by_id(contact_id)` - Get specific contact by ID

### Email Management Tools:
- `list_email_accounts()` - Show all configured accounts
- `get_unread_emails_from_account(account="personal")` - Get emails from specific account
- `get_unread_emails_all_accounts()` - Get emails from all accounts
- `send_email_from_account(..., account="work")` - Send from specific account
- `create_draft_tool(..., account="work")` - Create email drafts
- `mark_emails_as_read_tool(message_ids, account)` - Mark emails as read

### Smart Automation Examples:
```
User: "Send an email to Sergio about the Friday project update"
→ Model finds Sergio's contact → Gets email address → Sends email

User: "Email all clients about the new feature"  
→ Model searches contacts with tag 'client' → Sends bulk emails

User: "What's John's phone number?"
→ Model searches contacts for John → Returns contact details
```

## Environment Configuration

### .env file (for general settings):
```bash
WEATHER_API_KEY=your_weather_api_key
SECURITY_KEY=your_security_key
LOG_LEVEL=INFO
DEFAULT_EMAIL_ACCOUNT=personal
```

### email_accounts.json (for email accounts):
```json
{
  "personal": {
    "name": "personal",
    "provider": "gmail",
    "display_name": "Personal Gmail",
    "google_credentials_path": "secrets/credentials_personal.json",
    "google_token_path": "secrets/token_personal.json",
    "enabled": true,
    "default_account": true
  },
  "work": {
    "name": "work",
    "provider": "gmail",
    "display_name": "Work Gmail", 
    "google_credentials_path": "secrets/credentials_work.json",
    "google_token_path": "secrets/token_work.json",
    "enabled": true,
    "default_account": false
  }
}
```

## Migration from Single Account

### Old Way (Deprecated):
```python
from app import email_service
result = email_service.send_email(to="user@example.com", ...)
```

### New Way (Recommended):
```python
from app import email_manager
result = await email_manager.send_email(
    to="user@example.com", 
    account="personal", 
    ...
)
```

## Security Features 🔒

- **Credential Isolation** - Each account has separate credentials
- **Secure Storage** - All credentials stored in `app/secrets/`
- **Token Management** - Automatic token refresh per account
- **Account Control** - Enable/disable accounts individually
- **Path Flexibility** - Configurable credential paths

### <b>The project is under active development</b>

**Recent Updates:**
- ✅ Multi-account email support
- ✅ Contact management system with SQLite database
- ✅ Secure credential management
- ✅ MCP server integration with contact tools
- ✅ Account management utilities
- ✅ Smart email automation (contact lookup + email sending)
- ✅ Comprehensive documentation

**Coming Soon:**
- 🔄 Outlook/Exchange support
- 🔄 IMAP/SMTP support
- 🔄 Email synchronization
- 🔄 Web-based account management
- 🔄 Advanced email automation
