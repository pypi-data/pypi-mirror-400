"""Sync Django superuser from encrypted secrets."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.management.base import BaseCommand, CommandError

from djb.cli.context import CliContext
from djb.secrets import SopsError, load_secrets
from djb.types import Mode

if TYPE_CHECKING:
    from argparse import ArgumentParser
    from typing import Any


class Command(BaseCommand):
    help = "Create or update superuser from encrypted secrets"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--environment",
            "-e",
            type=str,
            default=None,
            help="Environment to load secrets from (default: auto-detect from DYNO/ENVIRONMENT)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        User = get_user_model()

        dry_run = options["dry_run"]

        # Try environment variables first (for Heroku/K8s where age key isn't available)
        username = os.environ.get("SUPERUSER_USERNAME")
        email = os.environ.get("SUPERUSER_EMAIL")
        password = os.environ.get("SUPERUSER_PASSWORD")

        # Also check for JSON format from K8s secrets (stored as {"username":...,"email":...,"password":...})
        if not all([username, email, password]):
            superuser_json = os.environ.get("superuser")
            if superuser_json:
                try:
                    creds = json.loads(superuser_json)
                    username = creds.get("username")
                    email = creds.get("email")
                    password = creds.get("password")
                except json.JSONDecodeError:
                    pass

        if all([username, email, password]):
            self.stdout.write("Loading superuser credentials from environment variables")
        else:
            # Fall back to encrypted secrets
            environment = options["environment"]
            if environment is None:
                if "DYNO" in os.environ:
                    environment = "production"
                else:
                    environment = os.environ.get("ENVIRONMENT", "dev")

            self.stdout.write(f"Loading secrets for environment: {environment}")

            # Map environment string to Mode enum
            mode_str = "development" if environment == "dev" else environment
            try:
                mode = Mode(mode_str)
            except ValueError:
                raise CommandError(
                    f"Invalid environment '{environment}'. "
                    f"Valid options: dev, development, staging, production"
                )

            try:
                runner = CliContext().runner
                secrets = load_secrets(
                    runner,
                    mode=mode,
                    secrets_dir=Path(settings.BASE_DIR) / "secrets",
                )
            except (FileNotFoundError, SopsError) as e:
                raise CommandError(f"Failed to load secrets: {e}")

            # Get superuser credentials
            superuser_config = secrets.get("superuser")
            if not superuser_config:
                raise CommandError(
                    f"No 'superuser' configuration found in {environment} secrets. "
                    "Add a superuser section with username, email, and password."
                )

            username = superuser_config.get("username")
            email = superuser_config.get("email")
            password = superuser_config.get("password")

        if not all([username, email, password]):
            raise CommandError("Superuser config must include 'username', 'email', and 'password'")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"[DRY RUN] Would sync superuser: {username} ({email})")
            )
            return

        # Check if user exists
        try:
            user = User.objects.get(username=username)
            if not isinstance(user, AbstractUser):
                raise CommandError(
                    f"User model {User.__name__} must inherit from AbstractUser "
                    "to use sync_superuser (set_password, is_staff, etc. required)"
                )
            user.email = email
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Updated superuser: {username} ({email})"))
        except User.DoesNotExist:
            create_superuser = getattr(User.objects, "create_superuser", None)
            if create_superuser is None:
                raise CommandError("User manager must have create_superuser method")
            user = create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS(f"Created superuser: {username} ({email})"))
