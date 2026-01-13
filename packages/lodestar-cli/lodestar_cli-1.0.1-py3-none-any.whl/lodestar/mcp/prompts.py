"""MCP prompt templates for Lodestar workflows."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

from lodestar.mcp.server import LodestarContext


def register_prompts(mcp: FastMCP, context: LodestarContext) -> None:
    """
    Register MCP prompts with the server.

    Args:
        mcp: FastMCP server instance.
        context: Lodestar server context with DB and spec access.
    """

    @mcp.prompt(
        name="lodestar_agent_workflow",
        title="Lodestar Agent Workflow",
        description="Step-by-step guide for working with Lodestar tasks from join to verify",
    )
    def agent_workflow() -> list[dict[str, str]]:
        """
        Provides a concise workflow recipe for AI agents working with Lodestar.

        This prompt guides agents through the standard task lifecycle:
        join -> next -> claim -> context -> done -> verify -> message handoff

        Returns:
            List of message dicts with role and content.
        """
        workflow_content = """# Lodestar Agent Workflow

Follow this workflow when working with Lodestar tasks:

## 1. Join as an Agent

Register yourself in the repository:

```bash
lodestar_agent_join(role="ai-agent", capabilities=["python", "testing"])
# Save the returned agent_id for subsequent commands
```

## 2. Find Available Work

Get the next claimable task:

```bash
lodestar_task_next()
# Returns tasks that are ready and have all dependencies verified
```

Or list all tasks to find specific work:

```bash
lodestar_task_list(status="ready")
```

## 3. Check Upstream Messages

**IMPORTANT**: Before claiming, check for messages from upstream (dependency) tasks:

```bash
# Get task details to see dependencies
task = lodestar_task_get(task_id="T001")

# Check each dependency for messages with context or warnings
for dep_id in task["dependsOn"]:
    messages = lodestar_message_list(task_id=dep_id, unread_by="YOUR_AGENT_ID")
    # Review messages for important context, warnings, or issues
```

Upstream messages may contain:
- Important context about implementation decisions
- Warnings about edge cases or limitations
- API changes or constraints
- Known issues or workarounds

## 4. Claim the Task

Before starting work, claim the task to prevent duplicate effort:

```bash
lodestar_task_claim(task_id="T001", agent_id="YOUR_AGENT_ID")
# You now have a 15-minute lease (renewable)
```

## 5. Get Task Context

Retrieve full task details including PRD context:

```bash
lodestar_task_get(task_id="T001")
# Or for even more context:
lodestar_task_context(task_id="T001")
```

This provides:
- Task description and acceptance criteria
- PRD context (frozen excerpts from requirements)
- Dependencies and dependent tasks
- Any drift warnings if PRD has changed

## 6. Do the Work

Implement the task following the acceptance criteria. Make sure to:
- Run tests frequently
- Commit your changes incrementally
- Complete within 15 minutes (leases auto-expire)

**Lease Management:**
- Leases are 15 minutes by default and auto-expire
- Use `lodestar_task_complete()` to atomically finish work (recommended)
- If you need more time, release and re-claim or work faster

## 7. Mark as Complete (Recommended)

**Recommended**: Use the atomic complete operation:

```bash
lodestar_task_complete(task_id="T001", agent_id="YOUR_AGENT_ID")
```

This combines done + verify in one atomic operation, preventing tasks from getting stuck in 'done' state if the process crashes.

**Alternative**: Separate done and verify steps:

```bash
# Mark as done
lodestar_task_done(task_id="T001", agent_id="YOUR_AGENT_ID")

# Then verify
lodestar_task_verify(task_id="T001", agent_id="YOUR_AGENT_ID")
```

Use separate steps only if you need time between completion and verification (e.g., waiting for CI, manual testing).

## 8. Message Downstream Tasks

**IMPORTANT**: After verifying, check for dependent tasks and message them if needed:

```bash
# Get task details to see dependents
task = lodestar_task_get(task_id="T001")

# If there are important warnings, context, or remaining issues:
for dependent_id in task["dependents"]:
    lodestar_message_send(
        task_id=dependent_id,
        from_agent_id="YOUR_AGENT_ID",
        body="Important: API rate limit of 100 req/min applies to all /users endpoints. Use caching for list operations.",
        severity="warning"
    )
```

Message downstream tasks when:
- There are important constraints or limitations they should know
- You made implementation decisions that affect downstream work
- There are edge cases or gotchas to be aware of
- You identified issues that couldn't be fixed in this task's scope
- There's useful context that will help them complete their work

## 9. Handoff (if blocked or incomplete)

If you're blocked or ending your session before completion:

```bash
# Release the task
lodestar_task_release(task_id="T001", agent_id="YOUR_AGENT_ID")

# Leave context for the next agent on THIS task
lodestar_message_send(
    task_id="T001",
    from_agent_id="YOUR_AGENT_ID",
    body="Progress: 60% complete. Token generation works in src/auth/token.py. Blocked on email template approval from design team. Next: implement template rendering in src/email/render.py",
    severity="handoff"
)
```

## Best Practices

- **Check upstream first**: Always check messages from dependency tasks before claiming
- **One task at a time**: Focus on completion before claiming another
- **Claim before working**: Don't work on unclaimed tasks
- **Work within 15 minutes**: Leases auto-expire, complete tasks promptly
- **Use task_complete**: Prefer atomic complete over separate done+verify
- **Verify thoroughly**: Ensure all acceptance criteria are met
- **Message downstream**: Alert dependent tasks of important context, warnings, or issues
- **Leave handoff context**: Help the next agent if you need to release
- **Check drift warnings**: Review PRD if context has changed

## Quick Command Reference

```
lodestar_agent_join()          # Register as agent
lodestar_task_next()           # Find claimable tasks
lodestar_message_list()        # Check upstream messages
lodestar_task_claim()          # Claim a task
lodestar_task_context()        # Get full context
lodestar_task_complete()       # Mark complete (recommended)
lodestar_task_done()           # Mark done (alt)
lodestar_task_verify()         # Mark verified (alt)
lodestar_message_send()        # Message downstream or handoff
lodestar_message_ack()         # Mark messages as read
lodestar_task_release()        # Release if blocked
```
"""

        return [
            {
                "role": "user",
                "content": workflow_content,
            }
        ]

    @mcp.prompt(
        name="lodestar_task_execute",
        title="Lodestar Task Execution Guide",
        description="Guide for executing a task following acceptance criteria and producing verification checklist",
    )
    def task_execute() -> list[dict[str, str]]:
        """
        Provides execution guidance for implementing and verifying Lodestar tasks.

        This prompt helps agents:
        - Follow acceptance criteria systematically
        - Create comprehensive verification checklists
        - Ensure quality and completeness before marking tasks done

        Returns:
            List of message dicts with role and content.
        """
        execute_content = """# Lodestar Task Execution Guide

When executing a claimed task, follow this systematic approach:

## 1. Review Task Context

Before writing any code, thoroughly review:

```bash
lodestar_task_context(task_id="YOUR_TASK_ID")
```

This provides:
- **Description**: What needs to be done
- **Acceptance Criteria**: Specific requirements that must be met
- **PRD Context**: Relevant product requirements
- **Dependencies**: What this task builds upon
- **Dependents**: What's blocked waiting for this

## 2. Create Your Verification Checklist

Based on the acceptance criteria, create a checklist BEFORE starting implementation:

**Example:**
```markdown
## Verification Checklist for [TASK_ID]

### Acceptance Criteria
- [ ] Criterion 1: [Specific requirement from task]
- [ ] Criterion 2: [Another requirement]
- [ ] Criterion 3: [etc.]

### Code Quality
- [ ] Code follows project style guide
- [ ] All linting checks pass (ruff check)
- [ ] Code is formatted correctly (ruff format)
- [ ] No type errors or warnings

### Testing
- [ ] Unit tests written for new functionality
- [ ] All tests pass (pytest)
- [ ] Edge cases covered
- [ ] Integration tests if needed

### Documentation
- [ ] Docstrings added for new functions/classes
- [ ] CLI documentation updated if commands changed
- [ ] README or guides updated if needed

### Git Hygiene
- [ ] Changes committed with descriptive message
- [ ] No debug code or commented-out code left behind
- [ ] No unintended files in commit
```

## 3. Implement Incrementally

Follow test-driven development:

1. **Read the existing code** to understand patterns and architecture
2. **Write tests first** for new functionality
3. **Implement in small steps**, running tests after each change
4. **Commit frequently** with clear messages
5. **Complete within 15 minutes** (leases auto-expire)

## 4. Verify Against Checklist

Before marking the task as done, go through your checklist:

```bash
# Run all quality checks
ruff check src tests
ruff format --check src tests
pytest
```

Document results in your verification checklist.

## 5. Pre-Completion Review

Ask yourself:
- ✅ Are ALL acceptance criteria met?
- ✅ Do all tests pass?
- ✅ Is the code production-ready?
- ✅ Would this pass code review?
- ✅ Is documentation up-to-date?

**If any answer is "no", do NOT mark as done yet.**

## 6. Mark as Done

Only when all checks pass:

```bash
lodestar_task_done(task_id="YOUR_TASK_ID", agent_id="YOUR_AGENT_ID")
```

## 7. Verify Thoroughly

The verification step is crucial - it unblocks dependent tasks:

```bash
lodestar_task_verify(task_id="YOUR_TASK_ID", agent_id="YOUR_AGENT_ID")
```

**Before verifying:**
- Run end-to-end tests
- Test as a user would
- Check all acceptance criteria one final time
- Review your verification checklist

## Common Pitfalls to Avoid

❌ **Don't**: Mark tasks done with failing tests
❌ **Don't**: Skip acceptance criteria review
❌ **Don't**: Verify without thorough testing
❌ **Don't**: Leave TODOs or commented code
❌ **Don't**: Forget to update documentation

✅ **Do**: Follow acceptance criteria exactly
✅ **Do**: Test incrementally and thoroughly
✅ **Do**: Commit early and often
✅ **Do**: Update docs when changing CLI commands
✅ **Do**: Use the verification checklist

## Quality Standards

Every task completion should meet these standards:

1. **Correctness**: Implements all acceptance criteria exactly
2. **Completeness**: No partial implementations or TODOs
3. **Quality**: Passes all linting and formatting checks
4. **Tested**: All tests pass, edge cases covered
5. **Documented**: Code and user-facing docs updated
6. **Clean**: No debug code, proper git hygiene

## Example Workflow

```bash
# 1. Get context
task_context = lodestar_task_context(task_id="T042")

# 2. Create verification checklist (in your editor/notes)

# 3. Implement incrementally
# - Write tests
# - Implement feature
# - Run tests
# - Commit changes

# 4. Run quality checks
ruff check src tests
ruff format --check src tests
pytest

# 5. Mark as done
lodestar_task_done(task_id="T042", agent_id="A123")

# 6. Verify thoroughly
lodestar_task_verify(task_id="T042", agent_id="A123")
```

Remember: **Quality over speed**. A properly completed task is better than rushing to "done" with incomplete work.
"""

        return [
            {
                "role": "user",
                "content": execute_content,
            }
        ]

    @mcp.prompt(
        name="lodestar_task_communication",
        title="Lodestar Task Communication Patterns",
        description="Guide for using task-focused messaging to coordinate with upstream and downstream tasks",
    )
    def task_communication() -> list[dict[str, str]]:
        """
        Provides guidance on using task-focused messaging for coordination.

        This prompt helps agents:
        - Check messages from upstream (dependency) tasks for context
        - Leave messages for downstream (dependent) tasks about issues/constraints
        - Use proper handoff messaging when blocked or incomplete

        Returns:
            List of message dicts with role and content.
        """
        communication_content = """# Lodestar Task Communication Patterns

Lodestar uses **task-focused messaging** to coordinate work across dependency chains. Messages are attached to tasks, not sent between agents directly.

## Why Task-Focused Messaging?

- **Persistent context**: Messages stay with the task across agent handoffs
- **Dependency awareness**: Messages flow naturally through task dependencies
- **No agent routing**: No need to know which agent will work on a task
- **Threaded history**: All communication about a task in one place

## Three Communication Patterns

### 1. Check Upstream Messages (Before Starting)

**When**: Before claiming a task, always check messages from dependencies.

**Why**: Upstream tasks may have left important context, warnings, or constraints.

```python
# Get task details to see dependencies
task = lodestar_task_get(task_id="F002")

# Check each dependency for unread messages
for dep_id in task.get("dependsOn", []):
    messages = lodestar_message_list(
        task_id=dep_id,
        unread_by="YOUR_AGENT_ID"
    )

    # Review each message
    for msg in messages["messages"]:
        print(f"From task {dep_id}:")
        print(f"  [{msg['meta'].get('severity', 'info')}] {msg['text']}")

    # Mark as read after reviewing
    if messages["count"] > 0:
        lodestar_message_ack(
            task_id=dep_id,
            agent_id="YOUR_AGENT_ID"
        )
```

**What to look for in upstream messages:**
- ⚠️ **Warnings**: Constraints, limitations, gotchas
- 📋 **Context**: Implementation decisions that affect downstream work
- 🐛 **Known issues**: Problems that couldn't be fixed in scope
- 🔧 **API changes**: Interface modifications to be aware of
- 📝 **Documentation**: Where to find relevant code/patterns

### 2. Message Downstream Tasks (After Completing)

**When**: After verifying a task, if there's important context for dependent tasks.

**Why**: Help downstream agents avoid issues and understand constraints.

```python
# After verifying, get task details to see dependents
task = lodestar_task_get(task_id="F001")

# Send messages to downstream tasks if needed
for dependent_id in task.get("dependents", []):
    lodestar_message_send(
        task_id=dependent_id,
        from_agent_id="YOUR_AGENT_ID",
        body="Important: The /users endpoint now has rate limiting (100 req/min). Use the caching layer in src/cache/user_cache.py for list operations to avoid hitting limits.",
        severity="warning"
    )
```

**When to message downstream:**
- ⚠️ Made a constraint that affects downstream work
- 📋 Made an implementation choice they should follow
- 🐛 Discovered edge cases they should handle
- 🔧 Changed an interface or API contract
- ❌ Identified work that's out of scope but needed

**Severity levels:**
- `info`: General context or helpful information
- `warning`: Important constraints or limitations to be aware of
- `handoff`: Progress update for next agent on same task
- `blocker`: Critical issue that prevents downstream work

### 3. Handoff Messages (When Blocked or Incomplete)

**When**: You need to release a task before completion.

**Why**: Help the next agent pick up where you left off.

```python
# Release the claim
lodestar_task_release(
    task_id="F001",
    agent_id="YOUR_AGENT_ID",
    reason="Blocked on API key approval from DevOps"
)

# Leave handoff message on the SAME task
lodestar_message_send(
    task_id="F001",  # Same task you're releasing
    from_agent_id="YOUR_AGENT_ID",
    body=\"\"\"Progress: 60% complete.

DONE:
- Token generation working (src/auth/token.py)
- Unit tests passing (tests/auth/test_token.py)
- Database schema updated with new token_meta column

BLOCKED:
- Waiting for SendGrid API key from DevOps (ticket #1234)

NEXT STEPS:
1. Get API key and add to .env
2. Implement email sending in src/email/send.py
3. Add integration test in tests/email/test_send.py
4. Update docs/email-setup.md with configuration steps\"\"\",
    severity="handoff",
    subject="60% complete - blocked on API key"
)
```

## Complete Example Workflow

```python
# 1. Find work
tasks = lodestar_task_next()
task_id = tasks["candidates"][0]["taskId"]

# 2. Check upstream messages BEFORE claiming
task = lodestar_task_get(task_id=task_id)
for dep_id in task.get("dependsOn", []):
    messages = lodestar_message_list(task_id=dep_id, unread_by="MY_AGENT_ID")
    # Review messages...
    if messages["count"] > 0:
        lodestar_message_ack(task_id=dep_id, agent_id="MY_AGENT_ID")

# 3. Claim and work
lodestar_task_claim(task_id=task_id, agent_id="MY_AGENT_ID")
# ... implement task ...

# 4. Complete
lodestar_task_done(task_id=task_id, agent_id="MY_AGENT_ID")
lodestar_task_verify(task_id=task_id, agent_id="MY_AGENT_ID")

# 5. Message downstream if needed
task = lodestar_task_get(task_id=task_id)
if task.get("dependents"):
    for dep_id in task["dependents"]:
        lodestar_message_send(
            task_id=dep_id,
            from_agent_id="MY_AGENT_ID",
            body="Note: Validation now requires both email AND phone. See src/validators.py",
            severity="warning"
        )
```

## Best Practices

✅ **DO:**
- Check upstream messages before claiming
- Mark messages as read after reviewing
- Leave specific, actionable messages for downstream
- Include file paths and code references in messages
- Use appropriate severity levels
- Be concise but complete in handoffs

❌ **DON'T:**
- Claim without checking upstream messages
- Leave vague messages like "some issues exist"
- Message about things already in acceptance criteria
- Forget to mark messages as read
- Over-communicate - only message when it adds value

## Message Severity Guide

| Severity | Use When | Example |
|----------|----------|---------|
| `info` | Helpful context, not critical | "I used lodash for array operations, pattern in utils.js" |
| `warning` | Important constraint or gotcha | "Rate limit: 100 req/min, use caching" |
| `handoff` | Incomplete work, progress update | "60% done, blocked on API key" |
| `blocker` | Critical issue preventing downstream | "Auth endpoint failing in prod, rollback needed" |

## Quick Reference

```python
# Check upstream (before claim)
lodestar_message_list(task_id=upstream_id, unread_by=my_id)

# Mark as read
lodestar_message_ack(task_id=task_id, agent_id=my_id)

# Message downstream (after verify)
lodestar_message_send(
    task_id=downstream_id,
    from_agent_id=my_id,
    body="...",
    severity="warning"  # or info, handoff, blocker
)

# Handoff (before release)
lodestar_message_send(
    task_id=same_task_id,
    from_agent_id=my_id,
    body="Progress: ...",
    severity="handoff"
)
```
"""

        return [
            {
                "role": "user",
                "content": communication_content,
            }
        ]

    @mcp.prompt(
        name="lodestar_task_planning",
        title="Lodestar Task Planning Guide",
        description="Guide for creating well-structured, INVEST-compliant tasks using MCP tools",
    )
    def task_planning() -> list[dict[str, str]]:
        """
        Provides guidance for planning and creating tasks using MCP task creation tools.

        This prompt helps agents:
        - Apply INVEST principles to create well-scoped tasks
        - Use lodestar_task_create, lodestar_task_update, lodestar_task_delete
        - Structure task descriptions properly
        - Manage dependencies and PRD references

        Returns:
            List of message dicts with role and content.
        """
        planning_content = """# Lodestar Task Planning Guide

Task planning agents use MCP tools to create and manage well-structured tasks that execution agents can complete within 15-minute leases.

## Core Principle: INVEST Criteria

Every task must be **INVEST-compliant** for effective coordination:

| Criterion | Meaning | Example |
|-----------|---------|---------|
| **I**ndependent | No waiting for others | "Add login form" not "Add login after auth" |
| **N**egotiable | Details refined during execution | Specify WHAT, not HOW |
| **V**aluable | Delivers user/developer value | Clear business reason |
| **E**stimable | Scope is clear | Bounded file changes |
| **S**mall | Fits in 15-minute lease | Split large work |
| **T**estable | Verifiable acceptance criteria | "Tests pass", "Returns 200" |

## Task Creation Workflow

### 1. Analyze Requirements

Break down features from PRD or requirements document:

```python
# Get repository status
status = lodestar_repo_status()

# Read PRD or requirements
# Identify logical units of work
# Apply INVEST criteria to each unit
```

### 2. Create Well-Structured Tasks

Use `lodestar_task_create` with proper structure:

```python
result = lodestar_task_create(
    title="Add email validation to signup form",
    description=\"\"\"WHAT: Add client-side email format validation
WHERE: src/components/SignupForm.tsx, src/utils/validation.ts
WHY: Users submit invalid emails causing bounce issues (PRD #signup-requirements)
SCOPE: Client-side only. Do NOT add server validation (separate task T043).
ACCEPT: 1) Invalid emails show error 2) Valid emails pass 3) Tests cover edge cases
REFS: Follow pattern in validation.ts, see F041 for form structure\"\"\",
    acceptance_criteria=[
        "Invalid emails show inline error message",
        "Valid emails pass validation",
        "Unit tests cover: empty, missing @, missing domain",
        "Integration test covers form submission flow"
    ],
    priority=5,
    status="ready",
    depends_on=["T041"],  # Form structure must exist first
    labels=["feature", "validation", "frontend"],
    locks=["src/components/SignupForm.tsx", "src/utils/validation.ts"],
    prd_source="PRD.md",
    prd_refs=["#signup-requirements", "#validation-rules"],
    validate_prd=True
)

print(f"Created task: {result['taskId']}")
```

### 3. Task Description Format

Always use this structured format:

```
WHAT:   [Concise statement of what to build/fix]
WHERE:  [File paths or modules to modify]
WHY:    [Business context - link to PRD section]
SCOPE:  [Explicit boundaries - what NOT to do]
ACCEPT: [Testable acceptance criteria - numbered]
REFS:   [Related tasks, docs, code patterns]
```

**Example:**

```
WHAT:   Add rate limiting to API endpoints
WHERE:  src/middleware/ratelimit.py, src/config/limits.py
WHY:    Prevent abuse and ensure fair usage (PRD #non-functional-requirements)
SCOPE:  Apply to /api/users/* only. Do NOT apply to /api/internal/* (different task).
ACCEPT: 1) 100 req/min limit enforced 2) 429 response on limit 3) Tests cover edge cases
REFS:   Follow pattern in auth_middleware.py; see T023 for config loading
```

## Task Decomposition Patterns

### Vertical Slicing (Recommended)

Break features into end-to-end slices that deliver value:

```
Feature: User Authentication
├── T100: Add login form UI (happy path only)
├── T101: Add JWT token generation
├── T102: Add auth middleware for protected routes
├── T103: Add error handling for invalid credentials
└── T104: Add "remember me" functionality
```

Each task is independently valuable and completable in 15 minutes.

### Horizontal Layering (Use Sparingly)

Sometimes you must layer by component:

```
Feature: User Profile
├── T200: Add database schema for user profiles
├── T201: Add profile API endpoints (depends on T200)
├── T202: Add profile UI components (depends on T201)
└── T203: Add profile edit validation (depends on T201)
```

Use when dependencies truly require this structure.

### Task Size Guidelines

**Too Large** (split it):
```
❌ "Implement complete user authentication system"
❌ "Add all validation to signup form"
❌ "Refactor entire auth module"
```

**Right Size** (15 minutes):
```
✅ "Add email format validation to signup form"
✅ "Implement JWT token generation function"
✅ "Add rate limiting middleware to /users endpoints"
```

**Too Small** (combine them):
```
❌ "Import lodash library"
❌ "Add single TODO comment"
❌ "Fix typo in variable name"
```

## Dependency Management

### Setting Dependencies

Tasks should depend on prerequisites:

```python
# Create parent task first
parent = lodestar_task_create(
    title="Add user database schema",
    task_id="T100"
)

# Create dependent task
child = lodestar_task_create(
    title="Add user API endpoints",
    task_id="T101",
    depends_on=["T100"]  # Must wait for schema
)
```

### Avoiding Cycles

Lodestar detects cycles automatically:

```python
# This will fail - creates A -> B -> A cycle
lodestar_task_create(
    task_id="A",
    depends_on=["B"]
)
lodestar_task_create(
    task_id="B",
    depends_on=["A"]  # ❌ Cycle detected
)
```

## PRD References

### Why Reference PRDs?

- Provides frozen context for task execution
- Detects drift if PRD changes after task creation
- Links implementation to requirements

### How to Reference

```python
lodestar_task_create(
    title="Implement feature X",
    description="...",
    prd_source="PRD.md",  # Path to PRD file
    prd_refs=[
        "#feature-x-requirements",  # Section anchors
        "#acceptance-criteria"
    ],
    prd_excerpt="Frozen excerpt from PRD for quick reference",
    validate_prd=True  # Validate file exists (default)
)
```

## Lock Patterns

Use locks to coordinate file access across tasks:

```python
lodestar_task_create(
    title="Add validation to signup form",
    locks=[
        "src/components/SignupForm.tsx",  # Exact file
        "src/utils/validation.ts",
        "tests/signup/**/*.test.ts"  # Glob pattern
    ]
)
```

Lodestar warns about lock conflicts when claiming tasks.

## Updating Tasks

Refine tasks after creation:

```python
# Add missing criteria
lodestar_task_update(
    task_id="T042",
    add_acceptance_criteria=["Tests pass in CI"],
    add_labels=["needs-review"]
)

# Update priority
lodestar_task_update(
    task_id="T042",
    priority=3  # Higher priority
)

# Remove outdated criteria
lodestar_task_update(
    task_id="T042",
    remove_acceptance_criteria=["Manual testing complete"]
)
```

## Deleting Tasks

Remove invalid or obsolete tasks:

```python
# Delete single task (fails if has dependents)
lodestar_task_delete(task_id="T042")

# Cascade delete with dependents
lodestar_task_delete(
    task_id="T042",
    cascade=True  # Deletes T042 and all dependent tasks
)
```

## Complete Planning Example

```python
# 1. Analyze feature from PRD
# Feature: Add email validation to signup flow

# 2. Break into INVEST-compliant tasks

# Task 1: Add validation utility
result1 = lodestar_task_create(
    title="Add email validation utility function",
    description=\"\"\"WHAT: Create reusable email validation function
WHERE: src/utils/validation.ts
WHY: Foundation for form validation (PRD #validation)
SCOPE: Pure validation function only. UI integration in separate task.
ACCEPT: 1) Validates format 2) Tests cover edge cases 3) JSDoc comments
REFS: Follow patterns in validation.ts\"\"\",
    task_id="VAL-001",
    acceptance_criteria=[
        "Function validates email format correctly",
        "Returns clear error messages",
        "Unit tests cover: empty, invalid format, valid emails"
    ],
    priority=1,
    labels=["validation", "utility"],
    locks=["src/utils/validation.ts"],
    prd_source="PRD.md",
    prd_refs=["#validation-rules"]
)

# Task 2: Integrate validation into form (depends on VAL-001)
result2 = lodestar_task_create(
    title="Add email validation to signup form",
    description=\"\"\"WHAT: Integrate email validation into SignupForm
WHERE: src/components/SignupForm.tsx
WHY: Prevent invalid email submissions (PRD #signup)
SCOPE: Client-side only. Server validation is separate task.
ACCEPT: 1) Shows error on invalid email 2) Validates on blur 3) Integration test
REFS: Use validation from VAL-001\"\"\",
    task_id="VAL-002",
    acceptance_criteria=[
        "Form shows validation error on blur",
        "Error clears when user fixes email",
        "Submit button disabled while invalid",
        "Integration test covers validation flow"
    ],
    depends_on=["VAL-001"],
    priority=2,
    labels=["validation", "frontend", "form"],
    locks=["src/components/SignupForm.tsx"],
    prd_source="PRD.md",
    prd_refs=["#signup-requirements"]
)

# 3. Verify task structure
for task_id in ["VAL-001", "VAL-002"]:
    task = lodestar_task_get(task_id=task_id)
    print(f"{task_id}: {task['title']}")
    print(f"  Claimable: {task['dependencies']['isClaimable']}")
```

## Best Practices

✅ **DO:**
- Apply INVEST criteria to every task
- Use structured WHAT/WHERE/WHY/SCOPE/ACCEPT format
- Reference PRD sections for traceability
- Set locks to prevent conflicts
- Create dependency chains that make sense
- Break large features into 15-minute tasks
- Use descriptive task IDs (e.g., "AUTH-042" not "T042")

❌ **DON'T:**
- Create tasks larger than 15 minutes
- Leave acceptance criteria vague or untestable
- Create circular dependencies
- Forget to set locks for shared files
- Skip PRD references when they exist
- Create micro-tasks (< 5 minutes)
- Use generic titles like "Fix bug" or "Update code"

## Quick Reference

```python
# Create task
lodestar_task_create(
    title="Concise, specific title",
    description="WHAT/WHERE/WHY/SCOPE/ACCEPT/REFS",
    acceptance_criteria=["Testable criterion 1", "..."],
    priority=5,  # Lower = higher priority
    depends_on=["PARENT-001"],
    labels=["feature", "auth"],
    locks=["src/auth/**/*.py"],
    prd_source="PRD.md",
    prd_refs=["#section"]
)

# Update task
lodestar_task_update(
    task_id="T042",
    priority=3,
    add_labels=["urgent"],
    add_acceptance_criteria=["New criterion"]
)

# Delete task
lodestar_task_delete(
    task_id="T042",
    cascade=False  # or True to delete dependents
)

# Check task structure
lodestar_task_get(task_id="T042")
```
"""

        return [
            {
                "role": "user",
                "content": planning_content,
            }
        ]
