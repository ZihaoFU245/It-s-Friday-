#!/usr/bin/env python3
"""
Test script for multi-account email setup

This script tests the multi-account email configuration without actually
sending emails or accessing Gmail APIs.
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.config import Config, EmailAccountConfig
from app.services.email_manager import EmailManager

def test_config():
    """Test the configuration loading."""
    print("Testing Configuration...")
    
    try:
        config = Config()
        print(f"✓ Config loaded successfully")
        print(f"✓ Default email account: {config.default_email_account}")
        print(f"✓ Number of email accounts: {len(config.email_accounts)}")
        
        for name, account in config.email_accounts.items():
            print(f"  - {name}: {account.provider} ({account.display_name}) {'[DEFAULT]' if account.default_account else ''}")
        
        return config
        
    except Exception as e:
        print(f"✗ Config loading failed: {e}")
        return None

def test_email_manager(config):
    """Test the EmailManager initialization."""
    print("\nTesting EmailManager...")
    
    try:
        email_manager = EmailManager(config)
        print(f"✓ EmailManager initialized successfully")
        
        # Test account discovery
        available_accounts = email_manager.available_accounts
        print(f"✓ Available accounts: {available_accounts}")
        
        # Test default account
        try:
            default_account = email_manager.get_default_account()
            print(f"✓ Default account: {default_account}")
        except Exception as e:
            print(f"⚠ Default account issue: {e}")
        
        # Test account validation (without actually connecting)
        summary = email_manager.get_summary()
        print(f"✓ Account summary generated:")
        print(f"  - Total accounts: {summary['total_accounts']}")
        print(f"  - Default account: {summary.get('default_account', 'None')}")
        
        return email_manager
        
    except Exception as e:
        print(f"✗ EmailManager initialization failed: {e}")
        return None

def test_skills_import():
    """Test importing the skills module."""
    print("\nTesting Skills Import...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "skills"))
        from all_skills import (
            get_unread_emails,
            get_all_unread_emails, 
            send_email,
            get_email_accounts
        )
        print("✓ Skills module imported successfully")
        print("✓ Multi-account email functions available:")
        print("  - get_unread_emails(account=...)")
        print("  - get_all_unread_emails()")
        print("  - send_email(..., account=...)")
        print("  - get_email_accounts()")
        
        return True
        
    except Exception as e:
        print(f"✗ Skills import failed: {e}")
        return False

def test_mcp_server_import():
    """Test importing the MCP server."""
    print("\nTesting MCP Server Import...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "skills"))
        import server
        print("✓ MCP server module imported successfully")
        print("✓ New MCP tools should be available:")
        print("  - get_unread_emails_from_account")
        print("  - get_unread_emails_all_accounts") 
        print("  - send_email_from_account")
        print("  - list_email_accounts")
        
        return True
        
    except Exception as e:
        print(f"✗ MCP server import failed: {e}")
        return False

def show_setup_instructions():
    """Show next steps for setup."""
    print("\n" + "="*60)
    print("SETUP INSTRUCTIONS")
    print("="*60)
    print()
    print("1. Configure your email accounts:")
    print("   python setup_email_accounts.py add personal gmail /path/to/personal_creds.json")
    print("   python setup_email_accounts.py add work gmail /path/to/work_creds.json --default")
    print()
    print("2. Or copy the example configuration:")
    print("   copy app\\email_accounts.json.example app\\email_accounts.json")
    print("   # Then edit app\\email_accounts.json with your actual paths")
    print()
    print("3. Test your setup:")
    print("   python test_multi_email_setup.py")
    print()
    print("4. Run the MCP server:")
    print("   cd skills && python server.py")
    print()
    print("5. Use the new MCP tools:")
    print("   - list_email_accounts()")
    print("   - get_unread_emails_from_account(account='personal')")
    print("   - send_email_from_account(to='...', subject='...', body='...', account='work')")
    print()

def main():
    """Run all tests."""
    print("ITS-FRIDAY Multi-Account Email Setup Test")
    print("="*50)
    
    # Test configuration
    config = test_config()
    if not config:
        show_setup_instructions()
        return False
    
    # Test email manager
    email_manager = test_email_manager(config)
    if not email_manager:
        show_setup_instructions()
        return False
    
    # Test skills import
    skills_ok = test_skills_import()
    
    # Test MCP server import 
    mcp_ok = test_mcp_server_import()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Configuration: {'✓ PASS' if config else '✗ FAIL'}")
    print(f"EmailManager: {'✓ PASS' if email_manager else '✗ FAIL'}")
    print(f"Skills Module: {'✓ PASS' if skills_ok else '✗ FAIL'}")
    print(f"MCP Server: {'✓ PASS' if mcp_ok else '✗ FAIL'}")
    
    all_passed = all([config, email_manager, skills_ok, mcp_ok])
    
    if all_passed:
        print("\n🎉 All tests passed! Your multi-account email setup is ready.")
        print("\nNext steps:")
        print("1. Configure your actual email accounts using setup_email_accounts.py")
        print("2. Run the MCP server: cd skills && python server.py")
        print("3. Use the new multi-account email tools!")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
        show_setup_instructions()
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
