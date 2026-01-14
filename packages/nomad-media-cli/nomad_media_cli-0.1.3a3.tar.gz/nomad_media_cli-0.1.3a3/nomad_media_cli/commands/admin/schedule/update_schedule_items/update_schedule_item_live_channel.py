import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the schedule the schedule item live channel is to be updated from.")
@click.option("--item-id", required=True, help="The ID of the item to be updated.")
@click.option("--days", help="The days of the schedule item live channel in JSON list format.")
@click.option("--duration-time-code", help="The duration time between time_code and end_time_code. Format: hh:mm:ss;ff.")
@click.option("--end-time-code", help="The end time code of the schedule item live channel. Format: hh:mm:ss;ff.")
@click.option("--live-channel", help="The live channel of the schedule item live channel in JSON dict format.")
@click.option("--time-code", help="The time code of the schedule item live channel. Format: hh:mm:ss;ff.")
@click.pass_context
def update_schedule_item_live_channel(ctx, schedule_id, item_id, days, duration_time_code, end_time_code, live_channel, time_code):
    """Update schedule item live channel"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.update_schedule_item_live_channel(
            schedule_id,
            item_id,
            validate_json(days, "days") if days else None,
            duration_time_code,
            end_time_code,
            validate_json(live_channel, "live_channel") if live_channel else None,
            time_code
        )
        click.echo("Schedule item live channel updated successfully.")
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error updating schedule item live channel: {e}"}))
        sys.exit(1)