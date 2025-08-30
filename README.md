# 💸 Budgeting-Assistant
A streamlit application that uses multimodal LLMs to extract structured data from images and PDFs. Furthermore, an assistant powered by an LLM Agent also interfaces with the database to respond to user questions using Retrieval Augmented Generation (RAG).

## 🌟 Features
- Purchase data extraction from images and PDFs
- Local data storage on a SQLite database
- Q&A chat with the LLM powered Budgeting assistant 

## 🛠️ Tech Stack
- **Streamlit** for the UI
- **LangChain** / **LangGraph** for interacting with LLMs
- **SQLite** for local data storage

## 🛠️ Prerequisites
- Git
- Python 3.9+
- Pip


## ⚡ Installation & Usage
```bash
# clone the Github repo
git clone "https://github.com/andrpani/Budgeting-Assistant.git"
cd Budgeting-Assistant

# create the virtual envinronment, activate it and install requirements
python3 -m venv .venv # python -m venv .venv on Windows
source .venv/bin/activate
pip install -r requirements.txt

# start the streamlit app
streamlit run Home.py

```


