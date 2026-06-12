# ⚖️ NyayaAI — Cybercrime Awareness Chatbot

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue)
![Groq](https://img.shields.io/badge/LLM-Groq-orange)

## 📌 Overview

NyayaAI is an intelligent cybercrime awareness chatbot built for Indian citizens.
It uses Retrieval Augmented Generation (RAG) to answer questions about cybercrime,
digital arrest scams, banking fraud, illegal loan apps, and how to report complaints
— all powered by official I4C government advisories and reports.

---

## 🎯 Problem Statement

India is witnessing a rapid rise in cybercrime cases. Citizens often lack awareness
about common scams, how to protect themselves, and how to report incidents.
NyayaAI bridges this gap by providing instant, accurate, and source-backed answers
using official government cybercrime data.

---

## 🧠 How It Works
User Question

↓

Streamlit Frontend

↓

FastAPI Backend

↓

RAG Pipeline:

Question → Vector Embedding
ChromaDB Search → Top 3 Relevant Chunks
Groq LLM → Generate Answer from Chunks

↓

Answer + Source + Category

↓

PostgreSQL → Save Chat History


---

## ✨ Features

- 🔐 **User Authentication** — Register, Login, Forgot Password with OTP verification
- 💬 **Intelligent Chat** — RAG based answers from official government PDFs
- 🧠 **Context Memory** — Follow-up questions handled with chat history
- 🌐 **Multilingual** — Responds in English, Hindi, or Hinglish based on user input
- 📁 **Source Tracking** — Every answer shows source PDF and page number
- 🏷️ **Category Tagging** — Answers tagged with relevant cybercrime category
- 💾 **Chat Summary** — AI generated 3-4 line summary of each chat session
- 🔄 **Multiple Chats** — Create and switch between multiple chat sessions
- 📊 **PostgreSQL Database** — Persistent storage for users, chats, summaries

---

## 🏗️ Architecture
NyayaAI/

├── ai/

│   ├── config.py              ← Central configuration

│   ├── ingest/

│   │   ├── pdf_extractor.py   ← Extract text from PDFs

│   │   ├── faq_extractor.py   ← Extract text from FAQs

│   │   └── chunker.py         ← Smart text chunking

│   ├── knowledge_base/

│   │   ├── embeddings.py      ← Text to vectors

│   │   └── vector_store.py    ← ChromaDB operations

│   └── rag/

│       ├── retriever.py       ← Semantic search

│       └── generator.py       ← LLM answer generation

│

├── backend/

│   ├── main.py                ← FastAPI application

│   ├── routes/

│   │   ├── auth.py            ← Auth endpoints

│   │   └── chat.py            ← Chat endpoints

│   ├── models/

│   │   ├── user.py            ← User, UserInfo, ChatSummary

│   │   └── chat.py            ← Conversation model

│   ├── schemas/               ← Pydantic models

│   └── utils/

│       ├── auth.py            ← JWT + password hashing

│       ├── otp.py             ← OTP generation

│       └── email.py           ← Email sender

│

└── frontend/

├── app.py                 ← Main Streamlit app

├── pages/

│   ├── login.py           ← Login + forgot password

│   └── register.py        ← 3 step registration

└── components/

├── chat.py            ← Chat display component

└── sidebar.py         ← Sidebar with chats + logout

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI |
| Database | PostgreSQL |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| LLM | Groq (llama-3.3-70b-versatile) |
| Auth | JWT + OTP Email Verification |
| ORM | SQLAlchemy |

---

## 📚 Data Sources

- TAU-397 Monthly Underground Banking Report — May 2026 (I4C, MHA)
- Advisory TAU-ADV-003 — Digital Arrest Scam (I4C, MHA)
- NCRP FAQ — cybercrime.gov.in
- Multiple I4C Cybercrime Advisories (CIS Series)

---

## 🚀 Local Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 15+
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/yuvrajsinghshek/NyayaAI.git
cd NyayaAI

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Setup environment
cp .env.example .env
# Edit .env with your credentials
```

### Environment Variables

```bash
# Required
GROQ_API_KEY=your_groq_api_key
DB_PASSWORD=your_postgres_password
MAIL_USERNAME=your_gmail
MAIL_PASSWORD=your_app_password
SECRET_KEY=your_secret_key
```

### Run Ingestion Pipeline

```bash
# Add PDFs to ai/data/pdfs/
# Add FAQ txt files to ai/data/faqs/

$env:PYTHONPATH = "D:\NyayaAI"  # Windows
python ai/ingest/ingest_pipeline.py
```

### Run Application

```bash
# Terminal 1 — Backend
$env:PYTHONPATH = "D:\NyayaAI"
uvicorn backend.main:app --reload

# Terminal 2 — Frontend
$env:PYTHONPATH = "D:\NyayaAI"
streamlit run frontend/app.py
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Register new user |
| POST | /auth/verify-otp | Verify email OTP |
| POST | /auth/user-info | Save user profile |
| POST | /auth/login | Login user |
| POST | /auth/forgot-password | Send reset OTP |
| POST | /auth/reset-password | Reset password |
| POST | /chat/ | Send message get answer |
| GET | /chat/history/{id} | Get chat history |
| POST | /chat/summary/{id} | Save chat summary |
| GET | /chat/summaries/{id} | Get all summaries |

---

## 👨💻 Developer

**Yuvraj Singh Shekhawat**
AI/ML Engineer
GitHub: [@yuvrajsinghshek](https://github.com/yuvrajsinghshek)

---

## 📄 License

This project is for educational and awareness purposes only.
Data sourced from official I4C, MHA Government of India publications.
