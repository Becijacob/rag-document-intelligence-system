
📌 Title
AI Multi-Document Assistant (RAG System)
📌 Overview
This project is a Generative AI-powered multi-document assistant that allows users to upload multiple PDFs and ask questions using Retrieval-Augmented Generation (RAG).

The system retrieves relevant content from documents and generates accurate, context-based answers using OpenAI.
📌 Features
- Upload multiple PDFs
- Ask questions across documents
- Chat-based UI
- Source and page tracking
- Avoids hallucination (grounded responses)
📌 Architecture

                ┌──────────────────────┐
                │      User (Browser)  │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   Streamlit Frontend │
                │  - Upload PDFs       │
                │  - Ask Questions     │
                └──────────┬───────────┘
                           │ HTTP API
                           ▼
                ┌──────────────────────┐
                │   FastAPI Backend    │
                │  /upload   /ask      │
                └──────────┬───────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ PDF Loader   │   │ Text Splitter│   │ Embeddings   │
│ (PyPDF)      │   │ (Chunking)   │   │ (OpenAI)     │
└──────────────┘   └──────────────┘   └──────┬───────┘
                                             │
                                             ▼
                                   ┌─────────────────┐
                                   │  Vector DB      │
                                   │  (Chroma)       │
                                   └──────┬──────────┘
                                          │
                                          ▼
                                   ┌─────────────────┐
                                   │ Retriever       │
                                   │ (Top-K search)  │
                                   └──────┬──────────┘
                                          │
                                          ▼
                                   ┌─────────────────┐
                                   │ OpenAI LLM      │
                                   │ (gpt-4o-mini)   │
                                   └──────┬──────────┘
                                          │
                                          ▼
                               ┌──────────────────────┐
                               │ Generated Answer     │
                               │ + Sources            │
                               └──────────────────────┘

📌 Tech Stack
FastAPI (Backend)
Streamlit (Frontend)
OpenAI (LLM)
ChromaDB (Vector Database)
LangChain (RAG pipeline)
Render (Deployment)

📌 How to Run
uvicorn main:app --reload
streamlit run app.py

📌 Example Questions
- Explain system architecture
- What happened in Q2?
- Compare performance across documents

📌 Screenshots

(Add images here)