import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--live-operator-id", required=True, help="The ID of the live operator.")
@click.pass_context
def cancel_broadcast(ctx, live_operator_id):
    """Cancel broadcast"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.cancel_broadcast(live_operator_id)
        click.echo("Broadcast canceled successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error canceling broadcast: {e}"}))
        sys.exit(1)