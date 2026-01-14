import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--default-video-asset", required=True, help="The default video asset of the intelligent schedule in JSON dict format.")
@click.option("--name", required=True, help="The name of the intelligent schedule.")
@click.option("--thumbnail-asset", help="The thumbnail asset of the intelligent schedule in JSON dict format.")
@click.option("--time-zone-id", help="The time zone ID of the intelligent schedule.")
@click.pass_context
def create_intelligent_schedule(ctx, default_video_asset, name, thumbnail_asset, time_zone_id):
    """Create intelligent schedule"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.create_intelligent_schedule(
            validate_json(default_video_asset, "default_video_asset"),
            name,
            validate_json(thumbnail_asset, "thumbnail_asset") if thumbnail_asset else None,
            time_zone_id
        )
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error creating intelligent schedule: {e}"}))
        sys.exit(1)