import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--email", required=True, help="The email of the user.")
@click.option("--first-name", help="The first name of the user.")
@click.option("--last-name", help="The last name of the user.")
@click.option("--password", required=True, help="The password of the user.")
@click.pass_context
def register(ctx, email, first_name, last_name, password):
    """Register user"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.register(email, first_name, last_name, password)
        click.echo("User registered successfully.")
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error registering user: {e}"}))
        sys.exit(1)