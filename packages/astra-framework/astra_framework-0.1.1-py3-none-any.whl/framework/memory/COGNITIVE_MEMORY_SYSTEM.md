# Astra Cognitive Memory System (CMS) - Implementation Plan & Architecture

## Executive Summary

This document outlines the architecture and implementation plan for Astra's **Cognitive Memory System (CMS)** - a next-generation memory layer designed to surpass both Mastra and Agno in capability, scalability, and developer experience. Rather than copying existing frameworks, we design from first principles inspired by cognitive science.

**Status**: 📋 Planning Phase  
**Target**: Enterprise-ready memory system with 4-tier architecture  
**Timeline**: Phased implementation (Phase 1A → 1B → 1C → Future phases)

---

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Memory Architecture Overview](#memory-architecture-overview)
3. [Four Memory Tiers](#four-memory-tiers)
4. [Implementation Plan](#implementation-plan)
5. [Comparison with Competitors](#comparison-with-competitors)
6. [Enterprise Features](#enterprise-features)
7. [File Structure](#file-structure)
8. [Verification & Testing](#verification--testing)
9. [Open Questions & Decisions](#open-questions--decisions)

---

## Current State Analysis

### ✅ What Exists Today

#### 1. Basic Conversation Buffer

**Location**: `packages/framework/src/framework/memory/`

- **`AgentMemory`**: Configuration class for short-term memory

  - `num_history_responses`: Number of recent messages (default: 10)
  - `add_history_to_messages`: Enable/disable history
  - `create_session_summary`: Optional summarization
  - `summary_prompt`: Custom summarization prompt

- **`MemoryManager`**: Manages conversation context
  - Retrieves recent messages via `AgentStorage`
  - Implements sliding window (2x `num_history_responses` for user+assistant pairs)
  - Basic summarization support (generates summary when messages exceed window)
  - Summary caching by `thread_id`

**Limitations**:

- ❌ No token-aware windowing (only message count)
- ❌ No message importance scoring
- ❌ No selective retention
- ❌ Summarization is basic (no overflow handling)

#### 2. Storage Infrastructure

**Location**: `packages/framework/src/framework/storage/`

- **`AgentStorage`**: High-level storage interface
  - Thread management (`ThreadStore`)
  - Message persistence (`MessageStore`)
  - Batch operations with `SaveQueueManager`
  - Supports LibSQL backend

**Strengths**:

- ✅ Async-first design
- ✅ Queue-based batching for performance
- ✅ Clean abstraction over storage backends

#### 3. KnowledgeBase (RAG for Documents)

**Location**: `packages/framework/src/framework/KnowledgeBase/`

- **`KnowledgeBase`**: Document-based RAG system
  - Vector storage (LanceDB support)
  - Embedders (HuggingFace, OpenAI)
  - Chunking strategies (Recursive)
  - Content management (add, search, delete)

**Note**: This is for **document knowledge bases**, not conversation memory. However, the infrastructure (vector DB, embedders) can be reused for Semantic Memory.

### ❌ What's Missing

1. **Persistent Facts** - No long-term declarative memory for user preferences, facts, state
2. **Semantic Memory** - No vector-based retrieval of past conversations by meaning
3. **Experience Memory** - No episodic memory for significant events/experiences
4. **Unified Interface** - No single `MemorySystem` that orchestrates all tiers
5. **Memory Processors** - No LLM-based extraction, consolidation, or decay
6. **Enterprise Features** - No multi-tenancy, RBAC, audit logging, GDPR support

---

## Memory Architecture Overview

### Design Principles

1. **Unified Interface**: Single `MemorySystem` class for all memory tiers
2. **Pluggable Backends**: Support multiple storage providers (SQLite, PostgreSQL, Redis, LanceDB)
3. **Scope Hierarchy**: Memory scoped by `user > session > agent > turn`
4. **Intelligent Management**: LLM-based extraction, consolidation, and decay
5. **Enterprise-Ready**: Multi-tenancy, encryption, audit logs, RBAC
6. **Fast & Observable**: Async everywhere, comprehensive tracing/logging

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Runtime                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            MemorySystem (Unified Interface)          │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│        ┌─────────────────┼─────────────────┐                │
│        │                 │                 │                 │
│  ┌─────▼─────┐  ┌────────▼────────┐  ┌─────▼─────┐         │
│  │Conversation│  │ PersistentFacts│  │ Semantic  │         │
│  │  Buffer    │  │                │  │  Memory   │         │
│  └────────────┘  └────────────────┘  └───────────┘         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          ExperienceMemory (Episodic)                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐
│   Memory     │  │   Memory      │  │   Memory     │
│ Processors   │  │  Backends     │  │  Backends    │
│              │  │               │  │              │
│ • Fact       │  │ • SQLite      │  │ • LanceDB    │
│   Extractor  │  │ • PostgreSQL  │  │ • Redis      │
│ • Event      │  │               │  │              │
│   Detector   │  │               │  │              │
│ • Consolidator│ │               │  │              │
│ • Decay      │  │               │  │              │
│   Manager    │  │               │  │              │
└──────────────┘  └───────────────┘  └──────────────┘
```

---

## Four Memory Tiers

### Tier 1: Conversation Buffer (Short-Term Memory)

**Human Analog**: Working memory - what you're actively thinking about right now.

**Current Implementation**: ✅ Basic (via `AgentMemory.num_history_responses`)

**Purpose**: Maintains immediate conversational context within the current session.

**Enhanced Features** (beyond current):

- ✅ Auto-summarization of overflow messages
- ✅ Token-aware windowing (not just message count)
- ✅ Message importance scoring
- ✅ Selective retention (keep important messages longer)

**Proposed Interface**:

```python
class ConversationBuffer:
    """Immediate context within current session."""

    window_size: int = 20          # Number of turns to keep
    token_limit: int | None = None # Optional token-based limit
    include_system: bool = True     # Include system messages
    summarize_overflow: bool = True    # Summarize when exceeding window
    summary_model: str | None       # Model for summarization
    importance_scoring: bool = True # Score messages by importance
```

**Operations**:

- `get_context(thread_id, limit)` - Retrieve recent messages
- `add_message(message)` - Add new message
- `summarize_overflow()` - Summarize old messages
- `prune()` - Remove old messages

---

### Tier 2: Persistent Facts (Long-Term Declarative Memory)

**Human Analog**: Semantic memory - facts you know (capitals, names, preferences).

**Current Implementation**: ❌ Not implemented

**Purpose**: Stores user preferences, learned facts, agent state, and structured data that persists across sessions.

**Characteristics**:

- Persistent (survives restarts)
- Structured or semi-structured (JSON, schemas)
- User-scoped or agent-scoped
- Updateable (facts can be corrected/updated)

**Example Facts**:

- "User prefers dark mode"
- "User's timezone is IST"
- "User's name is Himanshu"
- "Agent last completed task: product launch"

**Proposed Interface**:

```python
class PersistentFacts:
    """Long-term declarative memory for facts and preferences."""

    scope: MemoryScope  # USER | SESSION | AGENT | GLOBAL
    schema: type[BaseModel] | None  # Optional Pydantic schema
    auto_extract: bool = True       # Auto-extract facts from conversations
    extraction_model: str | None    # Model for fact extraction
```

**Operations**:

- `add(key, value, scope)` - Add a new fact
- `update(key, value)` - Update existing fact
- `delete(key)` - Remove a fact
- `get(key)` - Retrieve a fact
- `search(query)` - Search facts by keyword
- `extract_from_messages(messages)` - LLM extracts facts from conversation

**Intelligent Updates** (like Mem0):

- `ADD`: New fact detected
- `UPDATE`: Existing fact modified
- `DELETE`: Contradicting information received
- `NOOP`: No change needed

**Storage**: SQLite/PostgreSQL backend with JSON columns for flexible schemas.

---

### Tier 3: Semantic Memory (Long-Term Associative Memory)

**Human Analog**: Associative memory - recalling related concepts by meaning.

**Current Implementation**: ❌ Not implemented (KnowledgeBase exists for RAG but not for conversation memory)

**Purpose**: Uses vector embeddings to retrieve contextually relevant information from past conversations, documents, and knowledge bases based on semantic similarity rather than exact match.

**Characteristics**:

- Vector-based storage (embeddings)
- Similarity search (cosine, dot product)
- Scales to millions of memories
- Retrieves by meaning, not keywords

**Example**: When user asks about "deployment issues", system retrieves past conversations about "CI/CD problems", "server crashes", "production bugs" even if those exact words weren't mentioned.

**Proposed Interface**:

```python
class SemanticMemory:
    """Vector-based associative memory for semantic recall."""

    embedder: Embedder              # Embedding model
    vector_store: VectorStore       # Vector database
    top_k: int = 5                  # Number of results to retrieve
    similarity_threshold: float = 0.7
    index_conversations: bool = True  # Auto-index conversations
    index_facts: bool = True          # Index persistent facts too
```

**Operations**:

- `embed_and_store(content, metadata)` - Store with embedding
- `search(query, filters)` - Semantic similarity search
- `get_relevant_context(query)` - Get relevant memories for a query
- `reindex()` - Rebuild embeddings

**Storage**: LanceDB (existing), with support for Pinecone, Weaviate, etc.

**Reuse**: Can leverage existing `KnowledgeBase` infrastructure (embedders, vector DB).

---

### Tier 4: Experience Memory (Episodic Memory)

**Human Analog**: Autobiographical memory - remembering specific events/experiences.

**Current Implementation**: ❌ Not implemented

**Purpose**: Records significant agent experiences as contextual snapshots, enabling learning from past interactions.

**Why Not Mem0?**: Mem0 provides a turnkey solution, but for enterprise-ready framework, we should own the memory layer:

- No external API calls (local event extraction via LLM)
- No vendor lock-in (pluggable storage backends)
- Full control over event schemas
- Data privacy (all data stays in your infra)
- Cost efficiency (one-time compute vs per-API-call)

**Event Model**:

```python
class Experience(BaseModel):
    """A single episodic memory entry."""

    id: str
    timestamp: datetime
    event_type: str                 # success | failure | milestone | insight
    description: str                # What happened
    context: dict                   # State at the time
    outcome: str | None             # Result of the event
    significance: float             # 0.0 to 1.0 importance score
    decay_rate: float = 0.01       # How fast it loses relevance
    tags: list[str] = []
```

**Proposed Interface**:

```python
class ExperienceMemory:
    """Event-based autobiographical memory."""

    auto_detect: bool = True        # Auto-detect significant events
    detection_model: str | None     # LLM for event detection
    significance_threshold: float = 0.5
    max_experiences: int = 1000    # Max stored experiences
    decay_enabled: bool = True     # Enable time-based decay
```

**Event Types**:

- `success`: Task completed successfully
- `failure`: Error or failed attempt
- `milestone`: Significant achievement
- `insight`: Learned preference or pattern
- `correction`: User corrected agent behavior

**Operations**:

- `record(event)` - Record a new experience
- `recall(query, filters)` - Find relevant experiences
- `get_patterns()` - Identify recurring patterns
- `apply_decay()` - Reduce significance over time
- `prune()` - Remove low-significance old experiences

**Example Events**:

- "User got frustrated when response was too long - prefer concise answers"
- "Tool call failed on 2024-12-25 due to API timeout - retry worked"
- "User successfully completed onboarding in 3 steps"

---

## Unified Memory System

### MemoryConfig

```python
class MemoryConfig(BaseModel):
    """Configuration for the cognitive memory system."""

    # Tier 1: Conversation Buffer
    buffer_window_size: int = 20
    buffer_summarize_overflow: bool = True

    # Tier 2: Persistent Facts
    facts_enabled: bool = True
    facts_auto_extract: bool = True
    facts_scope: MemoryScope = MemoryScope.USER

    # Tier 3: Semantic Memory
    semantic_enabled: bool = True
    semantic_embedder: Embedder | None = None
    semantic_top_k: int = 5

    # Tier 4: Experience Memory
    experience_enabled: bool = True
    experience_auto_detect: bool = True
    experience_decay_enabled: bool = True

    # Storage
    storage_backend: StorageBackend = StorageBackend.SQLITE
    vector_backend: VectorBackend = VectorBackend.LANCEDB
```

### MemorySystem (Unified Interface)

```python
class MemorySystem:
    """Unified cognitive memory system for Astra agents."""

    def __init__(self, config: MemoryConfig):
        self.buffer = ConversationBuffer(...)
        self.facts = PersistentFacts(...)
        self.semantic = SemanticMemory(...)
        self.experience = ExperienceMemory(...)

    async def get_context(self, query: str, scope: MemoryScope) -> MemoryContext:
        """Retrieve relevant context from all memory tiers."""
        context = MemoryContext()

        # Get recent conversation
        context.buffer = await self.buffer.get_context(scope.thread_id)

        # Get relevant facts
        context.facts = await self.facts.search(query, scope)

        # Get semantically similar memories
        context.semantic = await self.semantic.search(query, scope)

        # Get relevant experiences
        context.experiences = await self.experience.recall(query, scope)

        return context

    async def process_turn(self, messages: list, outcome: TurnOutcome):
        """Process a conversation turn across all memory tiers."""
        # Update buffer
        await self.buffer.add_messages(messages)

        # Extract facts (if enabled)
        if self.config.facts_auto_extract:
            facts = await self.facts.extract_from_messages(messages)
            await self.facts.update(facts)

        # Index in semantic memory (if enabled)
        if self.config.semantic_enabled:
            await self.semantic.embed_and_store(messages)

        # Detect significant events (if enabled)
        if self.config.experience_auto_detect:
            events = await self.experience.detect_events(messages, outcome)
            for event in events:
                await self.experience.record(event)

    async def consolidate(self):
        """Run memory consolidation (summarization, dedup, decay)."""
        await self.buffer.summarize_overflow()
        await self.facts.deduplicate()
        await self.experience.apply_decay()
        await self.experience.prune()
```

---

## Enterprise Features

Beyond the 4 memory tiers, enterprise-ready memory systems need:

### 1. Multi-Tenancy

```python
class TenantConfig:
    tenant_id: str
    isolation_level: str  # "logical" | "physical"
    encryption_key: str | None
```

**Isolation Levels**:

- **Logical**: Shared database with tenant_id filtering
- **Physical**: Separate database per tenant

### 2. Access Control (RBAC)

```python
class MemoryPermission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

class MemoryACL:
    resource_id: str
    principal: str  # user_id or role
    permissions: list[MemoryPermission]
```

### 3. Audit Logging

```python
class MemoryAuditLog:
    timestamp: datetime
    action: str  # read | write | delete | search
    resource_type: str
    resource_id: str
    actor: str
    details: dict
```

### 4. Encryption at Rest

- Field-level encryption for sensitive facts
- Key rotation support
- Bring-your-own-key (BYOK)

### 5. Memory Quotas & Limits

```python
class MemoryQuota:
    max_facts: int = 10000
    max_experiences: int = 5000
    max_vector_entries: int = 100000
    max_storage_mb: int = 1000
```

### 6. Export/Import (GDPR Compliance)

```python
async def export_user_memory(user_id: str) -> MemoryExport:
    """Export all memory for a user (GDPR right to data portability)."""

async def delete_user_memory(user_id: str) -> bool:
    """Delete all memory for a user (GDPR right to be forgotten)."""
```

### 7. Observability

- Memory operation metrics (latency, throughput)
- Storage utilization dashboards
- Anomaly detection (unusual memory patterns)

---

## File Structure

```
packages/framework/src/framework/memory/
├── __init__.py
├── system.py              # MemorySystem (unified interface)
├── config.py              # MemoryConfig, MemoryScope, StorageBackend
├── types.py               # Common types, Experience, Fact, MemoryContext
│
├── tiers/
│   ├── __init__.py
│   ├── buffer.py          # ConversationBuffer (enhanced)
│   ├── facts.py           # PersistentFacts
│   ├── semantic.py        # SemanticMemory
│   └── experience.py      # ExperienceMemory
│
├── processors/
│   ├── __init__.py
│   ├── fact_extractor.py  # LLM-based fact extraction
│   ├── event_detector.py  # LLM-based event detection
│   ├── consolidator.py    # Memory consolidation
│   └── decay.py           # Time-based decay manager
│
├── backends/
│   ├── __init__.py
│   ├── base.py            # Abstract backend interfaces
│   ├── sqlite.py          # SQLite backend (facts, experiences)
│   ├── postgres.py        # PostgreSQL backend (facts, experiences)
│   ├── redis.py           # Redis backend (for buffer)
│   └── lancedb.py         # LanceDB backend (vectors) - reuse existing
│
└── enterprise/
    ├── __init__.py
    ├── multitenancy.py    # Tenant isolation
    ├── acl.py             # Access control
    ├── audit.py           # Audit logging
    ├── encryption.py      # Field-level encryption
    └── gdpr.py            # Export/delete operations
```

**Integration Points**:

- Reuse `KnowledgeBase/vectordb/lancedb.py` for Semantic Memory
- Reuse `KnowledgeBase/embedders/` for embeddings
- Extend `storage/` for Persistent Facts backend
- Enhance `memory/manager.py` → `tiers/buffer.py`

---

## Implementation Plan

### Phase 1A: Core Foundation (Current PR)

**Goal**: Basic memory system with enhanced buffer and persistent facts.

**Deliverables**:

1. ✅ `MemoryConfig` and `MemoryScope` enums
2. ✅ Enhanced `ConversationBuffer` (token-aware, importance scoring)
3. ✅ `PersistentFacts` with SQLite backend
4. ✅ Basic fact extraction (LLM-based)
5. ✅ Integration with existing `Agent` class
6. ✅ Basic examples and unit tests

**Files to Create**:

- `memory/config.py`
- `memory/types.py`
- `memory/tiers/buffer.py` (enhance existing)
- `memory/tiers/facts.py`
- `memory/processors/fact_extractor.py`
- `memory/backends/sqlite.py`

**Files to Modify**:

- `memory/memory.py` → Deprecate in favor of `MemoryConfig`
- `memory/manager.py` → Refactor to use `ConversationBuffer`
- `agents/agent.py` → Integrate `MemorySystem`

**Estimated Effort**: 2-3 weeks

---

### Phase 1B: Semantic & Experience (Next PR)

**Goal**: Complete 4-tier memory system with intelligent processors.

**Deliverables**:

1. ✅ `SemanticMemory` with LanceDB (reuse existing infrastructure)
2. ✅ `ExperienceMemory` with event detection
3. ✅ `MemorySystem` unified interface
4. ✅ Memory processors (extraction, consolidation, decay)
5. ✅ Integration examples
6. ✅ Comprehensive tests

**Files to Create**:

- `memory/tiers/semantic.py`
- `memory/tiers/experience.py`
- `memory/system.py`
- `memory/processors/event_detector.py`
- `memory/processors/consolidator.py`
- `memory/processors/decay.py`

**Files to Modify**:

- `memory/tiers/buffer.py` → Add summarization improvements
- `memory/tiers/facts.py` → Add intelligent updates

**Estimated Effort**: 3-4 weeks

---

### Phase 1C: Enterprise Features (Future PR)

**Goal**: Production-ready enterprise memory system.

**Deliverables**:

1. ✅ Multi-tenancy support
2. ✅ Access control (RBAC)
3. ✅ Audit logging
4. ✅ GDPR compliance (export/delete)
5. ✅ Encryption at rest
6. ✅ Memory quotas & limits
7. ✅ Observability integration

**Files to Create**:

- `memory/enterprise/multitenancy.py`
- `memory/enterprise/acl.py`
- `memory/enterprise/audit.py`
- `memory/enterprise/encryption.py`
- `memory/enterprise/gdpr.py`

**Estimated Effort**: 4-6 weeks

---

### Phase 2: Advanced Features (Future)

- Memory sharing between agents (team-level shared memory pools)
- Multimodal memory (images, audio, video)
- Memory graphs (knowledge graphs showing relationships)
- Conflict resolution (handle contradicting memories)

### Phase 3: Intelligence Layer (Future)

- Proactive memory (agent suggests based on memory)
- Memory synthesis (generate new insights from existing memories)
- Transfer learning (share learned patterns across similar users)
- Memory compression (intelligent lossy compression for old memories)

### Phase 4: Agentic Memory (Future)

- Self-directed memory (agent decides what to remember/forget)
- Memory goals (agent sets goals for what it wants to learn)
- Meta-memory (agent reasons about its own memory quality)
- Memory debugging (agent explains why it remembered something)

---

## Comparison with Competitors

| Feature                 | Astra CMS                             | Mastra             | Agno                        |
| ----------------------- | ------------------------------------- | ------------------ | --------------------------- |
| **Conversation Buffer** | ✅ Enhanced (token-aware, importance) | ✅ Basic           | ✅ Basic                    |
| **Persistent Facts**    | ✅ Scoped (USER/SESSION/AGENT/GLOBAL) | ✅ Working Memory  | ✅ User Memory              |
| **Semantic Memory**     | ✅ Native (conversation + documents)  | ✅ Semantic Recall | ✅ via RAG (documents only) |
| **Experience Memory**   | ✅ Native (event-based)               | ❌                 | ⚠️ Mem0 only (external)     |
| **Memory Processors**   | ✅ (extraction, consolidation, decay) | ✅                 | ❌                          |
| **Multi-Tenancy**       | ✅                                    | ❌                 | ❌                          |
| **RBAC**                | ✅                                    | ❌                 | ❌                          |
| **Audit Logging**       | ✅                                    | ❌                 | ❌                          |
| **GDPR Support**        | ✅                                    | ❌                 | ❌                          |
| **Memory Graphs**       | 🔮 Phase 2                            | ❌                 | ❌                          |
| **Multimodal**          | 🔮 Phase 2                            | ❌                 | ✅                          |
| **Agentic Memory**      | 🔮 Phase 4                            | ❌                 | ⚠️ Limited                  |

**Key Differentiators**:

1. **Native Experience Memory** - No external dependencies (unlike Agno's Mem0)
2. **Unified Interface** - Single `MemorySystem` for all tiers
3. **Enterprise-Ready** - Multi-tenancy, RBAC, audit, GDPR from the start
4. **Intelligent Processors** - LLM-based extraction, consolidation, decay
5. **Scope Hierarchy** - Fine-grained scoping (user > session > agent > turn)

---

## Verification & Testing

### Unit Tests

```bash
# Run all memory system tests
cd packages/framework
uv run pytest tests/memory/ -v
```

**Test Files**:

- `tests/memory/test_conversation_buffer.py` - Window management, summarization
- `tests/memory/test_persistent_facts.py` - CRUD, extraction, scoping
- `tests/memory/test_semantic_memory.py` - Embedding, search, relevance
- `tests/memory/test_experience_memory.py` - Event detection, decay, patterns
- `tests/memory/test_memory_system.py` - Integration of all tiers
- `tests/memory/test_processors.py` - Fact extraction, event detection, consolidation

### Integration Tests

```bash
# Test with real storage backends
uv run pytest tests/memory/integration/ -v --integration
```

**Integration Test Files**:

- `tests/memory/integration/test_sqlite_backend.py`
- `tests/memory/integration/test_lancedb_backend.py`
- `tests/memory/integration/test_memory_system_full.py`

### Example Verification

```bash
# Run memory examples
cd packages/framework
uv run python examples/memory/01_memory_config.py
uv run python examples/memory/02_persistent_facts.py
uv run python examples/memory/03_semantic_recall.py
uv run python examples/memory/04_experience_memory.py
uv run python examples/memory/05_full_memory_system.py
```

**Example Files to Create**:

- `examples/memory/01_memory_config.py` - Basic configuration
- `examples/memory/02_persistent_facts.py` - Fact extraction and retrieval
- `examples/memory/03_semantic_recall.py` - Semantic search across conversations
- `examples/memory/04_experience_memory.py` - Event detection and recall
- `examples/memory/05_full_memory_system.py` - Complete integration

---

## Open Questions & Decisions

### 1. Naming Convention

**Proposed Names**:

- `ConversationBuffer` (not "short-term")
- `PersistentFacts` (not "working memory")
- `SemanticMemory` (similar to others, but distinct implementation)
- `ExperienceMemory` (not "episodic" - more descriptive)

**Question**: Do you prefer these names or want to suggest alternatives?

**Recommendation**: ✅ **Approve** - Names are clear and descriptive.

---

### 2. Enterprise Features Scope

**Options**:

- **A) Part of core framework** (heavier but complete)
- **B) Optional add-on** (lighter core, paid enterprise tier)
- **C) Deferred to later phases**

**Recommendation**: **Option B** - Keep core lightweight, add enterprise features as optional plugins. This aligns with "Keep it SIMPLE" principle and allows faster Phase 1A/1B delivery.

**Rationale**:

- Most users don't need multi-tenancy/RBAC initially
- Can add enterprise features incrementally
- Maintains clean separation of concerns

---

### 3. Storage Backends Priority

**Initial Implementation**: SQLite + LanceDB

**Question**: Should we also prioritize:

- PostgreSQL support (enterprise standard)
- Redis support (high-performance buffer)
- Custom vector DB support (Pinecone, Weaviate, etc.)

**Recommendation**:

- **Phase 1A**: SQLite + LanceDB (sufficient for MVP)
- **Phase 1B**: Add PostgreSQL support (common enterprise requirement)
- **Phase 1C**: Add Redis for buffer (performance optimization)
- **Phase 2**: Add Pinecone/Weaviate support (via pluggable backends)

**Rationale**: Start simple, add backends based on demand.

---

### 4. Integration with Existing Agent Class

**Current**: `Agent` uses `AgentMemory` (basic config) and `MemoryManager`.

**Proposed**: `Agent` uses `MemorySystem` (unified interface).

**Migration Path**:

1. Keep `AgentMemory` for backward compatibility (deprecated)
2. Add `MemorySystem` as optional parameter
3. If `MemorySystem` provided, use it; else fall back to `MemoryManager`
4. In future version, make `MemorySystem` required

**Recommendation**: ✅ **Approve** - Gradual migration maintains backward compatibility.

---

### 5. Reuse of KnowledgeBase Infrastructure

**Question**: Should `SemanticMemory` reuse `KnowledgeBase` components?

**Recommendation**: ✅ **Yes** - Reuse embedders and vector DB infrastructure, but keep interfaces separate:

- `KnowledgeBase` → Document RAG (external knowledge)
- `SemanticMemory` → Conversation memory (agent memory)

**Rationale**: Avoid duplication, maintain clear separation of concerns.

---

## Implementation Checklist

### Phase 1A: Core Foundation

- [ ] Create `memory/config.py` with `MemoryConfig`, `MemoryScope`, `StorageBackend`
- [ ] Create `memory/types.py` with `MemoryContext`, `Fact`, `Experience` models
- [ ] Enhance `memory/tiers/buffer.py` (token-aware, importance scoring)
- [ ] Create `memory/tiers/facts.py` with SQLite backend
- [ ] Create `memory/processors/fact_extractor.py` (LLM-based extraction)
- [ ] Create `memory/backends/sqlite.py` for facts storage
- [ ] Refactor `memory/manager.py` to use `ConversationBuffer`
- [ ] Integrate `MemorySystem` into `agents/agent.py`
- [ ] Create example: `examples/memory/01_memory_config.py`
- [ ] Create example: `examples/memory/02_persistent_facts.py`
- [ ] Write unit tests for all components
- [ ] Update documentation

### Phase 1B: Semantic & Experience

- [ ] Create `memory/tiers/semantic.py` (reuse LanceDB infrastructure)
- [ ] Create `memory/tiers/experience.py` with event detection
- [ ] Create `memory/system.py` (unified interface)
- [ ] Create `memory/processors/event_detector.py`
- [ ] Create `memory/processors/consolidator.py`
- [ ] Create `memory/processors/decay.py`
- [ ] Create examples for semantic and experience memory
- [ ] Write integration tests
- [ ] Performance benchmarking

### Phase 1C: Enterprise Features

- [ ] Create `memory/enterprise/multitenancy.py`
- [ ] Create `memory/enterprise/acl.py`
- [ ] Create `memory/enterprise/audit.py`
- [ ] Create `memory/enterprise/encryption.py`
- [ ] Create `memory/enterprise/gdpr.py`
- [ ] Add PostgreSQL backend support
- [ ] Add Redis backend support
- [ ] Observability integration

---

## Conclusion

The Astra Cognitive Memory System (CMS) represents a significant advancement over existing frameworks by:

1. **Comprehensive Coverage**: All 4 memory tiers (buffer, facts, semantic, experience)
2. **Native Implementation**: No external dependencies (unlike Agno's Mem0)
3. **Enterprise-Ready**: Multi-tenancy, RBAC, audit, GDPR from the start
4. **Intelligent Processing**: LLM-based extraction, consolidation, decay
5. **Unified Interface**: Single `MemorySystem` for all memory operations
6. **Pluggable Architecture**: Support multiple storage backends

**Next Steps**:

1. Review and approve this plan
2. Start Phase 1A implementation
3. Iterate based on feedback

---

## References

- [Mastra Memory Documentation](https://docs.mastra.ai/memory/overview)
- [Agno Memory Documentation](https://docs.agno.com/basics/memory/overview)
- [Mem0 Documentation](https://docs.mem0.ai/) (for reference, not dependency)
- [Cognitive Science: Memory Types](https://en.wikipedia.org/wiki/Memory)

---

**Document Version**: 1.0  
**Last Updated**: 2024-12-26  
**Author**: Astra Framework Team
