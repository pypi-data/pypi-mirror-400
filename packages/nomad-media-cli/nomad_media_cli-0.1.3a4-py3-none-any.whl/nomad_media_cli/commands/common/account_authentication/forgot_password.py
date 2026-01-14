import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.pass_context
def forgot_password(ctx):
    """Forgot password"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.forgot_password()
        click.echo("Forgot password email sent successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error sending forgot password email: {e}"}))
        sys.exit(1)