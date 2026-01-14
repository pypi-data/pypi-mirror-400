import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the intelligent playlist to be gotten.")
@click.pass_context
def get_intelligent_playlist(ctx, schedule_id):
    """Get intelligent playlist"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.get_intelligent_playlist(schedule_id)
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error getting intelligent playlist: {e}"}))
        sys.exit(1)