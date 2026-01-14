import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--code", required=True, help="The code of the user.")
@click.option("--new-password", required=True, help="The new password of the user.")
@click.pass_context
def reset_password(ctx, code, new_password):
    """Reset password"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.reset_password(code, new_password)
        click.echo("Password reset successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error resetting password: {e}"}))
        sys.exit(1)