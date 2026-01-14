import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the schedule the asset item is to be added to.")
@click.option("--asset", required=True, help="The asset of the schedule item asset in JSON dict format.")
@click.option("--days", required=True, help="The days of the schedule item asset in JSON list format.")
@click.option("--duration-time-code", required=True, help="The duration time between time_code and end_time_code. Format: hh:mm:ss;ff.")
@click.option("--end-time-code", required=True, help="The end time code of the schedule item asset. Format: hh:mm:ss;ff.")
@click.option("--previous-item", help="The previous item of the schedule item asset.")
@click.option("--time-code", required=True, help="The time code of the schedule item asset. Format: hh:mm:ss;ff.")
@click.pass_context
def create_schedule_item_asset(ctx, schedule_id, asset, days, duration_time_code, end_time_code, previous_item, time_code):
    """Create schedule item asset"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.create_schedule_item_asset(
            schedule_id,
            validate_json(asset, "asset"),
            validate_json(days, "days"),
            duration_time_code,
            end_time_code,
            previous_item,
            time_code
        )
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error creating schedule item asset: {e}"}))
        sys.exit(1)