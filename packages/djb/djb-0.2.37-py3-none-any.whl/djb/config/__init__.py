"""
djb.config - Unified configuration system for djb CLI.

Quick start:
    from djb import get_djb_config

    config = get_djb_config()
    print(f"Mode: {config.mode}")        # development, staging, production
    print(f"Platform: {config.platform}")  # heroku
    print(f"Project: {config.project_name}")

Configuration is loaded with the following priority (highest to lowest):
1. Explicit kwargs passed to get_djb_config()
2. Environment variables (DJB_ prefix)
3. Local config (.djb/local.toml) - user-specific, gitignored
4. Project config (.djb/project.toml) - shared, committed
5. Core config (djb/config/core.toml) - djb defaults
6. Field default values

Each config file can have mode-based sections ([development], [staging]).
For non-production modes, the mode section is merged onto root values within each file.
File priority takes precedence over section priority.

The config_class option allows host projects to extend DjbConfig with custom fields.

Two config files are used:
- .djb/local.toml: User-specific settings (name, email, mode) - NOT committed
- .djb/project.toml: Project settings (project_name, platform) - committed

Local config can override any project setting for user experimentation.

## Public API

### Main API
- get_djb_config: Factory function to create config instances
- DjbConfig: Configuration class with reload() and augment() methods

### Config Storage
- get_config_dir: Get path to .djb/ directory
- LocalConfigIO, ProjectConfigType, CoreConfigIO, DerivedConfigType: Config store classes
- Create instances with config: `store = LocalConfigIO(config)`

### Field System (for extending DjbConfig)
- ConfigFieldABC: Abstract base class for config fields
- StringField, EnumField, ClassField: Common field types
- ProjectDirField, ProjectNameField, EmailField, SeedCommandField: Specialized fields
- ATTRSLIB_METADATA_KEY: Metadata key for storing ConfigField in attrs metadata

### Project Detection
- find_project_root: Find the project root directory
- find_pyproject_root: Find the nearest pyproject.toml

### Validation & Normalization
- ConfigValidationError: Exception for validation failures
- normalize_project_name: Normalize a string to DNS-safe label
- get_project_name_from_pyproject: Extract project name from pyproject.toml
- DEFAULT_PROJECT_NAME: Default project name when resolution fails
- DNS_LABEL_PATTERN: Pattern for validating DNS labels
"""

from djb.config.acquisition import (
    AcquisitionContext,
    AcquisitionResult,
    acquire_all_fields,
)
from djb.config.field import (
    ClassField,
    ConfigFieldABC,
    ConfigValidationError,
    StringField,
    pass_config,
)
from djb.config.fields import (
    CloudflareConfig,
    EnumField,
    HerokuConfig,
    HetznerConfig,
    K8sBackendConfig,
    K8sConfig,
)
from djb.config.constants import HetznerImage, HetznerLocation, HetznerServerType
from djb.config.config import (
    DjbConfig,
    DjbConfigBase,
    LetsEncryptConfig,
    get_djb_config,
    get_field_descriptor,
    normalize_and_validate,
)
from djb.config.fields import (
    DEFAULT_PROJECT_NAME,
    DNS_LABEL_PATTERN,
    EmailField,
    ProjectDirField,
    ProjectNameField,
    SeedCommandField,
    get_project_name_from_pyproject,
    normalize_project_name,
)
from djb.config.storage import (
    CoreConfigIO,
    DerivedConfigType,
    LocalConfigIO,
    ProjectConfigType,
    get_config_dir,
    navigate_config_path,
)
from djb.config.fields import find_project_root, find_pyproject_root
from djb.config.constants import ATTRSLIB_METADATA_KEY

__all__ = [
    # Main API
    "get_djb_config",
    "DjbConfig",
    "DjbConfigBase",
    # Nested config types
    "CloudflareConfig",
    "HerokuConfig",
    "HetznerConfig",
    "K8sBackendConfig",
    "K8sConfig",
    "LetsEncryptConfig",
    # Hetzner enums
    "HetznerImage",
    "HetznerLocation",
    "HetznerServerType",
    # Config storage
    "get_config_dir",
    "LocalConfigIO",
    "ProjectConfigType",
    "CoreConfigIO",
    "DerivedConfigType",
    "navigate_config_path",
    # Field system
    "ConfigFieldABC",
    "StringField",
    "EnumField",
    "ClassField",
    "ProjectDirField",
    "ProjectNameField",
    "EmailField",
    "SeedCommandField",
    "pass_config",
    "ATTRSLIB_METADATA_KEY",
    "get_field_descriptor",
    # Interactive acquisition (for field.acquire())
    "AcquisitionContext",
    "AcquisitionResult",
    "acquire_all_fields",
    # Project detection
    "find_project_root",
    "find_pyproject_root",
    # Validation & normalization
    "ConfigValidationError",
    "normalize_and_validate",
    "normalize_project_name",
    "get_project_name_from_pyproject",
    "DEFAULT_PROJECT_NAME",
    "DNS_LABEL_PATTERN",
]
