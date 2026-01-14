"""Tests for Task class including find_divergence binary search."""

from __future__ import annotations

from djb.machine_state import MachineStateABC, Task, task
from djb.machine_state.types import MachineContext


# =============================================================================
# Test Fixtures
# =============================================================================


class ConfigurableState(MachineStateABC):
    """State with configurable satisfaction for testing binary search."""

    def __init__(self, name_: str, satisfied: bool = True) -> None:
        self._name = name_
        self._satisfied = satisfied
        self.check_count = 0

    def check(self, ctx: MachineContext) -> bool:
        self.check_count += 1
        return self._satisfied

    @task
    def satisfy(self, ctx: MachineContext) -> None:
        self._satisfied = True

    def describe(self, ctx: MachineContext) -> str:
        return f"resource '{self._name}'"


# =============================================================================
# find_divergence Tests - All Satisfied
# =============================================================================


class TestFindDivergenceAllSatisfied:
    """Tests for find_divergence when all states are satisfied."""

    def test_single_satisfied_state(self, mock_machine_context) -> None:
        """Single satisfied state returns None."""
        ctx = mock_machine_context()
        state = ConfigurableState("a", satisfied=True)

        dag = state.satisfy(ctx)
        divergence = dag.find_divergence()

        assert divergence is None

    def test_all_satisfied_linear_chain(self, mock_machine_context) -> None:
        """All satisfied in linear chain returns None."""
        ctx = mock_machine_context()
        a = ConfigurableState("a", satisfied=True)
        b = ConfigurableState("b", satisfied=True)
        c = ConfigurableState("c", satisfied=True)

        task_a = a.satisfy(ctx)
        task_b = b.satisfy(ctx).after(task_a)
        task_c = c.satisfy(ctx).after(task_b)

        divergence = task_c.find_divergence()

        assert divergence is None


# =============================================================================
# find_divergence Tests - Finding Divergence Points
# =============================================================================


class TestFindDivergence:
    """Tests for find_divergence finding divergence points."""

    def test_first_state_unsatisfied(self, mock_machine_context) -> None:
        """Divergence at first state is found."""
        ctx = mock_machine_context()
        # In a real system, if first state unsatisfied, dependents are also unsatisfied
        a = ConfigurableState("a", satisfied=False)
        b = ConfigurableState("b", satisfied=False)
        c = ConfigurableState("c", satisfied=False)

        task_a = a.satisfy(ctx)
        task_b = b.satisfy(ctx).after(task_a)
        task_c = c.satisfy(ctx).after(task_b)

        divergence = task_c.find_divergence()

        assert divergence is task_a

    def test_middle_state_unsatisfied(self, mock_machine_context) -> None:
        """Divergence at middle state is found."""
        ctx = mock_machine_context()
        a = ConfigurableState("a", satisfied=True)
        b = ConfigurableState("b", satisfied=False)
        c = ConfigurableState("c", satisfied=True)

        task_a = a.satisfy(ctx)
        task_b = b.satisfy(ctx).after(task_a)
        task_c = c.satisfy(ctx).after(task_b)

        divergence = task_c.find_divergence()

        assert divergence is task_b

    def test_last_state_unsatisfied(self, mock_machine_context) -> None:
        """Divergence at last state is found."""
        ctx = mock_machine_context()
        a = ConfigurableState("a", satisfied=True)
        b = ConfigurableState("b", satisfied=True)
        c = ConfigurableState("c", satisfied=False)

        task_a = a.satisfy(ctx)
        task_b = b.satisfy(ctx).after(task_a)
        task_c = c.satisfy(ctx).after(task_b)

        divergence = task_c.find_divergence()

        assert divergence is task_c

    def test_divergence_in_diamond(self, mock_machine_context) -> None:
        """Divergence is found in diamond dependency structure."""
        ctx = mock_machine_context()
        # Diamond: A -> (B, C) -> D
        a = ConfigurableState("a", satisfied=True)
        b = ConfigurableState("b", satisfied=True)
        c = ConfigurableState("c", satisfied=False)  # Divergence
        d = ConfigurableState("d", satisfied=True)

        task_a = a.satisfy(ctx)
        task_b = b.satisfy(ctx).after(task_a)
        task_c = c.satisfy(ctx).after(task_a)
        task_d = d.satisfy(ctx).after(task_b, task_c)

        divergence = task_d.find_divergence()

        # Should find task_c as the first unsatisfied
        assert divergence is task_c


# =============================================================================
# find_divergence Tests - Efficiency
# =============================================================================


class TestBinarySearchEfficiency:
    """Tests verifying binary search is more efficient than linear for chains."""

    def test_fewer_checks_than_linear_for_chain(self, mock_machine_context) -> None:
        """Binary search should check fewer nodes than linear scan for chains."""
        ctx = mock_machine_context()

        # Linear chain (8 states), divergence at state 7
        states = [ConfigurableState(str(i), satisfied=(i < 6)) for i in range(8)]

        # Build chain: 0 -> 1 -> 2 -> ... -> 7
        tasks = []
        for i, state in enumerate(states):
            t = state.satisfy(ctx)
            if i > 0:
                t.after(tasks[i - 1])
            tasks.append(t)

        divergence = tasks[-1].find_divergence()

        assert divergence is tasks[6]  # First unsatisfied (index 6 = state "6")

        # Count total check calls
        total_checks = sum(s.check_count for s in states)

        # Binary search should check fewer than all 8 nodes
        assert total_checks < 8, f"Expected fewer than 8 check calls, got {total_checks}"


# =============================================================================
# Task.all() with find_divergence
# =============================================================================


class TestTaskAllDivergence:
    """Tests for find_divergence with Task.all() combined tasks."""

    def test_find_divergence_with_all(self, mock_machine_context) -> None:
        """find_divergence works with Task.all() combined tasks."""
        ctx = mock_machine_context()
        a = ConfigurableState("a", satisfied=True)
        b = ConfigurableState("b", satisfied=False)
        c = ConfigurableState("c", satisfied=True)

        combined = Task.all(a.satisfy(ctx), b.satisfy(ctx), c.satisfy(ctx))
        divergence = combined.find_divergence()

        assert divergence is not None
        # Should find b as the unsatisfied task
        assert divergence.state is b

    def test_find_divergence_independent_tasks(self, mock_machine_context) -> None:
        """find_divergence does not skip earlier unsatisfied tasks."""
        ctx = mock_machine_context()
        a = ConfigurableState("a", satisfied=False)
        b = ConfigurableState("b", satisfied=True)
        c = ConfigurableState("c", satisfied=True)

        combined = Task.all(a.satisfy(ctx), b.satisfy(ctx), c.satisfy(ctx))
        divergence = combined.find_divergence()

        assert divergence is not None
        assert divergence.state is a
