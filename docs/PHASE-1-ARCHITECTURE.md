# IJAIKE Journal AI Chatbot — Phase 1 Architecture Design

> **Status:** Phase 2 complete — Backend foundation implemented  
> **Version:** 1.1  
> **Date:** 2026-06-26

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Why This Architecture](#3-why-this-architecture)
4. [Folder Structure](#4-folder-structure)
5. [Database Schema](#5-database-schema)
6. [ER Diagram](#6-er-diagram)
7. [API Endpoints](#7-api-endpoints)
8. [User Flows](#8-user-flows)
9. [RAG Pipeline Design](#9-rag-pipeline-design)
10. [Authentication & Authorization](#10-authentication--authorization)
11. [APC Estimator Design](#11-apc-estimator-design)
12. [Storage Strategy](#12-storage-strategy)
13. [Configuration & Environment](#13-configuration--environment)
14. [Logging, Monitoring & Error Handling](#14-logging-monitoring--error-handling)
15. [Security Considerations](#15-security-considerations)
16. [Scalability & Deployment](#16-scalability--deployment)
17. [Phase Roadmap](#17-phase-roadmap)

---

## 1. Executive Summary

The IJAIKE Journal AI Chatbot is a **Retrieval-Augmented Generation (RAG)** system that answers questions about journal policies, submission workflows, APC pricing, published papers, and announcements using authoritative documents stored in a managed knowledge base.

**Core principles:**
- **Clean Architecture** — domain logic isolated from frameworks (FastAPI, SQLAlchemy, LangChain)
- **SOLID** — single-responsibility services, interface-based abstractions for storage, embeddings, and LLM
- **Production-ready** — JWT auth, role-based access, audit logs, configurable APC rules, citation-backed answers
- **Extensible** — local file storage abstracted behind an interface for future Azure Blob / S3 migration

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER (React + Vite)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │   Chat   │ │   APC    │ │  Admin   │ │  Auth    │ │  Notifications   │ │
│  │   UI     │ │Estimator │ │Dashboard │ │  Pages   │ │      Feed        │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘ │
│       └────────────┴────────────┴────────────┴──────────────────┘           │
│                                    │ Axios / REST                            │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │ HTTPS
┌────────────────────────────────────┼────────────────────────────────────────┐
│                         API GATEWAY LAYER (FastAPI)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │   Auth   │ │   Chat   │ │Knowledge │ │   APC    │ │  Notifications   │  │
│  │  Router  │ │  Router  │ │  Router  │ │  Router  │ │     Router       │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘  │
│       │            │            │            │                 │             │
│  ┌────┴────────────┴────────────┴────────────┴─────────────────┴─────────┐  │
│  │                    Middleware: JWT, CORS, Rate Limit, Logging          │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼────────────────────────────────────────┐
│                          SERVICE LAYER (Business Logic)                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │
│  │ AuthService │ │ ChatService │ │  RAGService │ │ DocumentIngestService│  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────┘  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │
│  │ APCService  │ │ UserService │ │Notification │ │   CitationService   │  │
│  │             │ │             │ │   Service   │ │                     │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────┘  │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
┌───────▼───────┐          ┌─────────▼─────────┐        ┌────────▼────────┐
│  PostgreSQL   │          │     ChromaDB        │        │  File Storage   │
│  (Metadata,   │          │  (Vector Embeddings │        │  (Local → Blob) │
│   Users,      │          │   + Chunk Metadata) │        │                 │
│   Chats, APC) │          │                     │        │                 │
└───────────────┘          └─────────┬───────────┘        └─────────────────┘
                                     │
                           ┌─────────▼─────────┐
                           │   OpenAI / Azure  │
                           │   OpenAI (LLM +   │
                           │   Embeddings)     │
                           └───────────────────┘
```

### Layer Responsibilities

| Layer | Responsibility |
|-------|----------------|
| **Client** | UI, state management, routing, API calls |
| **API** | HTTP routing, request validation (Pydantic), auth enforcement, response serialization |
| **Service** | Business rules, orchestration, transaction boundaries |
| **Domain** | Core entities, enums, interfaces (ports) |
| **Infrastructure** | DB repos, ChromaDB adapter, file storage, LangChain chains |

---

## 3. Why This Architecture

| Decision | Rationale |
|----------|-----------|
| **FastAPI + SQLAlchemy** | Async-capable, auto OpenAPI docs, mature ORM, type-safe with Pydantic v2 |
| **PostgreSQL** | ACID for users, chats, APC config, audit logs; JSONB for flexible metadata |
| **ChromaDB** | Lightweight, embeddable, good for single-tenant journal KB; easy local dev; can migrate to Pinecone/Qdrant later |
| **LangChain** | Standardized RAG chains, retrievers, document loaders; swappable components |
| **Sentence Transformers (fallback)** | Local embedding option when API keys unavailable or for cost control |
| **Clean folder split** | `api/` = thin controllers; `services/` = business logic; `chatbot/` = AI orchestration |
| **Storage abstraction** | `StorageBackend` interface — start with `LocalStorageBackend`, swap to `AzureBlobStorageBackend` |
| **JWT stateless auth** | Scales horizontally; refresh token rotation for security |
| **Separate ingest pipeline** | Document processing is CPU/IO heavy — can be async background task (Celery-ready design) |

---

## 4. Folder Structure

```
chatbot/
├── docs/
│   ├── PHASE-1-ARCHITECTURE.md          # This document
│   ├── API.md                           # API reference (Phase 2)
│   └── DEPLOYMENT.md                    # Deployment guide (Phase 9)
│
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── unit/
│   │   └── integration/
│   └── app/
│       ├── main.py                      # FastAPI app factory
│       ├── dependencies.py              # DI: get_db, get_current_user
│       │
│       ├── config/
│       │   ├── settings.py              # Pydantic Settings (env vars)
│       │   └── logging_config.py
│       │
│       ├── api/
│       │   ├── router.py                # Aggregates all routers
│       │   └── v1/
│       │       ├── auth.py
│       │       ├── chat.py
│       │       ├── documents.py
│       │       ├── knowledge_base.py
│       │       ├── apc.py
│       │       ├── users.py
│       │       ├── notifications.py
│       │       ├── faqs.py
│       │       └── admin.py
│       │
│       ├── auth/
│       │   ├── jwt.py                   # Token create/verify
│       │   ├── password.py              # bcrypt hashing
│       │   └── permissions.py           # Role-based decorators
│       │
│       ├── models/                      # SQLAlchemy ORM models
│       │   ├── base.py
│       │   ├── user.py
│       │   ├── conversation.py
│       │   ├── message.py
│       │   ├── document.py
│       │   ├── document_chunk.py
│       │   ├── apc_config.py
│       │   ├── faq.py
│       │   ├── notification.py
│       │   └── chat_log.py
│       │
│       ├── schemas/                     # Pydantic request/response DTOs
│       │   ├── auth.py
│       │   ├── user.py
│       │   ├── chat.py
│       │   ├── document.py
│       │   ├── apc.py
│       │   ├── faq.py
│       │   ├── notification.py
│       │   └── common.py
│       │
│       ├── database/
│       │   ├── session.py               # Engine, SessionLocal
│       │   └── repositories/            # Data access layer
│       │       ├── base.py
│       │       ├── user_repo.py
│       │       ├── conversation_repo.py
│       │       ├── document_repo.py
│       │       └── ...
│       │
│       ├── services/                    # Business logic
│       │   ├── auth_service.py
│       │   ├── user_service.py
│       │   ├── chat_service.py
│       │   ├── document_service.py
│       │   ├── ingest_service.py
│       │   ├── apc_service.py
│       │   ├── faq_service.py
│       │   ├── notification_service.py
│       │   └── citation_service.py
│       │
│       ├── chatbot/                     # AI orchestration
│       │   ├── chains/
│       │   │   ├── rag_chain.py
│       │   │   └── conversation_chain.py
│       │   ├── retrievers/
│       │   │   └── chroma_retriever.py
│       │   ├── memory/
│       │   │   └── conversation_memory.py
│       │   └── llm/
│       │       ├── factory.py           # OpenAI / Azure OpenAI factory
│       │       └── prompts.py           # Re-exports from prompts/
│       │
│       ├── embeddings/
│       │   ├── base.py                  # EmbeddingProvider interface
│       │   ├── openai_embeddings.py
│       │   └── sentence_transformer.py
│       │
│       ├── vectorstore/
│       │   ├── base.py                  # VectorStore interface
│       │   └── chroma_store.py
│       │
│       ├── parsers/                     # Document parsing
│       │   ├── base.py
│       │   ├── pdf_parser.py
│       │   ├── docx_parser.py
│       │   └── txt_parser.py
│       │
│       ├── chunking/
│       │   ├── base.py
│       │   └── semantic_chunker.py
│       │
│       ├── storage/                     # File storage abstraction
│       │   ├── base.py
│       │   └── local_storage.py
│       │
│       ├── prompts/
│       │   ├── system_prompts.py
│       │   ├── rag_prompt.py
│       │   └── suggested_questions.py
│       │
│       └── utils/
│           ├── exceptions.py
│           ├── pagination.py
│           └── file_validation.py
│
├── frontend/
│   ├── .env.example
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css
│       │
│       ├── assets/
│       │   └── images/
│       │
│       ├── components/
│       │   ├── common/
│       │   │   ├── Button.tsx
│       │   │   ├── Input.tsx
│       │   │   ├── Modal.tsx
│       │   │   ├── Spinner.tsx
│       │   │   └── ProtectedRoute.tsx
│       │   ├── chat/
│       │   │   ├── ChatWindow.tsx
│       │   │   ├── MessageBubble.tsx
│       │   │   ├── CitationCard.tsx
│       │   │   ├── SuggestedQuestions.tsx
│       │   │   └── ChatSidebar.tsx
│       │   ├── apc/
│       │   │   └── APCEstimator.tsx
│       │   ├── admin/
│       │   │   ├── DocumentUpload.tsx
│       │   │   ├── DocumentList.tsx
│       │   │   ├── UserManagement.tsx
│       │   │   ├── FAQEditor.tsx
│       │   │   ├── PolicyEditor.tsx
│       │   │   ├── ChatLogViewer.tsx
│       │   │   └── APCConfigEditor.tsx
│       │   └── layout/
│       │       ├── Navbar.tsx
│       │       ├── Sidebar.tsx
│       │       └── Footer.tsx
│       │
│       ├── pages/
│       │   ├── Home.tsx
│       │   ├── Login.tsx
│       │   ├── Register.tsx
│       │   ├── Chat.tsx
│       │   ├── APCEstimator.tsx
│       │   ├── Notifications.tsx
│       │   └── admin/
│       │       ├── Dashboard.tsx
│       │       ├── Documents.tsx
│       │       ├── Users.tsx
│       │       ├── FAQs.tsx
│       │       ├── Policies.tsx
│       │       ├── ChatLogs.tsx
│       │       └── APCConfig.tsx
│       │
│       ├── hooks/
│       │   ├── useAuth.ts
│       │   ├── useChat.ts
│       │   └── useNotifications.ts
│       │
│       ├── context/
│       │   ├── AuthContext.tsx
│       │   └── ChatContext.tsx
│       │
│       ├── services/
│       │   ├── api.ts                   # Axios instance + interceptors
│       │   ├── authService.ts
│       │   ├── chatService.ts
│       │   ├── documentService.ts
│       │   ├── apcService.ts
│       │   └── notificationService.ts
│       │
│       ├── layouts/
│       │   ├── MainLayout.tsx
│       │   └── AdminLayout.tsx
│       │
│       └── types/
│           ├── auth.ts
│           ├── chat.ts
│           ├── document.ts
│           └── apc.ts
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── .gitignore
└── README.md
```

---

## 5. Database Schema

### 5.1 Enums

```sql
-- User roles
CREATE TYPE user_role AS ENUM ('admin', 'author', 'reviewer', 'reader');

-- Document categories (knowledge base taxonomy)
CREATE TYPE document_category AS ENUM (
    'author_guidelines',
    'apc_policy',
    'editorial_policies',
    'faq',
    'published_paper',
    'special_issue',
    'journal_announcement',
    'call_for_papers',
    'other'
);

-- Document processing status
CREATE TYPE document_status AS ENUM ('pending', 'processing', 'indexed', 'failed');

-- Message roles in chat
CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');

-- Notification types
CREATE TYPE notification_type AS ENUM (
    'call_for_papers',
    'special_issue',
    'journal_announcement',
    'general'
);

-- Paper types for APC
CREATE TYPE paper_type AS ENUM ('research_article', 'review_article', 'short_communication', 'case_study');

-- Author categories for APC discounts
CREATE TYPE author_category AS ENUM (
    'regular',
    'developing_country',
    'student',
    'ijaike_member',
    'institutional_partner'
);
```

### 5.2 Tables

#### `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Login email |
| hashed_password | VARCHAR(255) | NOT NULL | bcrypt hash |
| full_name | VARCHAR(255) | NOT NULL | |
| role | user_role | NOT NULL, DEFAULT 'reader' | RBAC role |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | Soft disable |
| is_verified | BOOLEAN | NOT NULL, DEFAULT false | Email verification |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| last_login_at | TIMESTAMPTZ | NULL | |

**Indexes:** `idx_users_email`, `idx_users_role`

---

#### `refresh_tokens`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK → users.id ON DELETE CASCADE | |
| token_hash | VARCHAR(255) | UNIQUE, NOT NULL | Hashed refresh token |
| expires_at | TIMESTAMPTZ | NOT NULL | |
| revoked_at | TIMESTAMPTZ | NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

---

#### `conversations`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK → users.id ON DELETE CASCADE, NULL | NULL = anonymous/guest |
| title | VARCHAR(500) | NULL | Auto-generated from first message |
| is_archived | BOOLEAN | DEFAULT false | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

**Indexes:** `idx_conversations_user_id`, `idx_conversations_updated_at`

---

#### `messages`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| conversation_id | UUID | FK → conversations.id ON DELETE CASCADE | |
| role | message_role | NOT NULL | user / assistant / system |
| content | TEXT | NOT NULL | Message body |
| citations | JSONB | NULL | Array of citation objects |
| token_count | INTEGER | NULL | For usage tracking |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

**Citation JSONB structure:**
```json
[
  {
    "document_id": "uuid",
    "document_title": "Author Guidelines 2025",
    "page_number": 12,
    "section": "3.2 Manuscript Formatting",
    "chunk_id": "chroma-id",
    "relevance_score": 0.87,
    "excerpt": "Manuscripts must be submitted in..."
  }
]
```

**Indexes:** `idx_messages_conversation_id`, `idx_messages_created_at`

---

#### `documents`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| title | VARCHAR(500) | NOT NULL | Display title |
| filename | VARCHAR(500) | NOT NULL | Original filename |
| file_path | VARCHAR(1000) | NOT NULL | Storage path/key |
| file_type | VARCHAR(20) | NOT NULL | pdf, docx, txt |
| file_size_bytes | BIGINT | NOT NULL | |
| category | document_category | NOT NULL | KB taxonomy |
| status | document_status | NOT NULL, DEFAULT 'pending' | Ingest status |
| version | INTEGER | NOT NULL, DEFAULT 1 | Re-upload increments |
| metadata | JSONB | NULL | Author, DOI, issue, etc. |
| uploaded_by | UUID | FK → users.id | Admin who uploaded |
| chunk_count | INTEGER | DEFAULT 0 | |
| error_message | TEXT | NULL | If status = failed |
| indexed_at | TIMESTAMPTZ | NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| is_active | BOOLEAN | DEFAULT true | Soft delete |

**Indexes:** `idx_documents_category`, `idx_documents_status`, `idx_documents_is_active`

---

#### `document_chunks`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| document_id | UUID | FK → documents.id ON DELETE CASCADE | |
| chroma_id | VARCHAR(255) | UNIQUE, NOT NULL | Vector DB reference |
| chunk_index | INTEGER | NOT NULL | Order in document |
| content | TEXT | NOT NULL | Chunk text (for admin preview) |
| page_number | INTEGER | NULL | Source page |
| section_title | VARCHAR(500) | NULL | Detected heading |
| token_count | INTEGER | NULL | |
| metadata | JSONB | NULL | Extra chunk metadata |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

**Indexes:** `idx_document_chunks_document_id`, `idx_document_chunks_chroma_id`

---

#### `apc_pricing_rules`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| paper_type | paper_type | NOT NULL | |
| base_rate_per_page | DECIMAL(10,2) | NOT NULL | USD per page |
| minimum_pages | INTEGER | DEFAULT 1 | |
| maximum_pages | INTEGER | NULL | |
| flat_fee | DECIMAL(10,2) | NULL | Optional flat fee override |
| currency | VARCHAR(3) | DEFAULT 'USD' | |
| effective_from | DATE | NOT NULL | |
| effective_to | DATE | NULL | NULL = current |
| is_active | BOOLEAN | DEFAULT true | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

**Unique:** `(paper_type, effective_from)` where `is_active = true`

---

#### `apc_discount_rules`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| author_category | author_category | NOT NULL | |
| discount_type | VARCHAR(20) | NOT NULL | 'percentage' or 'fixed' |
| discount_value | DECIMAL(10,2) | NOT NULL | % or fixed amount |
| description | TEXT | NULL | |
| requires_approval | BOOLEAN | DEFAULT false | Waiver flag |
| is_active | BOOLEAN | DEFAULT true | |
| effective_from | DATE | NOT NULL | |
| effective_to | DATE | NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

---

#### `apc_waiver_requests` (optional tracking)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK → users.id | |
| author_category | author_category | NOT NULL | |
| justification | TEXT | NOT NULL | |
| status | VARCHAR(20) | DEFAULT 'pending' | pending/approved/rejected |
| reviewed_by | UUID | FK → users.id, NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

---

#### `faqs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| question | TEXT | NOT NULL | |
| answer | TEXT | NOT NULL | |
| category | VARCHAR(100) | NULL | submission, apc, formatting, etc. |
| display_order | INTEGER | DEFAULT 0 | |
| is_published | BOOLEAN | DEFAULT true | |
| created_by | UUID | FK → users.id | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

---

#### `notifications`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| title | VARCHAR(500) | NOT NULL | |
| content | TEXT | NOT NULL | |
| type | notification_type | NOT NULL | |
| link_url | VARCHAR(1000) | NULL | External link |
| document_id | UUID | FK → documents.id, NULL | Linked KB doc |
| is_published | BOOLEAN | DEFAULT false | |
| published_at | TIMESTAMPTZ | NULL | |
| expires_at | TIMESTAMPTZ | NULL | |
| created_by | UUID | FK → users.id | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

---

#### `chat_logs` (audit / admin analytics)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| conversation_id | UUID | FK → conversations.id | |
| user_id | UUID | FK → users.id, NULL | |
| query | TEXT | NOT NULL | User question |
| response | TEXT | NOT NULL | AI answer |
| citations | JSONB | NULL | |
| retrieved_chunk_ids | JSONB | NULL | Debug/audit |
| latency_ms | INTEGER | NULL | |
| model_used | VARCHAR(100) | NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

**Indexes:** `idx_chat_logs_created_at`, `idx_chat_logs_user_id`

---

#### `suggested_questions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| question | VARCHAR(500) | NOT NULL | |
| category | VARCHAR(100) | NULL | |
| target_role | user_role | NULL | Role-specific suggestions |
| display_order | INTEGER | DEFAULT 0 | |
| is_active | BOOLEAN | DEFAULT true | |

---

#### `policy_settings` (key-value config)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| key | VARCHAR(100) | UNIQUE, NOT NULL | e.g. `submission_deadline` |
| value | JSONB | NOT NULL | Flexible value |
| description | TEXT | NULL | |
| updated_by | UUID | FK → users.id | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

---

## 6. ER Diagram

```mermaid
erDiagram
    USERS ||--o{ CONVERSATIONS : "owns"
    USERS ||--o{ DOCUMENTS : "uploads"
    USERS ||--o{ REFRESH_TOKENS : "has"
    USERS ||--o{ CHAT_LOGS : "generates"
    USERS ||--o{ FAQS : "creates"
    USERS ||--o{ NOTIFICATIONS : "creates"
    USERS ||--o{ APC_WAIVER_REQUESTS : "submits"

    CONVERSATIONS ||--o{ MESSAGES : "contains"
    CONVERSATIONS ||--o{ CHAT_LOGS : "logged_in"

    DOCUMENTS ||--o{ DOCUMENT_CHUNKS : "split_into"
    DOCUMENTS ||--o{ NOTIFICATIONS : "linked_to"

    USERS {
        uuid id PK
        string email UK
        string hashed_password
        string full_name
        enum role
        boolean is_active
        timestamptz created_at
    }

    CONVERSATIONS {
        uuid id PK
        uuid user_id FK
        string title
        boolean is_archived
        timestamptz updated_at
    }

    MESSAGES {
        uuid id PK
        uuid conversation_id FK
        enum role
        text content
        jsonb citations
        timestamptz created_at
    }

    DOCUMENTS {
        uuid id PK
        string title
        string filename
        string file_path
        enum category
        enum status
        uuid uploaded_by FK
        integer chunk_count
        boolean is_active
    }

    DOCUMENT_CHUNKS {
        uuid id PK
        uuid document_id FK
        string chroma_id UK
        integer chunk_index
        text content
        integer page_number
        string section_title
    }

    APC_PRICING_RULES {
        uuid id PK
        enum paper_type
        decimal base_rate_per_page
        decimal flat_fee
        date effective_from
        boolean is_active
    }

    APC_DISCOUNT_RULES {
        uuid id PK
        enum author_category
        string discount_type
        decimal discount_value
        boolean requires_approval
    }

    FAQS {
        uuid id PK
        text question
        text answer
        string category
        boolean is_published
    }

    NOTIFICATIONS {
        uuid id PK
        string title
        text content
        enum type
        boolean is_published
        timestamptz published_at
    }

    CHAT_LOGS {
        uuid id PK
        uuid conversation_id FK
        uuid user_id FK
        text query
        text response
        jsonb citations
        integer latency_ms
    }
```

---

## 7. API Endpoints

**Base URL:** `/api/v1`  
**Auth:** `Authorization: Bearer <access_token>` unless marked `[Public]`

### 7.1 Authentication

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/auth/register` | [Public] | Register new user (default role: reader) |
| POST | `/auth/login` | [Public] | Login → access + refresh tokens |
| POST | `/auth/refresh` | [Public] | Refresh access token |
| POST | `/auth/logout` | Authenticated | Revoke refresh token |
| GET | `/auth/me` | Authenticated | Current user profile |
| POST | `/auth/change-password` | Authenticated | Change password |

### 7.2 Chat

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/chat/conversations` | Authenticated | Create new conversation |
| GET | `/chat/conversations` | Authenticated | List user's conversations (paginated) |
| GET | `/chat/conversations/{id}` | Authenticated | Get conversation with messages |
| PATCH | `/chat/conversations/{id}` | Authenticated | Update title / archive |
| DELETE | `/chat/conversations/{id}` | Authenticated | Delete conversation |
| POST | `/chat/conversations/{id}/messages` | Authenticated | Send message → RAG response |
| GET | `/chat/suggested-questions` | [Public] | Get suggested starter questions |

### 7.3 Knowledge Base / Documents

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/documents/upload` | Admin | Upload PDF/DOCX/TXT |
| GET | `/documents` | Admin | List all documents (filter by category, status) |
| GET | `/documents/{id}` | Admin | Document detail + chunks preview |
| PATCH | `/documents/{id}` | Admin | Update metadata / category |
| DELETE | `/documents/{id}` | Admin | Soft delete + remove from vector store |
| POST | `/documents/{id}/reindex` | Admin | Re-process and re-embed document |
| GET | `/documents/categories` | [Public] | List document categories |

### 7.4 APC Estimator

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/apc/estimate` | [Public] | Calculate APC estimate |
| GET | `/apc/paper-types` | [Public] | List paper types |
| GET | `/apc/author-categories` | [Public] | List author categories with discount info |
| GET | `/apc/pricing-rules` | Admin | List pricing rules |
| POST | `/apc/pricing-rules` | Admin | Create pricing rule |
| PUT | `/apc/pricing-rules/{id}` | Admin | Update pricing rule |
| GET | `/apc/discount-rules` | Admin | List discount rules |
| POST | `/apc/discount-rules` | Admin | Create discount rule |
| PUT | `/apc/discount-rules/{id}` | Admin | Update discount rule |

**APC Estimate Request:**
```json
{
  "paper_type": "research_article",
  "num_pages": 12,
  "author_category": "developing_country"
}
```

**APC Estimate Response:**
```json
{
  "paper_type": "research_article",
  "num_pages": 12,
  "author_category": "developing_country",
  "base_rate_per_page": 50.00,
  "subtotal": 600.00,
  "discount_type": "percentage",
  "discount_value": 25.00,
  "discount_amount": 150.00,
  "total": 450.00,
  "currency": "USD",
  "requires_waiver_approval": false,
  "breakdown": "12 pages × $50/page = $600. 25% developing country discount = -$150."
}
```

### 7.5 FAQs

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/faqs` | [Public] | Published FAQs (filter by category) |
| GET | `/faqs/{id}` | [Public] | Single FAQ |
| POST | `/faqs` | Admin | Create FAQ |
| PUT | `/faqs/{id}` | Admin | Update FAQ |
| DELETE | `/faqs/{id}` | Admin | Delete FAQ |

### 7.6 Notifications

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/notifications` | [Public] | Published notifications (paginated) |
| GET | `/notifications/{id}` | [Public] | Single notification |
| POST | `/notifications` | Admin | Create notification |
| PUT | `/notifications/{id}` | Admin | Update notification |
| DELETE | `/notifications/{id}` | Admin | Delete notification |
| POST | `/notifications/{id}/publish` | Admin | Publish notification |

### 7.7 Users (Admin)

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/users` | Admin | List users (paginated, filter by role) |
| GET | `/users/{id}` | Admin | User detail |
| PATCH | `/users/{id}` | Admin | Update role, active status |
| DELETE | `/users/{id}` | Admin | Deactivate user |

### 7.8 Admin

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/admin/dashboard` | Admin | Stats: docs, chats, users |
| GET | `/admin/chat-logs` | Admin | Paginated chat audit logs |
| GET | `/admin/chat-logs/{id}` | Admin | Single log with retrieved chunks |
| GET | `/admin/policies` | Admin | List policy settings |
| PUT | `/admin/policies/{key}` | Admin | Update policy setting |
| GET | `/admin/suggested-questions` | Admin | Manage suggested questions |
| POST | `/admin/suggested-questions` | Admin | Create suggested question |
| PUT | `/admin/suggested-questions/{id}` | Admin | Update |
| DELETE | `/admin/suggested-questions/{id}` | Admin | Delete |

### 7.9 Health

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/health` | [Public] | Service health check |
| GET | `/health/ready` | [Public] | DB + ChromaDB readiness |

---

## 8. User Flows

### 8.1 Author — Submit a Question About Formatting

```mermaid
sequenceDiagram
    actor Author
    participant UI as React Chat UI
    participant API as FastAPI
    participant ChatSvc as ChatService
    participant RAG as RAGService
    participant Chroma as ChromaDB
    participant LLM as OpenAI/Azure

    Author->>UI: Opens chat, clicks "Formatting guidelines"
    UI->>API: POST /chat/conversations (JWT)
    API->>ChatSvc: create_conversation()
    ChatSvc-->>API: conversation_id
    API-->>UI: { id, title }

    Author->>UI: Types question / uses suggestion
    UI->>API: POST /chat/conversations/{id}/messages
    API->>ChatSvc: process_message()
    ChatSvc->>RAG: retrieve_and_generate()
    RAG->>Chroma: similarity_search(query, top_k=5)
    Chroma-->>RAG: chunks + metadata (page, section)
    RAG->>LLM: prompt(context + history + query)
    LLM-->>RAG: answer
    RAG->>RAG: extract_citations()
    RAG-->>ChatSvc: { answer, citations }
    ChatSvc->>ChatSvc: save messages + chat_log
    ChatSvc-->>API: response
    API-->>UI: { message, citations[] }
    UI->>Author: Display answer with citation cards
```

### 8.2 Admin — Upload Knowledge Base Document

```mermaid
sequenceDiagram
    actor Admin
    participant UI as Admin Dashboard
    participant API as FastAPI
    participant DocSvc as DocumentService
    participant Ingest as IngestService
    participant Storage as LocalStorage
    participant Parser as PDF/DOCX Parser
    participant Embed as EmbeddingProvider
    participant Chroma as ChromaDB
    participant DB as PostgreSQL

    Admin->>UI: Upload "Author Guidelines.pdf"
    UI->>API: POST /documents/upload (multipart)
    API->>DocSvc: validate_file()
    DocSvc->>Storage: save(file)
    Storage-->>DocSvc: file_path
    DocSvc->>DB: INSERT document (status=pending)
    DocSvc->>Ingest: process_document_async(doc_id)
    DocSvc-->>API: { id, status: pending }
    API-->>UI: Upload accepted

    Ingest->>DB: UPDATE status=processing
    Ingest->>Parser: parse(file_path)
    Parser-->>Ingest: pages[] with text + page numbers
    Ingest->>Ingest: chunk(pages, chunk_size=1000, overlap=200)
    Ingest->>Embed: embed_documents(chunks)
    Embed-->>Ingest: vectors[]
    Ingest->>Chroma: add(ids, embeddings, metadatas)
    Ingest->>DB: INSERT document_chunks
    Ingest->>DB: UPDATE status=indexed, chunk_count
```

### 8.3 Reader — APC Estimation

```mermaid
flowchart TD
    A[Reader opens APC Estimator] --> B[Select paper type]
    B --> C[Enter number of pages]
    C --> D[Select author category]
    D --> E[Click Calculate]
    E --> F[POST /apc/estimate]
    F --> G{APCService}
    G --> H[Fetch active pricing rule for paper_type]
    G --> I[Fetch active discount for author_category]
    H --> J[Calculate: pages × rate OR flat_fee]
    I --> J
    J --> K[Apply discount percentage or fixed]
    K --> L[Return breakdown + total]
    L --> M[Display estimate with waiver note if applicable]
```

### 8.4 Role-Based Access Matrix

| Feature | Admin | Author | Reviewer | Reader | Guest |
|---------|-------|--------|----------|--------|-------|
| Chat (with history) | ✅ | ✅ | ✅ | ✅ | ❌* |
| APC Estimator | ✅ | ✅ | ✅ | ✅ | ✅ |
| View FAQs | ✅ | ✅ | ✅ | ✅ | ✅ |
| View Notifications | ✅ | ✅ | ✅ | ✅ | ✅ |
| Upload Documents | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage Users | ✅ | ❌ | ❌ | ❌ | ❌ |
| View Chat Logs | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage APC Rules | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage FAQs | ✅ | ❌ | ❌ | ❌ | ❌ |

*Guest can use a limited demo chat without persistence (optional Phase 6 enhancement).

---

## 9. RAG Pipeline Design

### 9.1 Pipeline Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  INGESTION  │    │  INDEXING   │    │  RETRIEVAL  │    │ GENERATION  │
│   PIPELINE  │───▶│   PIPELINE  │───▶│   PIPELINE  │───▶│   PIPELINE  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      │                   │                   │                   │
  Upload file         Chunk text          User query          LLM answer
  Parse PDF/DOCX      Generate embed      Embed query         + citations
  Extract metadata    Store in Chroma     Similarity search   Conversation memory
```

### 9.2 Ingestion Pipeline (Offline / Admin Triggered)

| Step | Component | Details |
|------|-----------|---------|
| 1. **Validate** | `file_validation.py` | Max size (50MB), allowed MIME types, virus scan hook |
| 2. **Store** | `LocalStorageBackend` | Path: `uploads/{category}/{uuid}/{filename}` |
| 3. **Parse** | `pdf_parser.py` (PyMuPDF/pdfplumber), `docx_parser.py` (python-docx), `txt_parser.py` | Extract text per page, detect headings |
| 4. **Chunk** | `semantic_chunker.py` | RecursiveCharacterTextSplitter: `chunk_size=1000`, `overlap=200`; preserve `page_number`, `section_title` in metadata |
| 5. **Embed** | `OpenAIEmbeddings` (primary) or `SentenceTransformer` (fallback: `all-MiniLM-L6-v2`) | Batch embed (batch_size=100) |
| 6. **Index** | `ChromaStore` | Collection: `ijaike_kb`; metadata filters: `category`, `document_id`, `page_number`, `section_title` |
| 7. **Persist** | PostgreSQL | `documents` + `document_chunks` tables |

### 9.3 Retrieval Pipeline (Online / Per Query)

| Step | Component | Details |
|------|-----------|---------|
| 1. **Query preprocessing** | `RAGService` | Trim, optional query expansion (future) |
| 2. **Embed query** | Same embedding model as ingestion | Must use identical model/dimensions |
| 3. **Similarity search** | `ChromaRetriever` | `top_k=5`, `score_threshold=0.7`, optional `category` filter |
| 4. **Rerank** (optional Phase 4+) | Cross-encoder reranker | Improve precision for ambiguous queries |
| 5. **Context assembly** | `CitationService` | Format chunks with `[Source: {title}, p.{page}, §{section}]` |
| 6. **Prompt construction** | `rag_prompt.py` | System prompt + retrieved context + conversation history (last 6 turns) + user query |
| 7. **LLM generation** | `ChatOpenAI` / `AzureChatOpenAI` | `temperature=0.2`, `max_tokens=1024` |
| 8. **Citation extraction** | `CitationService` | Map LLM response back to source chunks; always attach even if LLM doesn't cite |
| 9. **Guardrails** | System prompt | "Answer only from provided context; say 'I don't have that information' if not found" |

### 9.4 System Prompt (Core)

```
You are the IJAIKE Journal AI Assistant. You help authors, reviewers, editors, and readers
with questions about manuscript submission, formatting, APC policies, editorial guidelines,
published papers, special issues, and journal announcements.

RULES:
1. Answer ONLY using the provided context documents. Do not invent policies or prices.
2. If the context does not contain the answer, say: "I don't have specific information
   about that in the IJAIKE knowledge base. Please contact the editorial office."
3. Always be professional, concise, and accurate.
4. When citing, reference the source document name, page number, and section.
5. For APC questions, direct users to the APC Estimator for exact calculations.
6. Do not provide legal or medical advice.

CONTEXT:
{retrieved_context}

CONVERSATION HISTORY:
{chat_history}

USER QUESTION:
{user_query}
```

### 9.5 ChromaDB Collection Schema

```python
# Collection: ijaike_kb
{
    "ids": ["{document_id}_{chunk_index}"],
    "embeddings": [[float, ...]],  # 1536-dim (OpenAI) or 384-dim (MiniLM)
    "documents": ["chunk text..."],
    "metadatas": [{
        "document_id": "uuid",
        "document_title": "Author Guidelines 2025",
        "category": "author_guidelines",
        "page_number": 12,
        "section_title": "3.2 Formatting",
        "chunk_index": 45,
        "file_type": "pdf"
    }]
}
```

### 9.6 Multi-Turn Memory Strategy

| Approach | Implementation |
|----------|----------------|
| **Short-term** | Last N messages (6 turns) passed in prompt |
| **Long-term** | Full history in PostgreSQL `messages` table |
| **Summarization** (future) | Summarize conversations > 20 turns to save tokens |

### 9.7 Embedding Model Strategy

| Environment | Primary | Fallback |
|-------------|---------|----------|
| Production | `text-embedding-3-small` (OpenAI) | — |
| Azure | `text-embedding-ada-002` (Azure OpenAI) | — |
| Dev / Offline | — | `sentence-transformers/all-MiniLM-L6-v2` |

**Critical:** Same model must be used for ingestion and retrieval within a collection.

---

## 10. Authentication & Authorization

### 10.1 JWT Token Strategy

| Token | Lifetime | Storage (Frontend) | Purpose |
|-------|----------|-------------------|---------|
| Access Token | 15 minutes | Memory / sessionStorage | API authorization |
| Refresh Token | 7 days | httpOnly cookie (preferred) or secure storage | Token renewal |

### 10.2 Password Security

- **Hashing:** bcrypt with cost factor 12
- **Validation:** Min 8 chars, 1 uppercase, 1 digit (configurable)
- **Rate limiting:** 5 failed login attempts → 15 min lockout

### 10.3 RBAC Implementation

```python
# permissions.py
ROLE_PERMISSIONS = {
    "admin": ["*"],
    "author": ["chat:read", "chat:write", "apc:estimate", "faqs:read"],
    "reviewer": ["chat:read", "chat:write", "apc:estimate", "faqs:read"],
    "reader": ["chat:read", "chat:write", "apc:estimate", "faqs:read"],
}
```

FastAPI dependency: `require_role(["admin"])` or `require_permission("documents:write")`

---

## 11. APC Estimator Design

### 11.1 Calculation Logic

```python
def calculate_apc(paper_type, num_pages, author_category):
    pricing = get_active_pricing_rule(paper_type)
    
    if pricing.flat_fee:
        subtotal = pricing.flat_fee
    else:
        pages = clamp(num_pages, pricing.minimum_pages, pricing.maximum_pages)
        subtotal = pages * pricing.base_rate_per_page
    
    discount = get_active_discount_rule(author_category)
    
    if discount.discount_type == "percentage":
        discount_amount = subtotal * (discount.discount_value / 100)
    else:
        discount_amount = discount.discount_value
    
    total = max(subtotal - discount_amount, 0)
    
    return APCEstimate(
        subtotal=subtotal,
        discount_amount=discount_amount,
        total=total,
        requires_waiver_approval=discount.requires_approval,
        breakdown=format_breakdown(...)
    )
```

### 11.2 Default Pricing (Seed Data — Admin Configurable)

| Paper Type | Base Rate/Page (USD) | Min Pages |
|------------|---------------------|-----------|
| research_article | $50 | 6 |
| review_article | $60 | 8 |
| short_communication | $40 | 4 |
| case_study | $45 | 5 |

| Author Category | Discount | Waiver Required |
|-----------------|----------|-----------------|
| regular | 0% | No |
| developing_country | 25% | No |
| student | 50% | Yes |
| ijaike_member | 15% | No |
| institutional_partner | 30% | No |

---

## 12. Storage Strategy

### 12.1 Abstract Interface

```python
class StorageBackend(ABC):
    async def save(self, file: UploadFile, path: str) -> str: ...
    async def delete(self, path: str) -> None: ...
    async def get_url(self, path: str) -> str: ...
    async def exists(self, path: str) -> bool: ...
```

### 12.2 Implementations

| Class | Phase | Path Pattern |
|-------|-------|--------------|
| `LocalStorageBackend` | Phase 2 | `./uploads/{category}/{doc_id}/{filename}` |
| `AzureBlobStorageBackend` | Phase 9 | `ijaike-kb/{category}/{doc_id}/{filename}` |
| `S3StorageBackend` | Phase 9 | Same key pattern |

Configuration via `STORAGE_BACKEND=local|azure|s3` env var.

---

## 13. Configuration & Environment

### 13.1 Backend `.env.example`

```env
# App
APP_NAME=IJAIKE Chatbot
APP_ENV=development
DEBUG=true
SECRET_KEY=change-me-in-production
CORS_ORIGINS=http://localhost:5173

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/ijaike_chatbot

# JWT
JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI (or Azure)
LLM_PROVIDER=openai          # openai | azure
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# Azure OpenAI (if LLM_PROVIDER=azure)
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com/
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

# Embeddings fallback
EMBEDDING_PROVIDER=openai    # openai | sentence_transformer
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2

# ChromaDB
CHROMA_PERSIST_DIR=./data/chroma
CHROMA_COLLECTION_NAME=ijaike_kb

# Storage
STORAGE_BACKEND=local
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=50

# RAG
RAG_TOP_K=5
RAG_SCORE_THRESHOLD=0.7
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 13.2 Frontend `.env.example`

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=IJAIKE Journal Assistant
```

---

## 14. Logging, Monitoring & Error Handling

| Concern | Approach |
|---------|----------|
| **Logging** | Python `logging` + structured JSON logs (production); log level via env |
| **Request tracing** | `X-Request-ID` header propagated through services |
| **Error responses** | Consistent format: `{ "detail": "...", "code": "ERROR_CODE", "request_id": "..." }` |
| **Chat latency** | Log `latency_ms` in `chat_logs` table |
| **Ingest failures** | `documents.error_message` + admin notification |
| **Health checks** | `/health` (liveness), `/health/ready` (DB + Chroma connectivity) |

---

## 15. Security Considerations

| Area | Measure |
|------|---------|
| **Input validation** | Pydantic schemas on all endpoints; file type whitelist |
| **SQL injection** | SQLAlchemy ORM parameterized queries |
| **XSS** | React auto-escaping; sanitize markdown in chat |
| **CSRF** | SameSite cookies for refresh tokens |
| **Rate limiting** | slowapi: 60 req/min per IP on chat; 10 req/min on login |
| **File upload** | Size limits, MIME validation, store outside web root |
| **Secrets** | All keys in env vars; never committed |
| **CORS** | Whitelist frontend origin only |
| **Admin actions** | Audit log for document upload/delete, user role changes |

---

## 16. Scalability & Deployment

### 16.1 Phase 9 Target Architecture

```
                    ┌──────────────┐
                    │   Nginx /    │
                    │   Traefik    │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──────┐ ┌───▼───┐ ┌──────▼──────┐
       │  Frontend   │ │  API  │ │  API (n)    │
       │  (Static)   │ │  (1)  │ │  (scale)    │
       └─────────────┘ └───┬───┘ └──────┬──────┘
                           │            │
                    ┌──────▼────────────▼──────┐
                    │      PostgreSQL          │
                    └──────────────────────────┘
                    ┌──────────────────────────┐
                    │  ChromaDB (persistent) │
                    └──────────────────────────┘
                    ┌──────────────────────────┐
                    │  Azure Blob / S3         │
                    └──────────────────────────┘
```

### 16.2 Future Enhancements (Post-MVP)

- Celery + Redis for async document ingestion
- Cross-encoder reranking for better retrieval
- Hybrid search (BM25 + vector)
- Multi-language support
- Email notifications for waiver approvals
- Analytics dashboard (popular questions, retrieval quality)

---

## 17. Phase Roadmap

| Phase | Scope | Deliverables |
|-------|-------|--------------|
| **Phase 1** ✅ | Architecture design | This document — **awaiting approval** |
| **Phase 2** | Backend foundation | FastAPI skeleton, DB models, migrations, core services |
| **Phase 3** | Frontend foundation | React app, routing, layouts, API client |
| **Phase 4** | AI pipeline | Parsers, chunking, embeddings, ChromaDB, RAG chain |
| **Phase 5** | Integration | Wire chat UI ↔ RAG API, citations display |
| **Phase 6** | Authentication | JWT, RBAC, protected routes |
| **Phase 7** | Admin dashboard | Document upload, user mgmt, APC config, FAQs |
| **Phase 8** | Testing | Unit, integration, E2E tests |
| **Phase 9** | Deployment | Docker, CI/CD, production config |

---

## Approval Checklist

Please review and confirm:

- [ ] High-level architecture (layers, components)
- [ ] Folder structure
- [ ] Database schema (tables, enums, relationships)
- [ ] API endpoints (coverage, naming)
- [ ] User flows (author, admin, reader)
- [ ] RAG pipeline (ingestion, retrieval, generation)
- [ ] APC estimator logic
- [ ] Auth strategy (JWT, RBAC)
- [ ] Storage abstraction
- [ ] Phase roadmap order

**Reply with approval or requested changes to proceed to Phase 2.**
