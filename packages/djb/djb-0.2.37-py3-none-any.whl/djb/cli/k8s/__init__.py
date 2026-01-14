"""
djb deploy k8s - Kubernetes deployment commands.

This module provides commands for deploying Django applications to Kubernetes
clusters using microk8s, including cloud VPS provisioning (materialize),
infrastructure setup (terraform), local development simulation, and
application deployment.

Command Structure
-----------------
djb deploy k8s                    # Deploy application (default action)
djb deploy k8s materialize        # Create cloud VPS (Hetzner)
djb deploy k8s terraform          # Provision K8s infrastructure (microk8s, addons)
djb deploy k8s local start        # Start local Docker VPS for testing
djb deploy k8s local stop         # Stop local VPS
djb deploy k8s local reset        # Reset local VPS to fresh state
djb deploy k8s local ssh          # SSH into local VPS
djb deploy k8s local status       # Show local VPS status
djb deploy k8s logs               # Stream application logs
djb deploy k8s migrate            # Run Django migrations
djb deploy k8s seed               # Run seed command on cluster

Command Chaining
----------------
Commands are designed to chain automatically with confirmation prompts:

- `djb deploy k8s` checks if infrastructure ready -> invokes `terraform`
- `djb deploy k8s terraform` checks if server exists -> invokes `materialize`

This allows a single `djb deploy k8s --provider hetzner` to create the VPS,
provision K8s, and deploy the application.

Design Philosophy
-----------------
- "materialize" = make physical/real (create VPS)
- "terraform" = shape/transform (provision K8s infrastructure)
- "deploy" = deploy application

The `terraform` subcommand treats infrastructure as code with idempotent
health checks. Each execution checks the health of all infrastructure
components and only provisions/fixes what's missing or unhealthy.

The `local` subcommand group manages a Docker container that simulates a
blank Hetzner VPS, allowing developers to test the full deployment flow
locally before deploying to real infrastructure.

Exports:
    k8s: The Click command group for `djb deploy k8s` subcommands
"""

from djb.cli.k8s.k8s import k8s

__all__ = [
    "k8s",
]
