#!/usr/bin/env python3
"""
Test script to verify enhanced Google API authentication system.
This script tests the authentication for Gmail, Calendar, and Drive clients.
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_authentication():
    """Test authentication for all Google API clients."""
    print("🔧 Testing Enhanced Google API Authentication")
    print("=" * 50)
    
    try:
        print("\n📧 Testing Gmail Client Authentication...")
        from app.modules.google_clients.gmail_client import GmailClient
        gmail_client = GmailClient()
        
        # Test basic functionality
        profile = gmail_client.get_profile()
        user_info = gmail_client.get_user_info()
        
        print(f"✅ Gmail authentication successful!")
        print(f"   Email: {profile.get('emailAddress', 'Unknown')}")
        print(f"   Total messages: {profile.get('messagesTotal', 'Unknown')}")
        print(f"   Service: {user_info.get('service_name')}")
        print(f"   Scopes: {len(user_info.get('scopes', []))} scopes active")
        
    except Exception as e:
        print(f"❌ Gmail authentication failed: {e}")
        return False
    
    try:
        print("\n📅 Testing Calendar Client Authentication...")
        from app.modules.google_clients.calendar_client import CalendarClient
        calendar_client = CalendarClient()
        
        # Test basic functionality
        events = calendar_client.list_events(max_results=1)
        user_info = calendar_client.get_user_info()
        
        print(f"✅ Calendar authentication successful!")
        print(f"   Service: {user_info.get('service_name')}")
        print(f"   Scopes: {len(user_info.get('scopes', []))} scopes active")
        print(f"   Can access events: {'Yes' if isinstance(events, list) else 'No'}")
        
    except Exception as e:
        print(f"❌ Calendar authentication failed: {e}")
        return False
    
    try:
        print("\n💾 Testing Drive Client Authentication...")
        from app.modules.google_clients.drive_client import DriveClient
        drive_client = DriveClient()
        
        # Test basic functionality
        files = drive_client.list_files(page_size=1)
        user_info = drive_client.get_user_info()
        
        print(f"✅ Drive authentication successful!")
        print(f"   Service: {user_info.get('service_name')}")
        print(f"   Scopes: {len(user_info.get('scopes', []))} scopes active")
        print(f"   Can access files: {'Yes' if isinstance(files, list) else 'No'}")
        
    except Exception as e:
        print(f"❌ Drive authentication failed: {e}")
        return False
    
    print(f"\n🎉 All Google API clients authenticated successfully!")
    return True

def test_scope_management():
    """Test dynamic scope management."""
    print(f"\n🔧 Testing Scope Management...")
    
    try:
        from app.modules.google_clients.gmail_client import GmailClient
        gmail_client = GmailClient()
        
        # Test adding additional scopes (this would trigger re-auth if needed)
        original_scopes = gmail_client.scopes.copy()
        print(f"   Original scopes: {len(original_scopes)}")
        
        # Try to add a scope that might not be there
        additional_scopes = ["https://www.googleapis.com/auth/gmail.settings.basic"]
        success = gmail_client.add_scopes(additional_scopes)
        
        if success:
            print(f"✅ Scope management working (added {len(additional_scopes)} scope)")
        else:
            print(f"⚠️  Scope management tested (no new scopes needed)")
            
        return True
        
    except Exception as e:
        print(f"❌ Scope management test failed: {e}")
        return False

if __name__ == "__main__":
    print("Google API Authentication Test Suite")
    print("This will test the enhanced authentication system for all Google services")
    print()
    
    confirm = input("Continue with authentication test? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Test cancelled.")
        sys.exit(0)
    
    # Run authentication tests
    auth_success = test_authentication()
    
    if auth_success:
        # Run scope management tests
        scope_success = test_scope_management()
        
        if scope_success:
            print(f"\n🎊 All tests passed! The enhanced authentication system is working correctly.")
            sys.exit(0)
        else:
            print(f"\n⚠️  Authentication works but scope management has issues.")
            sys.exit(1)
    else:
        print(f"\n❌ Authentication tests failed.")
        sys.exit(1)
