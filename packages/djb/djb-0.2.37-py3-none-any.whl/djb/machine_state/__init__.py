"""Task-based declarative deployment system.

MachineState is declarative. Each state is one atomic property that must be true.
The Task-based model allows composing states into a DAG for execution.

The model:
    describe(ctx) -> str   # What is being managed (noun for user feedback)
    skip(ctx) -> bool      # Should this state be skipped? (default: False)
    check(ctx) -> bool     # Is this state satisfied?
    satisfy(ctx) -> Task   # Returns a Task that will make it satisfied

Core Concepts:
- MachineStateABC: Base class for all states
- Task: A node in the execution DAG
- @task: Decorator for leaf state satisfy methods
- HealthReport: Result of checking a DAG

Example - Leaf state:
    from djb.machine_state import MachineStateABC, task, MachineContext

    class VPSExists(MachineStateABC):
        def describe(self, ctx: MachineContext) -> str:
            return f"VPS '{ctx.config.server_name}'"

        def skip(self, ctx: MachineContext) -> bool:
            return not ctx.config.use_vps  # Skip if not using VPS

        def check(self, ctx: MachineContext) -> bool:
            return hetzner_api.server_exists(ctx.config.server_name)

        @task
        def satisfy(self, ctx: MachineContext) -> None:
            hetzner_api.create_server(ctx.config.server_name)

Example - Composite state (class attributes):
    class K8sCluster(MachineStateABC):
        dns = K8sAddon("dns")
        storage = K8sAddon("storage", depends_on=["dns"])
        ingress = K8sAddon("ingress", depends_on=["dns"])

        # satisfy() auto-generated from class attributes
        # check() and describe() should be implemented

Example - Composite with control flow (escape hatch):
    class ConditionalCluster(MachineStateABC):
        def satisfy(self, ctx: MachineContext) -> Task:
            dns = K8sAddon("dns").satisfy(ctx)
            if ctx.config.enable_storage:
                storage = K8sAddon("storage").satisfy(ctx).after(dns)
            ingress = K8sAddon("ingress").satisfy(ctx).after(dns)
            return Task.all(dns, storage, ingress)

Barrel Exports:
    MachineStateABC, CheckResult, Task, task, find_leaves, HealthReport,
    ExecuteResult, MachineContext, CacheConfig, BaseOptions, ForceCreateOptions,
    SearchStrategy, TOptions
"""

from .base import CheckResult, HealthReport, MachineStateABC, Task, find_leaves, task
from .types import (
    BaseOptions,
    CacheConfig,
    ExecuteResult,
    ForceCreateOptions,
    MachineContext,
    SearchStrategy,
    TOptions,
)

__all__ = [
    # Base class
    "MachineStateABC",
    # Check result
    "CheckResult",
    # Task system
    "Task",
    "task",
    "find_leaves",
    "HealthReport",
    # Result types
    "ExecuteResult",
    # Context
    "MachineContext",
    "CacheConfig",
    "TOptions",
    # Options
    "BaseOptions",
    "ForceCreateOptions",
    "SearchStrategy",
]
