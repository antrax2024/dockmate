def main() -> None:
    """Main entry point for the Docker Watch application."""
    # Importing here to avoid circular import issues
    from .click import cli

    # Execute the CLI command
    cli()
