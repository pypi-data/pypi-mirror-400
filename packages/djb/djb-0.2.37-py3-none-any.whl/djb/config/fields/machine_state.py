"""MachineStateConfig - Nested config for machine state settings."""

from __future__ import annotations

from djb.config.field import ConfigBase
from djb.config.fields.enum import EnumField
from djb.config.storage import CoreConfigIO
from djb.machine_state import SearchStrategy


class MachineStateConfig(ConfigBase):
    """Nested config for machine state settings.

    Fields:
        search_strategy: Strategy for finding first unsatisfied task in find_divergence().
            AUTO (default) uses binary search for linear chains, linear for DAGs.
            LINEAR always uses linear scan O(n).
            BINARY always uses binary search O(log n).

    Configured via TOML:
        [machine_state]
        search_strategy = "auto"

    Access values via:
        config.machine_state.search_strategy  # SearchStrategy.AUTO by default
    """

    search_strategy: SearchStrategy = EnumField(SearchStrategy, config_storage=CoreConfigIO)
