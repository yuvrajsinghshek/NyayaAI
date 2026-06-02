# NyayaAI — Cybercrime Awareness Chatbot

## Overview
RAG based cybercrime awareness chatbot.
Ask anything about cybercrime, digital arrest,
banking fraud, and how to report complaints.

## Tech Stack
- Knowledge Base : ChromaDB (local, free)
- Embeddings     : sentence-transformers (free)
- LLM            : Groq API (free)
- Frontend       : Streamlit (free)

## Setup
1. Clone the repo
2. pip install -r requirements.txt
3. Copy .env.example to .env
4. Add your Groq API key in .env
5. Run: streamlit run frontend/app.py

## How to Add New Data
1. Add new PDF to ai/data/pdfs/
2. Run ingestion pipeline
3. ChromaDB automatically updates
