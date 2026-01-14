"""Tests for MachineStateABC and Task-based execution."""

from __future__ import annotations

import pytest

from djb.machine_state import MachineStateABC, Task, find_leaves, task
from djb.machine_state.types import ExecuteResult, MachineContext


# =============================================================================
# Test Fixtures
# =============================================================================


class SimpleMachineState(MachineStateABC):
    """Minimal MachineState for testing."""

    def __init__(self, satisfied: bool = True) -> None:
        self._satisfied = satisfied

    def describe(self, ctx: MachineContext) -> str:
        return "test resource"

    def check(self, ctx: MachineContext) -> bool:
        return self._satisfied

    @task
    def satisfy(self, ctx: MachineContext) -> None:
        self._satisfied = True


class ParameterizedState(MachineStateABC):
    """State with custom description for testing parameterized states."""

    def __init__(self, addon_name: str, satisfied: bool = True) -> None:
        self.addon_name = addon_name
        self._satisfied = satisfied

    def check(self, ctx: MachineContext) -> bool:
        return self._satisfied

    @task
    def satisfy(self, ctx: MachineContext) -> None:
        self._satisfied = True

    def describe(self, ctx: MachineContext) -> str:
        return f"microk8s {self.addon_name} addon"


# =============================================================================
# MachineStateABC Tests
# =============================================================================


class TestMachineStateABC:
    """Tests for MachineStateABC base class."""

    def test_check_returns_bool(self, mock_machine_context) -> None:
        """check() returns a boolean."""
        state = SimpleMachineState(satisfied=True)
        ctx = mock_machine_context()

        result = state.check(ctx)

        assert result is True

    def test_check_returns_false_when_unsatisfied(self, mock_machine_context) -> None:
        """check() returns False when state needs work."""
        state = SimpleMachineState(satisfied=False)
        ctx = mock_machine_context()

        result = state.check(ctx)

        assert result is False

    def test_describe_returns_what_is_managed(self, mock_machine_context) -> None:
        """describe() returns what the state manages."""
        state = SimpleMachineState()
        ctx = mock_machine_context()

        assert state.describe(ctx) == "test resource"

    def test_describe_parameterized(self, mock_machine_context) -> None:
        """Parameterized states include parameter in description."""
        state = ParameterizedState("dns")
        ctx = mock_machine_context()

        assert state.describe(ctx) == "microk8s dns addon"


# =============================================================================
# Task Decorator Tests
# =============================================================================


class TestTaskDecorator:
    """Tests for @task decorator."""

    def test_task_decorator_returns_task(self, mock_machine_context) -> None:
        """@task decorator makes satisfy() return a Task."""
        state = SimpleMachineState(satisfied=False)
        ctx = mock_machine_context()

        result = state.satisfy(ctx)

        assert isinstance(result, Task)
        assert result.state is state

    def test_task_not_executed_immediately(self, mock_machine_context) -> None:
        """Task is not executed when created."""
        state = SimpleMachineState(satisfied=False)
        ctx = mock_machine_context()

        state.satisfy(ctx)

        # State should still be unsatisfied
        assert state.check(ctx) is False

    def test_task_run_executes_work(self, mock_machine_context) -> None:
        """Task.run() executes the work."""
        state = SimpleMachineState(satisfied=False)
        ctx = mock_machine_context()

        task_obj = state.satisfy(ctx)
        result = task_obj.run()

        assert result.success is True
        assert result.changed is True
        assert state.check(ctx) is True


# =============================================================================
# Task Execution Tests
# =============================================================================


class TestTaskExecution:
    """Tests for Task execution."""

    def test_run_already_satisfied(self, mock_machine_context) -> None:
        """run() returns success with no changes when satisfied."""
        state = SimpleMachineState(satisfied=True)
        ctx = mock_machine_context()

        task_obj = state.satisfy(ctx)
        result = task_obj.run()

        assert isinstance(result, ExecuteResult)
        assert result.success is True
        assert result.changed is False
        assert result.message == "Already satisfied"

    def test_run_needs_work(self, mock_machine_context) -> None:
        """run() satisfies state and returns changed=True."""
        state = SimpleMachineState(satisfied=False)
        ctx = mock_machine_context()

        task_obj = state.satisfy(ctx)
        result = task_obj.run()

        assert isinstance(result, ExecuteResult)
        assert result.success is True
        assert result.changed is True
        assert result.message == "Satisfied"

    def test_run_handles_exception(self, mock_machine_context) -> None:
        """run() returns failure on exception."""

        class FailingState(MachineStateABC):
            def describe(self, ctx: MachineContext) -> str:
                return "failing resource"

            def check(self, ctx: MachineContext) -> bool:
                return False

            @task
            def satisfy(self, ctx: MachineContext) -> None:
                raise RuntimeError("Failed to satisfy")

        state = FailingState()
        ctx = mock_machine_context()

        task_obj = state.satisfy(ctx)
        result = task_obj.run()

        assert result.success is False
        assert result.changed is False
        assert "Failed to satisfy" in result.message


# =============================================================================
# Task Dependency Tests
# =============================================================================


class TestTaskDependencies:
    """Tests for Task dependencies using after()."""

    def test_after_adds_dependency(self, mock_machine_context) -> None:
        """after() adds dependencies to a task."""
        state_a = SimpleMachineState()
        state_b = SimpleMachineState()
        ctx = mock_machine_context()

        task_a = state_a.satisfy(ctx)
        task_b = state_b.satisfy(ctx).after(task_a)

        assert task_a in task_b.depends_on

    def test_after_is_fluent(self, mock_machine_context) -> None:
        """after() returns self for chaining."""
        state_a = SimpleMachineState()
        state_b = SimpleMachineState()
        ctx = mock_machine_context()

        task_a = state_a.satisfy(ctx)
        result = state_b.satisfy(ctx).after(task_a)

        assert isinstance(result, Task)

    def test_dependencies_run_first(self, mock_machine_context) -> None:
        """Dependencies are run before the dependent task."""
        execution_order: list[str] = []

        class TrackedState(MachineStateABC):
            def __init__(self, name_: str, satisfied: bool = False) -> None:
                self._name = name_
                self._satisfied = satisfied

            def describe(self, ctx: MachineContext) -> str:
                return f"tracked resource '{self._name}'"

            def check(self, ctx: MachineContext) -> bool:
                return self._satisfied

            @task
            def satisfy(self, ctx: MachineContext) -> None:
                execution_order.append(self._name)
                self._satisfied = True

        ctx = mock_machine_context()
        first = TrackedState("first")
        second = TrackedState("second")
        third = TrackedState("third")

        # Build chain: first -> second -> third
        task_first = first.satisfy(ctx)
        task_second = second.satisfy(ctx).after(task_first)
        task_third = third.satisfy(ctx).after(task_second)

        task_third.run()

        assert execution_order == ["first", "second", "third"]

    def test_dependency_failure_stops_execution(self, mock_machine_context) -> None:
        """If a dependency fails, dependent task is not run."""
        executed: list[str] = []

        class FailingState(MachineStateABC):
            def describe(self, ctx: MachineContext) -> str:
                return "failing"

            def check(self, ctx: MachineContext) -> bool:
                return False

            @task
            def satisfy(self, ctx: MachineContext) -> None:
                executed.append("failing")
                raise RuntimeError("Failed")

        class DependentState(MachineStateABC):
            def describe(self, ctx: MachineContext) -> str:
                return "dependent"

            def check(self, ctx: MachineContext) -> bool:
                return False

            @task
            def satisfy(self, ctx: MachineContext) -> None:
                executed.append("dependent")

        ctx = mock_machine_context()
        failing = FailingState()
        dependent = DependentState()

        task_fail = failing.satisfy(ctx)
        task_dep = dependent.satisfy(ctx).after(task_fail)

        result = task_dep.run()

        assert result.success is False
        assert executed == ["failing"]  # dependent was not run


# =============================================================================
# Task.all() Tests
# =============================================================================


class TestTaskAll:
    """Tests for Task.all() combining multiple tasks."""

    def test_all_creates_combined_task(self, mock_machine_context) -> None:
        """Task.all() creates a task that depends on all inputs."""
        ctx = mock_machine_context()
        state_a = SimpleMachineState()
        state_b = SimpleMachineState()

        task_a = state_a.satisfy(ctx)
        task_b = state_b.satisfy(ctx)
        combined = Task.all(task_a, task_b)

        assert task_a in combined.depends_on
        assert task_b in combined.depends_on

    def test_all_runs_all_dependencies(self, mock_machine_context) -> None:
        """Task.all() runs all combined tasks."""
        executed: list[str] = []

        class TrackedState(MachineStateABC):
            def __init__(self, name_: str) -> None:
                self._name = name_
                self._satisfied = False

            def describe(self, ctx: MachineContext) -> str:
                return self._name

            def check(self, ctx: MachineContext) -> bool:
                return self._satisfied

            @task
            def satisfy(self, ctx: MachineContext) -> None:
                executed.append(self._name)
                self._satisfied = True

        ctx = mock_machine_context()
        a = TrackedState("a")
        b = TrackedState("b")
        c = TrackedState("c")

        combined = Task.all(a.satisfy(ctx), b.satisfy(ctx), c.satisfy(ctx))
        result = combined.run()

        assert result.success is True
        assert set(executed) == {"a", "b", "c"}


# =============================================================================
# Task Walk and Health Check Tests
# =============================================================================


class TestTaskWalk:
    """Tests for Task.walk() DAG traversal."""

    def test_walk_single_task(self, mock_machine_context) -> None:
        """walk() returns single task in list."""
        ctx = mock_machine_context()
        state = SimpleMachineState()

        task_obj = state.satisfy(ctx)
        walked = task_obj.walk()

        assert len(walked) == 1
        assert walked[0] is task_obj

    def test_walk_returns_topological_order(self, mock_machine_context) -> None:
        """walk() returns tasks in dependency order."""
        ctx = mock_machine_context()
        a = SimpleMachineState()
        b = SimpleMachineState()
        c = SimpleMachineState()

        task_a = a.satisfy(ctx)
        task_b = b.satisfy(ctx).after(task_a)
        task_c = c.satisfy(ctx).after(task_b)

        walked = task_c.walk()

        assert walked == [task_a, task_b, task_c]


class TestTaskHealthCheck:
    """Tests for Task.health_check()."""

    def test_health_check_all_satisfied(self, mock_machine_context) -> None:
        """health_check() reports all satisfied."""
        ctx = mock_machine_context()
        a = SimpleMachineState(satisfied=True)
        b = SimpleMachineState(satisfied=True)

        task_b = b.satisfy(ctx).after(a.satisfy(ctx))
        report = task_b.health_check()

        assert report.all_satisfied is True
        assert len(report.satisfied) == 2
        assert len(report.unsatisfied) == 0

    def test_health_check_some_unsatisfied(self, mock_machine_context) -> None:
        """health_check() reports unsatisfied tasks."""
        ctx = mock_machine_context()
        a = SimpleMachineState(satisfied=True)
        b = SimpleMachineState(satisfied=False)

        task_b = b.satisfy(ctx).after(a.satisfy(ctx))
        report = task_b.health_check()

        assert report.all_satisfied is False
        assert len(report.satisfied) == 1
        assert len(report.unsatisfied) == 1


class TestTaskDryRun:
    """Tests for Task.dry_run()."""

    def test_dry_run_all_satisfied(self, mock_machine_context) -> None:
        """dry_run() returns empty list when all satisfied."""
        ctx = mock_machine_context()
        state = SimpleMachineState(satisfied=True)

        result = state.satisfy(ctx).dry_run()

        assert result == []

    def test_dry_run_returns_unsatisfied_descriptions(self, mock_machine_context) -> None:
        """dry_run() returns descriptions of unsatisfied tasks."""
        ctx = mock_machine_context()
        state = SimpleMachineState(satisfied=False)

        result = state.satisfy(ctx).dry_run()

        assert result == ["test resource"]


# =============================================================================
# Leaf State Requirements Tests
# =============================================================================


class TestLeafStateRequiresImplementation:
    """Tests for leaf state implementation requirements."""

    def test_describe_not_implemented(self, mock_machine_context) -> None:
        """Leaf state without describe() raises NotImplementedError."""

        class LeafState(MachineStateABC):
            pass

        state = LeafState()
        ctx = mock_machine_context()

        with pytest.raises(NotImplementedError, match="must implement describe"):
            state.describe(ctx)

    def test_check_not_implemented(self, mock_machine_context) -> None:
        """Leaf state without check() raises NotImplementedError."""

        class LeafState(MachineStateABC):
            pass

        state = LeafState()
        ctx = mock_machine_context()

        with pytest.raises(NotImplementedError, match="must implement check"):
            state.check(ctx)

    def test_satisfy_not_implemented(self, mock_machine_context) -> None:
        """Leaf state without satisfy() raises NotImplementedError."""

        class LeafState(MachineStateABC):
            def check(self, ctx: MachineContext) -> bool:
                return False

        state = LeafState()
        ctx = mock_machine_context()

        with pytest.raises(NotImplementedError, match="must implement satisfy"):
            state.satisfy(ctx)


# =============================================================================
# Composite State (Class Attribute) Tests
# =============================================================================


class TestCompositeStateClassAttributes:
    """Tests for composite states using class attributes."""

    def test_default_describe_derives_from_class_name(self, mock_machine_context) -> None:
        """Default describe() derives from class name."""

        class K8sCluster(MachineStateABC):
            child = SimpleMachineState()

        class Microk8sAddon(MachineStateABC):
            child = SimpleMachineState()

        ctx = mock_machine_context()

        assert K8sCluster().describe(ctx) == "K8s cluster"
        assert Microk8sAddon().describe(ctx) == "Microk8s addon"

    def test_default_check_derives_from_children(self, mock_machine_context) -> None:
        """Default check() returns True only if all children are satisfied."""

        class Composite(MachineStateABC):
            child_a = SimpleMachineState(satisfied=True)
            child_b = SimpleMachineState(satisfied=True)

        composite = Composite()
        ctx = mock_machine_context()

        # All satisfied
        assert composite.check(ctx) is True

        # One unsatisfied
        composite.child_b._satisfied = False
        assert composite.check(ctx) is False

    def test_metaclass_discovers_substates(self) -> None:
        """Metaclass discovers MachineState class attributes at definition time."""

        class Composite(MachineStateABC):
            child_a = SimpleMachineState()
            child_b = SimpleMachineState()

        # Substates discovered at class definition, available on class and instance
        assert len(Composite._substates) == 2
        assert "child_a" in Composite._substates
        assert "child_b" in Composite._substates

    def test_metaclass_discovers_substates_on_subclass(self) -> None:
        """Metaclass discovers substates defined on subclasses."""

        class BaseComposite(MachineStateABC):
            child_a = SimpleMachineState()

        class ExtendedComposite(BaseComposite):
            child_b = SimpleMachineState()

        assert "child_b" in ExtendedComposite._substates

    def test_metaclass_ignores_private_attributes(self) -> None:
        """Metaclass ignores private attributes."""

        class Composite(MachineStateABC):
            child = SimpleMachineState()
            _private = SimpleMachineState()

        assert len(Composite._substates) == 1
        assert "child" in Composite._substates
        assert "_private" not in Composite._substates

    def test_metaclass_ignores_non_state_attributes(self) -> None:
        """Metaclass ignores non-MachineState attributes."""

        class Composite(MachineStateABC):
            child = SimpleMachineState()
            name = "not a state"
            count = 42

        assert len(Composite._substates) == 1
        assert "child" in Composite._substates

    def test_default_satisfy_builds_task_from_attributes(self, mock_machine_context) -> None:
        """Default satisfy() builds Task DAG from class attributes."""

        class Composite(MachineStateABC):
            child_a = SimpleMachineState()
            child_b = SimpleMachineState()

            def describe(self, ctx: MachineContext) -> str:
                return "composite"

            def check(self, ctx: MachineContext) -> bool:
                return True

        composite = Composite()
        ctx = mock_machine_context()

        task_obj = composite.satisfy(ctx)

        assert isinstance(task_obj, Task)
        # Should combine two independent children
        walked = task_obj.walk()
        assert len(walked) == 3  # child_a, child_b, combined

    def test_composite_runs_all_children(self, mock_machine_context) -> None:
        """Composite satisfy() runs all child states."""
        executed: list[str] = []

        class TrackedState(MachineStateABC):
            def __init__(self, name_: str) -> None:
                self._name = name_
                self._satisfied = False

            def describe(self, ctx: MachineContext) -> str:
                return self._name

            def check(self, ctx: MachineContext) -> bool:
                return self._satisfied

            @task
            def satisfy(self, ctx: MachineContext) -> None:
                executed.append(self._name)
                self._satisfied = True

        class Composite(MachineStateABC):
            dns = TrackedState("dns")
            storage = TrackedState("storage")
            ingress = TrackedState("ingress")

            def describe(self, ctx: MachineContext) -> str:
                return "cluster"

            def check(self, ctx: MachineContext) -> bool:
                return True

        composite = Composite()
        ctx = mock_machine_context()

        task_obj = composite.satisfy(ctx)
        result = task_obj.run()

        assert result.success is True
        assert set(executed) == {"dns", "storage", "ingress"}


class TestCompositeStateDependencies:
    """Tests for composite states with dependencies."""

    def test_depends_on_creates_task_dependencies(self, mock_machine_context) -> None:
        """depends_on attribute creates Task dependencies using instance references."""
        execution_order: list[str] = []

        class TrackedState(MachineStateABC):
            def __init__(
                self, name_: str, depends_on_: list[MachineStateABC] | None = None
            ) -> None:
                self._name = name_
                self._satisfied = False
                self.depends_on = depends_on_ or []

            def describe(self, ctx: MachineContext) -> str:
                return self._name

            def check(self, ctx: MachineContext) -> bool:
                return self._satisfied

            @task
            def satisfy(self, ctx: MachineContext) -> None:
                execution_order.append(self._name)
                self._satisfied = True

        class Composite(MachineStateABC):
            dns = TrackedState("dns")
            # Instance references: typos become NameError at class definition time
            storage = TrackedState("storage", depends_on_=[dns])
            ingress = TrackedState("ingress", depends_on_=[dns])

            def describe(self, ctx: MachineContext) -> str:
                return "cluster"

            def check(self, ctx: MachineContext) -> bool:
                return True

        composite = Composite()
        ctx = mock_machine_context()

        task_obj = composite.satisfy(ctx)
        task_obj.run()

        # dns must run before storage and ingress
        assert execution_order.index("dns") < execution_order.index("storage")
        assert execution_order.index("dns") < execution_order.index("ingress")

    def test_topological_sort_handles_chain(self, mock_machine_context) -> None:
        """Topological sort handles linear dependency chain."""
        execution_order: list[str] = []

        class TrackedState(MachineStateABC):
            def __init__(
                self, name_: str, depends_on_: list[MachineStateABC] | None = None
            ) -> None:
                self._name = name_
                self._satisfied = False
                self.depends_on = depends_on_ or []

            def describe(self, ctx: MachineContext) -> str:
                return self._name

            def check(self, ctx: MachineContext) -> bool:
                return self._satisfied

            @task
            def satisfy(self, ctx: MachineContext) -> None:
                execution_order.append(self._name)
                self._satisfied = True

        class Composite(MachineStateABC):
            first = TrackedState("first")
            second = TrackedState("second", depends_on_=[first])
            third = TrackedState("third", depends_on_=[second])

            def describe(self, ctx: MachineContext) -> str:
                return "chain"

            def check(self, ctx: MachineContext) -> bool:
                return True

        composite = Composite()
        ctx = mock_machine_context()

        task_obj = composite.satisfy(ctx)
        task_obj.run()

        assert execution_order == ["first", "second", "third"]

    def test_circular_dependency_impossible_with_instance_refs(self) -> None:
        """Circular dependencies are impossible with instance references.

        With instance references, you can't reference `b` before it's defined,
        so circular dependencies become a NameError at class definition time.
        This is caught by Python itself, not by our metaclass.
        """
        # This would raise NameError: name 'b' is not defined
        # class Composite(MachineStateABC):
        #     a = SomeState(depends_on_=[b])  # NameError!
        #     b = SomeState(depends_on_=[a])
        pass  # Test is documentation that circular deps are impossible


class TestFindLeaves:
    """Tests for find_leaves() helper."""

    def test_find_leaves_independent_tasks(self, mock_machine_context) -> None:
        """find_leaves() returns all tasks when independent."""
        ctx = mock_machine_context()
        a = SimpleMachineState()
        b = SimpleMachineState()
        c = SimpleMachineState()

        task_a = a.satisfy(ctx)
        task_b = b.satisfy(ctx)
        task_c = c.satisfy(ctx)

        leaves = find_leaves([task_a, task_b, task_c])

        assert len(leaves) == 3

    def test_find_leaves_with_dependencies(self, mock_machine_context) -> None:
        """find_leaves() excludes tasks that others depend on."""
        ctx = mock_machine_context()
        a = SimpleMachineState()
        b = SimpleMachineState()
        c = SimpleMachineState()

        task_a = a.satisfy(ctx)
        task_b = b.satisfy(ctx).after(task_a)
        task_c = c.satisfy(ctx).after(task_a)

        leaves = find_leaves([task_a, task_b, task_c])

        # task_a is depended on, so not a leaf
        assert task_a not in leaves
        assert task_b in leaves
        assert task_c in leaves
        assert len(leaves) == 2

    def test_find_leaves_linear_chain(self, mock_machine_context) -> None:
        """find_leaves() returns only end of chain."""
        ctx = mock_machine_context()
        a = SimpleMachineState()
        b = SimpleMachineState()
        c = SimpleMachineState()

        task_a = a.satisfy(ctx)
        task_b = b.satisfy(ctx).after(task_a)
        task_c = c.satisfy(ctx).after(task_b)

        leaves = find_leaves([task_a, task_b, task_c])

        assert leaves == [task_c]


class TestCompositeExplicitTaskBuilding:
    """Tests for composite states with explicit Task building (escape hatch)."""

    def test_explicit_satisfy_with_control_flow(self, mock_machine_context) -> None:
        """Composite can use explicit satisfy() with control flow."""
        executed: list[str] = []

        class TrackedState(MachineStateABC):
            def __init__(self, name_: str) -> None:
                self._name = name_
                self._satisfied = False

            def describe(self, ctx: MachineContext) -> str:
                return self._name

            def check(self, ctx: MachineContext) -> bool:
                return self._satisfied

            @task
            def satisfy(self, ctx: MachineContext) -> None:
                executed.append(self._name)
                self._satisfied = True

        class ConditionalComposite(MachineStateABC):
            def __init__(self, enable_storage: bool) -> None:
                self._enable_storage = enable_storage

            def describe(self, ctx: MachineContext) -> str:
                return "conditional cluster"

            def check(self, ctx: MachineContext) -> bool:
                return True

            def satisfy(self, ctx: MachineContext) -> Task:
                dns = TrackedState("dns").satisfy(ctx)

                tasks = [dns]
                if self._enable_storage:
                    storage = TrackedState("storage").satisfy(ctx).after(dns)
                    tasks.append(storage)

                ingress = TrackedState("ingress").satisfy(ctx).after(dns)
                tasks.append(ingress)

                return Task.all(*find_leaves(tasks))

        # Test with storage enabled
        composite = ConditionalComposite(enable_storage=True)
        ctx = mock_machine_context()
        composite.satisfy(ctx).run()

        assert set(executed) == {"dns", "storage", "ingress"}

        # Test with storage disabled
        executed.clear()
        composite2 = ConditionalComposite(enable_storage=False)
        composite2.satisfy(ctx).run()

        assert set(executed) == {"dns", "ingress"}
