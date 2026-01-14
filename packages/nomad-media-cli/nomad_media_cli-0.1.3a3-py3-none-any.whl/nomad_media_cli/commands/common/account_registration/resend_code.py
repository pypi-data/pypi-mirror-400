import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--email", required=True, help="The email of the user.")
@click.pass_context
def resend_code(ctx, email):
    """Resend verification code"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.resend_code(email)
        click.echo("Verification code resent successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error resending verification code: {e}"}))
        sys.exit(1)