# Documentation Index

This directory contains comprehensive architectural documentation for the memory-map-app project.

---

## 📚 Available Documents

### 1. [Architecture Alternatives](architecture_alternatives.md)
**Complete guide to alternative architectural patterns**

Covers 6 major architectural patterns:
- ✅ Service Layer (Current Implementation)
- Repository Pattern
- Domain-Driven Design (DDD)
- Clean Architecture (Hexagonal/Onion)
- Feature-Based (Vertical Slice)
- CQRS (Command Query Responsibility Segregation)
- Plugin/Adapter Architecture

**Includes:**
- Detailed explanations with diagrams
- Code examples for each pattern
- Pros and cons comparison
- When to use each pattern
- Comparison matrix
- Recommendations for your project

**Read this if:** You want to understand why we chose Service Layer and what alternatives exist.

---

### 2. [Migration Examples](migration_examples.md)
**Practical examples of migrating to alternative architectures**

Shows step-by-step migrations:
- Adding Repository Pattern on top of Service Layer
- Migrating to Vertical Slice Architecture
- Implementing CQRS for analytics
- Real-world example: Adding Pinecone support

**Includes:**
- Complete code examples
- Decision tree for when to migrate
- Phase-by-phase migration strategy
- Non-breaking change approaches

**Read this if:** You need to extend the architecture or support new requirements.

---

## 🏗️ Current Architecture

### Service Layer Pattern

```
┌─────────────────────────────────────────────────────┐
│          Presentation Layer                          │
│  ┌──────────────────┐    ┌────────────────────────┐│
│  │  Streamlit App   │    │    MCP Server          ││
│  │  (app/main.py)   │    │  (mcp_server/server.py)││
│  └────────┬─────────┘    └──────────┬─────────────┘│
└───────────┼────────────────────────────┼─────────────┘
            │                            │
            │    ┌──────────────────┐   │
            └───►│  MemoryService   │◄──┘
                 │  (services/)     │
                 └────────┬─────────┘
┌────────────────────────┼───────────────────────────┐
│          Business Logic Layer                       │
│   - search_memories()                               │
│   - add_text_memory()                               │
│   - add_image_memory()                              │
│   - get_memory_stats()                              │
└─────────────────────────┼──────────────────────────┘
                          │
            ┌─────────────┴──────────────┐
            │                            │
    ┌───────▼────────┐          ┌───────▼────────┐
    │  Data Loaders  │          │   Vector DBs   │
    │   (etl/)       │          │    (db/)       │
    └────────────────┘          └────────────────┘
```

---

## 🎯 Quick Reference

### When to Use Each Pattern

| Need | Pattern | Read |
|------|---------|------|
| Multiple databases | Repository | [Alternatives](architecture_alternatives.md#1-repository-pattern) |
| Complex business domain | DDD | [Alternatives](architecture_alternatives.md#2-domain-driven-design-ddd) |
| Framework independence | Clean Architecture | [Alternatives](architecture_alternatives.md#3-clean-architecture-hexagonalonion) |
| Independent features | Vertical Slice | [Alternatives](architecture_alternatives.md#4-feature-based-vertical-slice-architecture) |
| Separate read/write | CQRS | [Alternatives](architecture_alternatives.md#5-cqrs-command-query-responsibility-segregation) |
| Extensible platform | Plugin | [Alternatives](architecture_alternatives.md#6-pluginadapter-architecture) |

### Migration Path

```
Service Layer (Current)
    ↓ (Add multiple DB support)
Repository Pattern
    ↓ (Add complex business rules)
Domain-Driven Design
    ↓ (Need framework independence)
Clean Architecture
```

See [Migration Examples](migration_examples.md) for detailed steps.

---

## 📖 Related Documentation

- **Main Architecture Doc**: [../ARCHITECTURE.md](../ARCHITECTURE.md)
  - Service Layer implementation details
  - Code comparison before/after
  - Benefits and best practices

- **Project README**: [../README.md](../README.md)
  - Technology stack
  - Setup instructions
  - Usage guide

---

## 🚀 Quick Start for New Developers

1. **Understand Current Architecture**
   - Read [../ARCHITECTURE.md](../ARCHITECTURE.md)
   - Review `services/memory_service.py`
   - See how `app/main.py` and `mcp_server/server.py` use the service

2. **Learn About Alternatives**
   - Browse [architecture_alternatives.md](architecture_alternatives.md)
   - Understand why Service Layer was chosen

3. **Plan Future Changes**
   - Check [migration_examples.md](migration_examples.md)
   - Use decision tree to determine if architecture needs to evolve

---

## 💡 Key Principles

### 1. **YAGNI (You Aren't Gonna Need It)**
Don't implement patterns you don't need yet. Service Layer is appropriate for current scale.

### 2. **Evolve Gradually**
Add complexity only when requirements demand it. Migrate incrementally.

### 3. **Measure Before Changing**
Identify real pain points (performance, maintainability) before refactoring.

### 4. **Keep It Simple**
The best architecture is the simplest one that meets requirements.

---

## 📝 Contributing to Documentation

When adding new architectural patterns or examples:

1. **Update this README** with a new section
2. **Add comparison** to existing patterns
3. **Include code examples** showing actual implementation
4. **Explain trade-offs** clearly
5. **Provide decision criteria** for when to use it

---

## 🔗 External Resources

### Service Layer Pattern
- [Martin Fowler - Service Layer](https://martinfowler.com/eaaCatalog/serviceLayer.html)
- [Microsoft - Service Layer Pattern](https://docs.microsoft.com/en-us/previous-versions/msp-n-p/ee658090(v=pandp.10))

### Repository Pattern
- [Martin Fowler - Repository](https://martinfowler.com/eaaCatalog/repository.html)
- [Repository Pattern in Python](https://www.cosmicpython.com/book/chapter_02_repository.html)

### Domain-Driven Design
- [Domain-Driven Design by Eric Evans](https://www.domainlanguage.com/ddd/)
- [DDD Quickly](https://www.infoq.com/minibooks/domain-driven-design-quickly/)

### Clean Architecture
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)

### CQRS & Event Sourcing
- [CQRS by Greg Young](https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf)
- [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html)

---

## 📊 Architecture Decision Records (ADRs)

### ADR-001: Chose Service Layer over Clean Architecture
**Date:** 2025-10-17
**Status:** Accepted
**Context:** Need to eliminate code duplication between MCP server and Streamlit app
**Decision:** Implement Service Layer pattern
**Consequences:**
- ✅ Eliminates ~400 lines of duplicate code
- ✅ Easy for team to understand and maintain
- ✅ Can evolve to more complex patterns if needed
- ⚠️ Less flexible than Clean Architecture
- ⚠️ Tightly coupled to ChromaDB (acceptable for now)

### ADR-002: Used Dataclasses for DTOs
**Date:** 2025-10-17
**Status:** Accepted
**Context:** Need structured responses from service layer
**Decision:** Use Python `@dataclass` for DTOs (MemoryStats, SearchResult)
**Consequences:**
- ✅ Type safety and IDE support
- ✅ Immutability with `frozen=True`
- ✅ Clean, readable code
- ✅ Easy to extend
- ⚠️ Slightly more verbose than dicts

---

## ❓ FAQ

### Q: Why not use Clean Architecture from the start?
**A:** Clean Architecture adds significant complexity. Service Layer provides enough separation for current needs while keeping the codebase simple and maintainable.

### Q: When should we migrate to a more complex architecture?
**A:** Migrate when you encounter real pain points:
- Multiple databases needed → Repository Pattern
- Complex business rules → Domain-Driven Design
- Need framework independence → Clean Architecture
- Independent features → Vertical Slices

### Q: Can we mix architectural patterns?
**A:** Yes! Patterns can be combined. For example, you can use Service Layer + Repository Pattern together.

### Q: How do we keep architecture documentation up to date?
**A:**
1. Update docs when making architectural changes
2. Include architecture review in PR process
3. Update ADRs when making significant decisions
4. Review docs quarterly

---

## 📅 Last Updated

**Date:** 2025-10-17
**Version:** 1.0
**Author:** Claude Code assisted development
**Status:** Current implementation documented

---

## 🤝 Questions?

If you have questions about the architecture:
1. Check the [comparison matrix](architecture_alternatives.md#comparison-matrix)
2. Review [migration examples](migration_examples.md)
3. Open an issue with specific questions
4. Discuss in team architecture meetings

Remember: **Good architecture serves the code, not the other way around!**
