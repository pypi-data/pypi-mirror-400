import requests
from datetime import datetime, timedelta
from .auth import AuthUtils

class CalendarUtils:
    """Utilities for accessing Calendar resources via MS Graph API"""

    @staticmethod
    def get_calendar_events(start_datetime, end_datetime):
        """
        Get calendar events from MS Graph API.
        Args:
            start_datetime: Start date in ISO format withh Beijing timezone, e.g. 2023-10-01T00:00:00+08:00
            end_datetime: End date in ISO format withh Beijing timezone, e.g. 2023-10-31T23:59:59+08:00
        Returns:
            list: A list of simplified calendar events. 
            Each event is a dictionary with keys: 'meeting_name', 'start_time', 'end_time', and 'timezone'. 
        """
        print(f"start: {start_datetime}")
        print(f"end: {end_datetime}")

        access_token = AuthUtils.login()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            'Prefer': 'outlook.timezone="China Standard Time"',
            'Content-Type': 'application/json'
        }

        # url = "https://graph.microsoft.com/v1.0/me/events"
        url = "https://graph.microsoft.com/v1.0/me/calendar/calendarView"

        params = {
            '$select': 'subject,start,end',
            'startDateTime': start_datetime,
            'endDateTime': end_datetime,
        }
        
        simplified_events = []

        while url:
            # Make the request to get the chats
            response = requests.get(url, headers=headers, params=params)
    
            if response.status_code != 200:
                print(f"Error retrieving events: {response.text}")
                return False

            events = response.json().get('value', [])
            
            # format the events to a simplified structure
            for event in events:
                print(event.get('subject'))
                print(event.get('start', {}).get('dateTime'))
                simplified_events.append({
                    'meeting_name': event.get('subject', 'No Title'),
                    'start_time': event.get('start', {}).get('dateTime'),
                    'end_time': event.get('end', {}).get('dateTime'),
                    'timezone': event.get('start', {}).get('timeZone', 'China Standard Time')
                })

            # get the next page of chats
            url = response.json().get("@odata.nextLink")
            params = None  # No need to pass $top parameter for subsequent requests

    
        return simplified_events