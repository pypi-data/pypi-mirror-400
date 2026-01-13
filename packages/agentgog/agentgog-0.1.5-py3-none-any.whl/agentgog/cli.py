#!/usr/bin/env python3
"""
CLI interface for AI message classifier
"""
import sys
import os
import logging
import click
from console import fg, fx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_classifier import classify_message
from calendar_extractor import extract_calendar_details, add2calendar
from task_extractor import extract_task_details, add2task
from memo_extractor import extract_memo_details, add2keep

LOG_FILE = os.path.expanduser('~/agentgog.log')


def setup_logger():
    """Configure file logger for agentgog"""
    logger = logging.getLogger('agentgog')
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(LOG_FILE)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    return logger


logger = setup_logger()


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
@click.option('--interactive', '-i', is_flag=True, help='Enter interactive classification mode')
def main(message, interactive):
    """
    Classify messages into categories: CALENDAR, TASK, MEMO, or OTHER

    For CALENDAR events, recursively extracts details and calls add2calendar() tool

    Examples:
        agentgog "Meeting tomorrow at 10am"
        agentgog "Buy groceries"
        agentgog -i
    """
    logger.info("Agentgog started")
    print("i... in the main()")
    try:
        if interactive:
            interactive_mode()
            return

        if not message:
            click.echo("Error: Please provide a message to classify", err=True)
            click.echo("Use 'agentgog --help' for usage information", err=True)
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


def interactive_mode():
    """Interactive mode for classifying multiple messages"""
    print(format_output(f"{fx.bold}AI Message Classifier - Interactive Mode{fx.default}"))
    print(format_output(f"{fx.dim}Type 'quit' or 'exit' to leave{fx.default}\n"))

    while True:
        try:
            message = input(format_output(f"{fx.bold}Enter message:{fx.default} ")).strip()

            if message.lower() in ('quit', 'exit'):
                print(format_output(f"{fx.dim}Goodbye!{fx.default}"))
                break

            if not message:
                continue

            success, classification, raw_response = classify_message(message)

            if success:
                colors = {
                    'CALENDAR': 'green',
                    'TASK': 'blue',
                    'MEMO': 'yellow',
                    'OTHER': 'red'
                }
                color = colors.get(classification or 'OTHER', 'white')
                output = f"  → {fx.bold}Classification:{fx.default} {colorize(classification, color)}"
                print(format_output(output))
            else:
                error_msg = (raw_response.get('error') if raw_response else 'Unknown error')
                output = f"  → {fx.bold}{fg.red}Error:{fx.default} {error_msg}"
                print(format_output(output))

        except KeyboardInterrupt:
            print(format_output(f"\n{fx.dim}Goodbye!{fx.default}"))
            break


if __name__ == '__main__':
    main()
