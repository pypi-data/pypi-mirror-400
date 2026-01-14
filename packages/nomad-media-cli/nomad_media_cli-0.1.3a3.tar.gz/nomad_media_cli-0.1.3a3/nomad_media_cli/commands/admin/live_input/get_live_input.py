import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--live-input-id", required=True, help="The ID of the live input.")
@click.pass_context
def get_live_input(ctx, live_input_id):
    """Get live input"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.get_live_input(live_input_id)
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error getting live input: {e}"}))
        sys.exit(1)