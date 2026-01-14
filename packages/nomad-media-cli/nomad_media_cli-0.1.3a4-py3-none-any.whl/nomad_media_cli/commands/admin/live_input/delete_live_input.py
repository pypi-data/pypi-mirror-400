import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--live-input-id", required=True, help="The ID of the live input.")
@click.pass_context
def delete_live_input(ctx, live_input_id):
    """Delete live input"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.delete_live_input(live_input_id)
        click.echo("Live input deleted successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error deleting live input: {e}"}))
        sys.exit(1)