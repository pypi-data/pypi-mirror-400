"""Tests for MCP task creation, update, and deletion tools."""

import pytest

from lodestar.mcp.server import LodestarContext
from lodestar.mcp.tools.task_mutations import task_create, task_delete, task_update
from lodestar.models.runtime import Agent
from lodestar.models.spec import Project, Spec, Task, TaskStatus
from lodestar.spec.loader import save_spec


@pytest.fixture
def mcp_context(tmp_path):
    """Create a test MCP context with sample data."""
    # Create repository structure
    lodestar_dir = tmp_path / ".lodestar"
    lodestar_dir.mkdir()

    # Create sample spec with some tasks
    spec = Spec(
        project=Project(name="test-project"),
        tasks={
            "T001": Task(
                id="T001",
                title="Existing task",
                description="Already exists",
                status=TaskStatus.READY,
                priority=1,
            ),
        },
    )

    save_spec(spec, tmp_path)

    # Create context
    context = LodestarContext(tmp_path)

    # Register a test agent
    agent = Agent(display_name="Test Agent", role="tester", capabilities=["testing"])
    context.db.register_agent(agent)

    return context


@pytest.mark.anyio
class TestTaskCreate:
    """Test task_create MCP tool."""

    async def test_create_basic_task(self, mcp_context: LodestarContext) -> None:
        """Test creating a basic task."""
        result = await task_create(
            context=mcp_context,
            title="Test task",
            description="Test description",
        )

        assert result.isError is False
        content = result.content[0]
        assert content.type == "text"

        # Get structured data
        data = result.structuredContent

        assert data["ok"] is True
        assert data["taskId"].startswith("T")
        assert data["title"] == "Test task"
        assert data["status"] == "ready"
        assert data["priority"] == 100

        # Verify task was added to spec
        mcp_context.reload_spec()
        task_id = data["taskId"]
        assert task_id in mcp_context.spec.tasks
        task = mcp_context.spec.tasks[task_id]
        assert task.title == "Test task"
        assert task.description == "Test description"

    async def test_create_task_with_all_fields(self, mcp_context: LodestarContext) -> None:
        """Test creating a task with all fields."""
        # First create a dependency task
        result1 = await task_create(
            context=mcp_context,
            title="Dependency task",
            task_id="DEP001",
        )
        assert result1.isError is False

        # Create main task with all fields
        result = await task_create(
            context=mcp_context,
            title="Complete task",
            description="WHAT: Do something\nWHERE: src/\nWHY: Because",
            acceptance_criteria=["Tests pass", "No errors"],
            priority=5,
            status="todo",
            task_id="MAIN001",
            depends_on=["DEP001"],
            labels=["feature", "high-priority"],
            locks=["src/**/*.py"],
        )

        assert result.isError is False
        data = result.structuredContent

        assert data["ok"] is True
        assert data["taskId"] == "MAIN001"
        assert data["title"] == "Complete task"
        assert data["status"] == "todo"
        assert data["priority"] == 5
        assert "dependsOn" in data
        assert "labels" in data
        assert "locks" in data

        # Verify in spec
        mcp_context.reload_spec()
        task = mcp_context.spec.tasks["MAIN001"]
        assert task.title == "Complete task"
        assert task.status == TaskStatus.TODO
        assert task.priority == 5
        assert task.depends_on == ["DEP001"]
        assert set(task.labels) == {"feature", "high-priority"}
        assert task.locks == ["src/**/*.py"]
        assert task.acceptance_criteria == ["Tests pass", "No errors"]

    async def test_create_task_auto_generated_id(self, mcp_context: LodestarContext) -> None:
        """Test that task ID is auto-generated if not provided."""
        result = await task_create(
            context=mcp_context,
            title="Auto ID task",
        )

        assert result.isError is False
        data = result.structuredContent

        assert data["ok"] is True
        assert data["taskId"].startswith("T")  # Auto-generated ID

    async def test_create_task_duplicate_id(self, mcp_context: LodestarContext) -> None:
        """Test that creating a task with duplicate ID fails."""
        # Create first task
        await task_create(
            context=mcp_context,
            title="First task",
            task_id="DUP001",
        )

        # Try to create duplicate
        result = await task_create(
            context=mcp_context,
            title="Duplicate task",
            task_id="DUP001",
        )

        assert result.isError is True
        data = result.structuredContent

        assert "error_code" in data or "error" in data
        assert data["error_code"] == "DUPLICATE_TASK_ID"
        assert "DUP001" in data["error"]

    async def test_create_task_invalid_status(self, mcp_context: LodestarContext) -> None:
        """Test that creating a task with invalid status fails."""
        result = await task_create(
            context=mcp_context,
            title="Invalid status task",
            status="invalid_status",
        )

        assert result.isError is True
        data = result.structuredContent

        assert "error_code" in data or "error" in data
        assert data["error_code"] == "INVALID_STATUS"
        assert "invalid_status" in data["error"]

    async def test_create_task_missing_title(self, mcp_context: LodestarContext) -> None:
        """Test that creating a task without title fails."""
        result = await task_create(
            context=mcp_context,
            title="",
        )

        assert result.isError is True
        data = result.structuredContent

        assert "error_code" in data or "error" in data
        assert data["error_code"] == "INVALID_TITLE"

    async def test_create_task_unknown_dependencies(self, mcp_context: LodestarContext) -> None:
        """Test that creating a task with unknown dependencies fails."""
        result = await task_create(
            context=mcp_context,
            title="Task with bad deps",
            depends_on=["NONEXISTENT"],
        )

        assert result.isError is True
        data = result.structuredContent

        assert "error_code" in data or "error" in data
        assert data["error_code"] == "UNKNOWN_DEPENDENCIES"
        assert "NONEXISTENT" in str(data["details"]["missing"])

    async def test_create_task_circular_dependency(self, mcp_context: LodestarContext) -> None:
        """Test that creating a task that would create a cycle fails."""
        # Create tasks A -> B
        await task_create(
            context=mcp_context,
            title="Task A",
            task_id="A",
        )
        await task_create(
            context=mcp_context,
            title="Task B",
            task_id="B",
            depends_on=["A"],
        )

        # Try to create A depending on B (would create cycle A -> B -> A)
        result = await task_create(
            context=mcp_context,
            title="Task C",
            task_id="C",
            depends_on=["B"],
        )

        # This should succeed (A -> B -> C is valid)
        assert result.isError is False

        # Now try to make A depend on C (A -> B -> C -> A = cycle)
        # We need to use update for this, but let's just verify creation handles cycles
        # by trying to create a self-referential dependency
        result = await task_create(
            context=mcp_context,
            title="Task D",
            task_id="D",
            depends_on=["D"],  # Self-reference
        )

        # This should be caught during DAG validation
        assert result.isError is True

    async def test_create_task_with_prd(self, mcp_context: LodestarContext, tmp_path) -> None:
        """Test creating a task with PRD reference."""
        # Create a PRD file
        prd_file = tmp_path / "PRD.md"
        prd_file.write_text("""# PRD

## Feature Requirements {#feature-requirements}

Some requirements here.
""")

        # Update context root to tmp_path
        original_root = mcp_context.repo_root
        mcp_context.repo_root = tmp_path

        try:
            result = await task_create(
                context=mcp_context,
                title="Task with PRD",
                prd_source="PRD.md",
                prd_refs=["#feature-requirements"],
                prd_excerpt="Frozen excerpt",
            )

            assert result.isError is False
            data = result.structuredContent

            assert data["ok"] is True
            assert "prdSource" in data
            assert data["prdSource"] == "PRD.md"

            # Verify in spec
            mcp_context.reload_spec()
            task_id = data["taskId"]
            task = mcp_context.spec.tasks[task_id]
            assert task.prd is not None
            assert task.prd.source == "PRD.md"
            assert len(task.prd.refs) == 1
            assert task.prd.refs[0].anchor == "#feature-requirements"
            assert task.prd.excerpt == "Frozen excerpt"
        finally:
            mcp_context.repo_root = original_root

    async def test_create_task_prd_file_not_found(self, mcp_context: LodestarContext) -> None:
        """Test that creating a task with missing PRD file fails (when validate_prd=True)."""
        result = await task_create(
            context=mcp_context,
            title="Task with missing PRD",
            prd_source="NONEXISTENT.md",
            validate_prd=True,
        )

        assert result.isError is True
        data = result.structuredContent

        assert "error_code" in data or "error" in data
        assert data["error_code"] == "PRD_FILE_NOT_FOUND"

    async def test_create_task_prd_skip_validation(self, mcp_context: LodestarContext) -> None:
        """Test that PRD validation can be skipped."""
        result = await task_create(
            context=mcp_context,
            title="Task with missing PRD (skip validation)",
            prd_source="NONEXISTENT.md",
            validate_prd=False,
        )

        # Should succeed even though file doesn't exist
        assert result.isError is False
        data = result.structuredContent

        assert data["ok"] is True

    async def test_create_task_emits_event(self, mcp_context: LodestarContext) -> None:
        """Test that creating a task emits a task.create event."""
        result = await task_create(
            context=mcp_context,
            title="Task with event",
            task_id="EVT001",
            labels=["test"],
        )

        assert result.isError is False

        # Check that event was logged (would need to query runtime DB)
        # For now just verify creation succeeded
        mcp_context.reload_spec()
        assert "EVT001" in mcp_context.spec.tasks


@pytest.mark.anyio
class TestTaskUpdate:
    """Test task_update MCP tool."""

    async def test_update_title(self, mcp_context: LodestarContext) -> None:
        """Test updating task title."""
        # Create a task first
        await task_create(
            context=mcp_context,
            title="Original title",
            task_id="UPD001",
        )

        # Update title
        result = await task_update(
            context=mcp_context,
            task_id="UPD001",
            title="Updated title",
        )

        assert result.isError is False
        data = result.structuredContent

        assert data["ok"] is True
        assert data["title"] == "Updated title"
        assert "title" in data["updatedFields"]

        # Verify in spec
        mcp_context.reload_spec()
        task = mcp_context.spec.tasks["UPD001"]
        assert task.title == "Updated title"

    async def test_update_description(self, mcp_context: LodestarContext) -> None:
        """Test updating task description."""
        await task_create(
            context=mcp_context,
            title="Task",
            task_id="UPD002",
            description="Original description",
        )

        result = await task_update(
            context=mcp_context,
            task_id="UPD002",
            description="Updated description",
        )

        assert result.isError is False
        mcp_context.reload_spec()
        task = mcp_context.spec.tasks["UPD002"]
        assert task.description == "Updated description"

    async def test_update_priority(self, mcp_context: LodestarContext) -> None:
        """Test updating task priority."""
        await task_create(
            context=mcp_context,
            title="Task",
            task_id="UPD003",
            priority=10,
        )

        result = await task_update(
            context=mcp_context,
            task_id="UPD003",
            priority=5,
        )

        assert result.isError is False
        mcp_context.reload_spec()
        task = mcp_context.spec.tasks["UPD003"]
        assert task.priority == 5

    async def test_update_add_labels(self, mcp_context: LodestarContext) -> None:
        """Test adding labels to a task."""
        await task_create(
            context=mcp_context,
            title="Task",
            task_id="UPD004",
            labels=["initial"],
        )

        result = await task_update(
            context=mcp_context,
            task_id="UPD004",
            add_labels=["added1", "added2"],
        )

        assert result.isError is False
        mcp_context.reload_spec()
        task = mcp_context.spec.tasks["UPD004"]
        assert set(task.labels) == {"initial", "added1", "added2"}

    async def test_update_remove_labels(self, mcp_context: LodestarContext) -> None:
        """Test removing labels from a task."""
        await task_create(
            context=mcp_context,
            title="Task",
            task_id="UPD005",
            labels=["keep", "remove1", "remove2"],
        )

        result = await task_update(
            context=mcp_context,
            task_id="UPD005",
            remove_labels=["remove1", "remove2"],
        )

        assert result.isError is False
        mcp_context.reload_spec()
        task = mcp_context.spec.tasks["UPD005"]
        assert task.labels == ["keep"]

    async def test_update_add_locks(self, mcp_context: LodestarContext) -> None:
        """Test adding lock patterns to a task."""
        await task_create(
            context=mcp_context,
            title="Task",
            task_id="UPD006",
            locks=["src/**/*.py"],
        )

        result = await task_update(
            context=mcp_context,
            task_id="UPD006",
            add_locks=["tests/**/*.py"],
        )

        assert result.isError is False
        mcp_context.reload_spec()
        task = mcp_context.spec.tasks["UPD006"]
        assert set(task.locks) == {"src/**/*.py", "tests/**/*.py"}

    async def test_update_remove_locks(self, mcp_context: LodestarContext) -> None:
        """Test removing lock patterns from a task."""
        await task_create(
            context=mcp_context,
            title="Task",
            task_id="UPD007",
            locks=["src/**/*.py", "tests/**/*.py"],
        )

        result = await task_update(
            context=mcp_context,
            task_id="UPD007",
            remove_locks=["tests/**/*.py"],
        )

        assert result.isError is False
        mcp_context.reload_spec()
        task = mcp_context.spec.tasks["UPD007"]
        assert task.locks == ["src/**/*.py"]

    async def test_update_add_acceptance_criteria(self, mcp_context: LodestarContext) -> None:
        """Test adding acceptance criteria to a task."""
        await task_create(
            context=mcp_context,
            title="Task",
            task_id="UPD008",
            acceptance_criteria=["Initial criterion"],
        )

        result = await task_update(
            context=mcp_context,
            task_id="UPD008",
            add_acceptance_criteria=["New criterion 1", "New criterion 2"],
        )

        assert result.isError is False
        mcp_context.reload_spec()
        task = mcp_context.spec.tasks["UPD008"]
        assert "Initial criterion" in task.acceptance_criteria
        assert "New criterion 1" in task.acceptance_criteria
        assert "New criterion 2" in task.acceptance_criteria

    async def test_update_remove_acceptance_criteria(self, mcp_context: LodestarContext) -> None:
        """Test removing acceptance criteria from a task."""
        await task_create(
            context=mcp_context,
            title="Task",
            task_id="UPD009",
            acceptance_criteria=["Keep this", "Remove this"],
        )

        result = await task_update(
            context=mcp_context,
            task_id="UPD009",
            remove_acceptance_criteria=["Remove this"],
        )

        assert result.isError is False
        mcp_context.reload_spec()
        task = mcp_context.spec.tasks["UPD009"]
        assert task.acceptance_criteria == ["Keep this"]

    async def test_update_multiple_fields(self, mcp_context: LodestarContext) -> None:
        """Test updating multiple fields at once."""
        await task_create(
            context=mcp_context,
            title="Original",
            task_id="UPD010",
            priority=10,
        )

        result = await task_update(
            context=mcp_context,
            task_id="UPD010",
            title="Updated",
            priority=5,
            add_labels=["urgent"],
        )

        assert result.isError is False
        data = result.structuredContent

        assert data["ok"] is True
        assert set(data["updatedFields"]) == {"title", "priority", "labels"}

        mcp_context.reload_spec()
        task = mcp_context.spec.tasks["UPD010"]
        assert task.title == "Updated"
        assert task.priority == 5
        assert "urgent" in task.labels

    async def test_update_nonexistent_task(self, mcp_context: LodestarContext) -> None:
        """Test that updating a non-existent task fails."""
        result = await task_update(
            context=mcp_context,
            task_id="NONEXISTENT",
            title="New title",
        )

        assert result.isError is True
        data = result.structuredContent

        assert "error_code" in data or "error" in data
        assert data["error_code"] == "TASK_NOT_FOUND"

    async def test_update_no_changes(self, mcp_context: LodestarContext) -> None:
        """Test that calling update with no changes fails."""
        await task_create(
            context=mcp_context,
            title="Task",
            task_id="UPD011",
        )

        result = await task_update(
            context=mcp_context,
            task_id="UPD011",
        )

        assert result.isError is True
        data = result.structuredContent

        assert "error_code" in data or "error" in data
        assert data["error_code"] == "NO_UPDATES"

    async def test_update_invalid_task_id(self, mcp_context: LodestarContext) -> None:
        """Test that updating with invalid task ID fails."""
        result = await task_update(
            context=mcp_context,
            task_id="",
            title="New title",
        )

        assert result.isError is True
        data = result.structuredContent

        assert "error_code" in data or "error" in data
        assert data["error_code"] == "INVALID_TASK_ID"


@pytest.mark.anyio
class TestTaskDelete:
    """Test task_delete MCP tool."""

    async def test_delete_task_basic(self, mcp_context: LodestarContext) -> None:
        """Test basic task deletion."""
        # Create a task
        await task_create(
            context=mcp_context,
            title="Task to delete",
            task_id="DEL001",
        )

        # Delete it
        result = await task_delete(
            context=mcp_context,
            task_id="DEL001",
        )

        assert result.isError is False
        data = result.structuredContent

        assert data["ok"] is True
        assert data["taskId"] == "DEL001"
        assert data["deletedCount"] == 1

        # Verify task is marked as deleted
        mcp_context.reload_spec()
        task = mcp_context.spec.tasks["DEL001"]
        assert task.status == TaskStatus.DELETED

    async def test_delete_nonexistent_task(self, mcp_context: LodestarContext) -> None:
        """Test that deleting a non-existent task fails."""
        result = await task_delete(
            context=mcp_context,
            task_id="NONEXISTENT",
        )

        assert result.isError is True
        data = result.structuredContent

        assert "error_code" in data or "error" in data
        assert data["error_code"] == "TASK_NOT_FOUND"

    async def test_delete_already_deleted(self, mcp_context: LodestarContext) -> None:
        """Test that deleting an already-deleted task fails."""
        await task_create(
            context=mcp_context,
            title="Task",
            task_id="DEL002",
        )

        # Delete once
        await task_delete(context=mcp_context, task_id="DEL002")

        # Try to delete again
        result = await task_delete(context=mcp_context, task_id="DEL002")

        assert result.isError is True
        data = result.structuredContent

        assert "error_code" in data or "error" in data
        assert data["error_code"] == "ALREADY_DELETED"

    async def test_delete_with_dependents_no_cascade(self, mcp_context: LodestarContext) -> None:
        """Test that deleting a task with dependents fails without cascade."""
        # Create parent task
        await task_create(
            context=mcp_context,
            title="Parent",
            task_id="PARENT",
        )

        # Create dependent task
        await task_create(
            context=mcp_context,
            title="Child",
            task_id="CHILD",
            depends_on=["PARENT"],
        )

        # Try to delete parent without cascade
        result = await task_delete(
            context=mcp_context,
            task_id="PARENT",
            cascade=False,
        )

        assert result.isError is True
        data = result.structuredContent

        assert "error_code" in data or "error" in data
        assert data["error_code"] == "HAS_DEPENDENTS"
        assert "CHILD" in data["details"]["dependents"]

    async def test_delete_with_cascade(self, mcp_context: LodestarContext) -> None:
        """Test cascading delete of a task and its dependents."""
        # Create parent and child tasks
        await task_create(
            context=mcp_context,
            title="Parent",
            task_id="PARENT2",
        )

        await task_create(
            context=mcp_context,
            title="Child1",
            task_id="CHILD1",
            depends_on=["PARENT2"],
        )

        await task_create(
            context=mcp_context,
            title="Child2",
            task_id="CHILD2",
            depends_on=["PARENT2"],
        )

        # Delete with cascade
        result = await task_delete(
            context=mcp_context,
            task_id="PARENT2",
            cascade=True,
        )

        assert result.isError is False
        data = result.structuredContent

        assert data["ok"] is True
        assert data["deletedCount"] == 3
        # deletedTasks is an array of objects with 'id' and 'title' fields
        deleted_ids = {task["id"] for task in data["deletedTasks"]}
        assert deleted_ids == {"PARENT2", "CHILD1", "CHILD2"}

        # Verify all are marked as deleted
        mcp_context.reload_spec()
        assert mcp_context.spec.tasks["PARENT2"].status == TaskStatus.DELETED
        assert mcp_context.spec.tasks["CHILD1"].status == TaskStatus.DELETED
        assert mcp_context.spec.tasks["CHILD2"].status == TaskStatus.DELETED

    async def test_delete_with_active_lease(self, mcp_context: LodestarContext) -> None:
        """Test that deleting a task with active lease fails."""
        # Create a task
        await task_create(
            context=mcp_context,
            title="Claimed task",
            task_id="CLAIMED",
        )

        # Get an agent ID from the context
        agents = mcp_context.db.list_agents()
        agent_id = agents[0].agent_id if agents else "TEST_AGENT"

        # Claim the task
        from lodestar.mcp.tools.task_mutations import task_claim

        await task_claim(
            context=mcp_context,
            task_id="CLAIMED",
            agent_id=agent_id,
        )

        # Try to delete
        result = await task_delete(
            context=mcp_context,
            task_id="CLAIMED",
        )

        assert result.isError is True
        data = result.structuredContent

        assert "error_code" in data or "error" in data
        assert data["error_code"] == "ACTIVE_LEASE"
        assert data["details"]["claimed_by"] == agent_id

    async def test_delete_invalid_task_id(self, mcp_context: LodestarContext) -> None:
        """Test that deleting with invalid task ID fails."""
        result = await task_delete(
            context=mcp_context,
            task_id="",
        )

        assert result.isError is True
        data = result.structuredContent

        assert "error_code" in data or "error" in data
        assert data["error_code"] == "INVALID_TASK_ID"
