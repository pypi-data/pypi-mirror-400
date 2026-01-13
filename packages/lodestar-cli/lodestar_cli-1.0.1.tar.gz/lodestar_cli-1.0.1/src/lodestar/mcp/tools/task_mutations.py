"""Task mutation tools for MCP (create, claim, release, done, verify)."""

from __future__ import annotations

import contextlib
from datetime import UTC, datetime, timedelta

from mcp.server.fastmcp import Context
from mcp.types import CallToolResult

from lodestar.core.task_service import detect_lock_conflicts
from lodestar.mcp.notifications import notify_task_updated
from lodestar.mcp.output import error, format_summary, with_item
from lodestar.mcp.server import LodestarContext
from lodestar.mcp.validation import ValidationError, validate_task_id
from lodestar.models.runtime import Lease
from lodestar.models.spec import PrdContext, PrdRef, Task, TaskStatus


async def task_create(
    context: LodestarContext,
    title: str,
    description: str | None = None,
    acceptance_criteria: list[str] | None = None,
    priority: int = 100,
    status: str = "ready",
    task_id: str | None = None,
    depends_on: list[str] | None = None,
    labels: list[str] | None = None,
    locks: list[str] | None = None,
    prd_source: str | None = None,
    prd_refs: list[str] | None = None,
    prd_excerpt: str | None = None,
    validate_prd: bool = True,
    ctx: Context | None = None,
) -> CallToolResult:
    """
    Create a new task in the spec.

    Creates a new task with all specified parameters, validates dependencies and PRD
    references (if enabled), saves to spec.yaml, and emits a task.create event.

    Args:
        context: Lodestar server context
        title: Task title (required)
        description: Task description with WHAT/WHERE/WHY/SCOPE/ACCEPT/REFS (optional)
        acceptance_criteria: List of acceptance criteria (optional)
        priority: Priority value, lower = higher priority (default: 100)
        status: Initial status (default: "ready", options: todo, ready, blocked, done, verified)
        task_id: Task ID (auto-generated if not provided)
        depends_on: List of task IDs this task depends on (optional)
        labels: List of labels for categorization (optional)
        locks: List of file glob patterns for lock-based coordination (optional)
        prd_source: Path to PRD file relative to repo root (optional)
        prd_refs: List of PRD section anchors (optional, e.g., ["#feature-requirements"])
        prd_excerpt: Frozen PRD excerpt to embed in task (optional)
        validate_prd: Whether to validate PRD file and refs exist (default: True)
        ctx: Optional MCP context for logging

    Returns:
        CallToolResult with task details on success or error with validation details
    """
    from pathlib import Path

    from lodestar.spec import SpecError, SpecFileAccessError, SpecLockError

    # Log the create attempt
    if ctx:
        await ctx.info(f"Creating task: {title}")

    # Validate title
    if not title or not title.strip():
        return error(
            "title is required and cannot be empty",
            error_code="INVALID_TITLE",
        )

    # Validate status
    try:
        task_status = TaskStatus(status.lower())
    except ValueError:
        return error(
            f"Invalid status: {status}. Valid options: {', '.join(s.value for s in TaskStatus)}",
            error_code="INVALID_STATUS",
            details={"status": status, "valid_options": [s.value for s in TaskStatus]},
        )

    # Reload spec to get latest state
    context.reload_spec()

    # Generate task ID if not provided
    if task_id is None:
        existing_ids = [
            int(t[1:]) for t in context.spec.tasks if t.startswith("T") and t[1:].isdigit()
        ]
        next_num = max(existing_ids, default=0) + 1
        task_id = f"T{next_num:03d}"

    # Validate task ID format and uniqueness
    try:
        validated_task_id = validate_task_id(task_id)
    except ValidationError as e:
        if ctx:
            await ctx.error(f"Invalid task ID: {task_id}")
        return error(str(e), error_code="INVALID_TASK_ID")

    # Check for duplicate
    if validated_task_id in context.spec.tasks:
        return error(
            f"Task {validated_task_id} already exists",
            error_code="DUPLICATE_TASK_ID",
            details={"task_id": validated_task_id},
        )

    # Validate dependencies exist
    if depends_on:
        missing_deps = [d for d in depends_on if d not in context.spec.tasks]
        if missing_deps:
            return error(
                f"Unknown dependencies: {missing_deps}",
                error_code="UNKNOWN_DEPENDENCIES",
                details={"missing": missing_deps, "task_id": validated_task_id},
            )

    # Build PRD context if provided
    prd_context = None
    if prd_source:
        from lodestar.util.prd import compute_prd_hash, extract_prd_section

        prd_path = Path(context.repo_root) / prd_source

        # Validate PRD file exists if validation enabled
        if validate_prd and not prd_path.exists():
            return error(
                f"PRD file not found: {prd_source}. Set validate_prd=false to skip validation.",
                error_code="PRD_FILE_NOT_FOUND",
                details={"prd_source": prd_source, "resolved_path": str(prd_path)},
            )

        # Validate PRD anchors if validation enabled
        if validate_prd and prd_refs and prd_path.exists():
            invalid_anchors = []
            for ref in prd_refs:
                try:
                    extract_prd_section(prd_path, anchor=ref)
                except ValueError:
                    invalid_anchors.append(ref)

            if invalid_anchors:
                return error(
                    f"PRD anchors not found: {invalid_anchors}. Set validate_prd=false to skip validation.",
                    error_code="PRD_ANCHORS_NOT_FOUND",
                    details={
                        "invalid_anchors": invalid_anchors,
                        "prd_source": prd_source,
                    },
                )

        # Compute hash if file exists
        prd_hash = None
        if prd_path.exists():
            with contextlib.suppress(Exception):
                prd_hash = compute_prd_hash(prd_path)

        prd_context = PrdContext(
            source=prd_source,
            refs=[PrdRef(anchor=ref) for ref in (prd_refs or [])],
            excerpt=prd_excerpt,
            prd_hash=prd_hash,
        )

    # Create task
    now = datetime.now(UTC)
    task = Task(
        id=validated_task_id,
        title=title.strip(),
        description=description or "",
        acceptance_criteria=acceptance_criteria or [],
        status=task_status,
        priority=priority,
        depends_on=depends_on or [],
        labels=labels or [],
        locks=locks or [],
        prd=prd_context,
        created_at=now,
        updated_at=now,
    )

    # Add task to spec
    context.spec.tasks[validated_task_id] = task

    # Validate DAG to catch cycles
    from lodestar.spec.dag import validate_dag

    try:
        dag_result = validate_dag(context.spec)
        if dag_result.cycles:
            # Remove the task we just added
            del context.spec.tasks[validated_task_id]
            return error(
                f"Adding task {validated_task_id} would create dependency cycle(s): {dag_result.cycles}",
                error_code="DEPENDENCY_CYCLE",
                details={"cycles": dag_result.cycles, "task_id": validated_task_id},
            )
    except Exception as e:
        # Remove the task we just added
        del context.spec.tasks[validated_task_id]
        return error(
            f"DAG validation failed: {e}",
            error_code="DAG_VALIDATION_ERROR",
            details={"task_id": validated_task_id},
        )

    # Save spec with error handling
    try:
        context.save_spec()
    except (SpecLockError, SpecFileAccessError) as e:
        # Remove the task we added (it wasn't saved)
        del context.spec.tasks[validated_task_id]
        if ctx:
            await ctx.error(f"Failed to save spec: {e}")
        return error(
            str(e),
            error_code=type(e).__name__.upper(),
            details={"task_id": validated_task_id},
            retriable=e.retriable,
            suggested_action=e.suggested_action,
        )
    except SpecError as e:
        # Remove the task we added
        del context.spec.tasks[validated_task_id]
        if ctx:
            await ctx.error(f"Spec error: {e}")
        return error(
            str(e),
            error_code="SPEC_ERROR",
            details={"task_id": validated_task_id},
            retriable=getattr(e, "retriable", False),
            suggested_action=getattr(e, "suggested_action", None),
        )

    # Log successful creation
    if ctx:
        await ctx.info(f"Successfully created task {validated_task_id}: {title}")

    # Log event (task.create)
    event_data = {
        "title": title,
        "status": task_status.value,
        "priority": priority,
    }
    if depends_on:
        event_data["depends_on"] = depends_on
    if labels:
        event_data["labels"] = labels

    with contextlib.suppress(Exception):
        context.emit_event(
            event_type="task.create",
            task_id=validated_task_id,
            data=event_data,
        )

    # Notify clients of new task
    await notify_task_updated(ctx, validated_task_id)

    # Build summary
    summary = format_summary(
        "Created",
        validated_task_id,
        f"- {title}",
    )

    # Build response
    response_data = {
        "ok": True,
        "taskId": validated_task_id,
        "title": title,
        "status": task_status.value,
        "priority": priority,
        "createdAt": now.isoformat(),
    }

    if depends_on:
        response_data["dependsOn"] = depends_on
    if labels:
        response_data["labels"] = labels
    if locks:
        response_data["locks"] = locks
    if prd_context:
        response_data["prdSource"] = prd_source

    return with_item(summary, item=response_data)


async def task_update(
    context: LodestarContext,
    task_id: str,
    title: str | None = None,
    description: str | None = None,
    priority: int | None = None,
    add_labels: list[str] | None = None,
    remove_labels: list[str] | None = None,
    add_locks: list[str] | None = None,
    remove_locks: list[str] | None = None,
    add_acceptance_criteria: list[str] | None = None,
    remove_acceptance_criteria: list[str] | None = None,
    ctx: Context | None = None,
) -> CallToolResult:
    """
    Update an existing task's properties.

    Updates task metadata including title, description, priority, labels, locks,
    and acceptance criteria. Does NOT allow updating status or dependencies
    (use specific tools for those operations).

    Args:
        context: Lodestar server context
        task_id: Task ID to update (required)
        title: New title (optional)
        description: New description (optional)
        priority: New priority value (optional)
        add_labels: Labels to add (optional)
        remove_labels: Labels to remove (optional)
        add_locks: Lock patterns to add (optional)
        remove_locks: Lock patterns to remove (optional)
        add_acceptance_criteria: Acceptance criteria to add (optional)
        remove_acceptance_criteria: Acceptance criteria to remove (optional)
        ctx: Optional MCP context for logging

    Returns:
        CallToolResult with updated task details or error
    """
    from lodestar.spec import SpecError, SpecFileAccessError, SpecLockError

    # Log the update attempt
    if ctx:
        await ctx.info(f"Updating task {task_id}")

    # Validate task ID
    try:
        validated_task_id = validate_task_id(task_id)
    except ValidationError as e:
        if ctx:
            await ctx.error(f"Invalid task ID: {task_id}")
        return error(str(e), error_code="INVALID_TASK_ID")

    # Reload spec to get latest state
    context.reload_spec()

    # Get task from spec
    task = context.spec.get_task(validated_task_id)
    if task is None:
        return error(
            f"Task {validated_task_id} not found",
            error_code="TASK_NOT_FOUND",
            details={"task_id": validated_task_id},
        )

    # Track what fields were updated
    updated_fields = []

    # Update fields
    if title is not None:
        task.title = title.strip()
        updated_fields.append("title")

    if description is not None:
        task.description = description
        updated_fields.append("description")

    if priority is not None:
        task.priority = priority
        updated_fields.append("priority")

    # Handle labels
    if add_labels:
        for label in add_labels:
            if label not in task.labels:
                task.labels.append(label)
        updated_fields.append("labels")

    if remove_labels:
        original_count = len(task.labels)
        task.labels = [lb for lb in task.labels if lb not in remove_labels]
        if len(task.labels) < original_count:
            updated_fields.append("labels")

    # Handle locks
    if add_locks:
        for lock in add_locks:
            if lock not in task.locks:
                task.locks.append(lock)
        updated_fields.append("locks")

    if remove_locks:
        original_count = len(task.locks)
        task.locks = [lk for lk in task.locks if lk not in remove_locks]
        if len(task.locks) < original_count:
            updated_fields.append("locks")

    # Handle acceptance criteria
    if add_acceptance_criteria:
        for criterion in add_acceptance_criteria:
            if criterion not in task.acceptance_criteria:
                task.acceptance_criteria.append(criterion)
        updated_fields.append("acceptance_criteria")

    if remove_acceptance_criteria:
        original_count = len(task.acceptance_criteria)
        task.acceptance_criteria = [
            ac for ac in task.acceptance_criteria if ac not in remove_acceptance_criteria
        ]
        if len(task.acceptance_criteria) < original_count:
            updated_fields.append("acceptance_criteria")

    # Check if any updates were made
    if not updated_fields:
        return error(
            "No updates specified",
            error_code="NO_UPDATES",
            details={"task_id": validated_task_id},
        )

    # Update timestamp
    now = datetime.now(UTC)
    task.updated_at = now

    # Save spec with error handling
    try:
        context.save_spec()
    except (SpecLockError, SpecFileAccessError) as e:
        if ctx:
            await ctx.error(f"Failed to save spec: {e}")
        return error(
            str(e),
            error_code=type(e).__name__.upper(),
            details={"task_id": validated_task_id},
            retriable=e.retriable,
            suggested_action=e.suggested_action,
        )
    except SpecError as e:
        if ctx:
            await ctx.error(f"Spec error: {e}")
        return error(
            str(e),
            error_code="SPEC_ERROR",
            details={"task_id": validated_task_id},
            retriable=getattr(e, "retriable", False),
            suggested_action=getattr(e, "suggested_action", None),
        )

    # Log successful update
    if ctx:
        await ctx.info(
            f"Successfully updated task {validated_task_id}: {', '.join(set(updated_fields))}"
        )

    # Log event (task.update)
    event_data = {
        "updated_fields": list(set(updated_fields)),
    }

    with contextlib.suppress(Exception):
        context.emit_event(
            event_type="task.update",
            task_id=validated_task_id,
            data=event_data,
        )

    # Notify clients of task update
    await notify_task_updated(ctx, validated_task_id)

    # Build summary
    summary = format_summary(
        "Updated",
        validated_task_id,
        f"- {', '.join(set(updated_fields))}",
    )

    # Build response
    response_data = {
        "ok": True,
        "taskId": validated_task_id,
        "title": task.title,
        "updatedFields": list(set(updated_fields)),
        "updatedAt": now.isoformat(),
    }

    return with_item(summary, item=response_data)


async def task_delete(
    context: LodestarContext,
    task_id: str,
    cascade: bool = False,
    ctx: Context | None = None,
) -> CallToolResult:
    """
    Delete a task (soft delete - sets status to DELETED).

    Tasks are soft-deleted, not physically removed from spec. Deleted tasks
    are hidden from list by default but can be viewed with status filter.

    If the task has dependent tasks:
    - Without cascade: Returns error with list of dependents
    - With cascade: Deletes this task and all its dependents

    Args:
        context: Lodestar server context
        task_id: Task ID to delete (required)
        cascade: Whether to cascade delete to dependent tasks (default: False)
        ctx: Optional MCP context for logging

    Returns:
        CallToolResult with deletion confirmation or error with conflict details
    """
    from lodestar.core.task_service import compute_cascade_delete
    from lodestar.spec import SpecError, SpecFileAccessError, SpecLockError

    # Log the delete attempt
    if ctx:
        cascade_msg = " (with cascade)" if cascade else ""
        await ctx.info(f"Deleting task {task_id}{cascade_msg}")

    # Validate task ID
    try:
        validated_task_id = validate_task_id(task_id)
    except ValidationError as e:
        if ctx:
            await ctx.error(f"Invalid task ID: {task_id}")
        return error(str(e), error_code="INVALID_TASK_ID")

    # Reload spec to get latest state
    context.reload_spec()

    # Get task from spec
    task = context.spec.get_task(validated_task_id)
    if task is None:
        return error(
            f"Task {validated_task_id} not found",
            error_code="TASK_NOT_FOUND",
            details={"task_id": validated_task_id},
        )

    # Check if already deleted
    if task.status == TaskStatus.DELETED:
        return error(
            f"Task {validated_task_id} is already deleted",
            error_code="ALREADY_DELETED",
            details={"task_id": validated_task_id},
        )

    # Check for active leases
    active_lease = context.db.get_active_lease(validated_task_id)
    if active_lease:
        return error(
            f"Task {validated_task_id} has active lease held by {active_lease.agent_id}. Release the lease first.",
            error_code="ACTIVE_LEASE",
            details={
                "task_id": validated_task_id,
                "claimed_by": active_lease.agent_id,
                "expires_at": active_lease.expires_at.isoformat(),
            },
        )

    # Use service to compute cascade delete targets
    delete_result = compute_cascade_delete(validated_task_id, context.spec, cascade)

    # Check if blocked by dependents
    if delete_result.blocked_by:
        return error(
            f"Task {validated_task_id} has {len(delete_result.blocked_by)} dependent task(s). Use cascade=true to delete all.",
            error_code="HAS_DEPENDENTS",
            details={
                "task_id": validated_task_id,
                "dependents": delete_result.blocked_by,
                "dependent_titles": {
                    dep_id: context.spec.tasks[dep_id].title for dep_id in delete_result.blocked_by
                },
            },
        )

    # Mark all tasks as deleted
    deleted_tasks = []
    now = datetime.now(UTC)
    for tid in delete_result.tasks_to_delete:
        t = context.spec.tasks[tid]
        t.status = TaskStatus.DELETED
        t.updated_at = now
        deleted_tasks.append({"id": tid, "title": t.title})

    # Save spec with error handling
    try:
        context.save_spec()
    except (SpecLockError, SpecFileAccessError) as e:
        if ctx:
            await ctx.error(f"Failed to save spec: {e}")
        return error(
            str(e),
            error_code=type(e).__name__.upper(),
            details={"task_id": validated_task_id},
            retriable=e.retriable,
            suggested_action=e.suggested_action,
        )
    except SpecError as e:
        if ctx:
            await ctx.error(f"Spec error: {e}")
        return error(
            str(e),
            error_code="SPEC_ERROR",
            details={"task_id": validated_task_id},
            retriable=getattr(e, "retriable", False),
            suggested_action=getattr(e, "suggested_action", None),
        )

    # Log successful deletion
    if ctx:
        if len(deleted_tasks) > 1:
            await ctx.info(
                f"Successfully deleted {len(deleted_tasks)} tasks (cascade): {', '.join([t['id'] for t in deleted_tasks])}"
            )
        else:
            await ctx.info(f"Successfully deleted task {validated_task_id}")

    # Log event (task.delete)
    event_data = {
        "cascade": cascade,
        "deleted_count": len(deleted_tasks),
    }

    with contextlib.suppress(Exception):
        context.emit_event(
            event_type="task.delete",
            task_id=validated_task_id,
            data=event_data,
        )

    # Notify clients of task updates
    for deleted_task in deleted_tasks:
        await notify_task_updated(ctx, deleted_task["id"])

    # Build summary
    if len(deleted_tasks) > 1:
        summary = format_summary(
            "Deleted",
            f"{len(deleted_tasks)} tasks",
            f"(cascade from {validated_task_id})",
        )
    else:
        summary = format_summary("Deleted", validated_task_id)

    # Build response
    response_data = {
        "ok": True,
        "taskId": validated_task_id,
        "deletedTasks": deleted_tasks,
        "deletedCount": len(deleted_tasks),
        "cascade": cascade,
    }

    return with_item(summary, item=response_data)


async def task_claim(
    context: LodestarContext,
    task_id: str,
    agent_id: str,
    ttl_seconds: int | None = None,
    force: bool = False,
    ctx: Context | None = None,
) -> CallToolResult:
    """
    Claim a task with a time-limited lease.

    Creates an exclusive claim on a task that auto-expires after the TTL period.
    Claims fail if the task is already claimed or not claimable.

    Args:
        context: Lodestar server context
        task_id: Task ID to claim (required)
        agent_id: Agent ID making the claim (required)
        ttl_seconds: Lease duration in seconds (optional, default 900 = 15min, server clamps to bounds)
        force: Bypass lock conflict warnings (optional, default False)

    Returns:
        CallToolResult with lease object on success or conflict details on failure
    """
    # Log the claim attempt
    if ctx:
        await ctx.info(f"Claiming task {task_id} for agent {agent_id}")

    # Validate inputs
    try:
        validated_task_id = validate_task_id(task_id)
    except ValidationError as e:
        if ctx:
            await ctx.error(f"Invalid task ID: {task_id}")
        return error(str(e), error_code="INVALID_TASK_ID")

    if not agent_id or not agent_id.strip():
        return error(
            "agent_id is required and cannot be empty",
            error_code="INVALID_AGENT_ID",
        )

    # Validate agent exists in registry
    if not context.db.agent_exists(agent_id.strip()):
        return error(
            f"Agent '{agent_id}' is not registered. Use lodestar_agent_join first.",
            error_code="AGENT_NOT_REGISTERED",
            details={"agent_id": agent_id},
        )

    # Validate and clamp TTL (default 15min = 900s, min 60s, max 86400s = 24h)
    if ttl_seconds is None:
        ttl_seconds = 900  # 15 minutes
    elif ttl_seconds < 60:
        ttl_seconds = 60  # Min 1 minute
    elif ttl_seconds > 86400:
        ttl_seconds = 86400  # Max 24 hours

    # Reload spec to get latest state
    context.reload_spec()

    # Check task exists
    task = context.spec.get_task(validated_task_id)
    if task is None:
        return error(
            f"Task {validated_task_id} not found",
            error_code="TASK_NOT_FOUND",
            details={"task_id": validated_task_id},
        )

    # Check task is claimable
    verified = context.spec.get_verified_tasks()
    if not task.is_claimable(verified):
        unmet_deps = [d for d in task.depends_on if d not in verified]

        # Build helpful error message
        if unmet_deps:
            error_msg = (
                f"Task {validated_task_id} is not claimable because {len(unmet_deps)} "
                f"{'dependency' if len(unmet_deps) == 1 else 'dependencies'} must be verified first. "
                f"Note: Dependencies must be marked as 'verified' (not just 'done') to unblock dependent tasks."
            )
        else:
            error_msg = f"Task {validated_task_id} is not claimable (status: {task.status.value})"

        return error(
            error_msg,
            error_code="TASK_NOT_CLAIMABLE",
            details={
                "task_id": validated_task_id,
                "status": task.status.value,
                "unmet_dependencies": unmet_deps,
                "note": "Dependencies must be verified before dependent tasks become claimable. Use task.verify after task.done.",
            },
        )

    # Check for lock conflicts with actively-leased tasks
    warnings = []
    if task.locks and not force:
        lock_warnings = detect_lock_conflicts(task, context.spec, context.db)
        for warning in lock_warnings:
            warnings.append(
                {
                    "type": "LOCK_CONFLICT",
                    "message": warning,
                    "severity": "warning",
                }
            )

    # Create lease
    duration = timedelta(seconds=ttl_seconds)
    lease = Lease(
        task_id=validated_task_id,
        agent_id=agent_id,
        expires_at=datetime.now(UTC) + duration,
    )

    created_lease = context.db.create_lease(lease)

    if created_lease is None:
        # Task already claimed
        existing = context.db.get_active_lease(validated_task_id)
        conflict_details = {
            "task_id": validated_task_id,
            "claimed_by": existing.agent_id if existing else "unknown",
        }
        if existing:
            conflict_details["expires_at"] = existing.expires_at.isoformat()
            remaining = existing.expires_at - datetime.now(UTC)
            conflict_details["expires_in_seconds"] = int(remaining.total_seconds())

        if ctx:
            await ctx.warning(
                f"Task {validated_task_id} already claimed by {existing.agent_id if existing else 'unknown'}"
            )

        return error(
            f"Task {validated_task_id} already claimed by {existing.agent_id if existing else 'unknown'}",
            error_code="TASK_ALREADY_CLAIMED",
            details={"conflict": conflict_details},
        )

    # Log event (task.claim) - don't fail the claim if event logging fails
    with contextlib.suppress(Exception):
        context.emit_event(
            event_type="task.claim",
            task_id=validated_task_id,
            agent_id=agent_id,
            data={
                "lease_id": created_lease.lease_id,
                "ttl_seconds": ttl_seconds,
            },
        )

    # Notify clients of task update
    await notify_task_updated(ctx, validated_task_id)

    # Log successful claim
    if ctx:
        await ctx.info(
            f"Successfully claimed task {validated_task_id} (lease: {created_lease.lease_id}, expires in {ttl_seconds}s)"
        )

    # Check for handoff messages from previous agent(s)
    unread_messages = context.db.get_task_unread_messages(validated_task_id, agent_id, limit=10)
    unread_count = context.db.get_task_message_count(validated_task_id, unread_by=agent_id)

    handoff_message = None
    if unread_messages:
        # Get the most recent message for inline display
        latest = unread_messages[-1]  # Messages are in chronological order
        handoff_message = {
            "messageId": latest.message_id,
            "fromAgentId": latest.from_agent_id,
            "createdAt": latest.created_at.isoformat(),
            "text": latest.text,
            "subject": latest.meta.get("subject"),
            "severity": latest.meta.get("severity"),
        }

        if ctx:
            await ctx.info(
                f"Task has {unread_count} unread message(s) - most recent from {latest.from_agent_id}"
            )

    # Build lease object for response
    lease_data = {
        "leaseId": created_lease.lease_id,
        "taskId": validated_task_id,
        "agentId": agent_id,
        "expiresAt": created_lease.expires_at.isoformat(),
        "ttlSeconds": ttl_seconds,
        "createdAt": created_lease.created_at.isoformat(),
    }

    # Build summary
    summary = format_summary(
        "Claimed",
        validated_task_id,
        f"by {agent_id}",
    )

    # Build response with warnings and handoff message
    response_data = {
        "ok": True,
        "lease": lease_data,
        "warnings": warnings,
    }

    if handoff_message:
        response_data["handoffMessage"] = handoff_message
        response_data["unreadCount"] = unread_count

    return with_item(summary, item=response_data)


async def task_release(
    context: LodestarContext,
    task_id: str,
    agent_id: str,
    reason: str | None = None,
    ctx: Context | None = None,
) -> CallToolResult:
    """
    Release a claim on a task before TTL expiry.

    Frees the task for other agents to claim. Use this when blocked or
    unable to complete the task.

    Args:
        context: Lodestar server context
        task_id: Task ID to release (required)
        agent_id: Agent ID releasing the claim (required)
        reason: Optional reason for releasing (for logging/audit)

    Returns:
        CallToolResult with success status and previous lease details
    """
    # Log the release attempt
    if ctx:
        reason_msg = f" (reason: {reason})" if reason else ""
        await ctx.info(f"Releasing task {task_id} for agent {agent_id}{reason_msg}")

    # Validate inputs
    try:
        validated_task_id = validate_task_id(task_id)
    except ValidationError as e:
        if ctx:
            await ctx.error(f"Invalid task ID: {task_id}")
        return error(str(e), error_code="INVALID_TASK_ID")

    if not agent_id or not agent_id.strip():
        return error(
            "agent_id is required and cannot be empty",
            error_code="INVALID_AGENT_ID",
        )

    # Get active lease before releasing
    active_lease = context.db.get_active_lease(validated_task_id)

    if active_lease is None:
        return error(
            f"No active lease for task {validated_task_id}",
            error_code="NO_ACTIVE_LEASE",
            details={"task_id": validated_task_id},
        )

    # Verify the agent_id matches the lease
    if active_lease.agent_id != agent_id:
        return error(
            f"Task {validated_task_id} is claimed by {active_lease.agent_id}, not {agent_id}",
            error_code="LEASE_MISMATCH",
            details={
                "task_id": validated_task_id,
                "claimed_by": active_lease.agent_id,
                "requested_by": agent_id,
            },
        )

    # Release the lease
    success = context.db.release_lease(validated_task_id, agent_id)

    if not success:
        # This shouldn't happen since we checked for active lease above
        if ctx:
            await ctx.error(f"Failed to release lease for task {validated_task_id}")
        return error(
            f"Failed to release lease for task {validated_task_id}",
            error_code="RELEASE_FAILED",
            details={"task_id": validated_task_id, "agent_id": agent_id},
        )

    # Log successful release
    if ctx:
        await ctx.info(f"Successfully released task {validated_task_id}")

    # Log event (task.release)
    event_data = {
        "lease_id": active_lease.lease_id,
    }
    if reason:
        event_data["reason"] = reason

    with contextlib.suppress(Exception):
        context.emit_event(
            event_type="task.release",
            task_id=validated_task_id,
            agent_id=agent_id,
            data=event_data,
        )

    # Notify clients of task update
    await notify_task_updated(ctx, validated_task_id)

    # Build previous lease object for response
    previous_lease = {
        "leaseId": active_lease.lease_id,
        "taskId": validated_task_id,
        "agentId": agent_id,
        "expiresAt": active_lease.expires_at.isoformat(),
        "createdAt": active_lease.created_at.isoformat(),
    }

    # Build summary
    summary = format_summary(
        "Released",
        validated_task_id,
        f"by {agent_id}",
    )

    # Build response
    response_data = {
        "ok": True,
        "previousLease": previous_lease,
    }

    if reason:
        response_data["reason"] = reason

    return with_item(summary, item=response_data)


async def task_done(
    context: LodestarContext,
    task_id: str,
    agent_id: str,
    note: str | None = None,
    ctx: Context | None = None,
) -> CallToolResult:
    """
    Mark a task as done (pending verification).

    Sets the task status to 'done'. The task is considered complete but
    still needs verification before it unblocks dependent tasks.

    Args:
        context: Lodestar server context
        task_id: Task ID to mark as done (required)
        agent_id: Agent ID marking the task as done (required)
        note: Optional note about completion (for logging/audit)

    Returns:
        CallToolResult with success status and warnings
    """
    from lodestar.spec import SpecError, SpecFileAccessError, SpecLockError

    # Log the done marking attempt
    if ctx:
        note_msg = f" ({note})" if note else ""
        await ctx.info(f"Marking task {task_id} as done by agent {agent_id}{note_msg}")

    # Validate inputs
    try:
        validated_task_id = validate_task_id(task_id)
    except ValidationError as e:
        if ctx:
            await ctx.error(f"Invalid task ID: {task_id}")
        return error(str(e), error_code="INVALID_TASK_ID")

    if not agent_id or not agent_id.strip():
        return error(
            "agent_id is required and cannot be empty",
            error_code="INVALID_AGENT_ID",
        )

    # Reload spec to get latest state
    context.reload_spec()

    # Get task from spec
    task = context.spec.get_task(validated_task_id)
    if task is None:
        return error(
            f"Task {validated_task_id} not found",
            error_code="TASK_NOT_FOUND",
            details={"task_id": validated_task_id},
        )

    # Check if task is already done or verified
    warnings = []
    if task.status == TaskStatus.DONE:
        warnings.append(
            {
                "type": "ALREADY_DONE",
                "message": f"Task {validated_task_id} is already marked as done",
                "severity": "info",
            }
        )
    elif task.status == TaskStatus.VERIFIED:
        warnings.append(
            {
                "type": "ALREADY_VERIFIED",
                "message": f"Task {validated_task_id} is already verified",
                "severity": "info",
            }
        )

    # Check if task is claimed by the agent
    active_lease = context.db.get_active_lease(validated_task_id)
    if active_lease and active_lease.agent_id != agent_id:
        warnings.append(
            {
                "type": "NOT_CLAIMED_BY_YOU",
                "message": f"Task {validated_task_id} is claimed by {active_lease.agent_id}, not {agent_id}",
                "severity": "warning",
            }
        )

    # Update task status
    task.status = TaskStatus.DONE
    task.updated_at = datetime.now(UTC)
    task.completed_by = agent_id
    task.completed_at = datetime.now(UTC)

    # Save spec with error handling
    try:
        context.save_spec()
    except (SpecLockError, SpecFileAccessError) as e:
        # Return structured error with retriable info and current state
        if ctx:
            await ctx.error(f"Failed to save spec: {e}")
        return error(
            str(e),
            error_code=type(e).__name__.upper(),
            details={"task_id": validated_task_id},
            retriable=e.retriable,
            suggested_action=e.suggested_action,
            current_state={
                "task_id": validated_task_id,
                "task_status": task.status.value,
                "operation": "task.done",
            },
        )
    except SpecError as e:
        # Handle other spec errors
        if ctx:
            await ctx.error(f"Spec error: {e}")
        return error(
            str(e),
            error_code="SPEC_ERROR",
            details={"task_id": validated_task_id},
            retriable=getattr(e, "retriable", False),
            suggested_action=getattr(e, "suggested_action", None),
        )

    # Release lease if exists
    if active_lease:
        context.db.release_lease(validated_task_id, active_lease.agent_id)

    # Log successful marking as done
    if ctx:
        await ctx.info(f"Successfully marked task {validated_task_id} as done")

    # Log event (task.done)
    event_data = {
        "agent_id": agent_id,
    }
    if note:
        event_data["note"] = note

    with contextlib.suppress(Exception):
        context.emit_event(
            event_type="task.done",
            task_id=validated_task_id,
            agent_id=agent_id,
            data=event_data,
        )

    # Notify clients of task update
    await notify_task_updated(ctx, validated_task_id)

    # Check if this task has dependents waiting
    context.reload_spec()
    dependents = [t for t in context.spec.tasks.values() if validated_task_id in t.depends_on]
    if dependents:
        waiting_count = len([d for d in dependents if d.status == TaskStatus.READY])
        if waiting_count > 0:
            warnings.append(
                {
                    "type": "DEPENDENTS_WAITING",
                    "message": f"{waiting_count} dependent task(s) are waiting for verification of this task",
                    "severity": "info",
                    "note": f"Use task.verify to mark as verified and unblock {waiting_count} dependent task(s)",
                }
            )

    # Build summary
    summary = format_summary(
        "Done",
        validated_task_id,
        "- pending verification",
    )

    # Build response
    response_data = {
        "ok": True,
        "taskId": validated_task_id,
        "status": "done",
        "warnings": warnings,
        "nextStep": "Use task.verify to mark as verified and unblock dependent tasks"
        if dependents
        else None,
    }

    if note:
        response_data["note"] = note

    return with_item(summary, item=response_data)


async def task_verify(
    context: LodestarContext,
    task_id: str,
    agent_id: str,
    note: str | None = None,
    ctx: Context | None = None,
) -> CallToolResult:
    """
    Mark a task as verified (unblocks dependents).

    Verifies that the task is complete. This changes the status from 'done'
    to 'verified' and unblocks any dependent tasks that are waiting on this one.

    If the client provides a progressToken in the request metadata, this operation
    will emit progress notifications at key stages.

    Args:
        context: Lodestar server context
        task_id: Task ID to verify (required)
        agent_id: Agent ID verifying the task (required)
        note: Optional note about verification (for logging/audit)
        ctx: Optional MCP context for logging and progress notifications

    Returns:
        CallToolResult with success status and list of newly unblocked task IDs
    """
    from lodestar.spec import SpecError, SpecFileAccessError, SpecLockError

    # Log the verify attempt
    if ctx:
        note_msg = f" ({note})" if note else ""
        await ctx.info(f"Verifying task {task_id} by agent {agent_id}{note_msg}")

    # Report progress: validating inputs (10%)
    if ctx and hasattr(ctx, "report_progress"):
        await ctx.report_progress(10.0, 100.0, "Validating inputs..")

    # Validate inputs
    try:
        validated_task_id = validate_task_id(task_id)
    except ValidationError as e:
        if ctx:
            await ctx.error(f"Invalid task ID: {task_id}")
        return error(str(e), error_code="INVALID_TASK_ID")

    if not agent_id or not agent_id.strip():
        return error(
            "agent_id is required and cannot be empty",
            error_code="INVALID_AGENT_ID",
        )

    # Report progress: reloading spec (25%)
    if ctx and hasattr(ctx, "report_progress"):
        await ctx.report_progress(25.0, 100.0, "Reloading spec from disk..")

    # Reload spec to get latest state
    context.reload_spec()

    # Report progress: checking task status (40%)
    if ctx and hasattr(ctx, "report_progress"):
        await ctx.report_progress(40.0, 100.0, "Checking task status..")

    # Get task from spec
    task = context.spec.get_task(validated_task_id)
    if task is None:
        return error(
            f"Task {validated_task_id} not found",
            error_code="TASK_NOT_FOUND",
            details={"task_id": validated_task_id},
        )

    # Check if task is in DONE status
    warnings = []
    if task.status == TaskStatus.VERIFIED:
        warnings.append(
            {
                "type": "ALREADY_VERIFIED",
                "message": f"Task {validated_task_id} is already verified",
                "severity": "info",
            }
        )
    elif task.status != TaskStatus.DONE:
        return error(
            f"Task {validated_task_id} must be done before verifying (current status: {task.status.value})",
            error_code="TASK_NOT_DONE",
            details={
                "task_id": validated_task_id,
                "current_status": task.status.value,
            },
        )

    # Report progress: updating task status (55%)
    if ctx and hasattr(ctx, "report_progress"):
        await ctx.report_progress(55.0, 100.0, "Updating task status to verified..")

    # Update task status
    task.status = TaskStatus.VERIFIED
    task.updated_at = datetime.now(UTC)
    task.verified_by = agent_id
    task.verified_at = datetime.now(UTC)

    # Save spec with error handling
    try:
        context.save_spec()
    except (SpecLockError, SpecFileAccessError) as e:
        # Return structured error with retriable info and current state
        if ctx:
            await ctx.error(f"Failed to save spec: {e}")
        return error(
            str(e),
            error_code=type(e).__name__.upper(),
            details={"task_id": validated_task_id},
            retriable=e.retriable,
            suggested_action=e.suggested_action,
            current_state={
                "task_id": validated_task_id,
                "task_status": task.status.value,
                "operation": "task.verify",
            },
        )
    except SpecError as e:
        # Handle other spec errors
        if ctx:
            await ctx.error(f"Spec error: {e}")
        return error(
            str(e),
            error_code="SPEC_ERROR",
            details={"task_id": validated_task_id},
            retriable=getattr(e, "retriable", False),
            suggested_action=getattr(e, "suggested_action", None),
        )

    # Report progress: releasing lease (70%)
    if ctx and hasattr(ctx, "report_progress"):
        await ctx.report_progress(70.0, 100.0, "Releasing active lease..")

    # Auto-release any active lease
    active_lease = context.db.get_active_lease(validated_task_id)
    if active_lease:
        context.db.release_lease(validated_task_id, active_lease.agent_id)

    # Report progress: logging event (80%)
    if ctx and hasattr(ctx, "report_progress"):
        await ctx.report_progress(80.0, 100.0, "Logging verification event..")

    # Log event (task.verify)
    event_data = {
        "agent_id": agent_id,
    }
    if note:
        event_data["note"] = note

    with contextlib.suppress(Exception):
        context.emit_event(
            event_type="task.verify",
            task_id=validated_task_id,
            agent_id=agent_id,
            data=event_data,
        )

    # Notify clients of task update
    await notify_task_updated(ctx, validated_task_id)

    # Report progress: finding unblocked tasks (90%)
    if ctx and hasattr(ctx, "report_progress"):
        await ctx.report_progress(90.0, 100.0, "Finding newly unblocked tasks..")

    # Check what tasks are now unblocked
    context.reload_spec()  # Reload to get updated state
    new_claimable = context.spec.get_claimable_tasks()
    newly_unblocked = [t for t in new_claimable if validated_task_id in t.depends_on]
    newly_ready_ids = [t.id for t in newly_unblocked]

    # Notify clients about newly unblocked tasks
    for unblocked_id in newly_ready_ids:
        await notify_task_updated(ctx, unblocked_id)

    # Report progress: complete (100%)
    if ctx and hasattr(ctx, "report_progress"):
        if newly_ready_ids:
            await ctx.report_progress(
                100.0,
                100.0,
                f"Verified - unblocked {len(newly_ready_ids)} task(s)",
            )
        else:
            await ctx.report_progress(100.0, 100.0, "Verified - no tasks unblocked")

    # Log successful verification
    if ctx:
        if newly_ready_ids:
            await ctx.info(
                f"Successfully verified task {validated_task_id}, unblocked {len(newly_ready_ids)} task(s): {', '.join(newly_ready_ids)}"
            )
        else:
            await ctx.info(f"Successfully verified task {validated_task_id}")

    # Build summary
    summary = format_summary(
        "Verified",
        validated_task_id,
        f"- unblocked {len(newly_ready_ids)} task(s)" if newly_ready_ids else "",
    )

    # Build response
    response_data = {
        "ok": True,
        "taskId": validated_task_id,
        "status": "verified",
        "newlyReadyTaskIds": newly_ready_ids,
        "warnings": warnings,
    }

    if note:
        response_data["note"] = note

    return with_item(summary, item=response_data)


async def task_complete(
    context: LodestarContext,
    task_id: str,
    agent_id: str,
    note: str | None = None,
    ctx: Context | None = None,
) -> CallToolResult:
    """
    Mark a task as complete (done + verified in one atomic operation).

    This combines task_done and task_verify into a single atomic operation.
    Both status changes are made in a single spec save, preventing the task
    from being stuck in 'done' state if an agent crashes between operations.

    If the client provides a progressToken in the request metadata, this operation
    will emit progress notifications at key stages.

    Args:
        context: Lodestar server context
        task_id: Task ID to complete (required)
        agent_id: Agent ID completing the task (required)
        note: Optional note about completion (for logging/audit)
        ctx: Optional MCP context for logging and progress notifications

    Returns:
        CallToolResult with success status and list of newly unblocked task IDs
    """
    from lodestar.spec import SpecError, SpecFileAccessError, SpecLockError

    # Log the complete attempt
    if ctx:
        note_msg = f" ({note})" if note else ""
        await ctx.info(f"Completing task {task_id} (done + verify) by agent {agent_id}{note_msg}")

    # Report progress: validating inputs (10%)
    if ctx and hasattr(ctx, "report_progress"):
        await ctx.report_progress(10.0, 100.0, "Validating inputs..")

    # Validate inputs
    try:
        validated_task_id = validate_task_id(task_id)
    except ValidationError as e:
        if ctx:
            await ctx.error(f"Invalid task ID: {task_id}")
        return error(str(e), error_code="INVALID_TASK_ID")

    if not agent_id or not agent_id.strip():
        return error(
            "agent_id is required and cannot be empty",
            error_code="INVALID_AGENT_ID",
        )

    # Report progress: reloading spec (20%)
    if ctx and hasattr(ctx, "report_progress"):
        await ctx.report_progress(20.0, 100.0, "Reloading spec from disk..")

    # Reload spec to get latest state
    context.reload_spec()

    # Report progress: checking task status (30%)
    if ctx and hasattr(ctx, "report_progress"):
        await ctx.report_progress(30.0, 100.0, "Checking task status..")

    # Get task from spec
    task = context.spec.get_task(validated_task_id)
    if task is None:
        return error(
            f"Task {validated_task_id} not found",
            error_code="TASK_NOT_FOUND",
            details={"task_id": validated_task_id},
        )

    # Check if task is already verified
    warnings = []
    if task.status == TaskStatus.VERIFIED:
        warnings.append(
            {
                "type": "ALREADY_VERIFIED",
                "message": f"Task {validated_task_id} is already verified",
                "severity": "info",
            }
        )

    # Check if task is claimed by the agent
    active_lease = context.db.get_active_lease(validated_task_id)
    if active_lease and active_lease.agent_id != agent_id:
        warnings.append(
            {
                "type": "NOT_CLAIMED_BY_YOU",
                "message": f"Task {validated_task_id} is claimed by {active_lease.agent_id}, not {agent_id}",
                "severity": "warning",
            }
        )

    # Report progress: updating task status (50%)
    if ctx and hasattr(ctx, "report_progress"):
        await ctx.report_progress(50.0, 100.0, "Updating task status (done + verified)..")

    # Update task status to VERIFIED directly (atomic operation)
    now = datetime.now(UTC)
    task.status = TaskStatus.VERIFIED
    task.updated_at = now
    task.completed_by = agent_id
    task.completed_at = now
    task.verified_by = agent_id
    task.verified_at = now

    # Save spec with error handling (this is the atomic operation)
    try:
        context.save_spec()
    except (SpecLockError, SpecFileAccessError) as e:
        # Return structured error with retriable info and current state
        if ctx:
            await ctx.error(f"Failed to save spec: {e}")
        return error(
            str(e),
            error_code=type(e).__name__.upper(),
            details={"task_id": validated_task_id},
            retriable=e.retriable,
            suggested_action=e.suggested_action,
            current_state={
                "task_id": validated_task_id,
                "task_status": task.status.value,
                "operation": "task.complete",
            },
        )
    except SpecError as e:
        # Handle other spec errors
        if ctx:
            await ctx.error(f"Spec error: {e}")
        return error(
            str(e),
            error_code="SPEC_ERROR",
            details={"task_id": validated_task_id},
            retriable=getattr(e, "retriable", False),
            suggested_action=getattr(e, "suggested_action", None),
        )

    # Report progress: releasing lease (60%)
    if ctx and hasattr(ctx, "report_progress"):
        await ctx.report_progress(60.0, 100.0, "Releasing active lease..")

    # Auto-release any active lease
    if active_lease:
        context.db.release_lease(validated_task_id, active_lease.agent_id)

    # Report progress: logging events (70%)
    if ctx and hasattr(ctx, "report_progress"):
        await ctx.report_progress(70.0, 100.0, "Logging completion events..")

    # Log events (task.done and task.verify)
    event_data = {
        "agent_id": agent_id,
        "atomic": True,  # Indicate this was an atomic operation
    }
    if note:
        event_data["note"] = note

    # Log both done and verify events to maintain audit trail
    with contextlib.suppress(Exception):
        context.emit_event(
            event_type="task.done",
            task_id=validated_task_id,
            agent_id=agent_id,
            data=event_data,
        )
        context.emit_event(
            event_type="task.verify",
            task_id=validated_task_id,
            agent_id=agent_id,
            data=event_data,
        )

    # Notify clients of task update
    await notify_task_updated(ctx, validated_task_id)

    # Report progress: finding unblocked tasks (85%)
    if ctx and hasattr(ctx, "report_progress"):
        await ctx.report_progress(85.0, 100.0, "Finding newly unblocked tasks..")

    # Check what tasks are now unblocked
    context.reload_spec()  # Reload to get updated state
    new_claimable = context.spec.get_claimable_tasks()
    newly_unblocked = [t for t in new_claimable if validated_task_id in t.depends_on]
    newly_ready_ids = [t.id for t in newly_unblocked]

    # Notify clients about newly unblocked tasks
    for unblocked_id in newly_ready_ids:
        await notify_task_updated(ctx, unblocked_id)

    # Report progress: complete (100%)
    if ctx and hasattr(ctx, "report_progress"):
        if newly_ready_ids:
            await ctx.report_progress(
                100.0,
                100.0,
                f"Complete - unblocked {len(newly_ready_ids)} task(s)",
            )
        else:
            await ctx.report_progress(100.0, 100.0, "Complete - no tasks unblocked")

    # Log successful completion
    if ctx:
        if newly_ready_ids:
            await ctx.info(
                f"Successfully completed task {validated_task_id}, unblocked {len(newly_ready_ids)} task(s): {', '.join(newly_ready_ids)}"
            )
        else:
            await ctx.info(f"Successfully completed task {validated_task_id}")

    # Build summary
    summary = format_summary(
        "Complete",
        validated_task_id,
        f"- unblocked {len(newly_ready_ids)} task(s)" if newly_ready_ids else "",
    )

    # Build response
    response_data = {
        "ok": True,
        "taskId": validated_task_id,
        "status": "verified",
        "newlyReadyTaskIds": newly_ready_ids,
        "warnings": warnings,
    }

    if note:
        response_data["note"] = note

    return with_item(summary, item=response_data)


async def task_batch_verify(
    context: LodestarContext,
    task_ids: list[str],
    agent_id: str,
    notes: dict[str, str] | None = None,
    ctx: Context | None = None,
) -> CallToolResult:
    """
    Verify multiple tasks in a single batch operation.

    This is more efficient than calling task_verify multiple times when completing
    multiple independent tasks in sequence. Partial success is allowed - some tasks
    may succeed while others fail.

    Args:
        context: Lodestar server context
        task_ids: List of task IDs to verify (required, non-empty)
        agent_id: Agent ID verifying the tasks (required)
        notes: Optional dict mapping task IDs to verification notes
        ctx: Optional MCP context for logging

    Returns:
        CallToolResult with summary of successes and failures for each task
    """
    from lodestar.spec import SpecError

    # Log the batch verify attempt
    if ctx:
        await ctx.info(f"Batch verifying {len(task_ids)} tasks for agent {agent_id}")

    # Validate inputs
    if not task_ids:
        return error(
            "task_ids is required and cannot be empty",
            error_code="INVALID_INPUT",
        )

    if not agent_id or not agent_id.strip():
        return error(
            "agent_id is required and cannot be empty",
            error_code="INVALID_AGENT_ID",
        )

    # Limit batch size
    if len(task_ids) > 100:
        return error(
            f"Batch size exceeds maximum of 100 tasks (got {len(task_ids)})",
            error_code="BATCH_TOO_LARGE",
            details={"batch_size": len(task_ids), "max_size": 100},
        )

    # Validate task IDs
    validated_task_ids = []
    for task_id in task_ids:
        try:
            validated_task_ids.append(validate_task_id(task_id))
        except ValidationError as e:
            if ctx:
                await ctx.error(f"Invalid task ID in batch: {task_id}")
            return error(
                f"Invalid task ID in batch: {task_id} - {e}",
                error_code="INVALID_TASK_ID",
            )

    # Track results for each task
    results = []
    all_newly_ready = set()

    # Process each task
    for task_id in validated_task_ids:
        try:
            # Reload spec for each verification to get latest state
            context.reload_spec()

            # Get task from spec
            task = context.spec.get_task(task_id)
            if task is None:
                results.append(
                    {
                        "taskId": task_id,
                        "success": False,
                        "error": f"Task {task_id} not found",
                        "errorCode": "TASK_NOT_FOUND",
                    }
                )
                if ctx:
                    await ctx.warning(f"Task {task_id} not found in batch verify")
                continue

            # Check if task is in DONE status (or already VERIFIED)
            if task.status == TaskStatus.VERIFIED:
                results.append(
                    {
                        "taskId": task_id,
                        "success": True,
                        "status": "verified",
                        "newlyReadyTaskIds": [],
                        "warning": "Task was already verified",
                    }
                )
                if ctx:
                    await ctx.info(f"Task {task_id} already verified")
                continue
            elif task.status != TaskStatus.DONE:
                results.append(
                    {
                        "taskId": task_id,
                        "success": False,
                        "error": f"Task must be done before verifying (current status: {task.status.value})",
                        "errorCode": "TASK_NOT_DONE",
                    }
                )
                if ctx:
                    await ctx.warning(f"Task {task_id} not done (status: {task.status.value})")
                continue

            # Update task status
            task.status = TaskStatus.VERIFIED
            task.updated_at = datetime.now(UTC)
            task.verified_by = agent_id
            task.verified_at = datetime.now(UTC)

            # Get note for this task if provided
            note = notes.get(task_id) if notes else None

            # Save spec with error handling
            try:
                context.save_spec()
            except SpecError as e:
                # Log the error and continue with remaining tasks
                results.append(
                    {
                        "taskId": task_id,
                        "success": False,
                        "error": str(e),
                        "errorCode": type(e).__name__.upper(),
                        "retriable": getattr(e, "retriable", False),
                        "suggestedAction": getattr(e, "suggested_action", None),
                    }
                )
                if ctx:
                    await ctx.error(f"Failed to verify {task_id}: {e}")
                continue

            # Auto-release any active lease
            active_lease = context.db.get_active_lease(task_id)
            if active_lease:
                context.db.release_lease(task_id, active_lease.agent_id)

            # Log event
            event_data = {"agent_id": agent_id, "batch": True}
            if note:
                event_data["note"] = note

            with contextlib.suppress(Exception):
                context.emit_event(
                    event_type="task.verify",
                    task_id=task_id,
                    agent_id=agent_id,
                    data=event_data,
                )

            # Notify clients
            await notify_task_updated(ctx, task_id)

            # Check what tasks are now unblocked
            context.reload_spec()
            new_claimable = context.spec.get_claimable_tasks()
            newly_unblocked = [t for t in new_claimable if task_id in t.depends_on]
            newly_ready_ids = [t.id for t in newly_unblocked]

            # Add to global set of newly ready tasks
            all_newly_ready.update(newly_ready_ids)

            # Notify about newly unblocked tasks
            for unblocked_id in newly_ready_ids:
                await notify_task_updated(ctx, unblocked_id)

            # Record success
            results.append(
                {
                    "taskId": task_id,
                    "success": True,
                    "status": "verified",
                    "newlyReadyTaskIds": newly_ready_ids,
                }
            )

            if ctx:
                if newly_ready_ids:
                    await ctx.info(f"Verified {task_id}, unblocked {len(newly_ready_ids)} task(s)")
                else:
                    await ctx.info(f"Verified {task_id}")

        except Exception as e:
            # Catch unexpected errors
            results.append(
                {
                    "taskId": task_id,
                    "success": False,
                    "error": str(e),
                    "errorCode": "UNEXPECTED_ERROR",
                }
            )
            if ctx:
                await ctx.error(f"Unexpected error verifying {task_id}: {e}")

    # Calculate summary stats
    success_count = sum(1 for r in results if r["success"])
    failure_count = len(results) - success_count

    # Build summary
    if failure_count == 0 or success_count == 0:
        pass
    else:
        pass

    # Build response
    response_data = {
        "ok": success_count > 0,  # ok if at least one succeeded
        "summary": {
            "total": len(task_ids),
            "succeeded": success_count,
            "failed": failure_count,
        },
        "results": results,
        "allNewlyReadyTaskIds": sorted(all_newly_ready),
    }

    # Use format_summary for consistent formatting
    formatted_summary = format_summary(
        "Batch Verify",
        f"{success_count}/{len(task_ids)} tasks",
        f"unblocked {len(all_newly_ready)} task(s)" if all_newly_ready else "",
    )

    return with_item(formatted_summary, item=response_data)


def register_task_mutation_tools(mcp: object, context: LodestarContext) -> None:
    """
    Register task mutation tools with the FastMCP server.

    Args:
        mcp: FastMCP server instance
        context: Lodestar context to use for all tools
    """

    @mcp.tool(name="lodestar_task_create")
    async def create_tool(
        title: str,
        description: str | None = None,
        acceptance_criteria: list[str] | None = None,
        priority: int = 100,
        status: str = "ready",
        task_id: str | None = None,
        depends_on: list[str] | None = None,
        labels: list[str] | None = None,
        locks: list[str] | None = None,
        prd_source: str | None = None,
        prd_refs: list[str] | None = None,
        prd_excerpt: str | None = None,
        validate_prd: bool = True,
        ctx: Context | None = None,
    ) -> CallToolResult:
        """Create a new task in the spec.

        Creates a new task with all specified parameters, validates dependencies and PRD
        references (if enabled), saves to spec.yaml, and emits a task.create event.

        This tool enables planning agents to programmatically create well-structured tasks
        following the INVEST criteria (Independent, Negotiable, Valuable, Estimable, Small, Testable).

        Task Design Guidelines:
        - Keep tasks small (completable within 15-minute lease)
        - Write clear descriptions with WHAT/WHERE/WHY/SCOPE/ACCEPT/REFS sections
        - Reference PRD sections when available
        - Define measurable acceptance criteria
        - Set appropriate dependencies to sequence work
        - Use locks to prevent concurrent file modifications

        Args:
            title: Task title (required, concise statement of goal)
            description: Task description (optional, recommended format: WHAT/WHERE/WHY/SCOPE/ACCEPT/REFS)
            acceptance_criteria: List of testable acceptance criteria (optional, e.g., ["Tests pass", "Returns 200"])
            priority: Priority value, lower = higher priority (default: 100, range: 1-999)
            status: Initial status (default: "ready", options: todo, ready, blocked, done, verified)
            task_id: Task ID (optional, auto-generated as T### if not provided)
            depends_on: List of task IDs this task depends on (optional, establishes execution order)
            labels: List of labels for categorization (optional, e.g., ["feature", "frontend"])
            locks: List of file glob patterns for lock-based coordination (optional, e.g., ["src/auth/**"])
            prd_source: Path to PRD file relative to repo root (optional, e.g., "PRD.md")
            prd_refs: List of PRD section anchors (optional, e.g., ["#feature-requirements"])
            prd_excerpt: Frozen PRD excerpt to embed in task (optional)
            validate_prd: Whether to validate PRD file and refs exist (default: True)

        Returns:
            Success response with task details (taskId, title, status, priority, createdAt)
            or error with validation details.

            Possible errors:
            - INVALID_TITLE: Title missing or empty
            - INVALID_STATUS: Status not in valid options
            - INVALID_TASK_ID: Malformed task ID
            - DUPLICATE_TASK_ID: Task ID already exists
            - UNKNOWN_DEPENDENCIES: Referenced dependencies don't exist
            - DEPENDENCY_CYCLE: Would create circular dependency
            - PRD_FILE_NOT_FOUND: PRD file doesn't exist (when validate_prd=true)
            - PRD_ANCHORS_NOT_FOUND: PRD refs not found (when validate_prd=true)
            - SPEC_LOCK_ERROR: Couldn't acquire lock on spec file
            - SPEC_FILE_ACCESS_ERROR: File system error

        Example:
            lodestar_task_create(
                title="Add email validation to signup form",
                description="WHAT: Add client-side email format validation\\nWHERE: src/components/SignupForm.tsx\\nWHY: Users submit invalid emails causing bounce issues\\nSCOPE: Client-side only, server validation is separate task\\nACCEPT: Invalid emails show error, valid emails pass, tests cover edge cases",
                acceptance_criteria=["Invalid emails show inline error", "Valid emails pass validation", "Unit tests cover: empty, missing @, missing domain"],
                priority=2,
                depends_on=["F041"],
                labels=["feature", "frontend"],
                locks=["src/components/SignupForm.tsx", "src/utils/validation.ts"],
                prd_source="PRD.md",
                prd_refs=["#signup-requirements"]
            )
        """
        return await task_create(
            context=context,
            title=title,
            description=description,
            acceptance_criteria=acceptance_criteria,
            priority=priority,
            status=status,
            task_id=task_id,
            depends_on=depends_on,
            labels=labels,
            locks=locks,
            prd_source=prd_source,
            prd_refs=prd_refs,
            prd_excerpt=prd_excerpt,
            validate_prd=validate_prd,
            ctx=ctx,
        )

    @mcp.tool(name="lodestar_task_update")
    async def update_tool(
        task_id: str,
        title: str | None = None,
        description: str | None = None,
        priority: int | None = None,
        add_labels: list[str] | None = None,
        remove_labels: list[str] | None = None,
        add_locks: list[str] | None = None,
        remove_locks: list[str] | None = None,
        add_acceptance_criteria: list[str] | None = None,
        remove_acceptance_criteria: list[str] | None = None,
        ctx: Context | None = None,
    ) -> CallToolResult:
        """Update an existing task's properties.

        Updates task metadata including title, description, priority, labels, locks,
        and acceptance criteria. Does NOT allow updating status or dependencies
        (use specific tools like task_done, task_verify for status changes).

        This tool is useful for:
        - Refining task details during planning
        - Adjusting priorities as work progresses
        - Adding/removing labels for better categorization
        - Updating acceptance criteria based on new requirements
        - Managing file locks for coordination

        Args:
            task_id: Task ID to update (required)
            title: New title (optional)
            description: New description (optional)
            priority: New priority value, lower = higher priority (optional)
            add_labels: Labels to add (optional, e.g., ["urgent", "frontend"])
            remove_labels: Labels to remove (optional)
            add_locks: Lock patterns to add (optional, e.g., ["src/components/**"])
            remove_locks: Lock patterns to remove (optional)
            add_acceptance_criteria: Acceptance criteria to add (optional)
            remove_acceptance_criteria: Acceptance criteria to remove (optional)

        Returns:
            Success response with updated task details and list of updated fields,
            or error if task not found or no updates specified.

            Possible errors:
            - INVALID_TASK_ID: Malformed task ID
            - TASK_NOT_FOUND: Task doesn't exist
            - NO_UPDATES: No update parameters provided
            - SPEC_LOCK_ERROR: Couldn't acquire lock on spec file
            - SPEC_FILE_ACCESS_ERROR: File system error

        Example:
            lodestar_task_update(
                task_id="T042",
                title="Updated: Add email validation",
                priority=1,
                add_labels=["urgent"],
                add_acceptance_criteria=["Email validation works on mobile"]
            )
        """
        return await task_update(
            context=context,
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            add_labels=add_labels,
            remove_labels=remove_labels,
            add_locks=add_locks,
            remove_locks=remove_locks,
            add_acceptance_criteria=add_acceptance_criteria,
            remove_acceptance_criteria=remove_acceptance_criteria,
            ctx=ctx,
        )

    @mcp.tool(name="lodestar_task_delete")
    async def delete_tool(
        task_id: str,
        cascade: bool = False,
        ctx: Context | None = None,
    ) -> CallToolResult:
        """Delete a task (soft delete - sets status to DELETED).

        Tasks are soft-deleted, not physically removed from spec. Deleted tasks
        are hidden from list by default but can be viewed with status="deleted" filter.

        This tool handles dependency validation:
        - Without cascade: Returns error if task has dependents
        - With cascade: Deletes this task and all its dependent tasks

        Active leases must be released before deletion. This prevents accidental
        deletion of tasks being actively worked on.

        Args:
            task_id: Task ID to delete (required)
            cascade: Whether to cascade delete to dependent tasks (default: False)

        Returns:
            Success response with list of deleted tasks (may be multiple with cascade),
            or error with conflict details.

            Possible errors:
            - INVALID_TASK_ID: Malformed task ID
            - TASK_NOT_FOUND: Task doesn't exist
            - ALREADY_DELETED: Task is already deleted
            - ACTIVE_LEASE: Task has active lease (must release first)
            - HAS_DEPENDENTS: Task has dependents (use cascade=true to delete all)
            - SPEC_LOCK_ERROR: Couldn't acquire lock on spec file
            - SPEC_FILE_ACCESS_ERROR: File system error

        Example:
            # Delete single task (fails if has dependents)
            lodestar_task_delete(task_id="T042")

            # Delete task and all dependents
            lodestar_task_delete(task_id="T001", cascade=true)
        """
        return await task_delete(
            context=context,
            task_id=task_id,
            cascade=cascade,
            ctx=ctx,
        )

    @mcp.tool(name="lodestar_task_claim")
    async def claim_tool(
        task_id: str,
        agent_id: str,
        ttl_seconds: int | None = None,
        force: bool = False,
        ctx: Context | None = None,
    ) -> CallToolResult:
        """Claim a task with a time-limited lease.

        Creates an exclusive claim on a task that auto-expires after the TTL period.
        This prevents other agents from claiming the same task while you work on it.

        Claims will fail if:
        - Task is already claimed by another agent
        - Task is not in 'ready' status
        - Task has unmet dependencies (not all dependencies are verified)

        Args:
            task_id: Task ID to claim (required)
            agent_id: Agent ID making the claim (required)
            ttl_seconds: Lease duration in seconds (optional, default 900 = 15min, min 60, max 86400 = 24h)
            force: Bypass lock conflict warnings (optional, default False)

        Returns:
            Success response with lease object (leaseId, taskId, agentId, expiresAt, ttlSeconds)
            or error with conflict details if task is already claimed or not claimable.
            May include lock conflict warnings if task locks overlap with other active leases.
        """
        return await task_claim(
            context=context,
            task_id=task_id,
            agent_id=agent_id,
            ttl_seconds=ttl_seconds,
            force=force,
            ctx=ctx,
        )

    @mcp.tool(name="lodestar_task_release")
    async def release_tool(
        task_id: str,
        agent_id: str,
        reason: str | None = None,
        ctx: Context | None = None,
    ) -> CallToolResult:
        """Release a claim on a task before TTL expiry.

        Frees the task for other agents to claim. Use this when you're blocked
        or unable to complete the task. The lease is immediately removed and
        the task becomes available for others to claim.

        Note: You don't need to release after marking a task as done or verified -
        those operations automatically release the lease.

        Args:
            task_id: Task ID to release (required)
            agent_id: Agent ID releasing the claim (required)
            reason: Optional reason for releasing (for logging/audit purposes)

        Returns:
            Success response with previous lease details (leaseId, taskId, agentId, expiresAt)
            or error if no active lease exists or agent_id doesn't match the lease holder.
        """
        return await task_release(
            context=context,
            task_id=task_id,
            agent_id=agent_id,
            reason=reason,
            ctx=ctx,
        )

    @mcp.tool(name="lodestar_task_done")
    async def done_tool(
        task_id: str,
        agent_id: str,
        note: str | None = None,
        ctx: Context | None = None,
    ) -> CallToolResult:
        """Mark a task as done (pending verification).

        Sets the task status to 'done'. The task is considered complete but
        still requires verification (via task.verify) before it unblocks
        dependent tasks.

        Automatically releases the lease if the task is currently claimed.

        Args:
            task_id: Task ID to mark as done (required)
            agent_id: Agent ID marking the task as done (required)
            note: Optional note about completion (for logging/audit purposes)

        Returns:
            Success response with status='done' and any warnings.
            Warnings may include:
            - Task already done or verified
            - Task claimed by different agent (still marks as done)
        """
        return await task_done(
            context=context,
            task_id=task_id,
            agent_id=agent_id,
            note=note,
            ctx=ctx,
        )

    @mcp.tool(name="lodestar_task_verify")
    async def verify_tool(
        task_id: str,
        agent_id: str,
        note: str | None = None,
        ctx: Context | None = None,
    ) -> CallToolResult:
        """Mark a task as verified (unblocks dependents).

        Verifies that the task is complete. This changes the status from 'done'
        to 'verified' and unblocks any dependent tasks that were waiting on this one.

        Task must be in 'done' status before it can be verified.
        Automatically releases the lease if the task is currently claimed.

        If the client provides a progressToken in request metadata, this operation
        emits progress notifications at key stages (10%, 25%, 40%, 55%, 70%, 80%, 90%, 100%).

        Args:
            task_id: Task ID to verify (required)
            agent_id: Agent ID verifying the task (required)
            note: Optional note about verification (for logging/audit purposes)
            ctx: Optional MCP context for logging and progress notifications

        Returns:
            Success response with status='verified' and list of newly unblocked task IDs.
            Returns error if task is not in 'done' status.
            Returns warning if task is already verified.
        """
        return await task_verify(
            context=context,
            task_id=task_id,
            agent_id=agent_id,
            note=note,
            ctx=ctx,
        )

    @mcp.tool(name="lodestar_task_complete")
    async def complete_tool(
        task_id: str,
        agent_id: str,
        note: str | None = None,
        ctx: Context | None = None,
    ) -> CallToolResult:
        """Mark a task as complete (done + verified in one atomic operation).

        This combines task_done and task_verify into a single atomic operation.
        Both status changes are made in a single spec save, preventing the task
        from being stuck in 'done' state if an agent crashes between operations.

        This is the recommended way to complete tasks when:
        - You've finished the work and verified it works
        - You want to prevent crash-recovery issues
        - You're doing both done + verify in the same session

        If the client provides a progressToken in request metadata, this operation
        emits progress notifications at key stages (10%, 20%, 30%, 50%, 60%, 70%, 85%, 100%).

        Args:
            task_id: Task ID to complete (required)
            agent_id: Agent ID completing the task (required)
            note: Optional note about completion (for logging/audit purposes)
            ctx: Optional MCP context for logging and progress notifications

        Returns:
            Success response with status='verified' and list of newly unblocked task IDs.
            Warnings may include:
            - Task already verified
            - Task claimed by different agent (still completes the task)
        """
        return await task_complete(
            context=context,
            task_id=task_id,
            agent_id=agent_id,
            note=note,
            ctx=ctx,
        )

    @mcp.tool(name="lodestar_task_batch_verify")
    async def batch_verify_tool(
        task_ids: list[str],
        agent_id: str,
        notes: dict[str, str] | None = None,
        ctx: Context | None = None,
    ) -> CallToolResult:
        """Verify multiple tasks in a single batch operation.

        This is more efficient than calling task_verify multiple times when completing
        multiple independent tasks in sequence. Batch operations reduce round-trips
        and improve agent workflow efficiency.

        Partial success is allowed - some tasks may succeed while others fail. Each
        task result is reported individually.

        All dependent task unblocking happens correctly for successfully verified tasks.

        Args:
            task_ids: List of task IDs to verify (required, non-empty, max 100)
            agent_id: Agent ID verifying the tasks (required)
            notes: Optional dict mapping task IDs to verification notes

        Returns:
            Summary of successes and failures for each task, including:
            - total: Total number of tasks in batch
            - succeeded: Number of successfully verified tasks
            - failed: Number of failed verifications
            - results: Array of individual task results with success status, errors, and newly ready tasks
            - allNewlyReadyTaskIds: Combined list of all tasks unblocked by this batch

        Example:
            {
              "ok": true,
              "summary": {"total": 3, "succeeded": 2, "failed": 1},
              "results": [
                {"taskId": "F001", "success": true, "status": "verified", "newlyReadyTaskIds": ["F002"]},
                {"taskId": "F003", "success": true, "status": "verified", "newlyReadyTaskIds": []},
                {"taskId": "F004", "success": false, "error": "Task not found", "errorCode": "TASK_NOT_FOUND"}
              ],
              "allNewlyReadyTaskIds": ["F002"]
            }
        """
        return await task_batch_verify(
            context=context,
            task_ids=task_ids,
            agent_id=agent_id,
            notes=notes,
            ctx=ctx,
        )
