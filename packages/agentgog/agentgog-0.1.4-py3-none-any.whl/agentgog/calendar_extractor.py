#!/usr/bin/env python3
"""
Calendar extraction module for AI classifier

Handles calendar event detection and extraction using OpenRouter API
"""
import requests
import json
import os
import logging
from console import fg, fx
import datetime as dt
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "x-ai/grok-4.1-fast"

CALENDAR_EXTRACTION_PROMPT = """The following text was identified as a calendar event. Extract date, time, event name and details and call the tool add2calendar().

Current date and time: {current_datetime}

STRICT REQUIREMENTS:
- date: Must be in YYYY-MM-DD format. NEVER use relative expressions like "tomorrow", "next week", "in 2 days". You must convert any relative date to the actual calendar date.
- time: Must be in HH:MM format (24-hour). Use null if no time is specified. NEVER use "all day" or vague expressions.
- event_name: Title or name of the event
- details: Additional details, location, description (can be empty string)

Return a JSON object with the following structure:
{{
    "date": "YYYY-MM-DD format only - convert relative dates to actual dates",
    "time": "HH:MM format or null",
    "event_name": "title or name of the event",
    "details": "additional details, location, description or empty string"
}}

Examples:
Input: "Meeting with Alice tomorrow at 10am"
Output: {{"date": "2025-01-07", "time": "10:00", "event_name": "Meeting with Alice", "details": ""}}

Input: "Lunch with Bob on Friday"
Output: {{"date": "2025-01-10", "time": null, "event_name": "Lunch with Bob", "details": ""}}
""".format(current_datetime=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def update_event(event, date_, time_, hint, description):
    """
    Put proper dates and name to the calendar event

    Args:
        event: Google Calendar event dict
        date_: Date in YYYY-MM-DD format
        time_: Time in HH:MM format or None (defaults to 09:00)
        hint: Event summary/title
        description: Event description

    Returns:
        dict: Updated event dict
    """
    date_clean = date_.replace('-', '')
    time_clean = (time_ or '09:00').replace(':', '')

    formatted_date_time = f"{date_clean[:4]}-{date_clean[4:6]}-{date_clean[6:]}T{time_clean[:2]}:{time_clean[2:]}:00"
    start_time_obj = dt.datetime.strptime(formatted_date_time, "%Y-%m-%dT%H:%M:%S")
    end_time_obj = start_time_obj + dt.timedelta(hours=1)
    formatted_end_time = end_time_obj.strftime("%Y-%m-%dT%H:%M:%S")

    print(f"DEBUG: start_time = {start_time_obj}, formatted = {formatted_date_time}")
    print(f"DEBUG:   end_time = {end_time_obj}, formatted = {formatted_end_time}")

    event['start']['dateTime'] = formatted_date_time
    event['end']['dateTime'] = formatted_end_time
    event['summary'] = hint
    event['description'] = description
    return event


def add2calendar(date, time, event_name, details, timezone='Europe/Prague', reminder_minutes=15, location=''):
    """
    Add a calendar event to Google Calendar

    Args:
        date: Date string in YYYY-MM-DD format
        time: Time string in HH:MM format or None
        event_name: Name/title of the event
        details: Additional details or description
        timezone: Timezone string (default: 'Europe/Prague')
        reminder_minutes: Reminder minutes before event (default: 15)
        location: Event location (default: empty string)

    Returns:
        dict: Result of the calendar add operation
    """
    print(f"[add2calendar] Adding event: {event_name} on {date} at {time}")
    if details:
        print(f"[add2calendar] Details: {details}")

    event = {
        'summary': 'PLACEHOLDER',
        'location': location,
        'description': details or 'GPT added the meeting',
        'start': {
            'dateTime': 'PLACEHOLDER',
            'timeZone': timezone,
        },
        'end': {
            'dateTime': 'PLACEHOLDER',
            'timeZone': timezone,
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': reminder_minutes},
            ],
        },
    }

    date_normalized = date.replace('-', '') if date else '00000000'
    time_normalized = (time or '09:00').replace(':', '') if time else '0900'

    event = update_event(event, date_normalized, time_normalized, event_name, details)

    print(f"[add2calendar] Event constructed successfully!")
    print(f"[add2calendar] Event body: {json.dumps(event, indent=2)}")

    try:
        creds = None
        token_file = os.path.expanduser('~/.config/google/token.json')
        credentials_file = os.path.expanduser('~/.config/google/credentials.json')

        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(
                token_file,
                ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/tasks']
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print(f"[add2calendar] Refreshing expired credentials...")
                creds.refresh(Request())
            elif os.path.exists(credentials_file):
                print(f"[add2calendar] Running OAuth flow - browser will open...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file,
                    ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/tasks']
                )
                creds = flow.run_local_server(port=0)
            else:
                print(f"{fg.red}[add2calendar] Error: No credentials found.{fg.default}")
                print(f"{fg.yellow}Place OAuth credentials at: ~/.config/google/credentials.json{fg.default}")
                return {
                    "success": False,
                    "error": "No Google credentials found",
                    "event": event
                }

            os.makedirs(os.path.dirname(token_file), exist_ok=True)
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
            print(f"[add2calendar] Credentials saved to {token_file}")

        service = build('calendar', 'v3', credentials=creds)
        inserted_event = service.events().insert(calendarId='primary', body=event).execute()

        print(f"{fg.green}[add2calendar] Event created successfully!{fg.default}")
        print(f"{fg.dimgray}Event link: {inserted_event.get('htmlLink')}{fg.default}")

        return {
            "success": True,
            "date": date,
            "time": time,
            "event_name": event_name,
            "details": details,
            "event": event,
            "htmlLink": inserted_event.get('htmlLink')
        }

    except Exception as e:
        print(f"{fg.red}[add2calendar] Error inserting event: {e}{fg.default}")
        return {
            "success": False,
            "error": str(e),
            "event": event
        }


def get_api_key():
    """Retrieve OpenRouter API key from environment or file"""
    api_key = os.environ.get('OPENROUTER_API_KEY')

    if not api_key:
        key_file = os.path.expanduser('~/.openrouter.key')
        try:
            if os.path.isfile(key_file):
                with open(key_file, 'r') as f:
                    api_key = f.read().strip()
                    if api_key:
                        logger.debug(f"Loaded API key from {key_file}")
        except Exception as e:
            logger.warning(f"Failed to read API key from {key_file}: {e}")

    return api_key


def extract_calendar_details(message_text, timeout=10):
    """
    Extract calendar details from a message using OpenRouter API

    Args:
        message_text: The calendar event message to extract details from
        timeout: API request timeout in seconds (default: 10)

    Returns:
        tuple: (success: bool, details: dict or None, raw_response: dict)
    """
    print("i... in extract_calendar_details")
    api_key = get_api_key()

    if not api_key:
        logger.error("OPENROUTER_API_KEY environment variable not set and ~/.openrouter.key not found")
        return False, None, {"error": "Missing API key"}

    if not message_text or not message_text.strip():
        logger.warning("Empty message text provided for extraction")
        return False, None, {"error": "Empty message"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": CALENDAR_EXTRACTION_PROMPT
            },
            {
                "role": "user",
                "content": message_text
            }
        ]
    }

    try:
        logger.info(f"Extracting calendar details from: {message_text[:100]}...")
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()

        response_data = response.json()

        try:
            content = response_data['choices'][0]['message']['content'].strip()

            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            elif content.startswith('```'):
                content = content.replace('```', '').strip()

            details = json.loads(content)

            if not isinstance(details, dict):
                raise ValueError("Expected JSON object")

            logger.info(f"Extracted calendar details: {details}")
            return True, details, response_data

        except (KeyError, IndexError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to extract calendar details: {e}")
            return False, None, response_data

    except requests.exceptions.Timeout:
        logger.error(f"OpenRouter API request timed out after {timeout}s")
        return False, None, {"error": "Timeout"}

    except requests.exceptions.RequestException as e:
        logger.error(f"OpenRouter API request failed: {e}")
        return False, None, {"error": str(e)}

    except Exception as e:
        logger.error(f"Unexpected error during extraction: {e}", exc_info=True)
        return False, None, {"error": str(e)}
