import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the schedule the schedule preview is to be gotten from.")
@click.pass_context
def get_schedule_preview(ctx, schedule_id):
    """Get schedule preview"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.get_schedule_preview(schedule_id)
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error getting schedule preview: {e}"}))
        sys.exit(1)