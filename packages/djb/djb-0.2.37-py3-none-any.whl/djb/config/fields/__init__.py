"""
Specialized config field subclasses.

Re-exports all field classes for convenient importing.
"""

from djb.config.fields.bool import BoolField
from djb.config.fields.cloudflare import CloudflareConfig
from djb.config.fields.domain import DomainNameField
from djb.config.fields.domain_config import DomainNameConfig
from djb.config.fields.domain_names import DomainNamesMapField
from djb.config.fields.email import EmailField
from djb.config.fields.enum import EnumField
from djb.config.fields.heroku import HerokuConfig
from djb.config.fields.hetzner import HetznerConfig
from djb.config.fields.int import IntField
from djb.config.fields.ip import IPAddressField
from djb.config.fields.k8s import K8sBackendConfig, K8sConfig
from djb.config.fields.list import ListField
from djb.config.fields.log_level import DEFAULT_LOG_LEVEL, VALID_LOG_LEVELS, LogLevelField
from djb.config.fields.name import NameField
from djb.config.fields.project_dir import (
    PROJECT_DIR_ENV_KEY,
    ProjectDirField,
    find_project_root,
    find_pyproject_root,
)
from djb.config.fields.project_name import (
    DEFAULT_PROJECT_NAME,
    DNS_LABEL_PATTERN,
    ProjectNameField,
    get_project_name_from_pyproject,
    normalize_project_name,
)
from djb.config.fields.seed_command import SeedCommandField

__all__ = [
    # Field classes
    "BoolField",
    "DomainNameField",
    "DomainNameConfig",
    "DomainNamesMapField",
    "EnumField",
    "IntField",
    "IPAddressField",
    "ListField",
    "ProjectDirField",
    "ProjectNameField",
    "EmailField",
    "LogLevelField",
    "NameField",
    "SeedCommandField",
    # Nested config types
    "CloudflareConfig",
    "HerokuConfig",
    "HetznerConfig",
    "K8sBackendConfig",
    "K8sConfig",
    # Project detection
    "find_project_root",
    "find_pyproject_root",
    "PROJECT_DIR_ENV_KEY",
    # Helpers
    "normalize_project_name",
    "get_project_name_from_pyproject",
    "DNS_LABEL_PATTERN",
    "DEFAULT_PROJECT_NAME",
    "DEFAULT_LOG_LEVEL",
    "VALID_LOG_LEVELS",
]
