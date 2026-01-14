import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--live-operator-id", required=True, help="The ID of the live operator.")
@click.pass_context
def stop_broadcast(ctx, live_operator_id):
    """Stop broadcast"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.stop_broadcast(live_operator_id)
        click.echo("Broadcast stopped successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error stopping broadcast: {e}"}))
        sys.exit(1)