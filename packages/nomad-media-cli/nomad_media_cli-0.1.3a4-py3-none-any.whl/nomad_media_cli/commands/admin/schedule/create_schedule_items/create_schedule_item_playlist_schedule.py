import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the schedule the playlist schedule item is to be added to.")
@click.option("--days", required=True, help="The days of the schedule item playlist schedule in JSON list format.")
@click.option("--duration-time-code", required=True, help="The duration time between time_code and end_time_code. Format: hh:mm:ss;ff.")
@click.option("--end-time-code", required=True, help="The end time code of the schedule item playlist schedule. Format: hh:mm:ss;ff.")
@click.option("--playlist-schedule", required=True, help="The playlist schedule of the schedule item playlist schedule in JSON dict format.")
@click.option("--previous-item", help="The previous item of the schedule item playlist schedule.")
@click.option("--time-code", required=True, help="The time code of the schedule item playlist schedule. Format: hh:mm:ss;ff.")
@click.pass_context
def create_schedule_item_playlist_schedule(ctx, schedule_id, days, duration_time_code, end_time_code, playlist_schedule, previous_item, time_code):
    """Create schedule item playlist schedule"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.create_schedule_item_playlist_schedule(
            schedule_id,
            validate_json(days, "days"),
            duration_time_code,
            end_time_code,
            validate_json(playlist_schedule, "playlist_schedule"),
            previous_item,
            time_code
        )
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error creating schedule item playlist schedule: {e}"}))
        sys.exit(1)