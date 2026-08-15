# Visual Guide to Architecture Patterns

A visual comparison of different architectural patterns for the memory-map-app.

---

## 1. Service Layer (Current Implementation)

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│                                                              │
│    ┌──────────────────────┐      ┌────────────────────┐    │
│    │  Streamlit Web App   │      │    MCP Server      │    │
│    │                      │      │                    │    │
│    │  • UI Components     │      │  • Tool Handlers   │    │
│    │  • User Input        │      │  • Text Formatting │    │
│    │  • Display Logic     │      │  • Protocol Logic  │    │
│    └──────────┬───────────┘      └─────────┬──────────┘    │
└───────────────┼──────────────────────────────┼──────────────┘
                │                              │
                │  Calls service methods       │
                └──────────────┬───────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                    BUSINESS LOGIC LAYER                       │
│                                                               │
│              ┌───────────────────────────┐                   │
│              │    MemoryService          │                   │
│              │                           │                   │
│              │  • search_memories()      │                   │
│              │  • add_text_memory()      │                   │
│              │  • add_image_memory()     │                   │
│              │  • get_memory_stats()     │                   │
│              │  • list_recent_memories() │                   │
│              └─────────────┬─────────────┘                   │
└────────────────────────────┼─────────────────────────────────┘
                             │
                    Uses data loaders
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼──────────┐  ┌──────▼─────────┐  ┌──────▼─────────┐
│  TextDataLoader  │  │ ImageDataLoader│  │ MemoryRetriever│
│                  │  │                │  │                │
│  • load_text()   │  │ • load_image() │  │ • search()     │
│  • save_text()   │  │ • save_image() │  │ • retrieve()   │
└───────┬──────────┘  └──────┬─────────┘  └──────┬─────────┘
        │                    │                    │
┌───────▼────────────────────▼────────────────────▼───────────┐
│                      DATA LAYER                              │
│                                                              │
│      ┌──────────────┐              ┌──────────────┐        │
│      │  ChromaDB    │              │  ChromaDB    │        │
│      │  (Text)      │              │  (Images)    │        │
│      └──────────────┘              └──────────────┘        │
└──────────────────────────────────────────────────────────────┘

Benefits:
  ✅ Simple and clear
  ✅ No duplicate code
  ✅ Easy to test
  ✅ Good separation of concerns
```

---

## 2. Repository Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                          │
│             (Streamlit App, MCP Server)                      │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                   SERVICE LAYER                              │
│                                                              │
│              ┌───────────────────────────┐                  │
│              │    MemoryService          │                  │
│              │                           │                  │
│              │  Uses Repository          │                  │
│              │  Interfaces (abstractions)│                  │
│              └─────────────┬─────────────┘                  │
└────────────────────────────┼─────────────────────────────────┘
                             │
              Depends on abstractions
                             │
┌────────────────────────────▼─────────────────────────────────┐
│               REPOSITORY INTERFACES (Abstract)               │
│                                                              │
│    ┌────────────────────────────────────────────────┐      │
│    │       IMemoryRepository (Interface)            │      │
│    │                                                 │      │
│    │  • save(memory)                                │      │
│    │  • find_by_id(id)                              │      │
│    │  • search(query, limit)                        │      │
│    │  • delete(id)                                  │      │
│    └────────────────────┬───────────────────────────┘      │
└─────────────────────────┼───────────────────────────────────┘
                          │
         Implemented by concrete repositories
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼──────────┐ ┌────▼──────────┐ ┌───▼────────────┐
│ChromaRepository  │ │PineconeRepo   │ │FAISSRepository │
│                  │ │               │ │                │
│ ChromaDB-specific│ │Pinecone API   │ │FAISS-specific  │
│ implementation   │ │implementation │ │implementation  │
└──────────────────┘ └───────────────┘ └────────────────┘

Benefits:
  ✅ Easy to swap databases
  ✅ Multiple backends supported
  ✅ Testable with mocks
  ✅ Clear data access layer

Trade-offs:
  ⚠️ More abstractions
  ⚠️ Additional boilerplate
```

---

## 3. Clean Architecture (Hexagonal)

```
                    ┌────────────────────┐
                    │   Infrastructure   │ ← Outer Layer
                    │   (Frameworks)     │
                    └─────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
  ┌─────▼──────┐      ┌───────▼──────┐      ┌──────▼─────┐
  │ Streamlit  │      │  MCP Server  │      │  REST API  │
  │  Adapter   │      │   Adapter    │      │  Adapter   │
  └─────┬──────┘      └───────┬──────┘      └──────┬─────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│              INTERFACE ADAPTERS (Ports)                    │
│                                                             │
│   ┌──────────────────┐           ┌──────────────────┐    │
│   │   Controllers    │           │   Presenters     │    │
│   └──────────────────┘           └──────────────────┘    │
│                                                            │
│   ┌──────────────────────────────────────────────────┐   │
│   │        Repository Implementations                │   │
│   └──────────────────────────────────────────────────┘   │
└────────────────────────────┬───────────────────────────────┘
                             │
                    Dependencies point inward
                             │
┌────────────────────────────▼───────────────────────────────┐
│                  USE CASES (Application)                    │
│                                                             │
│   ┌──────────────────────────────────────────────────┐    │
│   │  • AddMemoryUseCase                              │    │
│   │  • SearchMemoriesUseCase                         │    │
│   │  • GetMemoryStatsUseCase                         │    │
│   │                                                   │    │
│   │  (Uses Port Interfaces - no concrete deps)       │    │
│   └──────────────────────────────────────────────────┘    │
└────────────────────────────┬───────────────────────────────┘
                             │
                    No external dependencies
                             │
┌────────────────────────────▼───────────────────────────────┐
│                  ENTITIES (Core Domain)                     │
│                                                             │
│   ┌──────────────────────────────────────────────────┐    │
│   │  • Memory                                        │    │
│   │  • Embedding                                     │    │
│   │  • MemoryMetadata                                │    │
│   │                                                   │    │
│   │  (Pure business logic, no framework deps)        │    │
│   └──────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘

Benefits:
  ✅ Framework independent
  ✅ Extremely testable
  ✅ Portable core logic
  ✅ Clear boundaries

Trade-offs:
  ⚠️ High complexity
  ⚠️ Steep learning curve
  ⚠️ More files and layers
```

---

## 4. Vertical Slice Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                          │
│             (Streamlit App, MCP Server)                      │
└─────────────────────────────┬───────────────────────────────┘
                              │
                    Routes to feature handlers
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼──────────┐  ┌───────▼──────────┐  ┌──────▼────────┐
│  Add Text Memory │  │  Search Memories │  │  Get Stats    │
│     Feature      │  │     Feature      │  │   Feature     │
│                  │  │                  │  │               │
│  ┌────────────┐ │  │  ┌────────────┐ │  │  ┌──────────┐ │
│  │  Handler   │ │  │  │  Handler   │ │  │  │ Handler  │ │
│  └──────┬─────┘ │  │  └──────┬─────┘ │  │  └────┬─────┘ │
│         │       │  │         │       │  │       │       │
│  ┌──────▼─────┐ │  │  ┌──────▼─────┐ │  │  ┌────▼─────┐ │
│  │  Service   │ │  │  │  Service   │ │  │  │ Service  │ │
│  └──────┬─────┘ │  │  └──────┬─────┘ │  │  └────┬─────┘ │
│         │       │  │         │       │  │       │       │
│  ┌──────▼─────┐ │  │  ┌──────▼─────┐ │  │  ┌────▼─────┐ │
│  │Repository  │ │  │  │Repository  │ │  │  │Repository│ │
│  └────────────┘ │  │  └────────────┘ │  │  └──────────┘ │
│                  │  │                  │  │               │
│  ┌────────────┐ │  │  ┌────────────┐ │  │  ┌──────────┐ │
│  │  Models    │ │  │  │  Models    │ │  │  │ Models   │ │
│  └────────────┘ │  │  └────────────┘ │  │  └──────────┘ │
└──────────────────┘  └──────────────────┘  └───────────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                  ┌────────────▼────────────┐
                  │   Shared Components     │
                  │  • Database             │
                  │  • Embedding Models     │
                  │  • Common Utils         │
                  └─────────────────────────┘

Benefits:
  ✅ Features self-contained
  ✅ Easy to find code
  ✅ Parallel development
  ✅ Feature teams alignment

Trade-offs:
  ⚠️ Code duplication possible
  ⚠️ Shared logic management
```

---

## 5. CQRS (Command Query Responsibility Segregation)

```
┌─────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                          │
└──────────────┬────────────────────────────────┬─────────────┘
               │                                │
        WRITES │                                │ READS
               │                                │
┌──────────────▼───────────────┐   ┌───────────▼──────────────┐
│   COMMAND SIDE (Write)       │   │   QUERY SIDE (Read)      │
│                              │   │                          │
│  ┌────────────────────────┐ │   │  ┌────────────────────┐ │
│  │  Commands              │ │   │  │  Queries           │ │
│  │                        │ │   │  │                    │ │
│  │  • AddMemoryCommand    │ │   │  │  • SearchQuery     │ │
│  │  • DeleteMemoryCommand │ │   │  │  • GetStatsQuery   │ │
│  └──────────┬─────────────┘ │   │  └──────────┬─────────┘ │
│             │                │   │             │           │
│  ┌──────────▼─────────────┐ │   │  ┌──────────▼─────────┐ │
│  │  Command Handlers      │ │   │  │  Query Handlers    │ │
│  │                        │ │   │  │                    │ │
│  │  • Process commands    │ │   │  │  • Return views    │ │
│  │  • Validate            │ │   │  │  • No business     │ │
│  │  • Emit events         │ │   │  │    logic           │ │
│  └──────────┬─────────────┘ │   │  └──────────┬─────────┘ │
│             │                │   │             │           │
│  ┌──────────▼─────────────┐ │   │  ┌──────────▼─────────┐ │
│  │  Write Model           │ │   │  │  Read Model        │ │
│  │  (Normalized)          │ │   │  │  (Denormalized)    │ │
│  │                        │ │   │  │                    │ │
│  │  ChromaDB Write Store  │ │   │  │  Optimized Cache   │ │
│  └────────────────────────┘ │   │  │  Pre-computed      │ │
└─────────────┬────────────────┘   │  │  Aggregates        │ │
              │                    │  └────────────────────┘ │
              │ Emit Events        └──────────▲──────────────┘
              │                               │
              │  ┌────────────────────────┐   │
              └─►│    Event Bus           │───┘
                 │                        │
                 │  • MemoryAddedEvent    │ Update Read Model
                 │  • MemoryDeletedEvent  │
                 └────────────────────────┘

Benefits:
  ✅ Optimized read/write separately
  ✅ Scales independently
  ✅ Different models for different needs

Trade-offs:
  ⚠️ Eventual consistency
  ⚠️ High complexity
  ⚠️ Event synchronization
```

---

## 6. Comparison: Code Organization

### Service Layer (Current)
```
memory-map-app/
├── services/
│   └── memory_service.py     ← All business logic here
├── app/
│   └── main.py               ← Streamlit presentation
├── mcp_server/
│   └── server.py             ← MCP presentation
├── db/
│   └── chroma_db.py          ← Data access
└── etl/
    └── data_loaders/         ← Data processing
```

### Repository Pattern
```
memory-map-app/
├── services/
│   └── memory_service.py     ← Uses repositories
├── repositories/
│   ├── interfaces.py         ← Abstract interfaces
│   ├── chroma_repository.py  ← ChromaDB impl
│   └── pinecone_repository.py← Pinecone impl
├── app/
│   └── main.py
└── mcp_server/
    └── server.py
```

### Clean Architecture
```
memory-map-app/
├── core/
│   ├── entities/             ← Pure domain models
│   └── use_cases/            ← Business rules
├── adapters/
│   ├── controllers/          ← Input adapters
│   ├── presenters/           ← Output adapters
│   └── repositories/         ← Data adapters
└── infrastructure/
    ├── web/                  ← Streamlit
    ├── mcp/                  ← MCP server
    └── database/             ← ChromaDB
```

### Vertical Slice
```
memory-map-app/
├── features/
│   ├── add_text_memory/
│   │   ├── handler.py
│   │   ├── service.py
│   │   ├── repository.py
│   │   └── models.py
│   ├── search_memories/
│   │   ├── handler.py
│   │   ├── service.py
│   │   ├── repository.py
│   │   └── models.py
│   └── get_stats/
│       ├── handler.py
│       └── service.py
└── shared/
    ├── database.py
    └── embedding.py
```

---

## Decision Flow Chart

```
                    START
                      │
                      ▼
         ┌────────────────────────┐
         │ Need to eliminate      │
         │ code duplication?      │
         └─────────┬──────────────┘
                   │ YES
                   ▼
         ┌────────────────────────┐
         │   Service Layer ✓      │
         │   (Current Solution)   │
         └─────────┬──────────────┘
                   │
         ┌─────────┼─────────┐
         │                   │
         ▼                   ▼
┌────────────────┐  ┌────────────────┐
│ Need multiple  │  │ Features very  │
│ databases?     │  │ independent?   │
└───────┬────────┘  └────────┬───────┘
        │ YES                │ YES
        ▼                    ▼
┌────────────────┐  ┌────────────────┐
│  Add           │  │  Migrate to    │
│  Repository    │  │  Vertical      │
│  Pattern       │  │  Slices        │
└───────┬────────┘  └────────────────┘
        │
        ▼
┌────────────────┐
│ Need framework │
│ independence?  │
└───────┬────────┘
        │ YES
        ▼
┌────────────────┐
│  Clean         │
│  Architecture  │
└────────────────┘
```

---

## Evolution Timeline

```
Week 1-4: Service Layer
├─ Eliminate duplication
├─ Basic abstraction
└─ Easy to maintain

Month 2-3: Add Repository (if needed)
├─ Support multiple DBs
├─ Swap implementations
└─ Better testability

Month 4-6: Vertical Slices (if features diverge)
├─ Feature independence
├─ Team scalability
└─ Parallel development

Month 6+: Clean Architecture (if needed)
├─ Framework independence
├─ Long-term maintainability
└─ Core business logic isolation
```

---

## Key Takeaway

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   "The best architecture is the simplest one that      │
│    meets your actual requirements."                    │
│                                                         │
│   Start simple (Service Layer) ✓                       │
│   → Add complexity only when needed                    │
│   → Measure real pain points first                     │
│   → Evolve gradually, not all at once                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Visual Summary

| Pattern | Layers | Complexity | Flexibility | Best For |
|---------|--------|------------|-------------|----------|
| **Service Layer** | 3 | ⭐ | ⭐⭐ | Most apps |
| **Repository** | 4 | ⭐⭐ | ⭐⭐⭐ | Multi-DB |
| **Clean Arch** | 5 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Enterprise |
| **Vertical Slice** | Varies | ⭐⭐ | ⭐⭐⭐ | Feature teams |
| **CQRS** | 6+ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | High scale |

---

Remember: **Start with Service Layer, evolve when requirements demand it!**
