#!/usr/bin/env python3
"""
Cleanup script to delete all Genie events from Google Calendar
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the current directory to Python path
import sys
sys.path.append(str(Path(__file__).parent))

from integrations.google_calendar_api import GoogleCalendarAPI, GoogleCalendarAPIError

def cleanup_genie_events():
    """
    Delete all Genie events from Google Calendar for today
    """
    print("🧹 Cleaning up Genie events from Google Calendar...")
    
    try:
        # Initialize Google Calendar API
        calendar_api = GoogleCalendarAPI()
        print("✅ Google Calendar API initialized")
        
        # Get today's date range
        today = datetime.now().date()
        start_time = datetime.combine(today, datetime.min.time())
        end_time = datetime.combine(today, datetime.max.time())
        
        print(f"📅 Looking for Genie events on {today.strftime('%Y-%m-%d')}")
        
        # Find all Genie events for today
        genie_events = calendar_api.find_genie_events(start_time, end_time)
        
        if not genie_events:
            print("✅ No Genie events found for today")
            return
        
        print(f"🔍 Found {len(genie_events)} Genie events to delete:")
        
        deleted_count = 0
        for event in genie_events:
            event_id = event['id']
            summary = event.get('summary', 'Unknown')
            start = event['start'].get('dateTime', event['start'].get('date', 'Unknown'))
            
            print(f"   🗑️  Deleting: {summary} ({start})")
            
            try:
                success = calendar_api.delete_event(event_id)
                if success:
                    deleted_count += 1
                    print(f"     ✅ Deleted successfully")
                else:
                    print(f"     ❌ Failed to delete")
            except Exception as e:
                print(f"     ❌ Error deleting: {e}")
        
        print(f"\n🎉 Cleanup completed!")
        print(f"   📊 Total events found: {len(genie_events)}")
        print(f"   ✅ Successfully deleted: {deleted_count}")
        print(f"   ❌ Failed to delete: {len(genie_events) - deleted_count}")
        
    except GoogleCalendarAPIError as e:
        print(f"❌ Google Calendar API error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    cleanup_genie_events() 