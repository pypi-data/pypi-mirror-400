from nomad_media_cli.helpers.utils import initialize_sdk
import click
import json
import sys

@click.command()
@click.pass_context
def get_user(ctx):
    """Get user information"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.get_user()
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({ "error": f"Error getting user: {e}" }))
        sys.exit(1)