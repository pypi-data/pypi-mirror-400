"""djb - Django + Bun deployment platform.

Import from submodules for best performance:
    from djb.core.logging import get_logger, setup_logging
    from djb.config import get_djb_config, DjbConfig
    from djb.cli.epilog import get_cli_epilog
    from djb.django import health_check, health_check_ready
"""

from djb._version import __version__

__all__ = ["__version__"]
