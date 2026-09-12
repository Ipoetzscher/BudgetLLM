# BudgetLLM

A local, human-in-the-loop budgeting assistant that categorizes bank transactions and learns from user corrections.

## Motivation

Manually categorizing transactions is tedious. This project combines deterministic merchant normalization, persistent merchant memory, LLM-assisted categorization, and human review to automate the repetitive work while keeping the user in control.

## Features

- Imports credit-card and bank transaction files
- Normalizes merchant descriptions and removes sensitive bank information before API calls
- Reuses previously-confirmed allocations whenever possible
- Sends new or ambiguous transactions to an LLM API followed by a Streamlit review interface for human confirmation and updates memory
- Generates tab-separated output for exporting into Google Sheets
- Includes an isolated pytest suite that does not call the API or modify real memory

## Tech Stack

- Python
- Streamlit
- OpenAI API
- JSON merchant memory
- pytest

## Status

Version 0.1 is under active development. Planned work includes SQLite persistence and a small Django REST API.
