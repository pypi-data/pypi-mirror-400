import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the schedule the intelligent schedule is to be updated.")
@click.option("--default-video-asset", required=True, help="The default video asset of the intelligent schedule in JSON dict format.")
@click.option("--name", help="The name of the intelligent schedule.")
@click.option("--thumbnail-asset", help="The thumbnail asset of the intelligent schedule in JSON dict format.")
@click.option("--time-zone-id", help="The time zone ID of the intelligent schedule.")
@click.pass_context
def update_intelligent_schedule(ctx, schedule_id, default_video_asset, name, thumbnail_asset, time_zone_id):
    """Update intelligent schedule"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.update_intelligent_schedule(
            schedule_id,
            validate_json(default_video_asset, "default_video_asset"),
            name,
            validate_json(thumbnail_asset, "thumbnail_asset") if thumbnail_asset else None,
            time_zone_id
        )
        click.echo("Intelligent schedule updated successfully.")
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error updating intelligent schedule: {e}"}))
        sys.exit(1)