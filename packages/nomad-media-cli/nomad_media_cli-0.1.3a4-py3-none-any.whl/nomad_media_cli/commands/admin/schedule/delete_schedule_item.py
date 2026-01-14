import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the schedule the schedule item is to be deleted from.")
@click.option("--item-id", required=True, help="The ID of the item to be deleted.")
@click.pass_context
def delete_schedule_item(ctx, schedule_id, item_id):
    """Delete schedule item"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.delete_schedule_item(schedule_id, item_id)
        click.echo("Schedule item deleted successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error deleting schedule item: {e}"}))
        sys.exit(1)