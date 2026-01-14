import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--playlist-id", required=True, help="The ID of the playlist.")
@click.option("--video-asset", required=True, help="The video asset of the playlist video in JSON dict format.")
@click.option("--previous-item", help="The previous item of the playlist video.")
@click.pass_context
def create_playlist_video(ctx, playlist_id, video_asset, previous_item):
    """Create playlist video"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.create_playlist_video(
            playlist_id,
            validate_json(video_asset, "video_asset"),
            previous_item
        )
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error creating playlist video: {e}"}))
        sys.exit(1)