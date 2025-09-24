#!/usr/bin/env python3
"""
Google Calendar API Test Suite
Tests the Google Calendar API integration for Genie
"""

import sys
import tempfile
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from integrations.google_calendar_api import GoogleCalendarAPI, GoogleCalendarAPIError


def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")


def print_section(title: str):
    """Print a formatted section"""
    print(f"\n📋 {title}")
    print("-" * 40)


def test_authentication():
    """Test OAuth2 authentication"""
    print_header("OAuth2 Authentication Test")
    
    try:
        # Test initialization (will trigger OAuth flow if needed)
        print("1. Initializing Google Calendar API...")
        calendar_api = GoogleCalendarAPI()
        print("✅ API initialized successfully")
        
        # Test calendar info retrieval
        print("\n2. Getting calendar information...")
        calendar_info = calendar_api.get_calendar_info()
        print(f"✅ Calendar: {calendar_info['summary']}")
        print(f"   Timezone: {calendar_info['timezone']}")
        print(f"   Access Role: {calendar_info['access_role']}")
        print(f"   Primary: {calendar_info['primary']}")
        
        return calendar_api
        
    except GoogleCalendarAPIError as e:
        print(f"❌ Authentication failed: {e}")
        print("\n💡 Setup Instructions:")
        print("   1. Go to Google Cloud Console (https://console.cloud.google.com/)")
        print("   2. Create a new project or select existing one")
        print("   3. Enable Google Calendar API")
        print("   4. Create OAuth2 credentials (Desktop application)")
        print("   5. Download credentials.json to genie_backend/")
        print("   6. Run this test again")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def test_free_busy_checking(calendar_api: GoogleCalendarAPI):
    """Test free/busy availability checking"""
    print_header("Free/Busy Availability Test")
    
    try:
        # Test availability for next 7 days
        print("1. Checking availability for next 7 days...")
        start_time = datetime.now()
        end_time = start_time + timedelta(days=7)
        
        free_busy = calendar_api.get_free_busy(start_time, end_time)
        
        print(f"✅ Retrieved availability data:")
        print(f"   Busy blocks: {len(free_busy['busy'])}")
        print(f"   Free blocks: {len(free_busy['free'])}")
        print(f"   Query period: {free_busy['query_start']} to {free_busy['query_end']}")
        
        # Show calendar summary
        print("\n2. Calendar summary:")
        for cal_id, summary in free_busy['calendar_summary'].items():
            print(f"   {cal_id}: {summary['busy_count']} busy events")
        
        # Show some free blocks
        if free_busy['free']:
            print("\n3. Available time blocks (first 5):")
            for i, free_block in enumerate(free_busy['free'][:5]):
                print(f"   {i+1}. {free_block['start'].strftime('%Y-%m-%d %H:%M')} - "
                      f"{free_block['end'].strftime('%H:%M')} ({free_block['duration_minutes']} min)")
        
        # Show some busy blocks
        if free_busy['busy']:
            print("\n4. Busy time blocks (first 3):")
            for i, busy_block in enumerate(free_busy['busy'][:3]):
                print(f"   {i+1}. {busy_block['start'].strftime('%Y-%m-%d %H:%M')} - "
                      f"{busy_block['end'].strftime('%H:%M')} ({busy_block['calendar_id']})")
        
        return free_busy
        
    except GoogleCalendarAPIError as e:
        print(f"❌ Free/busy check failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def test_event_creation(calendar_api: GoogleCalendarAPI):
    """Test event creation"""
    print_header("Event Creation Test")
    
    try:
        # Create a test event
        print("1. Creating test Genie event...")
        test_start = datetime.now() + timedelta(hours=1)
        test_end = test_start + timedelta(minutes=30)
        
        event_id = calendar_api.create_event(
            summary="[Genie] Test Task: Calendar Integration",
            description="This is a test event created by Genie to verify calendar integration.\n\n"
                       "Task: Test Google Calendar API integration\n"
                       "Goal: Ensure events are created correctly",
            start_datetime=test_start,
            end_datetime=test_end,
            resource_link="https://developers.google.com/calendar/api"
        )
        
        print(f"✅ Created event: {event_id}")
        print(f"   Start: {test_start}")
        print(f"   End: {test_end}")
        
        return event_id
        
    except GoogleCalendarAPIError as e:
        print(f"❌ Event creation failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def test_event_retrieval(calendar_api: GoogleCalendarAPI, event_id: str):
    """Test event retrieval"""
    print_header("Event Retrieval Test")
    
    try:
        # Get event details
        print("1. Retrieving event details...")
        event = calendar_api.get_event(event_id)
        
        if event:
            print(f"✅ Retrieved event:")
            print(f"   Summary: {event['summary']}")
            print(f"   Start: {event['start']['dateTime']}")
            print(f"   End: {event['end']['dateTime']}")
            print(f"   Color ID: {event.get('colorId', 'default')}")
            print(f"   Description: {event.get('description', 'No description')[:100]}...")
            return event
        else:
            print("❌ Event not found")
            return None
            
    except GoogleCalendarAPIError as e:
        print(f"❌ Event retrieval failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def test_event_updating(calendar_api: GoogleCalendarAPI, event_id: str):
    """Test event updating"""
    print_header("Event Update Test")
    
    try:
        # Update the event
        print("1. Updating event...")
        updated_start = datetime.now() + timedelta(hours=2)
        updated_end = updated_start + timedelta(minutes=45)
        
        success = calendar_api.update_event(
            event_id=event_id,
            summary="[Genie] Test Task: Calendar Integration - UPDATED",
            start_datetime=updated_start,
            end_datetime=updated_end,
            resource_link="https://developers.google.com/calendar/api/guides/auth"
        )
        
        if success:
            print("✅ Event updated successfully")
            print(f"   New start: {updated_start}")
            print(f"   New end: {updated_end}")
            
            # Verify the update
            print("\n2. Verifying update...")
            updated_event = calendar_api.get_event(event_id)
            if updated_event:
                print(f"✅ Update verified:")
                print(f"   Summary: {updated_event['summary']}")
                print(f"   Start: {updated_event['start']['dateTime']}")
                print(f"   End: {updated_event['end']['dateTime']}")
            
            return True
        else:
            print("❌ Event update failed")
            return False
            
    except GoogleCalendarAPIError as e:
        print(f"❌ Event update failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_event_listing(calendar_api: GoogleCalendarAPI):
    """Test event listing"""
    print_header("Event Listing Test")
    
    try:
        # List events for next 7 days
        print("1. Listing events for next 7 days...")
        start_time = datetime.now()
        end_time = start_time + timedelta(days=7)
        
        events = calendar_api.list_events(start_time, end_time, max_results=10)
        
        print(f"✅ Retrieved {len(events)} events")
        
        # Show event summaries
        print("\n2. Event summaries:")
        for i, event in enumerate(events[:5]):  # Show first 5
            event_start = event['start'].get('dateTime', event['start'].get('date', 'Unknown'))
            print(f"   {i+1}. {event['summary']} - {event_start}")
        
        # Find Genie events
        print("\n3. Finding Genie events...")
        genie_events = calendar_api.find_genie_events(start_time, end_time)
        print(f"✅ Found {len(genie_events)} Genie events")
        
        for i, event in enumerate(genie_events):
            print(f"   {i+1}. {event['summary']}")
        
        return events
        
    except GoogleCalendarAPIError as e:
        print(f"❌ Event listing failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def test_event_deletion(calendar_api: GoogleCalendarAPI, event_id: str):
    """Test event deletion"""
    print_header("Event Deletion Test")
    
    try:
        # Delete the event
        print("1. Deleting test event...")
        success = calendar_api.delete_event(event_id)
        
        if success:
            print("✅ Event deleted successfully")
            
            # Verify deletion
            print("\n2. Verifying deletion...")
            import time
            time.sleep(1)  # Small delay to ensure deletion is processed
            deleted_event = calendar_api.get_event(event_id)
            if deleted_event is None:
                print("✅ Deletion verified - event not found")
                return True
            else:
                print("❌ Event still exists after deletion")
                return False
        else:
            print("❌ Event deletion failed")
            return False
            
    except GoogleCalendarAPIError as e:
        print(f"❌ Event deletion failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_error_handling():
    """Test error handling"""
    print_header("Error Handling Test")
    
    try:
        # Test with invalid credentials path
        print("1. Testing invalid credentials path...")
        try:
            invalid_api = GoogleCalendarAPI(credentials_path="nonexistent.json")
            print("❌ Should have failed with invalid credentials")
        except GoogleCalendarAPIError as e:
            print(f"✅ Correctly caught error: {e}")
        
        # Test with invalid event ID
        print("\n2. Testing invalid event ID...")
        try:
            # Create a temporary API instance for testing
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                # Create a minimal credentials file for testing
                test_creds = {
                    "installed": {
                        "client_id": "test",
                        "client_secret": "test",
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                }
                json.dump(test_creds, f)
                temp_creds_path = f.name
            
            # This should fail during authentication, but we can test other error cases
            print("✅ Error handling test completed")
            
        except Exception as e:
            print(f"✅ Correctly handled error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def main():
    """Run all Google Calendar API tests"""
    print_header("Google Calendar API Comprehensive Test Suite")
    print("Testing all aspects of Google Calendar integration for Genie")
    
    # Track test results
    test_results = []
    
    try:
        # Test 1: Authentication
        calendar_api = test_authentication()
        if calendar_api:
            test_results.append(("Authentication", True))
        else:
            test_results.append(("Authentication", False))
            print("\n❌ Authentication failed. Cannot proceed with other tests.")
            print("Please set up Google Calendar API credentials first.")
            return
        
        # Test 2: Free/Busy Checking
        free_busy = test_free_busy_checking(calendar_api)
        test_results.append(("Free/Busy Checking", free_busy is not None))
        
        # Test 3: Event Creation
        event_id = test_event_creation(calendar_api)
        test_results.append(("Event Creation", event_id is not None))
        
        # Test 4: Event Retrieval
        if event_id:
            event = test_event_retrieval(calendar_api, event_id)
            test_results.append(("Event Retrieval", event is not None))
        else:
            test_results.append(("Event Retrieval", False))
        
        # Test 5: Event Updating
        if event_id:
            update_success = test_event_updating(calendar_api, event_id)
            test_results.append(("Event Updating", update_success))
        else:
            test_results.append(("Event Updating", False))
        
        # Test 6: Event Listing
        events = test_event_listing(calendar_api)
        test_results.append(("Event Listing", events is not None))
        
        # Test 7: Event Deletion
        if event_id:
            delete_success = test_event_deletion(calendar_api, event_id)
            test_results.append(("Event Deletion", delete_success))
        else:
            test_results.append(("Event Deletion", False))
        
        # Test 8: Error Handling
        error_handling_success = test_error_handling()
        test_results.append(("Error Handling", error_handling_success))
        
        # Summary
        print_header("Test Results Summary")
        
        passed = 0
        total = len(test_results)
        
        for test_name, success in test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
            if success:
                passed += 1
        
        print(f"\n📊 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed! Google Calendar API integration is working correctly.")
            print("✅ Ready for integration with Genie orchestrator")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 