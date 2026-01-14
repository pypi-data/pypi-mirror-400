import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--live-operator-id", required=True, help="The ID of the live operator.")
@click.pass_context
def get_completed_segments(ctx, live_operator_id):
    """Get completed segments"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.get_completed_segments(live_operator_id)
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error getting completed segments: {e}"}))
        sys.exit(1)