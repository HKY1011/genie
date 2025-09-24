#!/usr/bin/env python3
"""
Google Calendar API Integration for Genie

This module provides comprehensive Google Calendar integration for Genie,
enabling real-time availability checking and automatic mini-task scheduling.

Features:
- OAuth2 authentication with refreshable tokens
- Free/busy availability checking
- Event creation, updating, and deletion
- Conflict detection and resolution
- Automatic token refresh and error handling

Usage:
    # Initialize the API
    calendar_api = GoogleCalendarAPI()
    
    # Check availability
    free_slots = calendar_api.get_free_busy(
        start_datetime=datetime.now(),
        end_datetime=datetime.now() + timedelta(days=7)
    )
    
    # Create a mini-task event
    event_id = calendar_api.create_event(
        summary="[Genie] Build React component",
        description="Follow tutorial and implement user authentication",
        start_datetime=datetime.now() + timedelta(hours=1),
        end_datetime=datetime.now() + timedelta(hours=1, minutes=30),
        resource_link="https://react.dev/learn/authentication"
    )
    
    # Update event
    calendar_api.update_event(
        event_id=event_id,
        summary="[Genie] Build React component - UPDATED",
        start_datetime=datetime.now() + timedelta(hours=2)
    )
    
    # Delete event
    calendar_api.delete_event(event_id)
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleCalendarAPIError(Exception):
    """Custom exception for Google Calendar API operations"""
    pass


class GoogleCalendarAPI:
    """
    Google Calendar API integration for Genie
    
    Provides OAuth2 authentication, free/busy checking, and event management
    for seamless integration with Google Calendar.
    """
    
    # OAuth2 scopes for Google Calendar access
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    # Default timezone (can be overridden)
    DEFAULT_TIMEZONE = 'Asia/Kolkata'
    
    # Genie event color ID (for easy identification)
    GENIE_EVENT_COLOR_ID = '4'  # Blue color
    
    def __init__(self, 
                 credentials_path: str = "credentials.json",
                 token_path: str = "token.json",
                 calendar_id: str = "primary"):
        """
        Initialize Google Calendar API
        
        Args:
            credentials_path: Path to OAuth2 credentials file
            token_path: Path to store/load OAuth2 tokens
            calendar_id: Google Calendar ID (default: "primary")
        """
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.calendar_id = calendar_id
        
        # Initialize service
        self.service = None
        self.creds = None
        
        # Authenticate and build service
        self._authenticate()
        
        logger.info(f"Google Calendar API initialized for calendar: {calendar_id}")
    
    def _authenticate(self) -> None:
        """
        Authenticate with Google Calendar API using OAuth2
        
        Handles token refresh and credential management automatically.
        """
        try:
            # Check if credentials file exists
            if not self.credentials_path.exists():
                raise GoogleCalendarAPIError(
                    f"Credentials file not found: {self.credentials_path}. "
                    "Please download OAuth2 credentials from Google Cloud Console."
                )
            
            # Load existing token if available
            if self.token_path.exists():
                self.creds = Credentials.from_authorized_user_file(
                    str(self.token_path), self.SCOPES
                )
                logger.debug("Loaded existing OAuth2 token")
            
            # If no valid credentials available, authenticate
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    logger.info("Refreshing expired OAuth2 token")
                    self.creds.refresh(Request())
                else:
                    logger.info("Starting OAuth2 authentication flow")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_path), self.SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                
                # Save the credentials for next run
                with open(self.token_path, 'w') as token:
                    token.write(self.creds.to_json())
                logger.info(f"OAuth2 token saved to: {self.token_path}")
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=self.creds)
            logger.info("Google Calendar API service built successfully")
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise GoogleCalendarAPIError(f"Failed to authenticate with Google Calendar: {e}")
    
    def get_free_busy(self, 
                     start_datetime: datetime, 
                     end_datetime: datetime,
                     calendar_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get free/busy information for specified time range
        
        Args:
            start_datetime: Start time for availability check
            end_datetime: End time for availability check
            calendar_ids: List of calendar IDs to check (default: primary calendar)
            
        Returns:
            Dictionary with free/busy information including:
            - busy: List of busy time blocks
            - free: List of free time blocks
            - calendar_summary: Summary of calendar events
            
        Raises:
            GoogleCalendarAPIError: If API call fails
        """
        try:
            if not self.service:
                raise GoogleCalendarAPIError("Calendar service not initialized")
            
            # Use primary calendar if none specified
            if not calendar_ids:
                calendar_ids = [self.calendar_id]
            
            # Prepare request body
            body = {
                "timeMin": start_datetime.isoformat() + 'Z',
                "timeMax": end_datetime.isoformat() + 'Z',
                "items": [{"id": cal_id} for cal_id in calendar_ids]
            }
            
            logger.debug(f"Checking free/busy from {start_datetime} to {end_datetime}")
            
            # Call the API
            result = self.service.freebusy().query(body=body).execute()
            
            # Process the results
            free_busy_data = self._process_free_busy_result(result, start_datetime, end_datetime)
            
            logger.info(f"Retrieved free/busy data: {len(free_busy_data['busy'])} busy blocks, "
                       f"{len(free_busy_data['free'])} free blocks")
            
            return free_busy_data
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            raise GoogleCalendarAPIError(f"Failed to get free/busy data: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting free/busy: {e}")
            raise GoogleCalendarAPIError(f"Unexpected error: {e}")
    
    def _process_free_busy_result(self, 
                                 result: Dict[str, Any], 
                                 start_datetime: datetime, 
                                 end_datetime: datetime) -> Dict[str, Any]:
        """
        Process free/busy API result into usable format
        
        Args:
            result: Raw API response
            start_datetime: Start time of query
            end_datetime: End time of query
            
        Returns:
            Processed free/busy data
        """
        busy_blocks = []
        free_blocks = []
        calendar_summary = {}
        
        # Process each calendar's data
        for calendar_id, calendar_data in result.get('calendars', {}).items():
            calendar_busy = calendar_data.get('busy', [])
            calendar_summary[calendar_id] = {
                'busy_count': len(calendar_busy),
                'total_events': len(calendar_busy)
            }
            
            # Convert busy blocks to datetime objects
            for busy_block in calendar_busy:
                busy_start = datetime.fromisoformat(busy_block['start'].replace('Z', '+00:00'))
                busy_end = datetime.fromisoformat(busy_block['end'].replace('Z', '+00:00'))
                busy_blocks.append({
                    'start': busy_start,
                    'end': busy_end,
                    'calendar_id': calendar_id
                })
        
        # Sort busy blocks by start time
        busy_blocks.sort(key=lambda x: x['start'])
        
        # Calculate free blocks (gaps between busy blocks)
        current_time = start_datetime
        for busy_block in busy_blocks:
            if current_time < busy_block['start']:
                free_blocks.append({
                    'start': current_time,
                    'end': busy_block['start'],
                    'duration_minutes': int((busy_block['start'] - current_time).total_seconds() / 60)
                })
            current_time = max(current_time, busy_block['end'])
        
        # Add final free block if there's time remaining
        if current_time < end_datetime:
            free_blocks.append({
                'start': current_time,
                'end': end_datetime,
                'duration_minutes': int((end_datetime - current_time).total_seconds() / 60)
            })
        
        return {
            'busy': busy_blocks,
            'free': free_blocks,
            'calendar_summary': calendar_summary,
            'query_start': start_datetime,
            'query_end': end_datetime
        }
    
    def create_event(self, 
                    summary: str,
                    description: str,
                    start_datetime: datetime,
                    end_datetime: datetime,
                    resource_link: Optional[str] = None,
                    location: Optional[str] = None,
                    color_id: Optional[str] = None) -> str:
        """
        Create a new calendar event (mini-task)
        
        Args:
            summary: Event title/summary
            description: Event description/details
            start_datetime: Event start time
            end_datetime: Event end time
            resource_link: Optional resource URL for the task
            location: Optional location for the event
            color_id: Optional color ID for the event
            
        Returns:
            Google Calendar event ID
            
        Raises:
            GoogleCalendarAPIError: If event creation fails
        """
        try:
            if not self.service:
                raise GoogleCalendarAPIError("Calendar service not initialized")
            
            # Prepare event description with resource link
            full_description = description
            if resource_link:
                full_description += f"\n\n📚 Resource: {resource_link}"
            
            # Add Genie identifier
            full_description += "\n\n🤖 Created by Genie AI Assistant"
            
            # Prepare event body
            event = {
                'summary': summary,
                'description': full_description,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': self.DEFAULT_TIMEZONE
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': self.DEFAULT_TIMEZONE
                },
                'colorId': color_id or self.GENIE_EVENT_COLOR_ID,
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 5}
                    ]
                }
            }
            
            # Add location if provided
            if location:
                event['location'] = location
            
            logger.debug(f"Creating event: {summary} from {start_datetime} to {end_datetime}")
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            event_id = created_event['id']
            logger.info(f"Created calendar event: {event_id} - {summary}")
            
            return event_id
            
        except HttpError as e:
            logger.error(f"Failed to create calendar event: {e}")
            raise GoogleCalendarAPIError(f"Failed to create event: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating event: {e}")
            raise GoogleCalendarAPIError(f"Unexpected error: {e}")
    
    def update_event(self, 
                    event_id: str,
                    summary: Optional[str] = None,
                    description: Optional[str] = None,
                    start_datetime: Optional[datetime] = None,
                    end_datetime: Optional[datetime] = None,
                    resource_link: Optional[str] = None,
                    location: Optional[str] = None) -> bool:
        """
        Update an existing calendar event
        
        Args:
            event_id: Google Calendar event ID
            summary: New event title/summary
            description: New event description
            start_datetime: New start time
            end_datetime: New end time
            resource_link: New resource URL
            location: New location
            
        Returns:
            True if update successful
            
        Raises:
            GoogleCalendarAPIError: If update fails
        """
        try:
            if not self.service:
                raise GoogleCalendarAPIError("Calendar service not initialized")
            
            # Get existing event first
            existing_event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Update fields if provided
            if summary:
                existing_event['summary'] = summary
            
            if description or resource_link:
                # Prepare new description
                new_description = description or existing_event.get('description', '')
                if resource_link:
                    new_description += f"\n\n📚 Resource: {resource_link}"
                new_description += "\n\n🤖 Updated by Genie AI Assistant"
                existing_event['description'] = new_description
            
            if start_datetime:
                existing_event['start'] = {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': self.DEFAULT_TIMEZONE
                }
            
            if end_datetime:
                existing_event['end'] = {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': self.DEFAULT_TIMEZONE
                }
            
            if location:
                existing_event['location'] = location
            
            logger.debug(f"Updating event: {event_id}")
            
            # Update the event
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=existing_event
            ).execute()
            
            logger.info(f"Updated calendar event: {event_id}")
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Event not found: {event_id}")
                return False
            logger.error(f"Failed to update calendar event: {e}")
            raise GoogleCalendarAPIError(f"Failed to update event: {e}")
        except Exception as e:
            logger.error(f"Unexpected error updating event: {e}")
            raise GoogleCalendarAPIError(f"Unexpected error: {e}")
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete a calendar event
        
        Args:
            event_id: Google Calendar event ID
            
        Returns:
            True if deletion successful
            
        Raises:
            GoogleCalendarAPIError: If deletion fails
        """
        try:
            if not self.service:
                raise GoogleCalendarAPIError("Calendar service not initialized")
            
            logger.debug(f"Deleting event: {event_id}")
            
            # Delete the event
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"Deleted calendar event: {event_id}")
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Event not found for deletion: {event_id}")
                return False
            logger.error(f"Failed to delete calendar event: {e}")
            raise GoogleCalendarAPIError(f"Failed to delete event: {e}")
        except Exception as e:
            logger.error(f"Unexpected error deleting event: {e}")
            raise GoogleCalendarAPIError(f"Unexpected error: {e}")
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get event details by ID
        
        Args:
            event_id: Google Calendar event ID
            
        Returns:
            Event details dictionary or None if not found
            
        Raises:
            GoogleCalendarAPIError: If API call fails
        """
        try:
            if not self.service:
                raise GoogleCalendarAPIError("Calendar service not initialized")
            
            logger.debug(f"Getting event: {event_id}")
            
            # Get the event
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            logger.debug(f"Retrieved event: {event.get('summary', 'Unknown')}")
            return event
            
        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Event not found: {event_id}")
                return None
            logger.error(f"Failed to get calendar event: {e}")
            raise GoogleCalendarAPIError(f"Failed to get event: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting event: {e}")
            raise GoogleCalendarAPIError(f"Unexpected error: {e}")
    
    def list_events(self, 
                   start_datetime: datetime,
                   end_datetime: datetime,
                   max_results: int = 100) -> List[Dict[str, Any]]:
        """
        List events in a time range
        
        Args:
            start_datetime: Start time for event search
            end_datetime: End time for event search
            max_results: Maximum number of events to return
            
        Returns:
            List of event dictionaries
            
        Raises:
            GoogleCalendarAPIError: If API call fails
        """
        try:
            if not self.service:
                raise GoogleCalendarAPIError("Calendar service not initialized")
            
            logger.debug(f"Listing events from {start_datetime} to {end_datetime}")
            
            # Call the API
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_datetime.isoformat() + 'Z',
                timeMax=end_datetime.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"Retrieved {len(events)} events")
            
            return events
            
        except HttpError as e:
            logger.error(f"Failed to list calendar events: {e}")
            raise GoogleCalendarAPIError(f"Failed to list events: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing events: {e}")
            raise GoogleCalendarAPIError(f"Unexpected error: {e}")
    
    def find_genie_events(self, 
                         start_datetime: datetime,
                         end_datetime: datetime) -> List[Dict[str, Any]]:
        """
        Find Genie-created events in a time range
        
        Args:
            start_datetime: Start time for search
            end_datetime: End time for search
            
        Returns:
            List of Genie event dictionaries
        """
        try:
            all_events = self.list_events(start_datetime, end_datetime)
            
            # Filter for Genie events (those with Genie identifier in description)
            genie_events = []
            for event in all_events:
                description = event.get('description', '')
                if '🤖 Created by Genie AI Assistant' in description:
                    genie_events.append(event)
            
            logger.info(f"Found {len(genie_events)} Genie events")
            return genie_events
            
        except Exception as e:
            logger.error(f"Failed to find Genie events: {e}")
            return []
    
    def list_calendars(self) -> List[Dict[str, Any]]:
        """
        List all available calendars for the authenticated user
        
        Returns:
            List of calendar dictionaries with id, summary, and primary status
        """
        try:
            if not self.service:
                raise GoogleCalendarAPIError("Calendar service not initialized")
            
            calendar_list = self.service.calendarList().list().execute()
            calendars = []
            
            for calendar in calendar_list.get('items', []):
                calendars.append({
                    'id': calendar.get('id'),
                    'summary': calendar.get('summary'),
                    'description': calendar.get('description'),
                    'timezone': calendar.get('timeZone'),
                    'access_role': calendar.get('accessRole'),
                    'primary': calendar.get('primary', False),
                    'selected': calendar.get('selected', True)
                })
            
            return calendars
            
        except HttpError as e:
            logger.error(f"Failed to list calendars: {e}")
            raise GoogleCalendarAPIError(f"Failed to list calendars: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing calendars: {e}")
            raise GoogleCalendarAPIError(f"Unexpected error: {e}")

    def get_calendar_info(self) -> Dict[str, Any]:
        """
        Get information about the current calendar
        
        Returns:
            Dictionary with calendar information
        """
        try:
            if not self.service:
                raise GoogleCalendarAPIError("Calendar service not initialized")
            
            calendar = self.service.calendars().get(calendarId=self.calendar_id).execute()
            
            return {
                'id': calendar.get('id'),
                'summary': calendar.get('summary'),
                'description': calendar.get('description'),
                'timezone': calendar.get('timeZone'),
                'access_role': calendar.get('accessRole'),
                'primary': calendar.get('primary', False)
            }
            
        except HttpError as e:
            logger.error(f"Failed to get calendar info: {e}")
            raise GoogleCalendarAPIError(f"Failed to get calendar info: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting calendar info: {e}")
            raise GoogleCalendarAPIError(f"Unexpected error: {e}")


def demo_google_calendar_api():
    """
    Demo function showing how to use the Google Calendar API
    
    This demonstrates the complete workflow:
    1. Authentication
    2. Checking availability
    3. Creating events
    4. Updating events
    5. Deleting events
    """
    print("🎯 Google Calendar API Demo")
    print("=" * 50)
    
    try:
        # Initialize the API
        print("1. Initializing Google Calendar API...")
        calendar_api = GoogleCalendarAPI()
        print("✅ API initialized successfully")
        
        # Get calendar info
        print("\n2. Getting calendar information...")
        calendar_info = calendar_api.get_calendar_info()
        print(f"✅ Calendar: {calendar_info['summary']} ({calendar_info['timezone']})")
        
        # Check availability for next 7 days
        print("\n3. Checking availability for next 7 days...")
        start_time = datetime.now()
        end_time = start_time + timedelta(days=7)
        
        free_busy = calendar_api.get_free_busy(start_time, end_time)
        print(f"✅ Found {len(free_busy['busy'])} busy blocks")
        print(f"✅ Found {len(free_busy['free'])} free blocks")
        
        # Show some free blocks
        if free_busy['free']:
            print("\n📅 Available time blocks:")
            for i, free_block in enumerate(free_busy['free'][:3]):  # Show first 3
                print(f"   {i+1}. {free_block['start'].strftime('%Y-%m-%d %H:%M')} - "
                      f"{free_block['end'].strftime('%H:%M')} ({free_block['duration_minutes']} min)")
        
        # Create a demo event
        print("\n4. Creating a demo Genie event...")
        demo_start = datetime.now() + timedelta(hours=1)
        demo_end = demo_start + timedelta(minutes=30)
        
        event_id = calendar_api.create_event(
            summary="[Genie] Demo Task: Learn Google Calendar API",
            description="This is a demo event created by Genie to test calendar integration.\n\n"
                       "Task: Implement Google Calendar API in Genie backend\n"
                       "Goal: Enable automatic task scheduling",
            start_datetime=demo_start,
            end_datetime=demo_end,
            resource_link="https://developers.google.com/calendar/api"
        )
        print(f"✅ Created event: {event_id}")
        
        # Get event details
        print("\n5. Getting event details...")
        event = calendar_api.get_event(event_id)
        if event:
            print(f"✅ Event: {event['summary']}")
            print(f"   Start: {event['start']['dateTime']}")
            print(f"   End: {event['end']['dateTime']}")
        
        # Update the event
        print("\n6. Updating the event...")
        updated_start = demo_start + timedelta(minutes=15)
        updated_end = updated_start + timedelta(minutes=45)
        
        success = calendar_api.update_event(
            event_id=event_id,
            summary="[Genie] Demo Task: Learn Google Calendar API - UPDATED",
            start_datetime=updated_start,
            end_datetime=updated_end,
            resource_link="https://developers.google.com/calendar/api/guides/auth"
        )
        print(f"✅ Event updated: {success}")
        
        # Find Genie events
        print("\n7. Finding Genie events...")
        genie_events = calendar_api.find_genie_events(start_time, end_time)
        print(f"✅ Found {len(genie_events)} Genie events")
        
        # Clean up - delete the demo event
        print("\n8. Cleaning up - deleting demo event...")
        deleted = calendar_api.delete_event(event_id)
        print(f"✅ Event deleted: {deleted}")
        
        print("\n🎉 Google Calendar API Demo completed successfully!")
        print("✅ All operations working correctly")
        print("✅ Ready for integration with Genie orchestrator")
        
    except GoogleCalendarAPIError as e:
        print(f"❌ Calendar API Error: {e}")
        print("\n💡 Make sure you have:")
        print("   1. Downloaded credentials.json from Google Cloud Console")
        print("   2. Enabled Google Calendar API in your project")
        print("   3. Set up OAuth2 credentials")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    # Run the demo
    demo_google_calendar_api() 