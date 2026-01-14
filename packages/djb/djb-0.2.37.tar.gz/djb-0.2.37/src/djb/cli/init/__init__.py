"""djb init - Initialize djb development environment.

Command Structure:
    djb init                    # Run all initialization steps
    djb init config             # Configure project settings
    djb init project            # Update .gitignore and Django settings
    djb init deps               # Install dependencies
    djb init db                 # Initialize database and migrations
    djb init secrets            # Set up secrets management
    djb init hooks              # Install git hooks

Import the init command from djb.cli.init.init:
    from djb.cli.init.init import init
"""
