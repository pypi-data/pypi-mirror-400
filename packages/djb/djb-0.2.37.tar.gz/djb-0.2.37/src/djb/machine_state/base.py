"""Base class for the MachineState system.

MachineState is declarative. Each state is one atomic property that must be true.
The Task-based model allows composing states into a DAG for execution.

The model:
    describe(ctx) -> str   # What is being managed (noun for user feedback)
    skip(ctx) -> bool      # Should this state be skipped? (default: False)
    check(ctx) -> bool     # Is this state satisfied?
    satisfy(ctx) -> Task   # Returns a Task that will make it satisfied

Principles:
    1. Atomic states: Each MachineState = one boolean check + one action
    2. Decompose complexity: If you need complex state, split into multiple states
    3. Composition = AND: All tasks in a DAG must be satisfied
    4. Conditional skip: Override skip() to skip states not applicable in context
    5. Control flow allowed: satisfy() can use conditionals to build the Task DAG

Two ways to compose states:
    1. Class attributes (static, declarative):
        class K8sCluster(MachineStateABC):
            dns = K8sAddon("dns")
            storage = K8sAddon("storage", depends_on=[dns])
            ingress = K8sAddon("ingress", depends_on=[dns])

    2. Explicit Task building (dynamic, control flow):
        class ConditionalCluster(MachineStateABC):
            def satisfy(self, ctx) -> Task:
                dns = K8sAddon("dns").satisfy(ctx)
                if ctx.config.enable_storage:
                    storage = K8sAddon("storage").satisfy(ctx).after(dns)
                return Task.all(dns, storage, ...)

Task-based execution graph:
    Tasks represent deferred work that can be composed into a DAG.
    The DAG can be consumed in different ways:
    - run() - Execute the tasks
    - dry_run() - Preview what would happen
    - health_check() - Check current state without changes
"""

from __future__ import annotations

import functools
import re
from abc import ABC, ABCMeta
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Callable

from djb.config.utils import topological_sort

from .types import ExecuteResult, SearchStrategy


class CheckResult(Enum):
    """Internal result type for Task execution.

    Used by Task.run(), Task.health_check() etc. to track state.
    Not part of the public MachineState API - check() returns bool.
    """

    SATISFIED = "satisfied"
    UNSATISFIED = "unsatisfied"
    SKIP = "skip"


if TYPE_CHECKING:
    from .types import MachineContext


@dataclass
class HealthReport:
    """Report from checking a task DAG."""

    satisfied: list[str]  # Task descriptions that are satisfied
    unsatisfied: list[str]  # Task descriptions that need work
    skipped: list[str]  # Task descriptions that were skipped (not applicable)
    errors: list[str]  # Errors encountered during sensing

    @property
    def all_satisfied(self) -> bool:
        """True if all applicable tasks are satisfied (skipped tasks don't count)."""
        return len(self.unsatisfied) == 0 and len(self.errors) == 0


@dataclass
class Task:
    """A node in the execution DAG.

    Tasks are created by MachineState.satisfy() and can be composed
    using after() and Task.all().

    The ctx (MachineContext) is captured when the Task is created via satisfy(),
    so run(), dry_run(), health_check() etc. don't need it passed again.
    """

    state: MachineStateABC
    ctx: MachineContext
    work: Callable[[], None]
    depends_on: list[Task] = field(default_factory=list)
    _executed: bool = field(default=False, repr=False)

    def after(self, *deps: Task) -> Task:
        """Add dependencies (fluent API).

        Returns self for chaining.
        """
        self.depends_on.extend(deps)
        return self

    def run(self) -> ExecuteResult:
        """Execute this task and all dependencies.

        Runs dependencies first, then checks, then satisfies if needed.
        Check results:
        - SATISFIED: Skip satisfy, return changed=False
        - UNSATISFIED: Run satisfy, return changed=True
        - SKIP: Skip satisfy, return changed=False with "Skipped" message
        """
        # Skip if already executed (DAG may have shared nodes)
        if self._executed:
            return ExecuteResult(
                source=self.state,
                success=True,
                changed=False,
                message="Already executed",
            )

        # Execute dependencies first
        for dep in self.depends_on:
            result = dep.run()
            if not result.success:
                return result

        # Check skip first, then check
        try:
            check_result = self._get_check_result()

            if check_result == CheckResult.SKIP:
                self._executed = True
                return ExecuteResult(
                    source=self.state,
                    success=True,
                    changed=False,
                    message="Skipped (not applicable)",
                )

            if check_result == CheckResult.SATISFIED:
                self._executed = True
                return ExecuteResult(
                    source=self.state,
                    success=True,
                    changed=False,
                    message="Already satisfied",
                )
        except Exception as e:
            return ExecuteResult(
                source=self.state,
                success=False,
                changed=False,
                message=f"Check failed: {e}",
            )

        # Do the work (check_result == CheckResult.UNSATISFIED)
        try:
            self.ctx.log(self.state, "Satisfying...")
            self.work()
            self._executed = True
            return ExecuteResult(
                source=self.state,
                success=True,
                changed=True,
                message="Satisfied",
            )
        except Exception as e:
            return ExecuteResult(
                source=self.state,
                success=False,
                changed=False,
                message=str(e),
            )

    def _get_check_result(self) -> CheckResult:
        """Get the check result, calling skip() first.

        Returns:
            SKIP if skip() returns True
            SATISFIED if check() returns True
            UNSATISFIED if check() returns False
        """
        if self.state.skip(self.ctx):
            return CheckResult.SKIP
        return CheckResult.SATISFIED if self.state.check(self.ctx) else CheckResult.UNSATISFIED

    def dry_run(self) -> list[str]:
        """Preview what would be done (without executing).

        Returns list of descriptions for unsatisfied tasks.
        Skipped tasks (SKIP) are not included.
        """
        result: list[str] = []

        # Check dependencies first
        for dep in self.depends_on:
            result.extend(dep.dry_run())

        # Check this task
        try:
            check_result = self._get_check_result()
            if check_result == CheckResult.UNSATISFIED:
                result.append(self.state.describe(self.ctx))
            # SKIP and SATISFIED: don't add to result
        except Exception:
            result.append(f"{self.state.describe(self.ctx)} (check failed)")

        return result

    def health_check(self) -> HealthReport:
        """Check current state of all tasks in DAG."""
        satisfied: list[str] = []
        unsatisfied: list[str] = []
        skipped: list[str] = []
        errors: list[str] = []

        for task in self.walk():
            desc = task.state.describe(task.ctx)
            try:
                check_result = task._get_check_result()
                if check_result == CheckResult.SATISFIED:
                    satisfied.append(desc)
                elif check_result == CheckResult.UNSATISFIED:
                    unsatisfied.append(desc)
                else:  # SKIP
                    skipped.append(desc)
            except Exception as e:
                errors.append(f"{desc}: {e}")

        return HealthReport(
            satisfied=satisfied,
            unsatisfied=unsatisfied,
            skipped=skipped,
            errors=errors,
        )

    def find_divergence(self) -> Task | None:
        """Find first unsatisfied task, using configurable search strategy.

        The search strategy is controlled by ctx.options.search_strategy:
        - AUTO (default): Binary search for linear chains, linear for DAGs
        - LINEAR: Always use linear scan O(n)
        - BINARY: Always use binary search O(log n) - only valid for linear chains

        For linear chains, we can binary search because if task X is satisfied,
        all its dependencies (ancestors in the DAG) must also be satisfied.
        For DAGs with branches, this property doesn't apply to siblings, so
        we fall back to a linear scan to stay correct.

        Returns the first unsatisfied task in topological order, or None if all
        satisfied (or skipped).

        Efficiency: O(log n) for linear chains. For DAGs with parallel branches
        (diamond patterns), worst case is O(n) because checking a task only
        proves its ancestors are satisfied, not its siblings.
        """
        tasks = self.walk()
        if not tasks:
            return None

        # Get search strategy from options (default to AUTO if options not set)
        strategy = SearchStrategy.AUTO
        if self.ctx.options is not None:
            strategy = self.ctx.options.search_strategy

        # Determine actual algorithm based on strategy
        use_binary = False
        if strategy == SearchStrategy.AUTO:
            use_binary = self._is_linear_chain(tasks)
        elif strategy == SearchStrategy.BINARY:
            use_binary = True
        # LINEAR: use_binary stays False

        if not use_binary:
            return self._find_divergence_linear(tasks)

        # Binary search for divergence point
        lo, hi = 0, len(tasks) - 1

        while lo < hi:
            mid = (lo + hi) // 2
            try:
                check_result = tasks[mid]._get_check_result()
                if check_result in (CheckResult.SATISFIED, CheckResult.SKIP):
                    # Mid is satisfied/skipped, divergence must be after
                    lo = mid + 1
                else:
                    # Mid is unsatisfied, divergence is at or before
                    hi = mid
            except Exception:
                # Check failed - treat as unsatisfied
                hi = mid

        # lo == hi, check if this task is actually unsatisfied
        try:
            check_result = tasks[lo]._get_check_result()
            if check_result in (CheckResult.SATISFIED, CheckResult.SKIP):
                return None  # All satisfied/skipped
        except Exception:
            pass  # Check failed, treat as unsatisfied

        return tasks[lo]

    @staticmethod
    def _is_linear_chain(tasks: list[Task]) -> bool:
        """Return True if tasks form a strict linear chain in walk order."""
        if not tasks:
            return True
        if tasks[0].depends_on:
            return False
        for i in range(1, len(tasks)):
            deps = tasks[i].depends_on
            if len(deps) != 1 or deps[0] is not tasks[i - 1]:
                return False
        return True

    def _find_divergence_linear(self, tasks: list[Task]) -> Task | None:
        """Return first unsatisfied task by scanning in topological order."""
        for task in tasks:
            try:
                check_result = task._get_check_result()
                if check_result == CheckResult.UNSATISFIED:
                    return task
                # SATISFIED and SKIP: continue to next task
            except Exception:
                return task
        return None

    def walk(self) -> list[Task]:
        """Walk the DAG in topological order (dependencies first)."""
        visited: set[int] = set()
        result: list[Task] = []

        def visit(task: Task) -> None:
            task_id = id(task)
            if task_id in visited:
                return
            visited.add(task_id)
            for dep in task.depends_on:
                visit(dep)
            result.append(task)

        visit(self)
        return result

    @staticmethod
    def all(*tasks: Task) -> Task:
        """Combine multiple tasks into one.

        Returns a synthetic task that depends on all input tasks.
        Inherits ctx from the first dependency.
        """
        if not tasks:
            raise ValueError("Task.all() requires at least one task")

        # Inherit ctx from first dependency
        ctx = tasks[0].ctx

        class CombinedState(MachineStateABC):
            """Synthetic state for Task.all()."""

            def describe(self, ctx: MachineContext) -> str:
                return "Combined tasks"

            def check(self, ctx: MachineContext) -> bool:
                return True  # Always satisfied if deps are

            def satisfy(self, ctx: MachineContext) -> Task:
                return Task(state=self, ctx=ctx, work=lambda: None)

        combined = CombinedState()
        return Task(
            state=combined,
            ctx=ctx,
            work=lambda: None,
            depends_on=list(tasks),
        )


def task(method: Callable[..., None]) -> Callable[..., Task]:
    """Decorator to wrap a satisfy() method to return a Task.

    Usage:
        class MyState(MachineStateABC):
            @task
            def satisfy(self, ctx):
                # Do actual work here
                ...

    The decorated method will return a Task instead of executing immediately.
    The ctx is captured and stored on the Task.
    """

    @functools.wraps(method)
    def wrapper(self: MachineStateABC, ctx: MachineContext) -> Task:
        return Task(
            state=self,
            ctx=ctx,
            work=lambda: method(self, ctx),
            depends_on=[],
        )

    return wrapper


def find_leaves(tasks: list[Task]) -> list[Task]:
    """Find tasks that no other task in the collection depends on.

    Used by composite states to combine their substates into a single Task.
    The "leaves" are the end points of the DAG - running them will run
    all their dependencies transitively.

    Example:
        DAG:  dns -> storage
              dns -> ingress

        leaves = [storage, ingress]  # dns is depended on, so not a leaf
    """
    all_deps: set[int] = set()
    for t in tasks:
        for dep in t.depends_on:
            all_deps.add(id(dep))
    return [t for t in tasks if id(t) not in all_deps]


class MachineStateMeta(ABCMeta):
    """Metaclass that discovers and sorts substates at class definition time."""

    _substates: dict[str, "MachineStateABC"]
    _substates_sorted: list[tuple[str, "MachineStateABC"]]

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict,
        **kwargs,
    ):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        # Discover MachineStateABC instances in class attributes
        # Skip for the base class itself (MachineStateABC not yet defined)
        substates: dict[str, MachineStateABC] = {}
        state_base = globals().get("MachineStateABC")
        if bases and state_base is not None:  # Not the base class
            for attr_name, attr_value in namespace.items():
                if not attr_name.startswith("_") and isinstance(attr_value, state_base):
                    substates[attr_name] = attr_value

        # Topologically sort substates (dependencies first)
        if substates:
            # Build reverse map: instance -> name
            instance_to_name = {id(s): n for n, s in substates.items()}

            deps = {
                attr_name: [
                    instance_to_name[id(d)]
                    for d in (getattr(s, "depends_on", []) or [])
                    if id(d) in instance_to_name
                ]
                for attr_name, s in substates.items()
            }
            sorted_names = topological_sort(deps)
            cls._substates_sorted = [(n, substates[n]) for n in sorted_names]
        else:
            cls._substates_sorted = []

        cls._substates = substates
        return cls


class MachineStateABC(ABC, metaclass=MachineStateMeta):
    """Base class for all machine states.

    A MachineState represents a single atomic property that must be true.
    Each state has three core methods:

    - describe(): What is being managed (noun/sentence for user feedback).
    - check(): Is this state satisfied? Returns bool.
    - satisfy(): Returns a Task that will make it satisfied.

    Example - Leaf state (use @task decorator):

        class VPSExists(MachineStateABC):
            def describe(self, ctx: MachineContext) -> str:
                return f"VPS '{ctx.config.server_name}'"

            def check(self, ctx: MachineContext) -> bool:
                return hetzner_api.server_exists(ctx.config.server_name)

            @task
            def satisfy(self, ctx: MachineContext) -> None:
                server = hetzner_api.create_server(ctx.config.server_name)
                ctx.config.set("k8s.host", server.ip)

    Example - Composite state (builds a Task DAG):

        class K8sCluster(MachineStateABC):
            def describe(self, ctx: MachineContext) -> str:
                return "K8s cluster"

            def check(self, ctx: MachineContext) -> bool:
                # Optional: derive from DAG
                dag = self.satisfy(ctx)
                return dag.health_check().all_satisfied

            def satisfy(self, ctx: MachineContext) -> Task:
                dns = K8sAddon("dns").satisfy(ctx)
                storage = K8sAddon("storage").satisfy(ctx).after(dns)
                ingress = K8sAddon("ingress").satisfy(ctx).after(dns)
                return Task.all(dns, storage, ingress)
    """

    depends_on: list[MachineStateABC] = []

    def describe(self, ctx: MachineContext) -> str:
        """What is being managed by this state (noun or sentence).

        This is used for user feedback in logs and dry-run output.
        Should be a noun or short sentence describing the thing, not an action.

        Examples:
            - "VPS 'my-server'"
            - "SSH connection to 192.168.1.1"
            - "microk8s DNS addon"
            - "K8s cluster"

        For leaf states: Must override (too specific to derive).
        For composite states: Auto-derived from class name (e.g., K8sCluster -> "K8s cluster").
        """
        if not self._substates:
            raise NotImplementedError(f"{self.__class__.__name__} must implement describe()")
        return self._class_name_to_sentence()

    def skip(self, ctx: MachineContext) -> bool:
        """Should this state be skipped?

        Override to conditionally skip states that aren't applicable in context.
        Default returns False (don't skip).

        Examples:
            - Skip Hetzner provisioning when not using Hetzner provider
            - Skip TLS setup when no_tls flag is set
            - Skip CloudNativePG when no_cloudnativepg flag is set

        For composite states: Skip if ALL substates skip.
        """
        if not self._substates:
            return False

        # For composites: skip only if ALL substates skip
        return all(state.skip(ctx) for state in self._substates.values())

    def check(self, ctx: MachineContext) -> bool:
        """Is this state satisfied?

        Returns:
            True: State is satisfied, no work needed
            False: State needs satisfy() to be run

        Note: To skip a state entirely, override skip() instead.

        For leaf states: Check the actual resource (must override).
        For composite states: Auto-derived from substates (all must be satisfied).
        """
        if not self._substates:
            raise NotImplementedError(f"{self.__class__.__name__} must implement check()")

        # Check all substates - if any non-skipped is unsatisfied, return False
        for state in self._substates.values():
            if state.skip(ctx):
                continue
            if not state.check(ctx):
                return False
        return True

    def satisfy(self, ctx: MachineContext) -> Task:
        """Return a Task that will make this state satisfied.

        For leaf states: Use the @task decorator.
        For composite states: Use class attributes or build a Task DAG.

        Default behavior: If class has substate attributes, builds Task from them.
        Otherwise raises NotImplementedError (leaf states must override with @task).

        The Task is not executed immediately - the caller decides what to do
        with it (run, dry_run, health_check).

        For composites: If skip() returns True, returns None (callers must check).
        Skipped substates are also excluded from the DAG.
        """
        if not self._substates:
            raise NotImplementedError(
                f"{self.__class__.__name__} must implement satisfy() with @task decorator"
            )

        # If composite itself is skipped, return None - no Task at all.
        # Callers that embed this composite must check for None.
        if self.skip(ctx):
            return None  # type: ignore[return-value]

        # Build Task DAG from class attributes
        tasks: dict[int, Task] = {}
        for _, state in self._substates_sorted:
            t = state.satisfy(ctx)
            if t is None:
                continue
            for dep in getattr(state, "depends_on", []) or []:
                if id(dep) in tasks:
                    t.after(tasks[id(dep)])
            tasks[id(state)] = t

        # If all substates were skipped, return None
        if not tasks:
            return None  # type: ignore[return-value]

        # Combine leaf tasks (tasks that nothing else depends on)
        leaves = find_leaves(list(tasks.values()))
        if len(leaves) == 1:
            return leaves[0]
        return Task.all(*leaves)

    def _class_name_to_sentence(self) -> str:
        """Convert class name to sentence case (e.g., K8sCluster -> K8s cluster)."""
        name = self.__class__.__name__
        # Split on lower->upper transitions and acronym->word boundaries
        spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", name)
        spaced = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", spaced)
        parts = spaced.split()
        if not parts:
            return name
        sentence_parts: list[str] = [parts[0]]
        for part in parts[1:]:
            if part.isupper() or any(char.isdigit() for char in part):
                sentence_parts.append(part)
            else:
                sentence_parts.append(part.lower())
        return " ".join(sentence_parts)
