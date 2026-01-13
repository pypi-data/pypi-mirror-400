#!/usr/bin/env python3
"""
CLI interface for AI message classifier
"""
import sys
import os
import logging
import click
from console import fg, fx
from .ai_classifier import classify_message
from calendar_extractor import extract_calendar_details, add2calendar

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

    Examples:
        classify "Meeting tomorrow at 10am"
        classify -i
    """
    logger.info("Agentgog started")
    print("i... in cli main")
    try:
        if interactive:
            interactive_mode()
            return

        if not message:
            click.echo("Error: Please provide a message to classify", err=True)
            click.echo("Use 'classify --help' for usage information", err=True)
            sys.exit(1)

        message_text = ' '.join(message)
        logger.info(f"Running classification for: {message_text[:100]}...")
        success, classification, raw_response = classify_message(message_text)
        logger.info(f"Classification result: {classification}")
        print(f"i... in cli main, result = {success}")

        if success:
            colors = {
                'CALENDAR': 'green',
                'TASK': 'blue',
                'MEMO': 'yellow',
                'OTHER': 'red'
            }
            color = colors.get(classification, 'white')
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
                        details=calendar_details.get('details')
                    )
                else:
                    error_msg = (extract_response.get('error') if extract_response else 'Failed to extract calendar details')
                    output = f"{fx.bold}{fg.red}Error extracting calendar details:{fx.default} {error_msg}"
                    print(format_output(output))
                    sys.exit(1)
        else:
            error_msg = raw_response.get('error', 'Unknown error')
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
                color = colors.get(classification, 'white')
                output = f"  → {fx.bold}Classification:{fx.default} {colorize(classification, color)}"
                print(format_output(output))
            else:
                error_msg = raw_response.get('error', 'Unknown error')
                output = f"  → {fx.bold}{fg.red}Error:{fx.default} {error_msg}"
                print(format_output(output))

        except KeyboardInterrupt:
            print(format_output(f"\n{fx.dim}Goodbye!{fx.default}"))
            break


if __name__ == '__main__':
    main()
