#!/usr/bin/env python3
"""
Email Account Setup Helper

This script helps you configure multiple email accounts for the ITS-FRIDAY application.
It provides utilities to add, remove, and manage email account configurations.

Usage:
    python setup_email_accounts.py add personal gmail /path/to/personal_creds.json
    python setup_email_accounts.py add work gmail /path/to/work_creds.json
    python setup_email_accounts.py list
    python setup_email_accounts.py set-default personal
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.config import Config, EmailAccountConfig

def load_config() -> Config:
    """Load the current configuration."""
    return Config()

def save_config_to_file(config: Config, accounts: Dict[str, EmailAccountConfig]):
    """Save email account configuration to a JSON file."""
    config_file = Path(__file__).parent / "app" / "email_accounts.json"
    
    accounts_data = {}
    for name, account in accounts.items():
        accounts_data[name] = {
            "name": account.name,
            "provider": account.provider,
            "display_name": account.display_name,
            "google_credentials_path": str(account.google_credentials_path) if account.google_credentials_path else None,
            "google_token_path": str(account.google_token_path) if account.google_token_path else None,
            "enabled": account.enabled,
            "default_account": account.default_account
        }
    
    with open(config_file, 'w') as f:
        json.dump(accounts_data, f, indent=2)
    
    print(f"Email accounts configuration saved to {config_file}")

def load_config_from_file() -> Dict[str, EmailAccountConfig]:
    """Load email account configuration from JSON file."""
    config_file = Path(__file__).parent / "app" / "email_accounts.json"
    
    if not config_file.exists():
        return {}
    
    with open(config_file, 'r') as f:
        accounts_data = json.load(f)
    
    accounts = {}
    for name, data in accounts_data.items():
        accounts[name] = EmailAccountConfig(
            name=data["name"],
            provider=data["provider"],
            display_name=data.get("display_name", ""),
            google_credentials_path=Path(data["google_credentials_path"]) if data.get("google_credentials_path") else None,
            google_token_path=Path(data["google_token_path"]) if data.get("google_token_path") else None,
            enabled=data.get("enabled", True),
            default_account=data.get("default_account", False)
        )
    
    return accounts

def add_account(name: str, provider: str, credentials_path: str, display_name: str = "", set_default: bool = False):
    """Add a new email account."""
    config = load_config()
    existing_accounts = load_config_from_file()
    
    # Create credentials and token paths
    creds_path = Path(credentials_path)
    if not creds_path.exists():
        print(f"Error: Credentials file not found: {credentials_path}")
        return False
    
    # Create token path in secrets directory
    secrets_dir = Path(__file__).parent / "app" / "secrets"
    secrets_dir.mkdir(exist_ok=True)
    
    # Copy credentials to secrets directory
    target_creds_path = secrets_dir / f"credentials_{name}.json"
    token_path = secrets_dir / f"token_{name}.json"
    
    # Copy the credentials file
    import shutil
    shutil.copy2(creds_path, target_creds_path)
    
    # Create new account configuration
    new_account = EmailAccountConfig(
        name=name,
        provider=provider,
        display_name=display_name or f"{name.title()} {provider.title()} Account",
        google_credentials_path=target_creds_path,
        google_token_path=token_path,
        enabled=True,
        default_account=set_default
    )
    
    # If setting as default, unset other defaults
    if set_default:
        for account in existing_accounts.values():
            account.default_account = False
    
    existing_accounts[name] = new_account
    save_config_to_file(config, existing_accounts)
    
    print(f"Added email account '{name}' ({provider})")
    print(f"Credentials copied to: {target_creds_path}")
    print(f"Token will be saved to: {token_path}")
    if set_default:
        print(f"Set as default account")
    
    return True

def list_accounts():
    """List all configured email accounts."""
    accounts = load_config_from_file()
    
    if not accounts:
        print("No email accounts configured.")
        return
    
    print("Configured Email Accounts:")
    print("-" * 50)
    
    for name, account in accounts.items():
        status = "✓ Enabled" if account.enabled else "✗ Disabled"
        default_mark = " (DEFAULT)" if account.default_account else ""
        
        print(f"Name: {account.name}{default_mark}")
        print(f"Provider: {account.provider}")
        print(f"Display Name: {account.display_name}")
        print(f"Status: {status}")
        if account.google_credentials_path:
            print(f"Credentials: {account.google_credentials_path}")
        if account.google_token_path:
            print(f"Token: {account.google_token_path}")
        print("-" * 30)

def remove_account(name: str):
    """Remove an email account."""
    accounts = load_config_from_file()
    
    if name not in accounts:
        print(f"Account '{name}' not found.")
        return False
    
    del accounts[name]
    config = load_config()
    save_config_to_file(config, accounts)
    
    print(f"Removed email account '{name}'")
    return True

def set_default_account(name: str):
    """Set an account as the default."""
    accounts = load_config_from_file()
    
    if name not in accounts:
        print(f"Account '{name}' not found.")
        return False
    
    # Unset all defaults
    for account in accounts.values():
        account.default_account = False
    
    # Set new default
    accounts[name].default_account = True
    
    config = load_config()
    save_config_to_file(config, accounts)
    
    print(f"Set '{name}' as default email account")
    return True

def enable_account(name: str):
    """Enable an email account."""
    accounts = load_config_from_file()
    
    if name not in accounts:
        print(f"Account '{name}' not found.")
        return False
    
    accounts[name].enabled = True
    config = load_config()
    save_config_to_file(config, accounts)
    
    print(f"Enabled email account '{name}'")
    return True

def disable_account(name: str):
    """Disable an email account."""
    accounts = load_config_from_file()
    
    if name not in accounts:
        print(f"Account '{name}' not found.")
        return False
    
    accounts[name].enabled = False
    config = load_config()
    save_config_to_file(config, accounts)
    
    print(f"Disabled email account '{name}'")
    return True

def main():
    """Main command-line interface."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python setup_email_accounts.py add <name> <provider> <credentials_path> [display_name] [--default]")
        print("  python setup_email_accounts.py list")
        print("  python setup_email_accounts.py remove <name>")
        print("  python setup_email_accounts.py set-default <name>")
        print("  python setup_email_accounts.py enable <name>")
        print("  python setup_email_accounts.py disable <name>")
        print("")
        print("Examples:")
        print("  python setup_email_accounts.py add personal gmail /path/to/personal_creds.json")
        print("  python setup_email_accounts.py add work gmail /path/to/work_creds.json 'Work Email' --default")
        print("  python setup_email_accounts.py list")
        print("  python setup_email_accounts.py set-default personal")
        return
    
    command = sys.argv[1]
    
    if command == "add":
        if len(sys.argv) < 5:
            print("Usage: add <name> <provider> <credentials_path> [display_name] [--default]")
            return
        
        name = sys.argv[2]
        provider = sys.argv[3]
        credentials_path = sys.argv[4]
        display_name = sys.argv[5] if len(sys.argv) > 5 and not sys.argv[5].startswith('--') else ""
        set_default = "--default" in sys.argv
        
        add_account(name, provider, credentials_path, display_name, set_default)
    
    elif command == "list":
        list_accounts()
    
    elif command == "remove":
        if len(sys.argv) < 3:
            print("Usage: remove <name>")
            return
        remove_account(sys.argv[2])
    
    elif command == "set-default":
        if len(sys.argv) < 3:
            print("Usage: set-default <name>")
            return
        set_default_account(sys.argv[2])
    
    elif command == "enable":
        if len(sys.argv) < 3:
            print("Usage: enable <name>")
            return
        enable_account(sys.argv[2])
    
    elif command == "disable":
        if len(sys.argv) < 3:
            print("Usage: disable <name>")
            return
        disable_account(sys.argv[2])
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
