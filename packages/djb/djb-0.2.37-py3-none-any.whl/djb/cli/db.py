"""
djb db CLI - Database management commands.

Provides commands for setting up and managing PostgreSQL databases for development.
"""

from __future__ import annotations

import shutil
from collections.abc import Callable
from dataclasses import dataclass
from enum import IntEnum, auto
from time import sleep, time

import click

from djb.cli.context import CliContext, djb_pass_context
from djb.core.cmd_runner import RunResult
from djb.core.logging import get_logger
from djb.secrets import SopsError, load_secrets
from djb.types import Mode

logger = get_logger(__name__)


# Extensions required for the application.
# These are created during database initialization with superuser privileges.
REQUIRED_EXTENSIONS = ["postgis"]

# Template database name. Used by pytest-django to create test databases
# with extensions pre-installed.
TEMPLATE_DB_NAME = "template_postgis"

# Timeout for waiting for PostgreSQL to become available (seconds).
# Used by wait_for_postgres() when checking if the database server is ready.
POSTGRES_AVAILABILITY_TIMEOUT = 10.0

# Interval between PostgreSQL availability checks (seconds).
POSTGRES_WAIT_INTERVAL: float = 0.5


class DbStatus(IntEnum):
    """Database connection status levels."""

    UNINSTALLED = auto()  # PostgreSQL not installed
    UNREACHABLE = auto()  # PostgreSQL not running
    NO_DATABASE = auto()  # Database doesn't exist
    NO_USER = auto()  # User doesn't exist or wrong password
    OK = auto()  # Everything is working


@dataclass
class DbSettings:
    """Database connection settings."""

    name: str
    user: str
    password: str
    host: str
    port: int


def _get_db_settings_from_secrets(cli_ctx: CliContext) -> DbSettings | None:
    """Get database settings from development secrets.

    Loads the db_credentials from the development secrets file (secrets/development.yaml).

    Args:
        cli_ctx: CLI context with runner and config.

    Returns:
        DbSettings if successful, None if secrets can't be loaded or db_credentials not found.
    """
    secrets_dir = cli_ctx.config.project_dir / "secrets"
    if not secrets_dir.exists():
        return None

    try:
        secrets = load_secrets(cli_ctx.runner, mode=Mode.DEVELOPMENT, secrets_dir=secrets_dir)
    except SopsError as e:
        # SOPS decryption failed - likely user's key not in .sops.yaml
        error_msg = str(e).lower()
        if "decrypt" in error_msg or "key" in error_msg or "recipient" in error_msg:
            logger.info(
                "Could not decrypt development secrets (your key may not be in .sops.yaml yet)"
            )
        else:
            logger.info(f"Could not load development secrets: {e}")
        return None
    except (FileNotFoundError, KeyError, ValueError, TypeError) as e:
        # FileNotFoundError: secrets file doesn't exist
        # KeyError: expected key not in secrets dict
        # ValueError/TypeError: unexpected data format
        logger.debug(f"Could not load db settings from secrets: {e}")
        return None

    db_creds = secrets.get("db_credentials")

    if not isinstance(db_creds, dict):
        return None

    # Extract settings with defaults
    return DbSettings(
        name=db_creds.get("database", ""),
        user=db_creds.get("username", ""),
        password=db_creds.get("password", ""),
        host=db_creds.get("host", "localhost"),
        port=int(db_creds.get("port", 5432)),
    )


def _get_default_db_settings(cli_ctx: CliContext) -> DbSettings:
    """Get default database settings based on project name.

    Args:
        cli_ctx: CLI context with config.

    Returns:
        DbSettings with defaults based on project name.
    """
    project_name = cli_ctx.config.project_name or cli_ctx.config.project_dir.name

    # Sanitize project name for database use (replace hyphens with underscores)
    db_name = project_name.replace("-", "_")

    return DbSettings(
        name=db_name,
        user=db_name,
        password="foobarqux",  # Default dev password
        host="localhost",
        port=5432,
    )


def get_db_settings(cli_ctx: CliContext) -> DbSettings:
    """Get database settings from development secrets, falling back to project-name defaults.

    Args:
        cli_ctx: CLI context with runner and config.

    Priority:
    1. db_credentials from secrets/development.yaml
    2. Defaults based on project name (database=project_name, user=project_name, password=foobarqux)

    For new users who haven't been added to .sops.yaml yet, the fallback
    provides sensible defaults so they can still set up their local database.
    """
    settings = _get_db_settings_from_secrets(cli_ctx)
    if settings and settings.name and settings.user:
        return settings

    # Fall back to project-name defaults
    defaults = _get_default_db_settings(cli_ctx)
    logger.info(f"Using default database settings (db={defaults.name}, user={defaults.user})")
    return defaults


def check_postgres_installed() -> bool:
    """Check if PostgreSQL client tools are installed."""
    return shutil.which("psql") is not None


def check_postgres_running(cli_ctx: CliContext, host: str = "localhost", port: int = 5432) -> bool:
    """Check if PostgreSQL server is reachable."""
    if not shutil.which("pg_isready"):
        return False
    result = cli_ctx.runner.run(["pg_isready", "-h", host, "-p", str(port)])
    return result.returncode == 0


def _run_psql(
    cli_ctx: CliContext,
    query: str,
    database: str = "postgres",
    host: str = "localhost",
    port: int = 5432,
) -> RunResult:
    """Run a psql query against the specified database."""
    return cli_ctx.runner.run(["psql", "-h", host, "-p", str(port), database, "-tAc", query])


def _ensure_state(
    cli_ctx: CliContext,
    *,
    check: Callable[[], bool],
    query: str,
    already_msg: str,
    success_msg: str,
    fail_msg: str,
    host: str = "localhost",
    port: int = 5432,
) -> bool:
    """Run a query only if a check fails, with appropriate logging.

    Args:
        cli_ctx: CLI context with runner.
        check: Predicate that returns True if the desired state already exists.
        query: SQL query to run if check returns False.
        already_msg: Message to log if state already exists.
        success_msg: Message to log on successful query.
        fail_msg: Message prefix for failed query.
        host: PostgreSQL host.
        port: PostgreSQL port.

    Returns:
        True on success (either already done or query succeeded), False on failure.
    """
    if check():
        logger.info(already_msg)
        return True

    result = _run_psql(cli_ctx, query, host=host, port=port)
    if result.returncode != 0:
        logger.fail(f"{fail_msg}: {result.stderr.strip()}")
        return False

    logger.done(success_msg)
    return True


def database_exists(
    cli_ctx: CliContext, name: str, host: str = "localhost", port: int = 5432
) -> bool:
    """Check if a database exists."""
    result = _run_psql(
        cli_ctx,
        f"SELECT 1 FROM pg_database WHERE datname='{name}';",
        host=host,
        port=port,
    )
    return result.stdout.strip() == "1"


def user_exists(
    cli_ctx: CliContext, username: str, host: str = "localhost", port: int = 5432
) -> bool:
    """Check if a database user exists."""
    result = _run_psql(
        cli_ctx,
        f"SELECT 1 FROM pg_user WHERE usename='{username}';",
        host=host,
        port=port,
    )
    return result.stdout.strip() == "1"


def user_is_superuser(
    cli_ctx: CliContext, username: str, host: str = "localhost", port: int = 5432
) -> bool:
    """Check if a database user has superuser privileges."""
    result = _run_psql(
        cli_ctx,
        f"SELECT usesuper FROM pg_user WHERE usename='{username}';",
        host=host,
        port=port,
    )
    return result.stdout.strip() == "t"


def user_has_database_privileges(
    cli_ctx: CliContext, username: str, database: str, host: str = "localhost", port: int = 5432
) -> bool:
    """Check if a database user has all privileges on a database."""
    result = _run_psql(
        cli_ctx,
        f"SELECT has_database_privilege('{username}', '{database}', 'CREATE');",
        host=host,
        port=port,
    )
    return result.stdout.strip() == "t"


def password_is_correct(
    cli_ctx: CliContext, username: str, password: str, host: str = "localhost", port: int = 5432
) -> bool:
    """Check if a user's password is correct by attempting to connect."""
    result = cli_ctx.runner.run(
        [
            "psql",
            "-h",
            host,
            "-p",
            str(port),
            "-U",
            username,
            "-d",
            "postgres",
            "-c",
            "SELECT 1;",
        ],
        env={"PGPASSWORD": password},
    )
    return result.returncode == 0


def can_connect_as_user(cli_ctx: CliContext, settings: DbSettings) -> bool:
    """Check if we can connect to the database as the specified user."""
    result = cli_ctx.runner.run(
        [
            "psql",
            "-h",
            settings.host,
            "-p",
            str(settings.port),
            "-U",
            settings.user,
            "-d",
            settings.name,
            "-c",
            "SELECT 1;",
        ],
        env={"PGPASSWORD": settings.password},
    )
    return result.returncode == 0


def get_db_status(cli_ctx: CliContext, settings: DbSettings) -> DbStatus:
    """Get the current database status."""
    if not check_postgres_installed():
        return DbStatus.UNINSTALLED

    if not check_postgres_running(cli_ctx, settings.host, settings.port):
        return DbStatus.UNREACHABLE

    if not database_exists(cli_ctx, settings.name, settings.host, settings.port):
        return DbStatus.NO_DATABASE

    if not user_exists(cli_ctx, settings.user, settings.host, settings.port):
        return DbStatus.NO_USER

    if can_connect_as_user(cli_ctx, settings):
        return DbStatus.OK

    return DbStatus.NO_USER


def create_database(cli_ctx: CliContext, settings: DbSettings) -> bool:
    """Create the database if it doesn't exist.

    Returns:
        True if database was created or already exists, False on error.
    """
    return _ensure_state(
        cli_ctx,
        check=lambda: database_exists(cli_ctx, settings.name, settings.host, settings.port),
        query=f"CREATE DATABASE {settings.name};",
        already_msg=f"Database '{settings.name}' already exists",
        success_msg=f"Database '{settings.name}' created",
        fail_msg="Failed to create database",
        host=settings.host,
        port=settings.port,
    )


def create_template_database(
    cli_ctx: CliContext, host: str = "localhost", port: int = 5432
) -> bool:
    """Create a template database with required extensions.

    Template databases allow new databases to inherit extensions
    without needing superuser privileges. This is used by pytest-django
    to create test databases.

    Returns:
        True on success, False on error.
    """
    # Check if template already exists
    result = _run_psql(
        cli_ctx,
        f"SELECT 1 FROM pg_database WHERE datname = '{TEMPLATE_DB_NAME}';",
        host=host,
        port=port,
    )
    if result.stdout.strip() == "1":
        logger.info(f"Template database '{TEMPLATE_DB_NAME}' already exists")
        return True

    logger.next(f"Creating template database '{TEMPLATE_DB_NAME}'")

    # Create template database
    result = cli_ctx.runner.run(["createdb", "-h", host, "-p", str(port), TEMPLATE_DB_NAME])
    if result.returncode != 0:
        logger.fail(f"Failed to create template database: {result.stderr.strip()}")
        return False

    # Add required extensions to template
    for ext in REQUIRED_EXTENSIONS:
        result = cli_ctx.runner.run(
            [
                "psql",
                "-h",
                host,
                "-p",
                str(port),
                TEMPLATE_DB_NAME,
                "-c",
                f"CREATE EXTENSION IF NOT EXISTS {ext};",
            ],
        )
        if result.returncode != 0:
            logger.fail(f"Failed to add extension '{ext}' to template: {result.stderr.strip()}")
            return False
        logger.info(f"Extension '{ext}' added to template")

    # Mark as template database
    result = _run_psql(
        cli_ctx,
        f"UPDATE pg_database SET datistemplate = true WHERE datname = '{TEMPLATE_DB_NAME}';",
        host=host,
        port=port,
    )
    if result.returncode != 0:
        logger.warning(f"Could not mark as template: {result.stderr.strip()}")
        # Continue anyway - the database still works for tests

    logger.done(f"Template database '{TEMPLATE_DB_NAME}' created with extensions")
    return True


def create_extensions(cli_ctx: CliContext, settings: DbSettings) -> bool:
    """Create required PostgreSQL extensions in the main database.

    Extensions like PostGIS require superuser privileges to create.
    This runs during init when we have superuser access (peer authentication),
    before handing off to the application user.

    Returns:
        True on success, False on error.
    """
    if not REQUIRED_EXTENSIONS:
        return True

    # Check which extensions already exist
    check_result = cli_ctx.runner.run(
        [
            "psql",
            "-h",
            settings.host,
            "-p",
            str(settings.port),
            settings.name,
            "-tAc",
            "SELECT extname FROM pg_extension;",
        ],
    )
    existing_extensions = (
        set(check_result.stdout.strip().split("\n")) if check_result.returncode == 0 else set()
    )

    extensions_to_create = [ext for ext in REQUIRED_EXTENSIONS if ext not in existing_extensions]

    if not extensions_to_create:
        logger.note(f"PostgreSQL extensions already exist in '{settings.name}'")
        return True

    logger.next(f"Creating PostgreSQL extensions in '{settings.name}'")

    for ext in extensions_to_create:
        # Connect to the target database (extensions are database-specific)
        result = cli_ctx.runner.run(
            [
                "psql",
                "-h",
                settings.host,
                "-p",
                str(settings.port),
                settings.name,
                "-c",
                f"CREATE EXTENSION IF NOT EXISTS {ext};",
            ],
        )
        if result.returncode != 0:
            logger.fail(f"Failed to create extension '{ext}': {result.stderr.strip()}")
            return False
        logger.info(f"Extension '{ext}' created")

    logger.done("PostgreSQL extensions created")
    return True


def create_user_and_grant(cli_ctx: CliContext, settings: DbSettings) -> bool:
    """Create user and grant privileges if needed.

    This is idempotent. If the user exists and password matches, no changes are made.
    Grants all privileges on the database to the user.

    Returns:
        True on success, False on error.
    """
    is_superuser = user_is_superuser(cli_ctx, settings.user, settings.host, settings.port)
    user_existed = user_exists(cli_ctx, settings.user, settings.host, settings.port)

    # Ensure user exists
    if not _ensure_state(
        cli_ctx,
        check=lambda: user_existed,
        query=f"CREATE USER {settings.user} WITH PASSWORD '{settings.password}';",
        already_msg=f"User '{settings.user}' exists",
        success_msg=f"User '{settings.user}' created",
        fail_msg="Failed to create user",
        host=settings.host,
        port=settings.port,
    ):
        return False

    if is_superuser:
        logger.warning(f"User '{settings.user}' is a superuser")

    # Ensure password is correct (skip for newly created users)
    if user_existed:
        if not _ensure_state(
            cli_ctx,
            check=lambda: password_is_correct(
                cli_ctx, settings.user, settings.password, settings.host, settings.port
            ),
            query=f"ALTER USER {settings.user} WITH PASSWORD '{settings.password}';",
            already_msg=f"User '{settings.user}' password already matches",
            success_msg=f"User '{settings.user}' password updated",
            fail_msg=f"Failed to update user '{settings.user}' password",
            host=settings.host,
            port=settings.port,
        ):
            return False

    # Ensure privileges on database
    def has_privileges() -> bool:
        if is_superuser:
            return True
        return user_has_database_privileges(
            cli_ctx, settings.user, settings.name, settings.host, settings.port
        )

    if not _ensure_state(
        cli_ctx,
        check=has_privileges,
        query=f"GRANT ALL PRIVILEGES ON DATABASE {settings.name} TO {settings.user};",
        already_msg=f"User '{settings.user}' already has privileges on '{settings.name}'",
        success_msg=f"Privileges granted on '{settings.name}'",
        fail_msg="Failed to grant privileges",
        host=settings.host,
        port=settings.port,
    ):
        return False

    return True


def grant_schema_permissions(cli_ctx: CliContext, settings: DbSettings) -> bool:
    """Grant schema permissions to the user.

    PostgreSQL 15+ requires explicit schema permissions for creating tables.

    Returns:
        True on success, False on error.
    """
    logger.next(f"Granting schema permissions to '{settings.user}'")

    # Connect to the target database to grant schema permissions
    result = cli_ctx.runner.run(
        [
            "psql",
            "-h",
            settings.host,
            "-p",
            str(settings.port),
            settings.name,
            "-c",
            f"GRANT ALL ON SCHEMA public TO {settings.user};",
        ],
    )

    if result.returncode == 0:
        logger.done("Schema permissions granted")
        return True
    else:
        # This might fail if the user doesn't have permission, but that's often OK
        logger.warning(f"Could not grant schema permissions: {result.stderr.strip()}")
        return True  # Non-fatal


def wait_for_postgres(
    cli_ctx: CliContext,
    host: str = "localhost",
    port: int = 5432,
    timeout: float = POSTGRES_AVAILABILITY_TIMEOUT,
) -> bool:
    """Wait for PostgreSQL to become available.

    Args:
        cli_ctx: CLI context with runner.
        host: PostgreSQL host
        port: PostgreSQL port
        timeout: Maximum seconds to wait

    Returns:
        True if PostgreSQL is available, False if timeout
    """
    logger.next(f"Waiting for PostgreSQL at {host}:{port}")
    start_time = time()

    while time() - start_time < timeout:
        if check_postgres_running(cli_ctx, host, port):
            logger.done("PostgreSQL is ready")
            return True
        sleep(POSTGRES_WAIT_INTERVAL)

    logger.fail(f"PostgreSQL not available after {timeout}s")
    return False


def start_postgres_service(cli_ctx: CliContext) -> bool:
    """Attempt to start PostgreSQL service via Homebrew.

    Args:
        cli_ctx: CLI context with runner.

    Returns:
        True if service started or already running, False on error.
    """
    if cli_ctx.runner.check(["brew", "services", "list"]):
        logger.next("Starting PostgreSQL service")
        result = cli_ctx.runner.run(["brew", "services", "start", "postgresql@17"])
        if result.returncode == 0:
            return True
        # Try without version suffix
        result = cli_ctx.runner.run(["brew", "services", "start", "postgresql"])
        return result.returncode == 0
    return False


def init_database(
    cli_ctx: CliContext,
    *,
    start_service: bool = True,
    quiet: bool = False,
) -> bool:
    """Initialize database with user and permissions.

    This is the main entry point for database initialization.
    It's idempotent - safe to run multiple times.

    Args:
        cli_ctx: CLI context with runner and config.
        start_service: Whether to attempt starting PostgreSQL if not running
        quiet: Suppress non-error output

    Returns:
        True on success, False on error
    """
    settings = get_db_settings(cli_ctx)

    if not quiet:
        logger.info(f"Database: {settings.name}")
        logger.info(f"User: {settings.user}")
        logger.info(f"Host: {settings.host}:{settings.port}")

    # Check PostgreSQL installation
    if not check_postgres_installed():
        logger.fail("PostgreSQL is not installed")
        logger.tip("Install with: brew install postgresql@17")
        return False

    # Check if PostgreSQL is running
    if not check_postgres_running(cli_ctx, settings.host, settings.port):
        if start_service:
            if not start_postgres_service(cli_ctx):
                logger.fail("Could not start PostgreSQL service")
                return False
            if not wait_for_postgres(cli_ctx, settings.host, settings.port):
                return False
        else:
            logger.fail("PostgreSQL is not running")
            logger.tip("Start with: brew services start postgresql@17")
            return False

    # Create template database for tests (needs superuser, do this first)
    if not create_template_database(cli_ctx, settings.host, settings.port):
        return False

    # Check current status
    status = get_db_status(cli_ctx, settings)

    # Create database if needed
    if status <= DbStatus.NO_DATABASE:
        if not create_database(cli_ctx, settings):
            return False

    # Create extensions in main database (needs superuser, before user creation)
    # Always run this - it's idempotent and ensures extensions exist
    if not create_extensions(cli_ctx, settings):
        return False

    # Create user and grant privileges
    if not create_user_and_grant(cli_ctx, settings):
        return False

    # Grant schema permissions (PostgreSQL 15+)
    if status != DbStatus.OK:
        grant_schema_permissions(cli_ctx, settings)

    # Verify final connection
    if can_connect_as_user(cli_ctx, settings):
        if not quiet:
            logger.done("Database initialization complete")
        return True
    else:
        logger.fail("Could not verify database connection")
        return False


@click.group("db")
def db():
    """Database management commands.

    Commands for setting up and managing PostgreSQL databases
    for local development.
    """
    pass


@db.command("init")
@click.option(
    "--no-start",
    is_flag=True,
    help="Don't attempt to start PostgreSQL service if not running",
)
@djb_pass_context
def db_init(cli_ctx: CliContext, no_start: bool):
    """Initialize development database.

    Creates the PostgreSQL database and user specified in Django settings.
    Uses defaults based on project name if Django settings aren't available.

    This command is idempotent. If the database and user already exist with
    correct credentials, this is a no-op.

    \b
    What this does:
    * Checks if PostgreSQL is installed and running
    * Creates the database if it doesn't exist
    * Creates the user if it doesn't exist
    * Grants necessary permissions

    \b
    Examples:
      djb db init           # Initialize database
      djb db init --no-start  # Don't auto-start PostgreSQL
    """
    logger.next("Initializing development database")

    if not init_database(cli_ctx, start_service=not no_start):
        raise click.ClickException("Database initialization failed")


@db.command("status")
@djb_pass_context
def db_status(cli_ctx: CliContext):
    """Show database connection status.

    Checks PostgreSQL installation, service status, and whether
    the database and user exist and are accessible.
    """
    settings = get_db_settings(cli_ctx)

    logger.info("Database configuration:")
    logger.info(f"  Name: {settings.name}")
    logger.info(f"  User: {settings.user}")
    logger.info(f"  Host: {settings.host}:{settings.port}")
    logger.note()

    status = get_db_status(cli_ctx, settings)

    status_messages = {
        DbStatus.UNINSTALLED: (
            "PostgreSQL is not installed",
            "Install with: brew install postgresql@17",
        ),
        DbStatus.UNREACHABLE: (
            "PostgreSQL is not running",
            "Start with: brew services start postgresql@17",
        ),
        DbStatus.NO_DATABASE: (f"Database '{settings.name}' does not exist", "Run: djb db init"),
        DbStatus.NO_USER: (
            f"User '{settings.user}' doesn't exist or password is incorrect",
            "Run: djb db init",
        ),
        DbStatus.OK: ("Database is configured and accessible", None),
    }

    message, tip = status_messages[status]

    if status == DbStatus.OK:
        logger.done(message)
    else:
        logger.fail(message)
        if tip:
            logger.tip(tip)
