# MCP Integration Test Script

This document provides a comprehensive test script for a test agent to verify all Lodestar MCP features.

## Prerequisites

1. Lodestar repository is initialized (`.lodestar/` directory exists)
2. MCP server is running and connected
3. Agent has access to all `lodestar_*` MCP tools

---

## Phase 0: Test Fixture Setup

**Purpose**: Create test tasks that will be used throughout the test script.

### Test 0.1: Create Base Test Task

**Tool**: `lodestar_task_create`

**Parameters**:
```json
{
  "task_id": "MCP-BASE-001",
  "title": "Base Test Task - Ready",
  "description": "WHAT: A claimable task for testing MCP claim/complete workflow\nWHERE: MCP test suite\nWHY: Validate task lifecycle operations",
  "acceptance_criteria": ["Can be claimed", "Can be completed", "Can be verified"],
  "priority": 1,
  "status": "ready",
  "labels": ["test", "mcp", "fixture"],
  "locks": ["tests/mcp/**"]
}
```

**Expected Result**:
- Returns `ok: true`
- Returns `taskId: "MCP-BASE-001"`
- Task is claimable (status ready, no dependencies)

**Save**: Store `MCP-BASE-001` for use in claim/complete tests

### Test 0.2: Create Feature Test Tasks

**Tool**: `lodestar_task_create` (call 3 times)

**Task 1**:
```json
{
  "task_id": "MCP-FEAT-001",
  "title": "Feature Task - High Priority",
  "description": "High priority feature task for testing filtering",
  "priority": 2,
  "status": "ready",
  "labels": ["feature", "backend", "test"]
}
```

**Task 2**:
```json
{
  "task_id": "MCP-FEAT-002",
  "title": "Feature Task - Low Priority",
  "description": "Low priority feature task for testing filtering",
  "priority": 10,
  "status": "ready",
  "labels": ["feature", "frontend", "test"]
}
```

**Task 3**:
```json
{
  "task_id": "MCP-BUG-001",
  "title": "Bug Fix Task",
  "description": "Bug fix task for testing label filtering",
  "priority": 1,
  "status": "ready",
  "labels": ["bug", "critical", "test"]
}
```

**Expected Result**: All 3 tasks created successfully

### Test 0.3: Create Dependency Chain

**Tool**: `lodestar_task_create` (call 3 times)

**Task 1** (Parent):
```json
{
  "task_id": "MCP-DEP-001",
  "title": "Parent Task",
  "description": "Task that others depend on",
  "priority": 5,
  "status": "ready",
  "labels": ["test", "dependency"]
}
```

**Task 2** (Child - depends on parent):
```json
{
  "task_id": "MCP-DEP-002",
  "title": "Child Task",
  "description": "Task that depends on MCP-DEP-001",
  "priority": 6,
  "status": "ready",
  "depends_on": ["MCP-DEP-001"],
  "labels": ["test", "dependency"]
}
```

**Task 3** (Grandchild - depends on child):
```json
{
  "task_id": "MCP-DEP-003",
  "title": "Grandchild Task",
  "description": "Task that depends on MCP-DEP-002",
  "priority": 7,
  "status": "ready",
  "depends_on": ["MCP-DEP-002"],
  "labels": ["test", "dependency"]
}
```

**Expected Result**:
- All 3 tasks created
- Only `MCP-DEP-001` is claimable initially
- `MCP-DEP-002` and `MCP-DEP-003` are NOT claimable (dependencies not verified)

### Test 0.4: Create Task with Lock Patterns

**Tool**: `lodestar_task_create` (call 2 times)

**Task 1**:
```json
{
  "task_id": "MCP-LOCK-001",
  "title": "Task with Broad Lock",
  "description": "Task with src/** lock pattern",
  "priority": 8,
  "status": "ready",
  "labels": ["test", "locks"],
  "locks": ["src/**"]
}
```

**Task 2**:
```json
{
  "task_id": "MCP-LOCK-002",
  "title": "Task with Overlapping Lock",
  "description": "Task with overlapping lock pattern for conflict detection",
  "priority": 9,
  "status": "ready",
  "labels": ["test", "locks"],
  "locks": ["src/auth/**", "src/core/**"]
}
```

**Expected Result**: Both tasks created with lock patterns

### Test 0.5: Verify Test Fixtures

**Tool**: `lodestar_task_list`

**Expected Result**:
- At least 9 test tasks exist (MCP-BASE-001, MCP-FEAT-001/002, MCP-BUG-001, MCP-DEP-001/002/003, MCP-LOCK-001/002)
- All tasks have status `ready`
- Can filter by `label: "test"` to see all test fixtures

---

## Phase 1: Repository Status

### Test 1.1: Get Repository Status

**Tool**: `lodestar_repo_status`

**Expected Result**:
- Returns `repoRoot` path
- Returns `specPath` pointing to `.lodestar/spec.yaml`
- Returns `runtimePath` pointing to `.lodestar/runtime.sqlite`
- Returns `project` object with `name`
- Returns `counts` object with task and agent statistics
- Returns `suggestedNextActions` array

**Verify**:
```json
{
  "repoRoot": "<path>",
  "specPath": "<path>/.lodestar/spec.yaml",
  "runtimePath": "<path>/.lodestar/runtime.sqlite",
  "project": { "name": "..." },
  "counts": {
    "tasks": { "total": N, "byStatus": {...}, "claimable": N },
    "agents": { "registered": N, "activeLeases": N },
    "messages": { "total": N, "unread": N }
  },
  "suggestedNextActions": [...]
}
```

---

## Phase 2: Agent Lifecycle

### Test 2.1: Register Agent (Join)

**Tool**: `lodestar_agent_join`

**Parameters**:
```json
{
  "name": "MCP Test Agent",
  "client": "test-runner",
  "model": "test-model",
  "capabilities": ["testing", "mcp-validation"],
  "ttl_seconds": 900
}
```

**Expected Result**:
- Returns `agentId` (non-empty string)
- Returns `displayName` matching input name
- Returns `registeredAt` timestamp
- Returns `leaseDefaults` with `ttlSeconds`
- TTL should be clamped to 60-7200 range

**Save**: Store `agentId` for subsequent tests

### Test 2.2: List Agents

**Tool**: `lodestar_agent_list`

**Expected Result**:
- Returns array of agent objects
- Newly registered agent appears in the list
- Each agent has `agentId`, `displayName`, `status`, `lastSeen`

### Test 2.3: Agent Heartbeat

**Tool**: `lodestar_agent_heartbeat`

**Parameters**:
```json
{
  "agent_id": "<agentId from Test 2.1>"
}
```

**Expected Result**:
- Returns `agentId` matching input
- Returns updated `heartbeatAt` timestamp
- Agent status should be "active" when listed

### Test 2.4: Heartbeat with Invalid Agent ID

**Tool**: `lodestar_agent_heartbeat`

**Parameters**:
```json
{
  "agent_id": "NONEXISTENT-AGENT"
}
```

**Expected Result**:
- Returns error with `isError: true`
- Error code should be `AGENT_NOT_FOUND`

---

## Phase 3: Task Listing and Filtering

### Test 3.1: List All Tasks

**Tool**: `lodestar_task_list`

**Parameters**: (none - defaults)

**Expected Result**:
- Returns `items` array of task summaries
- Returns `count` (number of items returned)
- Returns `total` (total tasks in spec)
- By default excludes deleted tasks
- Tasks sorted by priority (lower first)

### Test 3.2: Filter by Status

**Tool**: `lodestar_task_list`

**Parameters**:
```json
{
  "status": "ready"
}
```

**Expected Result**:
- All returned tasks have `status: "ready"`

**Repeat for**: `done`, `verified`, `deleted`, `all`

### Test 3.3: Filter by Label

**Tool**: `lodestar_task_list`

**Parameters**:
```json
{
  "label": "feature"
}
```

**Expected Result**:
- All returned tasks have `"feature"` in their `labels` array

### Test 3.4: Pagination

**Tool**: `lodestar_task_list`

**Parameters**:
```json
{
  "limit": 2
}
```

**Expected Result**:
- Returns at most 2 items
- Returns `nextCursor` if more results exist

**Follow-up**:
```json
{
  "limit": 2,
  "cursor": "<nextCursor from previous>"
}
```

**Expected Result**:
- Returns next page of results starting after cursor

### Test 3.5: Combined Filters

**Tool**: `lodestar_task_list`

**Parameters**:
```json
{
  "status": "ready",
  "label": "feature",
  "limit": 5
}
```

**Expected Result**:
- All returned tasks are `ready` AND have `feature` label

---

## Phase 4: Task Details

### Test 4.1: Get Task Details

**Tool**: `lodestar_task_get`

**Parameters**:
```json
{
  "task_id": "<existing task ID>"
}
```

**Expected Result**:
- Returns full task object with:
  - `id`, `title`, `description`, `acceptanceCriteria`
  - `status`, `priority`, `labels`, `locks`
  - `createdAt`, `updatedAt` (ISO timestamps)
  - `dependencies` object: `dependsOn`, `dependents`, `isClaimable`
  - `prd` object (if task has PRD context)
  - `runtime` object: `claimed`, `claimedBy`
  - `warnings` array

### Test 4.2: Get Non-Existent Task

**Tool**: `lodestar_task_get`

**Parameters**:
```json
{
  "task_id": "NONEXISTENT-TASK"
}
```

**Expected Result**:
- Returns error with `isError: true`
- Error code: `TASK_NOT_FOUND`

### Test 4.3: Invalid Task ID

**Tool**: `lodestar_task_get`

**Parameters**:
```json
{
  "task_id": ""
}
```

**Expected Result**:
- Returns error with `isError: true`
- Error code: `INVALID_TASK_ID`

---

## Phase 5: Task Discovery

### Test 5.1: Get Next Claimable Tasks

**Tool**: `lodestar_task_next`

**Parameters**: (none - defaults)

**Expected Result**:
- Returns `candidates` array of claimable tasks
- Returns `rationale` explaining selection
- Returns `totalClaimable` count
- Only tasks with `status: ready` and all dependencies verified

### Test 5.2: Next Tasks with Label Filter

**Tool**: `lodestar_task_next`

**Parameters**:
```json
{
  "labels": ["feature", "bug"],
  "limit": 3
}
```

**Expected Result**:
- All candidates have at least one of the specified labels
- Returns at most 3 candidates
- Returns `filters` object in response

### Test 5.3: Next Tasks with Priority Filter

**Tool**: `lodestar_task_next`

**Parameters**:
```json
{
  "max_priority": 5
}
```

**Expected Result**:
- All candidates have `priority <= 5`
- Returns `filters` with `maxPriority: 5`

---

## Phase 6: Task Creation (CRUD)

### Test 6.1: Create Task with Minimal Fields

**Tool**: `lodestar_task_create` (if available) or use CLI

**Parameters**:
```json
{
  "title": "MCP Test Task - Minimal",
  "description": "A task created via MCP for testing"
}
```

**Expected Result**:
- Returns `ok: true`
- Returns auto-generated `taskId`
- Returns `status: "ready"` (default)
- Returns `priority: 100` (default)

**Save**: Store `taskId` for subsequent tests

### Test 6.2: Create Task with Full Fields

**Tool**: `lodestar_task_create`

**Parameters**:
```json
{
  "task_id": "MCP-TEST-001",
  "title": "MCP Full Test Task",
  "description": "WHAT: Test task creation\nWHERE: MCP\nWHY: Validate MCP functionality",
  "acceptance_criteria": ["Tool call succeeds", "Task appears in list"],
  "priority": 5,
  "status": "ready",
  "labels": ["test", "mcp"],
  "locks": ["tests/mcp/**"]
}
```

**Expected Result**:
- Returns `ok: true`
- Returns `taskId: "MCP-TEST-001"`
- All fields match input

### Test 6.3: Create Task with Dependencies

**Tool**: `lodestar_task_create`

**Parameters**:
```json
{
  "task_id": "MCP-TEST-002",
  "title": "MCP Dependent Task",
  "description": "Task that depends on MCP-TEST-001",
  "depends_on": ["MCP-TEST-001"],
  "priority": 10
}
```

**Expected Result**:
- Returns `ok: true`
- Task is NOT claimable (dependency not verified)

### Test 6.4: Create Task with Invalid Dependency

**Tool**: `lodestar_task_create`

**Parameters**:
```json
{
  "title": "Task with Bad Dependency",
  "depends_on": ["NONEXISTENT-TASK"]
}
```

**Expected Result**:
- Returns error
- Error indicates dependency doesn't exist

### Test 6.5: Update Task

**Tool**: `lodestar_task_update` (if available)

**Parameters**:
```json
{
  "task_id": "MCP-TEST-001",
  "title": "MCP Test Task (Updated)",
  "priority": 3,
  "add_labels": ["updated"],
  "remove_labels": ["test"]
}
```

**Expected Result**:
- Returns `ok: true`
- Returns `updatedFields` listing changed fields

### Test 6.6: Delete Task

**Tool**: `lodestar_task_delete` (if available)

**Note**: Test with a disposable task, not critical test tasks

**Parameters**:
```json
{
  "task_id": "MCP-TEST-002",
  "cascade": false
}
```

**Expected Result**:
- Returns `ok: true`
- Task status becomes `deleted`
- Task hidden from default list

---

## Phase 7: Task Claiming and Leases

### Test 7.1: Claim Task

**Tool**: `lodestar_task_claim`

**Use**: `MCP-BASE-001` from Phase 0 fixtures

**Parameters**:
```json
{
  "task_id": "MCP-BASE-001",
  "agent_id": "<agentId from Test 2.1>",
  "ttl_seconds": 900
}
```

**Expected Result**:
- Returns `ok: true`
- Returns `lease` object with:
  - `leaseId`, `taskId: "MCP-BASE-001"`, `agentId`
  - `expiresAt` timestamp
  - `ttlSeconds: 900`
  - `createdAt`
- `warnings` array (may contain lock conflicts)

**Save**: Store `leaseId` for subsequent tests

### Test 7.2: Claim with Unregistered Agent

**Tool**: `lodestar_task_claim`

**Use**: `MCP-FEAT-001` from Phase 0 fixtures

**Parameters**:
```json
{
  "task_id": "MCP-FEAT-001",
  "agent_id": "UNREGISTERED-AGENT"
}
```

**Expected Result**:
- Returns error with `isError: true`
- Error code: `AGENT_NOT_REGISTERED`

### Test 7.3: Claim Already-Claimed Task

**Tool**: `lodestar_task_claim`

**Use**: Try to re-claim `MCP-BASE-001` which is already claimed from Test 7.1

**Parameters**:
```json
{
  "task_id": "MCP-BASE-001",
  "agent_id": "<agentId from Test 2.1>"
}
```

**Expected Result**:
- Returns error
- Error code: `TASK_ALREADY_CLAIMED` (or similar)
- Error message mentions task is already claimed

### Test 7.4: Claim Non-Claimable Task (Dependencies)

**Tool**: `lodestar_task_claim`

**Use**: `MCP-DEP-002` from Phase 0 fixtures (depends on MCP-DEP-001 which is not verified)

**Parameters**:
```json
{
  "task_id": "MCP-DEP-002",
  "agent_id": "<agentId from Test 2.1>"
}
```

**Expected Result**:
- Returns error
- Error code: `TASK_NOT_CLAIMABLE`
- Error message explains dependencies not satisfied

### Test 7.5: Release Claimed Task

**Tool**: `lodestar_task_release`

**Use**: Release `MCP-BASE-001` claimed in Test 7.1

**Parameters**:
```json
{
  "task_id": "MCP-BASE-001",
  "agent_id": "<agentId from Test 2.1>",
  "reason": "Testing release functionality"
}
```

**Expected Result**:
- Returns success
- Task is no longer claimed
- Task can be claimed again

---

## Phase 8: Task Completion

### Test 8.1: Mark Task Done

**Setup**: Re-claim `MCP-BASE-001` first (it was released in Test 7.5)

**Tool**: `lodestar_task_done`

**Parameters**:
```json
{
  "task_id": "MCP-BASE-001",
  "agent_id": "<agentId from Test 2.1>",
  "note": "Work completed via MCP test"
}
```

**Expected Result**:
- Returns `ok: true`
- Returns `status: "done"`
- Lease is automatically released

### Test 8.2: Verify Task

**Tool**: `lodestar_task_verify`

**Use**: Verify `MCP-BASE-001` which is now in "done" state

**Parameters**:
```json
{
  "task_id": "MCP-BASE-001",
  "agent_id": "<agentId from Test 2.1>",
  "note": "Verified working correctly"
}
```

**Expected Result**:
- Returns `ok: true`
- Returns `status: "verified"`
- Returns `newlyReadyTaskIds` (should be empty - no tasks depend on MCP-BASE-001)

### Test 8.3: Atomic Complete (Done + Verify)

**Setup**: Claim `MCP-FEAT-001` first

**Tool**: `lodestar_task_complete`

**Use**: Atomically complete `MCP-FEAT-001`

**Parameters**:
```json
{
  "task_id": "MCP-FEAT-001",
  "agent_id": "<agentId from Test 2.1>",
  "note": "Completed and verified atomically"
}
```

**Expected Result**:
- Returns `ok: true`
- Returns `status: "verified"` (skips "done" state)
- Returns `newlyReadyTaskIds` (should be empty)
- Lease automatically released

### Test 8.4: Batch Verify

**Setup**:
1. Claim and complete `MCP-DEP-001` (parent task)
2. Mark it as "done" but NOT verified
3. Claim and complete `MCP-FEAT-002` (independent task)
4. Mark it as "done" but NOT verified
5. Now batch verify both

**Tool**: `lodestar_task_batch_verify`

**Parameters**:
```json
{
  "task_ids": ["MCP-DEP-001", "MCP-FEAT-002"],
  "agent_id": "<agentId from Test 2.1>",
  "notes": {
    "MCP-DEP-001": "Verified in batch - should unblock MCP-DEP-002",
    "MCP-FEAT-002": "Also verified in batch"
  }
}
```

**Expected Result**:
- Returns summary with `total: 2`, `succeeded: 2`, `failed: 0`
- Returns individual `results` for each task
- Returns `allNewlyReadyTaskIds` containing `["MCP-DEP-002"]`
- Verifying `MCP-DEP-001` should unblock `MCP-DEP-002` (which depends on it)

---

## Phase 9: Task Context

### Test 9.1: Get PRD Context

**Setup**: Use a task that has PRD references

**Tool**: `lodestar_task_context`

**Parameters**:
```json
{
  "task_id": "<task with PRD>",
  "max_chars": 2000
}
```

**Expected Result**:
- Returns `taskId`, `title`, `description`
- Returns `prdSource`, `prdRefs`, `prdExcerpt` (if PRD exists)
- Returns `prdSections` (live content from PRD file)
- Returns `drift` object: `changed`, `details`
- Returns `content` (combined, truncated)
- Returns `warnings` for any issues

### Test 9.2: Context for Task Without PRD

**Tool**: `lodestar_task_context`

**Parameters**:
```json
{
  "task_id": "<task without PRD>"
}
```

**Expected Result**:
- Returns basic task info
- PRD fields are null or empty
- No PRD drift warnings

---

## Phase 10: Messaging

### Test 10.1: Send Message to Task

**Tool**: `lodestar_message_send`

**Parameters**:
```json
{
  "from_agent_id": "<agentId>",
  "task_id": "<task ID>",
  "body": "Test message from MCP integration test",
  "subject": "MCP Test",
  "severity": "info"
}
```

**Expected Result**:
- Returns `messageId`
- Returns `deliveredTo` array (e.g., `["task:F001"]`)
- Returns `sentAt` timestamp

**Save**: Store `messageId` and `taskId`

### Test 10.2: List Task Messages

**Tool**: `lodestar_message_list`

**Parameters**:
```json
{
  "task_id": "<taskId from Test 10.1>",
  "limit": 50
}
```

**Expected Result**:
- Returns `messages` array
- Returns `count`
- Returns `task_id`
- Message from Test 10.1 appears in list
- Each message has: `message_id`, `from_agent_id`, `task_id`, `text`, `created_at`, `read_by`, `meta`

### Test 10.3: List Unread Messages

**Tool**: `lodestar_message_list`

**Parameters**:
```json
{
  "task_id": "<taskId>",
  "unread_by": "<different agentId>"
}
```

**Expected Result**:
- Returns only messages not read by specified agent

### Test 10.4: Acknowledge Messages

**Tool**: `lodestar_message_ack`

**Parameters**:
```json
{
  "task_id": "<taskId>",
  "agent_id": "<agentId>",
  "message_ids": ["<messageId from Test 10.1>"]
}
```

**Expected Result**:
- Returns `ok: true`
- Returns `task_id`
- Returns `updatedCount`
- Subsequent unread query excludes acknowledged messages

### Test 10.5: Acknowledge All Messages

**Tool**: `lodestar_message_ack`

**Parameters**:
```json
{
  "task_id": "<taskId>",
  "agent_id": "<agentId>"
}
```

(Note: omit `message_ids` to mark all as read)

**Expected Result**:
- All messages for that task marked as read by agent

---

## Phase 11: Events

### Test 11.1: Pull Events

**Tool**: `lodestar_events_pull`

**Parameters**:
```json
{
  "since_cursor": 0,
  "limit": 100
}
```

**Expected Result**:
- Returns `events` array
- Returns `count`
- Returns `nextCursor` (for pagination)
- Events include operations from previous tests

**Event Types to Verify**:
- `agent.joined` - From Test 2.1
- `task.claimed` - From Test 7.1
- `task.released` - From Test 7.5
- `task.done` - From Test 8.1
- `task.verified` - From Test 8.2
- `message.sent` - From Test 10.1

### Test 11.2: Filter Events by Type

**Tool**: `lodestar_events_pull`

**Parameters**:
```json
{
  "since_cursor": 0,
  "filter_types": ["task.claimed", "task.verified"]
}
```

**Expected Result**:
- Only returns events of specified types

### Test 11.3: Paginate Events

**Tool**: `lodestar_events_pull`

**Parameters**:
```json
{
  "since_cursor": 0,
  "limit": 5
}
```

**Expected Result**:
- Returns at most 5 events
- Returns `nextCursor` for next page

**Follow-up**:
```json
{
  "since_cursor": <nextCursor>,
  "limit": 5
}
```

---

## Phase 12: Agent Departure

### Test 12.1: Agent Leave

**Tool**: `lodestar_agent_leave`

**Parameters**:
```json
{
  "agent_id": "<agentId from Test 2.1>",
  "reason": "MCP integration test complete"
}
```

**Expected Result**:
- Returns confirmation
- Returns `leftAt` timestamp
- May return warnings about active leases

### Test 12.2: Verify Agent Left

**Tool**: `lodestar_agent_list`

**Expected Result**:
- Agent status should be "offline" or removed from active agents

---

## Phase 13: Error Handling

### Test 13.1: Empty Required Fields

Test various tools with empty required fields:

| Tool | Parameter | Expected Error |
|------|-----------|----------------|
| `lodestar_task_get` | `task_id: ""` | `INVALID_TASK_ID` |
| `lodestar_task_claim` | `agent_id: ""` | `INVALID_AGENT_ID` |
| `lodestar_message_send` | `body: ""` | Validation error |
| `lodestar_agent_heartbeat` | `agent_id: ""` | `INVALID_AGENT_ID` |

### Test 13.2: Invalid Status Values

**Tool**: `lodestar_task_list`

**Parameters**:
```json
{
  "status": "invalid_status"
}
```

**Expected Result**:
- Returns validation error
- Error mentions valid status values

### Test 13.3: TTL Clamping

**Tool**: `lodestar_agent_join`

**Parameters**:
```json
{
  "name": "TTL Test",
  "ttl_seconds": 10
}
```

**Expected Result**:
- Succeeds (TTL clamped to minimum 60)
- `leaseDefaults.ttlSeconds >= 60`

**Also test**:
- `ttl_seconds: 100000` should clamp to max 7200

### Test 13.4: Message Length Limit

**Tool**: `lodestar_message_send`

**Parameters**:
```json
{
  "from_agent_id": "<agentId>",
  "task_id": "<taskId>",
  "body": "<string longer than 16KB>"
}
```

**Expected Result**:
- Returns validation error
- Error mentions maximum length exceeded

---

## Phase 14: Lock Conflict Detection

### Test 14.1: Detect Overlapping Locks

**Setup**:
1. Use `MCP-LOCK-001` (locks: `["src/**"]`) and `MCP-LOCK-002` (locks: `["src/auth/**", "src/core/**"]`) from Phase 0
2. Claim `MCP-LOCK-001` first

**Tool**: `lodestar_task_claim`

**Parameters** (claim MCP-LOCK-001 first):
```json
{
  "task_id": "MCP-LOCK-001",
  "agent_id": "<agentId>"
}
```

**Then claim MCP-LOCK-002**:
```json
{
  "task_id": "MCP-LOCK-002",
  "agent_id": "<agentId>"
}
```

**Expected Result**:
- MCP-LOCK-001 claim succeeds with no warnings
- MCP-LOCK-002 claim succeeds but with warning
- `warnings` array contains `LOCK_CONFLICT` warning
- Warning mentions overlapping patterns (`src/auth/**` overlaps with `src/**`)

### Test 14.2: Force Bypass Lock Warning

**Tool**: `lodestar_task_claim`

**Setup**: Release MCP-LOCK-002 first, then re-claim with force flag

**Parameters**:
```json
{
  "task_id": "MCP-LOCK-002",
  "agent_id": "<agentId>",
  "force": true
}
```

**Expected Result**:
- Succeeds without warnings (force bypasses lock conflict detection)

---

## Phase 15: Test Experience Feedback

**Purpose**: Collect the agent's experience and provide actionable feedback for improving Lodestar MCP.

### Test 15.1: Document User Experience

Based on your experience running all the tests above, document the following:

#### A. Usability Assessment

For each category, rate your experience (1-5 stars) and provide comments:

1. **Tool Discoverability** (How easy was it to understand which tool to use?)
   - Rating: ⭐⭐⭐⭐⭐
   - Comments:

2. **Error Messages** (Were errors clear and actionable?)
   - Rating: ⭐⭐⭐⭐⭐
   - Comments:

3. **Response Structure** (Was structured content easy to parse and use?)
   - Rating: ⭐⭐⭐⭐⭐
   - Comments:

4. **API Consistency** (Did tools follow predictable patterns?)
   - Rating: ⭐⭐⭐⭐⭐
   - Comments:

5. **Documentation Alignment** (Did tools work as documented?)
   - Rating: ⭐⭐⭐⭐⭐
   - Comments:

#### B. Issues Encountered

List any issues, bugs, or unexpected behaviors encountered during testing:

| Test # | Tool | Issue | Severity | Details |
|--------|------|-------|----------|---------|
| | | | High/Medium/Low | |

#### C. Missing Features

Identify any missing features or capabilities that would improve the MCP experience:

1.
2.
3.

#### D. Workflow Pain Points

Describe any workflows that were unnecessarily complex or cumbersome:

1.
2.
3.

### Test 15.2: Create Prioritized Recommendations

**Task**: Create a task in Lodestar with your prioritized list of MCP improvements.

**Tool**: `lodestar_task_create`

**Parameters**:
```json
{
  "task_id": "MCP-FEEDBACK-<DATE>",
  "title": "MCP Integration Test Feedback - <DATE>",
  "description": "# MCP Test Feedback\n\n## Executive Summary\n<1-2 sentence overview of MCP quality>\n\n## Critical Issues (P0)\n<Issues that block or severely impact MCP usage>\n\n## High Priority Improvements (P1)\n<Important improvements for better UX>\n\n## Medium Priority Enhancements (P2)\n<Nice-to-have features and polish>\n\n## Low Priority Items (P3)\n<Future considerations>\n\n## Positive Highlights\n<What worked particularly well>",
  "acceptance_criteria": [
    "All critical issues documented with reproduction steps",
    "Recommendations are specific and actionable",
    "Each item has clear priority and rationale"
  ],
  "priority": 1,
  "status": "ready",
  "labels": ["feedback", "mcp", "testing", "ux"]
}
```

**Expected Content Structure**:

Your description should follow this template:

```markdown
# MCP Integration Test Feedback - YYYY-MM-DD

## Executive Summary
[2-3 sentences on overall MCP quality, readiness, and biggest wins/gaps]

## Critical Issues (P0)
**Must fix before production use**

### Issue 1: [Title]
- **Tool**: `lodestar_tool_name`
- **Impact**: [What breaks or is blocked]
- **Reproduction**: [Minimal steps to reproduce]
- **Expected**: [What should happen]
- **Actual**: [What actually happened]
- **Suggested Fix**: [Proposed solution]

## High Priority Improvements (P1)
**Should fix soon for better UX**

### Improvement 1: [Title]
- **Area**: [Which tool(s) or workflow]
- **Current Behavior**: [What happens now]
- **Proposed**: [What should happen instead]
- **Benefit**: [Why this matters]
- **Effort Estimate**: [Small/Medium/Large]

## Medium Priority Enhancements (P2)
**Nice to have, improves polish**

### Enhancement 1: [Title]
- Brief description
- Value proposition

## Low Priority Items (P3)
**Future considerations**

- Item 1
- Item 2

## Positive Highlights
**What worked well**

1. [Feature/Tool]: [Why it was great]
2. [Feature/Tool]: [Why it was great]

## Test Coverage Summary
- **Tests Passed**: X/Y
- **Tests Failed**: Z
- **Tests Skipped**: W
- **Overall Assessment**: [Ready/Needs Work/Not Ready]

## Additional Notes
[Any other observations, patterns, or insights]
```

**Example** of a well-structured issue:

```markdown
### Issue 1: task_claim doesn't validate agent registration first
- **Tool**: `lodestar_task_claim`
- **Impact**: Confusing error messages when agent forgets to join
- **Reproduction**:
  1. Don't call `lodestar_agent_join`
  2. Call `lodestar_task_claim` with arbitrary agent_id
  3. Observe error about task not claimable (misleading)
- **Expected**: Error should say "Agent ABC not registered. Please call lodestar_agent_join first."
- **Actual**: Error says "Task not claimable" or generic failure
- **Suggested Fix**: Add agent validation step before task claimability check
```

**Deliverable**: Create the task with your complete, prioritized feedback.

---

## Cleanup

After all tests complete:

1. Review your feedback task to ensure all findings are documented
2. Delete disposable test tasks (keep MCP-FEEDBACK task)
3. Leave agent gracefully (Test 12.1)
4. Verify no orphaned leases remain

---

## Test Summary Checklist

| Phase | Test | Status |
|-------|------|--------|
| **0** | **Test Fixture Setup** | |
| 0.1 | Create Base Test Task | [ ] |
| 0.2 | Create Feature Test Tasks | [ ] |
| 0.3 | Create Dependency Chain | [ ] |
| 0.4 | Create Lock Pattern Tasks | [ ] |
| 0.5 | Verify Test Fixtures | [ ] |
| **1** | **Repository Status** | |
| 1.1 | Repository Status | [ ] |
| **2** | **Agent Lifecycle** | |
| 2.1 | Agent Join | [ ] |
| 2.2 | Agent List | [ ] |
| 2.3 | Agent Heartbeat | [ ] |
| 2.4 | Invalid Heartbeat | [ ] |
| **3** | **Task Listing** | |
| 3.1 | List All Tasks | [ ] |
| 3.2 | Filter by Status | [ ] |
| 3.3 | Filter by Label | [ ] |
| 3.4 | Pagination | [ ] |
| 3.5 | Combined Filters | [ ] |
| **4** | **Task Details** | |
| 4.1 | Get Task Details | [ ] |
| 4.2 | Get Non-Existent | [ ] |
| 4.3 | Invalid Task ID | [ ] |
| **5** | **Task Discovery** | |
| 5.1 | Next Claimable | [ ] |
| 5.2 | Next with Labels | [ ] |
| 5.3 | Next with Priority | [ ] |
| **6** | **Task CRUD** | |
| 6.1 | Create Minimal Task | [ ] |
| 6.2 | Create Full Task | [ ] |
| 6.3 | Create with Deps | [ ] |
| 6.4 | Create Invalid Dep | [ ] |
| 6.5 | Update Task | [ ] |
| 6.6 | Delete Task | [ ] |
| **7** | **Task Claiming** | |
| 7.1 | Claim Task | [ ] |
| 7.2 | Claim Unregistered | [ ] |
| 7.3 | Claim Already Claimed | [ ] |
| 7.4 | Claim Non-Claimable | [ ] |
| 7.5 | Release Task | [ ] |
| **8** | **Task Completion** | |
| 8.1 | Mark Done | [ ] |
| 8.2 | Verify Task | [ ] |
| 8.3 | Atomic Complete | [ ] |
| 8.4 | Batch Verify | [ ] |
| **9** | **Task Context** | |
| 9.1 | PRD Context | [ ] |
| 9.2 | Context No PRD | [ ] |
| **10** | **Messaging** | |
| 10.1 | Send Message | [ ] |
| 10.2 | List Messages | [ ] |
| 10.3 | Unread Messages | [ ] |
| 10.4 | Ack Messages | [ ] |
| 10.5 | Ack All | [ ] |
| **11** | **Events** | |
| 11.1 | Pull Events | [ ] |
| 11.2 | Filter Events | [ ] |
| 11.3 | Paginate Events | [ ] |
| **12** | **Agent Departure** | |
| 12.1 | Agent Leave | [ ] |
| 12.2 | Verify Left | [ ] |
| **13** | **Error Handling** | |
| 13.1 | Empty Fields | [ ] |
| 13.2 | Invalid Status | [ ] |
| 13.3 | TTL Clamping | [ ] |
| 13.4 | Message Length | [ ] |
| **14** | **Lock Conflicts** | |
| 14.1 | Lock Conflict | [ ] |
| 14.2 | Force Bypass | [ ] |
| **15** | **Feedback** | |
| 15.1 | Document Experience | [ ] |
| 15.2 | Create Feedback Task | [ ] |

---

## Notes

- **Run tests in order** - Many tests depend on state from previous tests (especially Phase 0 fixtures)
- **Store IDs** - Keep track of agentId, taskId, leaseId, messageId between tests
- **Use fixture tasks** - Phase 0 creates reusable test tasks (MCP-BASE-*, MCP-FEAT-*, MCP-DEP-*, MCP-LOCK-*)
- **Phase 15 is critical** - The feedback phase is the most important deliverable; be thorough
- **Clean up after** - Delete disposable test tasks but keep the MCP-FEEDBACK task
- **Test count** - 70+ individual test cases across 16 phases
