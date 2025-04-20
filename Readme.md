
# LLM-based RAG Search

A fully functional Retrieval-Augmented Generation (RAG) system that combines web search, article scraping, and summarization using OpenAI's GPT-4o model. The system is designed with a Flask backend(also used langchain for temporary chat memorization on server) and a Streamlit frontend to provide users with concise, relevant summaries based on real-time web content.


## Project Structure

![Project Structure](https://i.imgur.com/Azca2G2.png)



## Features

- Search articles using the Serper (Google Search) API

- Scrape article content using BeautifulSoup

- Store query-response context using LangChain memory

- Summarize content using OpenAI's GPT-4o

- Intuitive Streamlit frontend for real-time querying

- Modular Flask backend for easy integration and scaling

## Tech Stack

- Python

- Flask — for building the backend API

- Streamlit — for frontend UI

- LangChain — for memory and conversational context

- OpenAI GPT-4o API — for summarization and answer generation

- Serper API — for Google Search queries

- BeautifulSoup — for HTML parsing and article scraping


## UI Overview

- Enter a query in the Streamlit frontend

- Backend searches articles, scrapes content, summarizes and temporary server memorization

- Get a clear, concise answer directly on the frontend
## Installation Setup

### 1. Clone the Repository

```
git clone https://github.com/yourusername/rag-search-system.git
cd rag-search-system
```
### 2. Backend Setup
```
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Run the backend server:

```
python app.py
```

### 3. Frontend Setup (Streamlit)

```
cd ../frontend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```
Run the frontend:

```
streamlit run app.py
```
## Example Use Case

### Query: "What's the latest update on the NVIDIA CUDA?"

- System searches news articles

- Scrapes relevant information

- GPT-4o summarizes insights

- Displays a neat, contextual summary on Streamlit
## Acknowledgements

- [OpenAI](https://www.openai.com)
- [Serper.dev](https://serper.dev)
- [LangChain](https://www.langchain.com)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [Streamlit](https://streamlit.io)

