import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--email", required=True, help="The email of the user.")
@click.option("--code", required=True, help="The code of the user.")
@click.pass_context
def verify(ctx, email, code):
    """Verify user account"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.verify(email, code)
        click.echo("User account verified successfully.")
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error verifying user account: {e}"}))
        sys.exit(1)