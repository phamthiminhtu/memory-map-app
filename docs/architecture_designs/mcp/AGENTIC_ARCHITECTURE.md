# Agentic Architecture Documentation

## Overview

The memory-map application features an **agentic architecture** that enables AI assistants to intelligently answer complex queries by selecting and combining multiple specialized tools.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                    User Query                        │
│         "What was I doing on October 15?"           │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│              Claude Desktop (Agent)                  │
│  ┌─────────────────────────────────────────────┐   │
│  │  1. Analyzes Intent:                        │   │
│  │     - Temporal (October 15)                 │   │
│  │     - Narrative (story format)              │   │
│  │     - Multi-source (text + images)          │   │
│  │                                              │   │
│  │  2. Selects Tool:                           │   │
│  │     → synthesize_memory_story                │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│              MCP Server (Tools Layer)               │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  Tool Registry (Command Pattern)             │  │
│  │  ┌────────────────────────────────────────┐  │  │
│  │  │  synthesize_memory_story               │  │  │
│  │  │  search_memories_by_date               │  │  │
│  │  │  search_text_memories                  │  │  │
│  │  │  search_image_memories                 │  │  │
│  │  │  search_memories (legacy)              │  │  │
│  │  │  add_text_memory                       │  │  │
│  │  │  get_memory_stats                      │  │  │
│  │  │  list_recent_memories                  │  │  │
│  │  └────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│           Memory Service (Business Logic)           │
│                                                      │
│  Core Methods:                                       │
│  • search_text_memories_only()                      │
│  • search_image_memories_only()                     │
│  • search_memories_by_date()                        │
│  • synthesize_memories() ⭐                          │
│  • _extract_date_from_text()                        │
│  • _filter_by_date_range()                          │
│  • _create_timeline()                               │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│            Data Layer (Vector Databases)            │
│                                                      │
│  ┌──────────────┐         ┌──────────────────┐     │
│  │  Text DB     │         │  Image DB        │     │
│  │  (ChromaDB)  │         │  (ChromaDB)      │     │
│  │              │         │                  │     │
│  │  Embeddings: │         │  Embeddings:     │     │
│  │  MiniLM-L6   │         │  CLIP ViT-B/32   │     │
│  └──────────────┘         └──────────────────┘     │
└─────────────────────────────────────────────────────┘
```

## Component Details

### 1. MCP Server Layer

**Location:** [`mcp_server/`](../mcp_server/)

**Components:**
- **[server.py](../mcp_server/server.py)** - Main MCP server entry point
- **[config.py](../mcp_server/config.py)** - Configuration and environment initialization
- **[handlers.py](../mcp_server/handlers.py)** - Tool handlers (Command Pattern)
- **[formatters.py](../mcp_server/formatters.py)** - Response formatting

**Design Patterns:**
- **Command Pattern**: Each tool has a dedicated handler class
- **Registry Pattern**: `ToolRegistry` dispatches to appropriate handlers
- **Factory Pattern**: `MCPConfig` creates configured instances

### 2. Memory Service Layer

**Location:** [`services/memory_service.py`](../services/memory_service.py)

**Key Methods:**

#### Specialized Search
```python
def search_text_memories_only(query: str, n_results: int) -> SearchResult
def search_image_memories_only(query: str, n_results: int) -> SearchResult
```

#### Date-Aware Search
```python
def search_memories_by_date(
    query: str,
    start_date: str,
    end_date: str = None
) -> SearchResult
```

#### Agentic Synthesis ⭐
```python
def synthesize_memories(
    query: str,
    start_date: str = None,
    end_date: str = None,
    n_results_per_type: int = 10
) -> SynthesisResult
```

**Features:**
- Date extraction from text using regex patterns
- Timeline creation with chronological sorting
- Multi-source synthesis (text + images)
- Metadata enhancement with timestamps

### 3. Data Layer

**Components:**
- **Text Database**: ChromaDB with Sentence Transformers (all-MiniLM-L6-v2)
- **Image Database**: ChromaDB with CLIP (ViT-B/32)
- **Loaders**: `TextDataLoader`, `ImageDataLoader`

**Data Flow:**
```
Memory Input → Loader → Embedding Generation → ChromaDB → Vector Storage
```

## Agentic Flow Example

### Query: "What was I doing on October 15?"

**Step 1: Intent Analysis**
```
Detected:
- Temporal intent: "October 15"
- Activity intent: "doing"
- Narrative need: Story format
```

**Step 2: Tool Selection**
```
Claude selects: synthesize_memory_story
Reason: Best fit for date + narrative query
```

**Step 3: Tool Execution**
```python
# Handler receives request
SynthesizeMemoryStoryHandler.handle({
    "query": "daily activities",
    "start_date": "October 15",
    "n_results_per_type": 10
})

# Calls MemoryService
service.synthesize_memories(
    query="daily activities",
    start_date="2025-10-15",
    n_results_per_type=10
)
```

**Step 4: Memory Service Processing**
```python
# 1. Search text memories
text_results = search_text_memories_only("daily activities", 10)

# 2. Search image memories
image_results = search_image_memories_only("daily activities", 10)

# 3. Filter by date
filtered_text = _filter_by_date_range(text_results, "2025-10-15")
filtered_images = _filter_by_date_range(image_results, "2025-10-15")

# 4. Create timeline
timeline = _create_timeline(filtered_text + filtered_images)

# 5. Return structured result
return SynthesisResult(
    text_memories=filtered_text,
    image_memories=filtered_images,
    timeline=timeline,
    ...
)
```

**Step 5: Formatting**
```python
# Formatter creates readable response
formatter.format_synthesis(synthesis_result)
# Returns chronological timeline with metadata
```

**Step 6: Claude Generates Narrative**
```
Claude receives timeline and creates:

"On October 15, 2025, you had a productive day:

Morning:
- Started with a jog in the park (text memory, 8:00 AM)

Midday:
- Team meeting about Q4 roadmap (text memory, 2:00 PM)

Evening:
- Finished reading 'Design of Everyday Things' (text memory, 8:00 PM)"
```

## Key Design Decisions

### 1. Tool Specialization
**Why:** Allows Claude to make informed decisions about which tool fits the query
- `search_text_memories` - Text-only searches
- `search_image_memories` - Image-only searches
- `synthesize_memory_story` - Full synthesis with timeline

### 2. Command Pattern for Handlers
**Why:** Clean separation, easy to add new tools, testable
```python
class ToolHandler:
    def handle(self, arguments: Dict) -> List[TextContent]

class ToolRegistry:
    handlers: Dict[str, ToolHandler]
    def handle(self, tool_name: str, arguments: Dict)
```

### 3. Date Extraction & Filtering
**Why:** Enables temporal queries without explicit dates
- Extracts dates from text using regex patterns
- Supports natural language dates ("last Monday", "October 15")
- Falls back to file timestamps for images

### 4. Timeline Synthesis
**Why:** Creates coherent narratives from disparate sources
- Sorts memories chronologically
- Combines text and images
- Provides structured data for Claude's narrative generation

## Configuration Management

**Location:** [`mcp_server/config.py`](../mcp_server/config.py)

```python
class MCPConfig:
    """Manages MCP server configuration"""

    def __init__(self, project_root: Path = None)
    def ensure_data_directories(self) -> None
    def get_persist_directories(self) -> Tuple[str, str]
    def get_memory_service_config(self) -> dict

def initialize_mcp_environment() -> MCPConfig:
    """Main initialization entry point"""
```

**Benefits:**
- Centralized path management
- Automatic directory creation
- Easy testing with custom root paths
- Clean separation from business logic

## Testing the Agentic Flow

### Demo Script
```bash
python examples/agentic_flow_demo.py
```

### Claude Desktop
See [examples/claude_desktop_usage.md](../examples/claude_desktop_usage.md)

### Manual Testing
```python
from services.memory_service import MemoryService

service = MemoryService()

# Add test memory
service.add_text_memory(
    text="Morning jog on October 15, 2025",
    tags="exercise, routine"
)

# Synthesize
result = service.synthesize_memories(
    query="activities",
    start_date="2025-10-15"
)

print(result.timeline)
```

## Extension Points

### Adding New Tools
1. Create handler in `handlers.py`:
```python
class NewToolHandler(ToolHandler):
    def handle(self, arguments: Dict) -> List[TextContent]:
        # Implementation
```

2. Register in `ToolRegistry.__init__`:
```python
self.handlers["new_tool"] = NewToolHandler(memory_service, formatter)
```

3. Add tool definition in `server.py`:
```python
Tool(
    name="new_tool",
    description="...",
    inputSchema={...}
)
```

### Adding New Memory Types
1. Create loader in `etl/data_loaders/`
2. Add to `MemoryService.__init__`
3. Create specialized search method
4. Update synthesis logic

### Enhancing Date Parsing
Edit `MemoryService._extract_date_from_text()`:
```python
date_patterns = [
    r'pattern1',
    r'pattern2',
    # Add new patterns
]
```

## Performance Considerations

- **Embedding Cache**: Loaders cache model instances
- **Batch Processing**: ChromaDB handles batch searches efficiently
- **Timeline Creation**: O(n log n) sorting, negligible for typical use
- **Date Filtering**: In-memory filtering after search (future: DB-level)

## Future Enhancements

1. **Relationship Tracking**: Link related memories
2. **Semantic Clustering**: Group similar memories automatically
3. **Multi-hop Reasoning**: Chain multiple tool calls
4. **Memory Summarization**: LLM-based memory compression
5. **Export Formats**: JSON, Markdown timeline exports
