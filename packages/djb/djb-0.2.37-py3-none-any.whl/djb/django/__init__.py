"""Django integration views for djb.

Provides reusable views for health checks and monitoring.

Exports:
    health_check: Liveness probe - fast check if Django is alive
    health_check_ready: Readiness probe - validates all homepage URLs
"""

from djb.django.views import health_check, health_check_ready

__all__ = ["health_check", "health_check_ready"]
