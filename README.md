# 📚 Manus Clone – Custom RAG Chatbot

A production-ready, Manus-style Retrieval-Augmented Generation (RAG) system that enables seamless Q&A over your own documents. Designed for reliability, cost-efficiency, and extensibility.

![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?style=flat-square)
![Supabase](https://img.shields.io/badge/Supabase-DB-blue?style=flat-square)
![Pinecone](https://img.shields.io/badge/Pinecone-Vector%20DB-purple?style=flat-square)
![Next.js](https://img.shields.io/badge/Next.js-Frontend-black?style=flat-square)
![OpenAI](https://img.shields.io/badge/OpenAI-gpt--3.5--turbo-orange?style=flat-square)

---

## ✨ Features

- 🔗 End-to-End RAG pipeline with auto chunking, embedding, and storage
- 🗂️ Data Room auto-sync (add, update, delete)
- 💬 Persistent chat with history & infinite scroll
- 📝 Auto-title chats using first message
- 📄 Document + chunk traceability for each answer
- 🧠 Final AI-generated summary response
- ⚙️ Customizable RAG parameters
- 💰 Cost-effective: `text-embedding-3-small` + `gpt-3.5-turbo`

---

## 🛠️ Stack Overview

| Layer            | Tech                             |
|------------------|----------------------------------|
| Backend API      | FastAPI                          |
| Vector DB        | Pinecone                         |
| Database         | Supabase                         |
| Frontend         | Next.js 15, React 19, TailwindCSS |
| Embeddings       | OpenAI `text-embedding-3-small`  |
| Chat Completion  | OpenAI `gpt-3.5-turbo`            |
| Document Support | PDF, DOCX                         |
| Containerization | Docker (⚠️ macOS issues)         |

---

## 📁 Data Room Behavior

- Place your files inside a folder named `Data Room` at the project root.
- Run:

```bash
# NPM Copy Data Room Guide

## Running the Command

```bash
npm run copy-data-room
```

# NPM Copy Data Room Guide

## Running the Command

```bash
npm run copy-data-room
```

## What the App Does

The application performs the following operations:

- **Parse and chunk documents** - Processes documents by breaking them into manageable chunks
- **Embed and store them in the vector DB** - Creates vector embeddings and stores them in the database
- **Sync deletions and updates as well** - Maintains synchronization by handling document deletions and updates

## Environment Configuration

Create a `.env` file and fill in:

```env
# Supabase
SUPABASE_URL=
SUPABASE_KEY=

# OpenAI
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536

# Pinecone
PINECONE_API_KEY=
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
PINECONE_INDEX_NAME=manus-clone

# Chunking
MAX_TOKENS_PER_CHUNK=512
OVERLAPPING_TOKEN=50

# Data for RAG
DATA_ROOM_PATH='../Data Room'
```

🛠️ Almost all RAG parameters are customizable!

## Getting Started

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

## Docker (Experimental)

Docker is initialized but **not currently working on macOS** due to a known issue with Next.js container builds.

## Scripts

```bash
npm run dev                # Start Next.js dev server
npm run build              # Build for production
npm run start              # Start production server
npm run copy-data-room     # Sync Data Room files
npm run generate-types     # Generate OpenAPI TS types
```

## Authentication

Not implemented yet. Supabase Auth integration is planned.

## API Notes

* Uses `openapi-typescript` to generate frontend API types
* Chat message history supports pagination for infinite scrolling
* Analyzer tracks which documents/chunks were used per query

## Roadmap

* ✅ Supabase Auth
* 🧪 Docker fix for macOS (Next.js)
* 🔍 Enhance analyzer UI
* 🧩 Role-based chat access

## Acknowledgments

Inspired by manus.ai, rebuilt with flexibility, transparency, and developer-first architecture in mind.
