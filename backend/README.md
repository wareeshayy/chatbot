# IJAIKE Journal AI Chatbot — Backend

FastAPI backend with **MongoDB** (Beanie ODM).

## Quick Start

### 1. Start MongoDB

**Docker (recommended):**
```powershell
cd D:\web-projects\chatbot
docker compose -f docker/docker-compose.yml up -d
```

**MongoDB Atlas:** Set `MONGODB_URL` in `backend\.env`

### 2. Install & setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-core.txt
.\setup-database.ps1
```

Default admin: `admin@ijaike.org` / `Admin@12345`

### 3. Start API

```powershell
uvicorn app.main:app --reload --port 8000
```

Docs: http://localhost:8000/docs

## Database

| Setting | Default |
|---------|---------|
| URL | `mongodb://admin:admin123@localhost:27017/ijaike_chatbot?authSource=admin` |
| DB Name | `ijaike_chatbot` |

Collections: `users`, `conversations`, `messages`, `documents`, `document_chunks`, `apc_pricing_rules`, etc.

## Environment variables

See `.env.example` — key variable is `MONGODB_URL`.
