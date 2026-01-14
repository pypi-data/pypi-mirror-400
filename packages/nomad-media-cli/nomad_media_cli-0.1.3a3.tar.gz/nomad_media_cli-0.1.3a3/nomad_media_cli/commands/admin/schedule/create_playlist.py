import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--name", required=True, help="The name of the playlist.")
@click.option("--thumbnail-asset", help="The thumbnail asset of the playlist in JSON dict format.")
@click.option("--loop-playlist", required=True, type=click.BOOL, help="Whether the playlist is looped.")
@click.option("--default-video-asset", required=True, help="The default video asset of the playlist in JSON dict format.")
@click.pass_context
def create_playlist(ctx, name, thumbnail_asset, loop_playlist, default_video_asset):
    """Create playlist"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.create_playlist(
            name,
            validate_json(thumbnail_asset, "thumbnail_asset") if thumbnail_asset else None,
            loop_playlist,
            validate_json(default_video_asset, "default_video_asset")
        )
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error creating playlist: {e}"}))
        sys.exit(1)