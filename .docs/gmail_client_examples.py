"""
Gmail Client Usage Examples

This file demonstrates how to use the enhanced Gmail client for various email operations.
Make sure you have proper Gmail API credentials set up before running these examples.
"""

import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__), '..')))

from app.modules.google_clients.gmail_client import GmailClient
from datetime import datetime


def main():
    """Main function demonstrating Gmail client usage."""
    
    print("Gmail Client Examples")
    print("=" * 50)
    
    try:
        # Initialize the Gmail client
        print("1. Initializing Gmail client...")
        client = GmailClient()
        print("✓ Gmail client initialized successfully")
        
        # Get user profile
        print("\n2. Getting user profile...")
        profile = client.get_profile()
        print(f"✓ Email: {profile['emailAddress']}")
        print(f"✓ Total messages: {profile['messagesTotal']}")
        print(f"✓ Total threads: {profile['threadsTotal']}")
        
        # Example 1: List recent messages
        print("\n3. Listing recent messages...")
        messages = client.list_messages(max_results=5)
        print(f"✓ Found {len(messages)} recent messages")
        
        if messages:
            # Get and format the first message
            print("\n4. Getting details of the first message...")
            first_msg_id = messages[0]['id']
            raw_message = client.get_raw_message(first_msg_id)
            formatted_message = client.get_formatted_message(raw_message)
            
            print(f"✓ Subject: {formatted_message['subject']}")
            print(f"✓ From: {formatted_message['from']}")
            print(f"✓ Date: {formatted_message['date']}")
            print(f"✓ Snippet: {formatted_message['snippet']}")
        
        # Example 2: Count unread emails
        print("\n5. Counting unread emails...")
        unread_count = client.count_unread(hours=24, category="PRIMARY")
        print(f"✓ Unread emails in last 24 hours: {unread_count}")
        
        # Example 3: Search for emails
        print("\n6. Searching for emails...")
        search_results = client.search_messages("is:unread", max_results=3)
        print(f"✓ Found {len(search_results)} unread messages")
        
        # Example 4: List labels
        print("\n7. Listing labels...")
        labels = client.list_labels()
        print(f"✓ Found {len(labels)} labels:")
        for label in labels[:5]:  # Show first 5 labels
            print(f"   - {label['name']} (ID: {label['id']})")
        
        # Example 5: Create a draft
        print("\n8. Creating a draft email...")
        draft = client.create_draft(
            to=profile['emailAddress'],  # Send to yourself
            subject="Test Draft from Gmail Client",
            body="This is a test draft created by the Gmail client example script."
        )
        print(f"✓ Draft created with ID: {draft['id']}")
        
        # Example 6: List drafts
        print("\n9. Listing drafts...")
        drafts = client.list_drafts(max_results=5)
        print(f"✓ Found {len(drafts)} drafts")
        
        # Example 7: Update the draft we just created
        print("\n10. Updating the draft...")
        updated_draft = client.update_draft(
            draft_id=draft['id'],
            to=profile['emailAddress'],
            subject="Updated Test Draft from Gmail Client",
            body="This draft has been updated by the Gmail client example script."
        )
        print(f"✓ Draft updated: {updated_draft['id']}")
        
        # Example 8: Get thread information
        print("\n11. Getting thread information...")
        threads = client.list_threads(max_results=3)
        if threads:
            thread_id = threads[0]['id']
            thread_details = client.get_thread(thread_id)
            print(f"✓ Thread {thread_id} has {len(thread_details['messages'])} messages")
        
        # Example 9: Demonstrate attachment handling (if any messages have attachments)
        print("\n12. Checking for attachments...")
        messages_with_attachments = []
        for msg in messages[:3]:  # Check first 3 messages
            raw_msg = client.get_raw_message(msg['id'])
            formatted_msg = client.get_formatted_message(raw_msg)
            if formatted_msg['attachments']:
                messages_with_attachments.append(formatted_msg)
        
        print(f"✓ Found {len(messages_with_attachments)} messages with attachments")
        for msg in messages_with_attachments:
            print(f"   Message: {msg['subject']}")
            for att in msg['attachments']:
                print(f"   - Attachment: {att['filename']} ({att['mimeType']})")
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("\nNote: A draft email was created in your account.")
        print("You can find it in your Gmail drafts folder.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Set up Gmail API credentials (credentials.json)")
        print("2. Enabled the Gmail API in Google Cloud Console")
        print("3. Configured the correct scopes")
        return 1
    
    return 0


def demonstrate_sending_email():
    """Demonstrate sending an email (commented out for safety)."""
    print("\nEmail Sending Example (commented out for safety)")
    print("-" * 50)
    
    # Uncomment the following code to actually send an email
    # WARNING: This will send a real email!
    
    """
    try:
        client = GmailClient()
        profile = client.get_profile()
        
        # Send email to yourself
        result = client.send_email(
            to=profile['emailAddress'],
            subject="Test Email from Gmail Client",
            body="This is a test email sent using the Gmail client!",
            html_body="<h1>Test Email</h1><p>This is a <b>test email</b> sent using the Gmail client!</p>"
        )
        
        print(f"✓ Email sent successfully! Message ID: {result['id']}")
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
    """
    
    print("To enable email sending, uncomment the code in demonstrate_sending_email()")


def demonstrate_advanced_features():
    """Demonstrate advanced Gmail client features."""
    print("\nAdvanced Features Examples")
    print("-" * 50)
    
    try:
        client = GmailClient()
        
        # Example: Mark messages as read/unread
        print("1. Message state management...")
        messages = client.list_messages(max_results=1, query="is:unread")
        if messages:
            msg_id = messages[0]['id']
            print(f"   Found unread message: {msg_id}")
            
            # Mark as read, then unread again
            client.mark_as_read(msg_id)
            print("   ✓ Marked as read")
            
            client.mark_as_unread(msg_id)
            print("   ✓ Marked as unread")
        
        # Example: Label management
        print("\n2. Label management...")
        
        # Create a test label
        test_label = client.create_label("Test Label from Script")
        print(f"   ✓ Created label: {test_label['name']} (ID: {test_label['id']})")
        
        # Update the label
        updated_label = client.update_label(
            test_label['id'], 
            name="Updated Test Label",
            visibility="labelShow"
        )
        print(f"   ✓ Updated label: {updated_label['name']}")
        
        # Delete the test label
        client.delete_label(test_label['id'])
        print("   ✓ Deleted test label")
        
        # Example: History synchronization
        print("\n3. History synchronization...")
        profile = client.get_profile()
        current_history_id = profile['historyId']
        print(f"   Current history ID: {current_history_id}")
        
        # Try to get recent history (might be empty if no recent changes)
        history = client.get_history(current_history_id)
        if history:
            print(f"   ✓ Found {len(history.get('history', []))} history records")
        else:
            print("   ✓ No recent history changes")
        
        print("\n✓ Advanced features demonstration completed!")
        
    except Exception as e:
        print(f"\n❌ Error in advanced features: {e}")


if __name__ == "__main__":
    result = main()
    
    # Ask if user wants to see advanced examples
    choice = input("\nWould you like to see advanced features examples? (y/N): ").strip().lower()
    if choice == 'y':
        demonstrate_advanced_features()
    
    # Ask if user wants to see sending examples
    choice = input("\nWould you like to see email sending examples? (y/N): ").strip().lower()
    if choice == 'y':
        demonstrate_sending_email()
    
    sys.exit(result)
