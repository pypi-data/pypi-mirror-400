# Team Implementation Plan

## Overview

Implementation plan for Astra Teams with support for both sequential and parallel delegation patterns.

## Architecture

```
framework/team/
├── __init__.py              # Public API exports
└── team.py                  # Main Team class (all code here)
    ├── TeamMember dataclass
    ├── TeamExecutionContext dataclass
    ├── Team exceptions
    ├── DELEGATION_TOOL constant
    └── Team class with all methods
```

**Note**: All code consolidated into `team.py` to avoid small files. Only separate if a module grows >500 lines.

## Core Components

### 1. Team Class (`team.py`)

**Purpose**: Main team orchestrator, similar to Agent but for multi-agent coordination.

**Key Responsibilities**:

- Team initialization and validation
- Member management
- Execution orchestration (invoke/stream)
- Memory and storage integration
- Middleware and guardrail application

**Key Methods**:

- `__init__()` - Initialize team with members, model, config
- `invoke()` - Execute team with sequential/parallel delegation
- `stream()` - Stream team execution
- `_execute_team_run()` - Main execution orchestrator (large, well-commented)
- `_build_leader_system_prompt()` - Build system prompt with member info
- `_create_delegation_tool()` - Create delegation tool for leader

**Configuration**:

```python
class Team:
    # Required
    name: str
    model: Model
    members: list[TeamMember]

    # Core behavior
    instructions: str | None = None
    description: str | None = None
    id: str | None = None

    # Execution control
    allow_parallel: bool = False  # Enable parallel delegation
    max_parallel: int = 3  # Max concurrent delegations
    max_delegations: int = 10  # Safety limit
    timeout: float = 300.0  # Global timeout (seconds)
    member_timeout: float = 60.0  # Per-member timeout

    # Memory & Storage
    memory: AgentMemory | None = None
    storage: AgentStorage | None = None

    # Middleware & Guardrails
    input_middlewares: list[InputMiddleware] | None = None
    output_middlewares: list[OutputMiddleware] | None = None
    guardrails: dict[str, Any] | None = None
```

### 2. TeamMember (in `team.py`)

**Purpose**: Wrapper for agent with team-specific metadata.

```python
@dataclass
class TeamMember:
    id: str
    name: str
    description: str
    agent: Agent
    priority: int = 0  # For priority-based routing (future)
    enabled: bool = True  # Can disable members
```

### 3. TeamExecutionContext (in `team.py`)

**Purpose**: Track execution state throughout team run.

```python
@dataclass
class TeamExecutionContext:
    """Execution context for team runs."""
    run_id: str
    thread_id: str | None
    user_id: str | None
    start_time: float
    timeout: float
    max_delegations: int

    # Runtime state (thread-safe updates needed for parallel)
    delegation_count: int = 0
    delegations: list[dict[str, Any]] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)

    # Time tracking
    elapsed_time: float = 0.0

    def check_timeout(self) -> None:
        """Raise if timeout exceeded."""

    def check_delegation_limit(self) -> None:
        """Raise if max delegations exceeded."""
```

### 4. Delegation Tool (in `team.py`)

**Purpose**: Tool definition for leader LLM to delegate tasks.

```python
DELEGATION_TOOL = {
    "name": "delegate_task_to_member",
    "description": "Delegate a task to a team member...",
    "parameters": {
        "type": "object",
        "properties": {
            "member_id": {"type": "string", "description": "..."},
            "task": {"type": "string", "description": "..."},
        },
        "required": ["member_id", "task"]
    }
}
```

## Implementation Details

### Phase 1: Core Team Structure

#### 1.1 Team Initialization

- Validate members (non-empty, unique IDs)
- Validate model
- Build member lookup dict
- Lazy initialize context (like Agent)
- Build system prompt with member descriptions

#### 1.2 Member Management

- Store members as dict for O(1) lookup
- Validate member IDs during delegation
- Support member enable/disable

### Phase 2: Execution Flow

#### 2.1 Main Execution Method (`_execute_team_run`)

**Orchestrator function (max 100 lines)** that coordinates:

1. Pre-execution setup
2. Leader decision loop
3. Delegation execution
4. Post-execution cleanup

**Broken into smaller functions**:

- `_prepare_execution_context()` - Create context, load history
- `_build_leader_messages()` - Build messages for leader
- `_process_leader_response()` - Handle leader LLM response
- `_handle_delegation_tool_calls()` - Process delegation requests
- `_finalize_execution()` - Save to storage, apply middlewares

#### 2.2 Sequential Delegation

**Function: `_execute_sequential_delegations()` (max 100 lines)**

Handles one-by-one execution with result passing:

- Loop through delegations
- Execute each with timeout
- Pass result to next delegation
- Handle errors and retries

**Helper functions**:

- `_execute_single_delegation()` - Execute one delegation with timeout/retry
- `_format_delegation_result()` - Format result for next delegation

#### 2.3 Parallel Delegation

**Function: `_execute_parallel_delegations()` (max 100 lines)**

Handles concurrent execution with proper synchronization:

- Create async tasks for each delegation
- Execute with `asyncio.gather()` and timeout
- Aggregate results maintaining order
- Handle partial failures

**Helper functions**:

- `_create_delegation_tasks()` - Create async tasks for delegations
- `_aggregate_parallel_results()` - Combine results with error handling
- `_execute_single_delegation()` - Reused from sequential (thread-safe)

**Race Condition Prevention**:

- Use `asyncio.gather()` for safe parallel execution
- Each delegation task is independent (no shared mutable state)
- Context updates use atomic operations or locks if needed
- Storage writes are queued (AgentStorage handles concurrency)

### Phase 3: Memory Integration

#### 3.1 Conversation History

- Load history from `storage.get_history(thread_id)`
- Extract past delegations from history
- Add to leader's system prompt
- Help leader make better routing decisions

#### 3.2 Implementation

```python
async def _load_conversation_context(
    thread_id: str | None,
    storage: AgentStorage | None,
) -> list[dict[str, Any]]:
    """
    Load conversation history and extract delegation patterns.

    Returns:
        List of message dicts + delegation summary
    """
    if not storage or not thread_id:
        return []

    history = await storage.get_history(thread_id, limit=20)

    # Extract delegations from history
    delegations = self._extract_past_delegations(history)

    # Format for leader context
    return self._format_history_for_leader(history, delegations)
```

### Phase 4: Error Handling & Resilience

#### 4.1 Timeout Handling

- Global timeout for entire team run
- Per-member timeout for individual delegations
- Graceful timeout handling (return partial results)

#### 4.2 Retry Logic

- Exponential backoff for failed delegations
- Max retries per delegation
- Circuit breaker pattern (future)

#### 4.3 Error Aggregation

- Collect errors from parallel executions
- Return partial results when some members fail
- Log all errors for debugging

### Phase 5: Streaming Support

#### 5.1 Stream Method

- Stream leader decisions
- Stream delegation progress
- Stream member execution
- Stream final response

```python
async def stream(
    self,
    message: str,
    thread_id: str | None = None,
    **kwargs,
) -> AsyncIterator[str]:
    """
    Stream team execution with real-time updates.

    Yields:
        - Leader decision chunks
        - Delegation status updates
        - Member execution chunks
        - Final response chunks
    """
```

## File Structure

```
framework/team/
├── __init__.py
│   └── Exports: Team, TeamMember, TeamError, etc.
│
└── team.py (~800-1000 lines, all code consolidated)
    ├── Constants
    │   └── DELEGATION_TOOL
    │
    ├── Exceptions
    │   ├── TeamError
    │   ├── DelegationError
    │   ├── MemberNotFoundError
    │   └── TeamTimeoutError
    │
    ├── Dataclasses
    │   ├── TeamMember
    │   └── TeamExecutionContext
    │
    └── Team Class
        ├── __init__() - Initialization & validation
        ├── invoke() - Public API
        ├── stream() - Streaming API
        ├── _execute_team_run() - Main orchestrator (~80 lines)
        ├── _prepare_execution_context() - Setup (~60 lines)
        ├── _build_leader_messages() - Message building (~70 lines)
        ├── _process_leader_response() - Response handling (~80 lines)
        ├── _handle_delegation_tool_calls() - Delegation routing (~90 lines)
        ├── _execute_sequential_delegations() - Sequential execution (~90 lines)
        ├── _execute_parallel_delegations() - Parallel execution (~90 lines)
        ├── _execute_single_delegation() - Single delegation (~80 lines)
        ├── _build_leader_system_prompt() - Prompt building (~70 lines)
        ├── _load_conversation_context() - Memory loading (~80 lines)
        ├── _extract_past_delegations() - History parsing (~60 lines)
        ├── _finalize_execution() - Cleanup (~60 lines)
        └── Helper methods (validation, formatting, etc.)
```

**Function Size Rule**: Maximum 100 lines per function. Break down larger logic into separate functions.

## Implementation Order

1. **Foundation**

   - Create team.py file
   - Implement exceptions (TeamError, DelegationError, etc.)
   - Implement TeamMember dataclass
   - Implement TeamExecutionContext dataclass
   - Define DELEGATION_TOOL constant

2. **Core Team**

   - Implement Team.**init**() with validation
   - Implement \_validate_members() helper
   - Implement \_build_leader_system_prompt()
   - Implement \_create_delegation_tool()

3. **Sequential Execution**

   - Implement \_execute_team_run() orchestrator
   - Implement \_prepare_execution_context()
   - Implement \_build_leader_messages()
   - Implement \_process_leader_response()
   - Implement \_handle_delegation_tool_calls()
   - Implement \_execute_sequential_delegations()
   - Implement \_execute_single_delegation()
   - Implement invoke() public method

4. **Memory Integration**

   - Implement \_load_conversation_context()
   - Implement \_extract_past_delegations()
   - Integrate with storage in \_prepare_execution_context()

5. **Parallel Execution**

   - Implement \_execute_parallel_delegations()
   - Implement \_create_delegation_tasks()
   - Implement \_aggregate_parallel_results()
   - Add parallel/sequential routing in \_handle_delegation_tool_calls()

6. **Error Handling**

   - Add timeout handling in \_execute_single_delegation()
   - Add retry logic with exponential backoff
   - Add error aggregation in parallel execution
   - Update context checks (timeout, delegation limits)

7. **Streaming**

   - Implement stream() method
   - Stream leader decisions
   - Stream delegation progress
   - Stream member execution

8. **Polish**
   - Fix edge cases
   - Add documentation
   - Performance optimization
   - Code review and refactoring

## Code Style Guidelines

1. **Function Size**: Maximum 100 lines per function

   - Break down complex logic into separate functions
   - Each function should handle one clear responsibility
   - Use helper functions to separate entire logic blocks

2. **Comments**:

   - Explain WHY, not just WHAT
   - Document complex logic
   - Include examples in docstrings

3. **Type Hints**: Full type hints everywhere (following ruff rules)

4. **Error Messages**: Clear, actionable error messages

5. **Naming**:
   - Don't copy Agno names exactly
   - Use descriptive names
   - Follow Python conventions

## Race Conditions & Thread Safety

### Potential Race Conditions

1. **Parallel Delegation Execution**

   - **Issue**: Multiple members executing simultaneously, updating shared state
   - **Solution**: Each delegation task is independent, no shared mutable state
   - **Implementation**: Use `asyncio.gather()` which handles task isolation

2. **Context Updates (delegation_count, elapsed_time)**

   - **Issue**: Multiple parallel tasks updating context counters
   - **Solution**:
     - Use atomic operations (int increment is atomic in Python)
     - Or use `asyncio.Lock` if needed (unlikely for simple counters)
     - Update context after all delegations complete

3. **Storage Writes**

   - **Issue**: Concurrent writes to same thread_id
   - **Solution**: AgentStorage uses SaveQueueManager with batching, handles concurrency internally

4. **Member Lookup**
   - **Issue**: Concurrent access to members dict
   - **Solution**: Dict reads are thread-safe in Python (GIL), no writes during execution

### Thread Safety Strategy

- **Read-only operations**: Safe (dict lookups, reading agent configs)
- **State updates**: Use atomic operations or update after gather completes
- **Storage**: AgentStorage handles concurrency internally
- **No shared mutable state**: Each delegation task operates independently

### Implementation Notes

```python
# Safe: Each task is independent
async def _execute_parallel_delegations(...):
    tasks = [
        _execute_single_delegation(member, task, context)
        for member, task in delegations
    ]
    # gather() ensures isolation
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Update context AFTER all complete (no race condition)
    context.delegation_count += len(delegations)
    return results
```

## Function Breakdown (Max 100 Lines Each)

### Core Execution Functions

1. **`_execute_team_run()`** (~80 lines)

   - Orchestrates entire execution flow
   - Calls helper functions for each phase

2. **`_prepare_execution_context()`** (~60 lines)

   - Create execution context
   - Load conversation history
   - Apply input middlewares

3. **`_build_leader_messages()`** (~70 lines)

   - Build system prompt with members
   - Add conversation history
   - Format user message

4. **`_process_leader_response()`** (~80 lines)

   - Call leader LLM
   - Detect tool calls vs final response
   - Handle errors

5. **`_handle_delegation_tool_calls()`** (~90 lines)

   - Extract delegation requests
   - Validate member IDs
   - Route to sequential/parallel
   - Aggregate results

6. **`_execute_sequential_delegations()`** (~90 lines)

   - Loop through delegations
   - Execute one by one
   - Pass results between delegations

7. **`_execute_parallel_delegations()`** (~90 lines)

   - Create async tasks
   - Execute with gather
   - Handle errors and timeouts
   - Aggregate results

8. **`_execute_single_delegation()`** (~80 lines)
   - Execute one member agent
   - Handle timeout
   - Retry on failure
   - Return formatted result

### Helper Functions

9. **`_build_leader_system_prompt()`** (~70 lines)

   - Format member descriptions
   - Add instructions
   - Include delegation guidelines

10. **`_load_conversation_context()`** (~80 lines)

    - Load history from storage
    - Extract past delegations
    - Format for leader

11. **`_extract_past_delegations()`** (~60 lines)

    - Parse history messages
    - Find delegation patterns
    - Format summary

12. **`_finalize_execution()`** (~60 lines)

    - Apply output middlewares
    - Save to storage
    - Return final response

13. **`_validate_members()`** (~50 lines)

    - Check non-empty
    - Check unique IDs
    - Validate agent instances

14. **`_format_delegation_result()`** (~40 lines)
    - Format result for next delegation
    - Handle errors
    - Add metadata

## Edge Cases & Missing Scenarios

### 1. Leader Response Scenarios

**Case 1.1: Leader responds directly (no delegation)**

- **Scenario**: Leader LLM decides to answer directly without delegating
- **Handling**: Check if `response.tool_calls` is empty, return `response.content` as final answer
- **Implementation**: In `_process_leader_response()`, check for tool_calls before delegation

**Case 1.2: Leader makes invalid tool calls**

- **Scenario**: Tool call name is not "delegate_task_to_member"
- **Handling**: Log warning, ignore invalid tool calls, continue with valid ones
- **Implementation**: In `_handle_delegation_tool_calls()`, filter by tool name

**Case 1.3: Leader tool call has missing/invalid arguments**

- **Scenario**: `member_id` or `task` missing, or wrong types
- **Handling**: Validate arguments, return error to leader, let leader retry
- **Implementation**: In `_handle_delegation_tool_calls()`, validate each tool call

**Case 1.4: Leader makes multiple tool calls at once**

- **Scenario**: Leader delegates to multiple members simultaneously
- **Handling**:
  - If `allow_parallel=True`: Execute all in parallel
  - If `allow_parallel=False`: Execute sequentially
- **Implementation**: In `_handle_delegation_tool_calls()`, check parallel flag

### 2. Member Execution Scenarios

**Case 2.1: Member is disabled**

- **Scenario**: `member.enabled = False`
- **Handling**: Return error message to leader, suggest alternative member
- **Implementation**: In `_execute_single_delegation()`, check `member.enabled`

**Case 2.2: Member doesn't exist**

- **Scenario**: Leader requests non-existent `member_id`
- **Handling**: Return clear error with available member IDs
- **Implementation**: In `_handle_delegation_tool_calls()`, validate member_id exists

**Case 2.3: Member agent raises exception**

- **Scenario**: Member's `agent.invoke()` raises exception
- **Handling**: Catch exception, format error message, return to leader
- **Implementation**: In `_execute_single_delegation()`, wrap in try/except

**Case 2.4: Member returns empty response**

- **Scenario**: Member agent returns empty string
- **Handling**: Return placeholder message or let leader handle
- **Implementation**: In `_format_delegation_result()`, check for empty

**Case 2.5: Member agent has its own tools**

- **Scenario**: Member agent uses tools during execution
- **Handling**: This is fine, member executes independently
- **Implementation**: No special handling needed, member.agent.invoke() handles it

### 3. Parallel Execution Edge Cases

**Case 3.1: max_parallel > number of delegations**

- **Scenario**: Only 2 delegations but max_parallel=5
- **Handling**: Cap at actual number of delegations
- **Implementation**: In `_execute_parallel_delegations()`, use `min(len(delegations), max_parallel)`

**Case 3.2: Some succeed, some fail**

- **Scenario**: 3 parallel delegations, 2 succeed, 1 fails
- **Handling**: Aggregate successful results, include error for failed one
- **Implementation**: In `_aggregate_parallel_results()`, handle exceptions from gather

**Case 3.3: All fail in parallel**

- **Scenario**: All parallel delegations fail
- **Handling**: Return all errors to leader, let leader decide next action
- **Implementation**: In `_aggregate_parallel_results()`, format all errors

**Case 3.4: Timeout during parallel execution**

- **Scenario**: Parallel execution exceeds timeout
- **Handling**: Cancel remaining tasks, return partial results
- **Implementation**: Use `asyncio.wait_for()` with timeout, handle `asyncio.TimeoutError`

**Case 3.5: allow_parallel=True but max_parallel=1**

- **Scenario**: Parallel enabled but only 1 concurrent allowed
- **Handling**: This is effectively sequential, but still use parallel infrastructure
- **Implementation**: No special case needed, will naturally serialize

### 4. Storage & Memory Edge Cases

**Case 4.1: thread_id provided but storage is None**

- **Scenario**: User provides thread_id but team has no storage
- **Handling**: Ignore thread_id, proceed without history
- **Implementation**: In `_load_conversation_context()`, check storage first

**Case 4.2: storage.get_history() fails**

- **Scenario**: Storage throws exception when loading history
- **Handling**: Log error, continue without history (graceful degradation)
- **Implementation**: Wrap in try/except, return empty list on error

**Case 4.3: History is empty**

- **Scenario**: New thread, no history exists
- **Handling**: Return empty list, proceed normally
- **Implementation**: Already handled, empty list is valid

**Case 4.4: History extraction fails**

- **Scenario**: `_extract_past_delegations()` fails to parse history
- **Handling**: Return empty delegations list, continue with history only
- **Implementation**: Wrap in try/except, return empty on error

### 5. Configuration Validation Edge Cases

**Case 5.1: timeout < member_timeout**

- **Scenario**: Global timeout (60s) < member timeout (120s)
- **Handling**: Use min(timeout, member_timeout) for member, or validate in **init**
- **Implementation**: In `__init__()`, validate or auto-adjust

**Case 5.2: max_delegations=0**

- **Scenario**: User sets max_delegations to 0
- **Handling**: Validate in **init**, raise error or set to 1
- **Implementation**: In `_validate_config()`, check max_delegations > 0

**Case 5.3: Empty members list**

- **Scenario**: Team created with no members
- **Handling**: Validate in **init**, raise clear error
- **Implementation**: In `_validate_members()`, check len(members) > 0

**Case 5.4: Member with None agent**

- **Scenario**: TeamMember created with agent=None
- **Handling**: Validate in **init** or during delegation
- **Implementation**: In `_validate_members()`, check each member.agent is not None

### 6. Tool Call Validation Edge Cases

**Case 6.1: Tool call arguments not a dict**

- **Scenario**: `tool_call.arguments` is string instead of dict
- **Handling**: Try to parse JSON, or return error
- **Implementation**: In `_handle_delegation_tool_calls()`, validate and parse

**Case 6.2: Tool call missing required arguments**

- **Scenario**: `member_id` or `task` missing from arguments
- **Handling**: Return error message to leader
- **Implementation**: In `_handle_delegation_tool_calls()`, validate required fields

**Case 6.3: Tool call with wrong argument types**

- **Scenario**: `member_id` is not string, `task` is not string
- **Handling**: Validate types, return error if invalid
- **Implementation**: In `_handle_delegation_tool_calls()`, type check arguments

### 7. Streaming Edge Cases

**Case 7.1: Stream fails mid-execution**

- **Scenario**: Network error during streaming
- **Handling**: Catch exception, yield error message, close stream
- **Implementation**: In `stream()`, wrap in try/except

**Case 7.2: Member streaming fails**

- **Scenario**: Member agent.stream() raises exception
- **Handling**: Catch exception, yield error, continue with other members
- **Implementation**: In streaming delegation handler, catch and handle

**Case 7.3: Leader streaming fails**

- **Scenario**: Leader model.stream() raises exception
- **Handling**: Catch exception, yield error, close stream
- **Implementation**: In `stream()`, catch leader streaming errors

### 8. Retry & Timeout Edge Cases

**Case 8.1: Retry exhausts but member still fails**

- **Scenario**: Member fails after max retries
- **Handling**: Return error to leader, let leader decide
- **Implementation**: In `_execute_single_delegation()`, raise after retries

**Case 8.2: Timeout during retry**

- **Scenario**: Retry takes too long, exceeds member_timeout
- **Handling**: Cancel retry, return timeout error
- **Implementation**: Use `asyncio.wait_for()` around retry loop

**Case 8.3: Global timeout during delegation**

- **Scenario**: Team run exceeds global timeout
- **Handling**: Cancel all operations, return partial results
- **Implementation**: In `_execute_team_run()`, check timeout before each delegation

### 9. Middleware & Guardrail Edge Cases

**Case 9.1: Input middleware raises exception**

- **Scenario**: Middleware.process() raises exception
- **Handling**: Catch exception, log error, continue without middleware or abort
- **Implementation**: In `_prepare_execution_context()`, wrap middleware calls

**Case 9.2: Output middleware raises exception**

- **Scenario**: Output middleware fails during finalization
- **Handling**: Catch exception, log error, return response without middleware
- **Implementation**: In `_finalize_execution()`, wrap middleware calls

**Case 9.3: Guardrail blocks execution**

- **Scenario**: Input guardrail raises InputGuardrailError
- **Handling**: Abort execution, return error to user
- **Implementation**: In `_prepare_execution_context()`, let guardrail errors propagate

### 10. Infinite Loop Prevention

**Case 10.1: Leader keeps delegating in loop**

- **Scenario**: Leader never returns final response, keeps delegating
- **Handling**: Enforce max_delegations limit, abort after limit
- **Implementation**: In `_execute_team_run()`, check limit before each delegation

**Case 10.2: Leader delegates to same member repeatedly**

- **Scenario**: Leader keeps delegating to same member for same task
- **Handling**: Detect cycles, abort or return error
- **Implementation**: Track delegation history, detect repeated patterns (future enhancement)

### 11. Context & State Edge Cases

**Case 11.1: Context timeout check during parallel execution**

- **Scenario**: Multiple parallel tasks checking timeout simultaneously
- **Handling**: Use atomic time check, or check once before gather
- **Implementation**: Check timeout before creating parallel tasks

**Case 11.2: Storage write fails**

- **Scenario**: `storage.add_message()` fails
- **Handling**: Log error, continue execution (storage is not critical path)
- **Implementation**: Wrap storage calls in try/except, log and continue

### Implementation Checklist

Add these validations and handlers:

- [ ] Validate tool call format and arguments
- [ ] Handle disabled members
- [ ] Handle missing members
- [ ] Handle empty member responses
- [ ] Cap max_parallel to actual delegation count
- [ ] Aggregate partial results from parallel execution
- [ ] Handle storage failures gracefully
- [ ] Validate configuration in **init**
- [ ] Handle streaming failures
- [ ] Prevent infinite delegation loops
- [ ] Handle middleware exceptions
- [ ] Handle timeout during retries
- [ ] Check global timeout before each delegation

## Future Enhancements (Not in MVP)

1. Circuit breaker pattern
2. Priority-based routing
3. Dependency detection for parallel execution
4. Advanced memory (semantic recall)
5. Cost tracking
6. Observability integration
7. Delegation cycle detection
8. Smart retry strategies
