"""
Email Manager Usage Examples

This file demonstrates how to use the new EmailManager for multi-account email management.
EmailManager replaces the deprecated EmailService and provides support for multiple email accounts.
"""

import asyncio
import sys
import os
import json

# Add the app directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import email_manager


async def main():
    """Demonstrate EmailManager usage."""
    print("📧 Email Manager Demo")
    print("=" * 50)
    
    try:
        # Get summary of all email accounts
        print("\n📋 Email Accounts Summary:")
        summary = email_manager.get_summary()
        print(f"   Total Accounts: {summary['total_accounts']}")
        print(f"   Default Account: {summary['default_account']}")
        print(f"   Configured Accounts: {', '.join(summary['accounts'])}")
        
        # Get detailed account information
        print("\n🔧 Account Details:")
        account_info = email_manager.get_all_account_info()
        for account_name, info in account_info.items():
            status = "✅" if info.get('status') == 'ready' else "❌"
            print(f"   {status} {account_name}: {info.get('email', 'Unknown')} ({info.get('provider', 'Unknown')})")
        
        # Demonstrate unread messages from default account
        print("\n📥 Getting Unread Messages (Default Account):")
        try:
            unread_messages = email_manager.get_unread_messages(max_results=3)
            
            if unread_messages and len(unread_messages) > 0:
                print(f"   Found {len(unread_messages)} unread messages:")
                for i, msg in enumerate(unread_messages[:3], 1):
                    print(f"   {i}. {msg.get('subject', 'No Subject')[:50]}...")
                    print(f"      From: {msg.get('from', 'Unknown')}")
                    print(f"      Date: {msg.get('date', 'Unknown')}")
                    print()
            else:
                print("   No unread messages found")
        except Exception as e:
            print(f"   ❌ Error getting unread messages: {e}")
        
        # Demonstrate unread count for all accounts
        print("\n📊 Unread Count (All Accounts):")
        try:
            count_results = email_manager.count_all_unread_messages()
            if count_results.get('success'):
                total = count_results.get('total_unread', 0)
                print(f"   Total Unread: {total}")
                for account, count in count_results.get('accounts', {}).items():
                    print(f"   {account}: {count}")
            else:
                print(f"   ❌ Error counting: {count_results.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ Error counting unread: {e}")
        
        # Demonstrate getting unread from all accounts
        print("\n📥 Getting Unread Messages (All Accounts):")
        try:
            all_unread = email_manager.get_all_unread_messages(max_results_per_account=2)
            for account, messages in all_unread.items():
                if messages:
                    print(f"   {account}: {len(messages)} messages")
                    for msg in messages[:1]:  # Show first message from each account
                        print(f"      • {msg.get('subject', 'No Subject')[:40]}...")
                else:
                    print(f"   {account}: No unread messages")
        except Exception as e:
            print(f"   ❌ Error getting all unread: {e}")
        
        # Demonstrate sending (commented out to avoid actually sending)
        print("\n📤 Email Sending Examples (Demo - Not Executed):")
        print("""
        # Send from default account
        result = await email_manager.send_email(
            to="recipient@example.com",
            subject="Test from EmailManager",
            body="Hello from the multi-account email manager!"
        )
        
        # Send from specific account
        result = await email_manager.send_email(
            to=["user1@example.com", "user2@example.com"],
            subject="Rich Email from Work Account",
            body="Plain text version",
            html_body="<h1>HTML Version</h1><p>Rich content!</p>",
            account="work",
            cc="manager@company.com"
        )
        
        # Send with attachments
        result = await email_manager.send_email(
            to="client@example.com",
            subject="Documents",
            body="Please find attached documents.",
            attachments=["document.pdf", "spreadsheet.xlsx"],
            account="personal"
        )
        """)
        
        print("\n✅ Email Manager Demo Complete!")
        print("\nKey Benefits of EmailManager:")
        print("   ✅ Multi-account support")
        print("   ✅ Unified API across accounts") 
        print("   ✅ Account auto-detection")
        print("   ✅ Comprehensive error handling")
        print("   ✅ Provider-agnostic design")
        print("   ✅ Backwards compatibility")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("   Make sure email accounts are properly configured")
        print("   See app/email_accounts.json.example for setup")


def sync_demo():
    """Demonstrate synchronous usage."""
    print("\n🔄 Synchronous Usage Demo:")
    
    try:
        # Sync methods that are already available
        count_result = email_manager.count_unread_messages()
        print(f"   Default account unread count: {count_result.get('count', 0)}")
        
        account_info = email_manager.get_all_account_info()
        print(f"   Available accounts: {list(account_info.keys())}")
        
        summary = email_manager.get_summary()
        print(f"   Total configured accounts: {summary['total_accounts']}")
        
    except Exception as e:
        print(f"   ❌ Sync demo error: {e}")


if __name__ == "__main__":
    print("Starting Email Manager demonstration...")
    print("Note: This requires email accounts to be configured in app/email_accounts.json")
    print("See MULTI_ACCOUNT_SETUP_SUMMARY.md for setup instructions")
    print()
    
    # Run async demo
    asyncio.run(main())
    
    # Run sync demo  
    sync_demo()
    
    print("\n" + "=" * 50)
    print("📚 For more information, see:")
    print("   - MULTI_ACCOUNT_SETUP_SUMMARY.md")
    print("   - app/services/email_manager.py") 
    print("   - app/modules/email_clients/README.md")
