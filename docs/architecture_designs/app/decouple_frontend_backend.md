# Frontend-Backend Decoupling Plan

## Current Architecture (Updated)

### Backend Structure (Python)

```
backend/
├── core/                        # Core business logic
│   ├── processors/             # Data ingestion and embedding
│   │   ├── base_loader.py      # Base class for all processors
│   │   ├── text_loader.py      # Text processing & embedding
│   │   └── image_loader.py     # Image processing & embedding (CLIP)
│   └── retrievers/             # Data retrieval and search
│       └── memory_retriever.py # Unified memory search
├── services/                   # Service layer
│   └── memory_service.py       # Main business logic orchestrator
├── db/                         # Database layer
│   ├── chroma_db.py           # ChromaDB wrapper
│   ├── auth.py                # Authentication utilities
│   └── faiss_index.py         # FAISS index management
├── utils/                      # Shared utilities
│   └── text_cleaning.py
└── app/                        # Streamlit UI (to be replaced)
    ├── main.py
    └── components.py
```

### Components Classification

**Backend Components (Keep in Python):**
- ✅ `core/processors/` - Data ingestion, embedding generation
- ✅ `core/retrievers/` - Search and retrieval logic
- ✅ `services/memory_service.py` - Business logic orchestrator
- ✅ `db/` - Database layer (ChromaDB, FAISS)
- ✅ `utils/` - Shared utilities

**Frontend Components (Migrate to TypeScript/React):**
- 🔄 `app/main.py` - UI rendering (to be replaced)
- 🔄 `app/components.py` - UI components (to be replaced)

---

## Migration Plan Overview

### Phase 1: Build FastAPI REST API
Wrap existing MemoryService with REST API endpoints

### Phase 2: Create Next.js + TypeScript Frontend
Build modern React UI with modern component library

### Phase 3: Integration, Testing & Deployment
Connect frontend to backend, test, and deploy

### Phase 4: Optional Advanced Features
Authentication, real-time sync, collaboration, mobile app

## Next Steps

1. **Create FastAPI Backend**
   - Define Pydantic models for requests/responses
   - Create REST endpoints for memory operations
   - Add CORS, error handling, file upload

2. **Initialize Next.js Frontend**
   - Set up Next.js 14 with TypeScript
   - Install shadcn/ui, Tailwind CSS
   - Create component structure

3. **Implement Core Features**
   - Memory add/search/view functionality
   - Image upload with drag-and-drop
   - Responsive design

4. **Polish & Deploy**
   - Testing (pytest, Jest, Playwright)
   - Docker containerization
   - Deployment strategy
