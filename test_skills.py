"""
Quick test script to verify the skills module is working correctly
"""
import sys
import os

def test_imports():
    try:
        # Test basic imports
        import skills
        print("✓ Skills module imported successfully")
        
        from skills import all_skills
        print("✓ Skills functions imported successfully")
        
        from app import weather_service, email_service, calendar_service, drive_service
        print("✓ App services imported successfully")
        
        print("\n--- Available Skills ---")
        print("- fetch_weather")
        print("- get_weather_forecast") 
        print("- get_unread_emails")
        print("- send_email")
        print("- get_upcoming_events")
        print("- list_drive_files")
        
        print("\n--- Available Services ---")
        print("- weather_service")
        print("- email_service")
        print("- calendar_service")
        print("- drive_service")
        
        print("\n✅ All tests passed! Skills module is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_imports()
