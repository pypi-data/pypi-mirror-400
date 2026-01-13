#!/usr/bin/env python3
"""
Memo extraction module for AI classifier

Handles memo detection and extraction using OpenRouter API
Stores memos in Simplenote
"""
import requests
import json
import os
import logging
from console import fg, fx
import datetime as dt
import simplenote

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "x-ai/grok-4.1-fast"

MEMO_EXTRACTION_PROMPT = """The following text was identified as a memo/note to remember. Extract a concise title, the main content, and any labels/tags, then call the tool add2keep().

Current date and time: {current_datetime}

STRICT REQUIREMENTS:
- title: Short, descriptive title for the memo (max 50 characters)
- content: Main content/details to remember (MUST be  the original text)
- labels: List of labels/tags for categorization (can be empty list). Allowed labels: ['home', 'administration', 'important', 'web']

Return a JSON object with the following structure:
{{
    "title": "concise memo title (max 50 chars)",
    "content": "main content or details to remember",
    "labels": ["label1", "label2"] or []
}}

Examples:
Input: "Remember that my passport number is 123456789"
Output: {{"title": "Passport number", "content": "Passport number is 123456789", "labels": ["important"]}}

Input: "Mom's birthday is on December 15th"
Output: {{"title": "Mom's birthday", "content": "December 15th", "labels": ["home"]}}

Input: "Remember: there are 2 QR codes on Alianz document"
Output: {{"title": "Alianz document", "content": "there are 2 QR codes on Alianz document", "labels": ['administration']}}

Input: "The WiFi password is: Guest1234"
Output: {{"title": "WiFi password", "content": "Guest1234", "labels": ["web"]}}
""".format(current_datetime=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def get_simplenote_client():
    """
    Get Simplenote client with credentials from environment

    Returns:
        simplenote.Simplenote or None
    """
    user = os.environ.get('SIMPLENOTE_LOCAL_USER')
    password = os.environ.get('SIMPLENOTE_LOCAL_PASSWORD')

    if not user or not password:
        print(f"{fg.red}[add2keep] Error: SIMPLENOTE_LOCAL_USER and SIMPLENOTE_LOCAL_PASSWORD not set{fg.default}")
        print(f"{fg.yellow}Run: export SIMPLENOTE_LOCAL_USER=user@example.com{fg.default}")
        print(f"{fg.yellow}      export SIMPLENOTE_LOCAL_PASSWORD=yourpassword{fg.default}")
        return None

    try:
        return simplenote.Simplenote(user, password)
    except Exception as e:
        print(f"{fg.red}[add2keep] Error creating Simplenote client: {e}{fg.default}")
        return None


def add2keep(title, content, labels=None):
    """
    Add a memo to Simplenote

    Args:
        title: Title of the memo
        content: Main content/details to remember
        labels: List of labels/tags (default: empty list)

    Returns:
        dict: Result of the memo add operation
    """
    print(f"[add2keep] Adding memo: {title}")
    if labels:
        print(f"[add2keep] Labels: {labels}")

    note_content = f"{title}\n\n{content}\n\n*{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

    sn = get_simplenote_client()
    if not sn:
        return {
            "success": False,
            "error": "Simplenote credentials not configured",
            "title": title,
            "content": content,
            "labels": labels or []
        }

    try:
        note = {
            'content': note_content
        }

        if labels:
            note['tags'] = labels

        result = sn.add_note(note)

        if isinstance(result, tuple):
            note_data, status = result
        else:
            note_data = result

        print(f"{fg.green}[add2keep] Memo saved successfully!{fg.default}")
        print(f"[add2keep] Note key: {note_data.get('key', 'unknown')}")

        return {
            "success": True,
            "title": title,
            "content": content,
            "labels": labels or [],
            "note_key": note_data.get('key'),
            "note": note_data
        }

    except Exception as e:
        print(f"{fg.red}[add2keep] Error saving to Simplenote: {e}{fg.default}")
        return {
            "success": False,
            "error": str(e),
            "title": title,
            "content": content,
            "labels": labels or []
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


def extract_memo_details(message_text, timeout=10):
    """
    Extract memo details from a message using OpenRouter API

    Args:
        message_text: The memo message to extract details from
        timeout: API request timeout in seconds (default: 10)

    Returns:
        tuple: (success: bool, details: dict or None, raw_response: dict)
    """
    print("i... in extract_memo_details")
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
                "content": MEMO_EXTRACTION_PROMPT
            },
            {
                "role": "user",
                "content": message_text
            }
        ]
    }

    try:
        logger.info(f"Extracting memo details from: {message_text[:100]}...")
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

            logger.info(f"Extracted memo details: {details}")
            return True, details, response_data

        except (KeyError, IndexError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to extract memo details: {e}")
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
