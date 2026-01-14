import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the schedule the schedule item is to be gotten from.")
@click.option("--item-id", required=True, help="The ID of the item to be gotten.")
@click.pass_context
def get_schedule_item(ctx, schedule_id, item_id):
    """Get schedule item"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.get_schedule_item(schedule_id, item_id)
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error getting schedule item: {e}"}))
        sys.exit(1)