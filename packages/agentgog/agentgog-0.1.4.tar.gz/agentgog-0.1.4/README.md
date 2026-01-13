# agentgog

AI message classifier that categorizes messages into CALENDAR, TASK, MEMO, or OTHER using OpenRouter API.

## Features

- Classify messages into categories
- Extract details and integrate with external services:
  - **CALENDAR**: Add events to Google Calendar
  - **TASK**: Add tasks to Google Tasks
  - **MEMO**: Save notes to local storage

## Installation

```bash
uv pip install -e .
```

## Usage

```bash
# Classify a single message
agentgog "Meeting tomorrow at 10am"

# Interactive mode
agentgog -i
```

## Logging

All runs are logged to `~/agentgog.log` with timestamps and classification results.

## Configuration

Set your OpenRouter API key:
```bash
export OPENROUTER_API_KEY="your-key-here"
```
Or save it to `~/.openrouter.key`
