#!/usr/bin/env python3
"""
AI message classifier using OpenRouter API

Classifies messages into categories: CALENDAR, TASK, MEMO, or OTHER
"""
import requests
import os
import logging
import click
import sys
from console import fg, fx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calendar_extractor import extract_calendar_details, add2calendar
from task_extractor import extract_task_details, add2task
from memo_extractor import extract_memo_details, add2keep

LOG_FILE = os.path.expanduser('~/agentgog.log')


def setup_logger():
    """Configure file logger for agentgog"""
    logger = logging.getLogger('agentgog')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(LOG_FILE)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    return logger


logger = setup_logger()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "x-ai/grok-4.1-fast"

SYSTEM_PROMPT = """You are a very responsible classifier. For every user message, output exactly one uppercase token and nothing else: CALENDAR, TASK, MEMO, or OTHER. Rules:
- CALENDAR: scheduling intent or an event/reminder with a date/time or scheduling words (e.g., "tomorrow", "at 3pm", "on Jan 5", "meeting", "appointment", "schedule", "remind me on"). If both scheduling and other intent appear, choose CALENDAR.
- TASK: actionable instruction or to‑do without specific scheduling (imperative verbs like "buy", "write", "call", "create", "finish", requests to add a task). If both task and memo appear, choose TASK.
- MEMO: factual note or something meant to be remembered (phrases like "remember", "note", "memo", personal info to keep, facts).
- OTHER: none of the above (questions, casual chat, ambiguous content).

Tie-breakers: prefer CALENDAR over TASK over MEMO. Always return only the tag (no punctuation, no explanation).

Examples:
"Meeting with Alice tomorrow at 10am" -> CALENDAR
"Buy groceries" -> TASK
"Remember my passport number: 1234" -> MEMO
"What's the weather like?" -> OTHER
"""


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


def classify_message(message_text, timeout=10):
    """
    Classify a message using OpenRouter API

    Args:
        message_text: The message content to classify
        timeout: API request timeout in seconds (default: 10)

    Returns:
        tuple: (success: bool, classification: str, raw_response: dict)
            - success: True if API call succeeded
            - classification: One of CALENDAR, TASK, MEMO, OTHER, or None on error
            - raw_response: Full API response dict or error dict
    """
    print("i... in classify_message() ")
    api_key = get_api_key()

    if not api_key:
        logger.error("OPENROUTER_API_KEY environment variable not set and ~/.openrouter.key not found")
        return False, None, {"error": "Missing API key"}

    if not message_text or not message_text.strip():
        logger.warning("Empty message text provided for classification")
        return False, "OTHER", {"error": "Empty message"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": message_text
            }
        ]
    }

    try:
        logger.info(f"Classifying message: {message_text[:100]}...")
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()

        response_data = response.json()

        try:
            classification = response_data['choices'][0]['message']['content'].strip()

            valid_classes = ['CALENDAR', 'TASK', 'MEMO', 'OTHER']
            if classification not in valid_classes:
                logger.warning(f"Unexpected classification: {classification}, defaulting to OTHER")
                classification = 'OTHER'

            logger.info(f"Classification result: {classification}")
            return True, classification, response_data

        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract classification from response: {e}")
            return False, None, response_data

    except requests.exceptions.Timeout:
        logger.error(f"OpenRouter API request timed out after {timeout}s")
        return False, None, {"error": "Timeout"}

    except requests.exceptions.RequestException as e:
        logger.error(f"OpenRouter API request failed: {e}")
        return False, None, {"error": str(e)}

    except Exception as e:
        logger.error(f"Unexpected error during classification: {e}", exc_info=True)
        return False, None, {"error": str(e)}


def classify_message_simple(message_text, timeout=10):
    """
    Simplified classification function that returns just the classification

    Args:
        message_text: The message content to classify
        timeout: API request timeout in seconds (default: 10)

    Returns:
        str: Classification (CALENDAR, TASK, MEMO, OTHER) or None on error
    """
    success, classification, _ = classify_message(message_text, timeout)
    return classification if success else None


def colorize(text, color):
    """Add color to text"""
    colors = {
        'green': fg.green,
        'blue': fg.cyan,
        'yellow': fg.yellow,
        'red': fg.red,
        'white': fg.default
    }
    color_func = colors.get(color, fg.default)
    return color_func + text + fg.default


def format_output(text):
    """Format text with basic styling"""
    result = text
    result = result.replace('[bold]', f"{fx.bold}")
    result = result.replace('[/bold]', f"{fx.default}")
    result = result.replace('[dim]', f"{fx.dim}")
    result = result.replace('[/dim]', f"{fx.default}")
    result = result.replace('[bold green]', f"{fx.bold}{fg.green}")
    result = result.replace('[/bold green]', f"{fx.default}{fx.default}")
    result = result.replace('[bold red]', f"{fx.bold}{fg.red}")
    result = result.replace('[/bold red]', f"{fx.default}{fx.default}")
    result = result.replace('[bold cyan]', f"{fx.bold}{fg.cyan}")
    result = result.replace('[/bold cyan]', f"{fx.default}{fx.default}")
    result = result.replace('[bold yellow]', f"{fx.bold}{fg.yellow}")
    result = result.replace('[/bold yellow]', f"{fx.default}{fx.default}")
    result = result.replace('[green]', f"{fg.green}")
    result = result.replace('[/green]', f"{fx.default}")
    result = result.replace('[cyan]', f"{fg.cyan}")
    result = result.replace('[/cyan]', f"{fx.default}")
    result = result.replace('[blue]', f"{fg.cyan}")
    result = result.replace('[/blue]', f"{fx.default}")
    result = result.replace('[yellow]', f"{fg.yellow}")
    result = result.replace('[/yellow]', f"{fx.default}")
    result = result.replace('[red]', f"{fg.red}")
    result = result.replace('[/red]', f"{fx.default}")
    return result


@click.command()
@click.argument('message', nargs=-1, type=click.STRING)
def main(message):
    """
    Classify messages into categories: CALENDAR, TASK, MEMO, or OTHER

    For CALENDAR events, recursively extracts details and calls add2calendar() tool

    Examples:
        p2 "Meeting tomorrow at 10am"
        p2 "Buy groceries"
    """
    logger.info("Agentgog started")
    print("i... in the main()")
    try:
        if not message:
            click.echo("Error: Please provide a message to classify", err=True)
            click.echo("Use 'p2 --help' for usage information", err=True)
            sys.exit(1)

        message_text = ' '.join(message)
        success, classification, raw_response = classify_message(message_text)

        print(f"i... in ai_classification result {success}")

        if success:
            colors = {
                'CALENDAR': 'green',
                'TASK': 'blue',
                'MEMO': 'yellow',
                'OTHER': 'red'
            }
            color = colors.get(classification or 'OTHER', 'white')
            output = f"{fx.bold}Classification:{fx.default} {colorize(classification, color)}"
            print(format_output(output))

            if classification == 'CALENDAR':
                print(format_output(f"{fx.bold}[cyan]Extracting calendar details...[/cyan]{fx.default}"))
                extract_success, calendar_details, extract_response = extract_calendar_details(message_text)

                if extract_success and calendar_details:
                    print(format_output(f"{fx.bold}[cyan]Calling add2calendar() tool...[/cyan]{fx.default}"))
                    result = add2calendar(
                        date=calendar_details.get('date'),
                        time=calendar_details.get('time'),
                        event_name=calendar_details.get('event_name'),
                        details=calendar_details.get('details'),
                        timezone='Europe/Prague'
                    )
                else:
                    error_msg = (extract_response.get('error') if extract_response else 'Failed to extract calendar details')
                    output = f"{fx.bold}{fg.red}Error extracting calendar details:{fx.default} {error_msg}"
                    print(format_output(output))
                    sys.exit(1)

            elif classification == 'TASK':
                print(format_output(f"{fx.bold}[cyan]Extracting task details...[/cyan]{fx.default}"))
                extract_success, task_details, extract_response = extract_task_details(message_text)

                if extract_success and task_details:
                    print(format_output(f"{fx.bold}[cyan]Calling add2task() tool...[/cyan]{fx.default}"))
                    result = add2task(
                        task_name=task_details.get('task_name'),
                        due_date=task_details.get('due_date'),
                        priority=task_details.get('priority'),
                        details=task_details.get('details')
                    )
                else:
                    error_msg = (extract_response.get('error') if extract_response else 'Failed to extract task details')
                    output = f"{fx.bold}{fg.red}Error extracting task details:{fx.default} {error_msg}"
                    print(format_output(output))
                    sys.exit(1)

            elif classification == 'MEMO':
                print(format_output(f"{fx.bold}[cyan]Extracting memo details...[/cyan]{fx.default}"))
                extract_success, memo_details, extract_response = extract_memo_details(message_text)

                if extract_success and memo_details:
                    print(format_output(f"{fx.bold}[cyan]Calling add2keep() tool...[/cyan]{fx.default}"))
                    result = add2keep(
                        title=memo_details.get('title'),
                        content=memo_details.get('content'),
                        labels=memo_details.get('labels')
                    )
                else:
                    error_msg = (extract_response.get('error') if extract_response else 'Failed to extract memo details')
                    output = f"{fx.bold}{fg.red}Error extracting memo details:{fx.default} {error_msg}"
                    print(format_output(output))
                    sys.exit(1)
        else:
            error_msg = (raw_response.get('error') if raw_response else 'Unknown error')
            output = f"{fx.bold}{fg.red}Error:{fx.default} {error_msg}"
            print(format_output(output))
            sys.exit(1)
    finally:
        logger.info("Agentgog ended")


if __name__ == "__main__":
    print("i... MAIN in ai_classifier")
    main()
