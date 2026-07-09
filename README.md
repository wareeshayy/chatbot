# IJAIKE Journal AI Chatbot

A production-ready RAG-powered AI chatbot application specifically designed for the **International Journal of Artificial Intelligence & Knowledge Engineering (IJAIKE)**. The chatbot answers author inquiries regarding submission guidelines, formatting requirements, peer review policy, and Article Processing Charges (APC).

---

## 🚀 Project Architecture

The application is structured as a monorepo containing both the frontend client and backend services:

* **`/frontend`**: [Next.js](https://nextjs.org/) client application built with TypeScript, ReactMarkdown, and TailwindCSS styles. Features a premium dark-themed full Chat Panel and a lightweight floating Chat Widget.
* **`/backend`**: [FastAPI](https://fastapi.tiangolo.com/) server powered by Python. Connects to MongoDB Atlas using Beanie ODM for chat transcripts, and ChromaDB for vector retrieval (RAG). Supports both Google Gemini and OpenRouter (GPT-4o) LLM providers.
* **`/data`**: PDF and JSON assets representing the official IJAIKE knowledge base.
* **`/docker`**: Container configurations for local MongoDB databases.

---

## 🛠️ Quick Start Guide

### 1. Prerequisite Setup

Before starting, ensure you have the following installed on your system:
* **Node.js** (v18+)
* **Python** (3.11+)

---

### 2. Run the Backend API

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements-core.txt
   ```
4. Set up your `.env` variables (e.g., MongoDB URI, LLM Provider, OpenRouter / Gemini API Keys). See `backend/.env.example`.
5. Seed the database with the journal guidelines and document embeddings:
   ```bash
   python -m scripts.setup_db
   ```
6. Launch the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   * *Swagger Docs are available at:* [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 3. Run the Frontend Client

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Set the API connection URL in `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1
   ```
4. Start the Next.js development server:
   ```bash
   npm run dev
   ```
   * *Open the application at:* [http://localhost:3000](http://localhost:3000)

---

## 🌟 Key Features

* **Dual Interface**: Includes a comprehensive **Chat Panel** workspace for in-depth conversations alongside a floating **ChatWidget** overlay ready to embed on any webpage.
* **Smart RAG Context**: Performs semantic retrieval across official journal policy documents in real-time, referencing chunks with matching percentages and page citation pointers.
* **APC Estimator Tool**: Fully interactive frontend calculator to estimate journal Article Processing Charges based on paper length, category, and discounts.
* **Multiple LLM Engines**: Configurable backend factory supporting Google Gemini and OpenRouter (GPT-4o/Claude) with rate-limiting safety parameters (`max_tokens`).
* **Voice Transcription**: Built-in Web Speech API voice input directly in the chatbot interfaces.
