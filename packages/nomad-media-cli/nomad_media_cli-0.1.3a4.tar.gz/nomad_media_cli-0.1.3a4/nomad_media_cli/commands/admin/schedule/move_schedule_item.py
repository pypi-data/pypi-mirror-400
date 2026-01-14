import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the schedule the schedule item is to be moved from.")
@click.option("--item-id", required=True, help="The ID of the item to be moved.")
@click.option("--previous-item", help="The previous item of the schedule item.")
@click.pass_context
def move_schedule_item(ctx, schedule_id, item_id, previous_item):
    """Move schedule item"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.move_schedule_item(schedule_id, item_id, previous_item)
        click.echo("Schedule item moved successfully.")
        click.echo(result)

    except Exception as e:
        click.echo(json.dumps({"error": f"Error moving schedule item: {e}"}))
        sys.exit(1)