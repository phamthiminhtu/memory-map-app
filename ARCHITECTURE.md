# Architecture & Modularization Strategy

## Overview

This document explains the modularization strategy used to eliminate code duplication between the MCP server and Streamlit app.

## Problem

Previously, both `mcp_server/server.py` and `app/main.py` contained duplicate business logic for:
- Searching memories
- Adding text/image memories
- Getting memory statistics
- Listing recent memories

This violated the DRY (Don't Repeat Yourself) principle and made maintenance difficult.

## Solution: Service Layer Pattern

We introduced a **Service Layer** that encapsulates all business logic in a single, reusable module.

### Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│          Presentation Layer                              │
│  ┌──────────────────┐    ┌────────────────────────┐    │
│  │  Streamlit App   │    │    MCP Server          │    │
│  │  (app/main.py)   │    │  (mcp_server/server.py)│    │
│  └────────┬─────────┘    └──────────┬─────────────┘    │
└───────────┼────────────────────────────┼─────────────────┘
            │                            │
            │    ┌──────────────────┐   │
            └───►│  MemoryService   │◄──┘
                 │  (services/)     │
                 └────────┬─────────┘
┌────────────────────────┼───────────────────────────────┐
│          Business Logic Layer                           │
│   - search_memories()                                   │
│   - add_text_memory()                                   │
│   - add_image_memory()                                  │
│   - get_memory_stats()                                  │
│   - list_recent_memories()                              │
└─────────────────────────┼──────────────────────────────┘
                          │
            ┌─────────────┴──────────────┐
            │                            │
    ┌───────▼────────┐          ┌───────▼────────┐
    │  Data Loaders  │          │   Vector DBs   │
    │   (etl/)       │          │    (db/)       │
    └────────────────┘          └────────────────┘
┌──────────────────────────────────────────────────────┐
│          Data Layer                                   │
└──────────────────────────────────────────────────────┘
```

## Key Components

### 1. Service Layer (`services/memory_service.py`)

The `MemoryService` class provides:
- **Single Responsibility**: All memory management logic in one place
- **Dependency Injection**: Databases and loaders initialized in constructor
- **Type Safety**: Uses dataclasses for structured responses
- **Testability**: Easy to mock dependencies for unit testing

#### Key Methods:

```python
class MemoryService:
    def search_memories(query, n_results) -> SearchResult
    def add_text_memory(text, title, tags, description) -> str
    def add_image_memory(image_path, title, tags, description) -> str
    def get_memory_stats() -> MemoryStats
    def list_recent_memories(limit, memory_type) -> List[Dict]
```

#### Data Transfer Objects (DTOs):

```python
@dataclass
class MemoryStats:
    total_count: int
    text_count: int
    image_count: int

@dataclass
class SearchResult:
    memories: List[Dict[str, Any]]
    query: str
    count: int
```

### 2. Presentation Layers

#### Streamlit App (`app/main.py`)
- Initializes `MemoryService` once using `@st.cache_resource`
- UI rendering and user interaction
- Formats service responses for web display

#### MCP Server (`mcp_server/server.py`)
- Initializes `MemoryService` globally
- Exposes memory operations via MCP protocol
- Formats service responses as text for AI tools

## Benefits

### 1. **DRY Principle**
- Business logic written once
- Changes propagate automatically to all consumers

### 2. **Separation of Concerns**
- **Service Layer**: Pure business logic
- **Presentation**: UI-specific formatting
- **Data Layer**: Database operations

### 3. **Maintainability**
- Single source of truth for business rules
- Easier to debug and test
- Changes isolated to appropriate layers

### 4. **Scalability**
- Easy to add new presentation layers (CLI, REST API, etc.)
- Service layer remains unchanged
- Can swap implementations without affecting consumers

### 5. **Testability**
- Service can be unit tested independently
- Mock dependencies for integration tests
- Presentation layers test UI/formatting only

## Code Comparison

### Before Modularization

**MCP Server:**
```python
# 200+ lines of duplicate logic
text_chroma_db = ChromaDB(persist_directory="data/chroma_text")
text_loader = TextDataLoader(chroma_db=text_chroma_db)
metadata = {'type': 'text', 'text': text}
doc_id = text_loader.load_text(text, metadata)
```

**Streamlit App:**
```python
# Same 200+ lines duplicated
text_db, text_loader = init_text_components()
metadata = {}
if title: metadata['title'] = title
text_loader.save_text_memory(text=memory_text, metadata=metadata)
```

### After Modularization

**MCP Server:**
```python
# Clean, simple call
doc_id = memory_service.add_text_memory(
    text=text, title=title, tags=tags, description=description
)
```

**Streamlit App:**
```python
# Same simple interface
service.add_text_memory(
    text=memory_text, title=title, tags=tags, description=description
)
```

## Future Enhancements

The service layer architecture enables:
1. **REST API**: Add Flask/FastAPI endpoints using `MemoryService`
2. **CLI Tool**: Create command-line interface with same service
3. **Batch Operations**: Add bulk import/export methods
4. **Caching**: Implement service-level caching strategies
5. **Async Support**: Convert to async methods for better performance
6. **Monitoring**: Add metrics and logging at service layer

## Best Practices Applied

1. **Single Responsibility Principle**: Each class has one reason to change
2. **Dependency Inversion**: Depend on abstractions, not concrete implementations
3. **Interface Segregation**: Small, focused method signatures
4. **Open/Closed Principle**: Open for extension, closed for modification
5. **Don't Repeat Yourself**: Single source of truth for business logic

## Testing Strategy

```python
# Unit Tests (services_test.py)
def test_search_memories():
    mock_db = MockChromaDB()
    service = MemoryService(text_db=mock_db, image_db=mock_db)
    result = service.search_memories("test query", n_results=5)
    assert result.count == 5

# Integration Tests (integration_test.py)
def test_end_to_end_flow():
    service = MemoryService()
    doc_id = service.add_text_memory("test")
    results = service.search_memories("test")
    assert len(results.memories) > 0
```

## Conclusion

The service layer pattern successfully eliminated ~400 lines of duplicate code while improving:
- Code maintainability
- Testability
- Scalability
- Developer experience

This architecture follows industry best practices and makes the codebase more professional and easier to extend.
