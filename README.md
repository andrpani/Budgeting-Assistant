# Budgeting-Assistant
A budgenting assistant based on an LLM agent that helps you track your expenses by extracting information from PDF and images of receipts. It also acts as a Q&amp;A chat.

## Features
- Extraction of structured purchase and item data from PDF and Image (PNG and JPG/JPEG) data sources
- Storing of the extracted data in a local database using SQLite

## Tech Stack
- **LangChain** / **LangGraph** as LLM interface and orchestration libraries
- **SQLite** as database

## Prerequisites
- Git
- Python 
- Pip
- SQLite3


## Installation
```bash
# clone the repository
git clone "https://github.com/andrpani/Budgeting-Assistant.git"
# create the virtual envinronment, activate it and install requirements
python3 -m venv .venv 
# python -m venv .venv on Windows
source .venv/bin/activate
pip install -r requirements.txt

# build the database
sqlite3 mydatabase.db < schema.sql

# create a .env file and put there all the API keys

# modify the config.json to reflect the API choices

```

## Usage
```bash
# start the agent
python3 agent.py
```

