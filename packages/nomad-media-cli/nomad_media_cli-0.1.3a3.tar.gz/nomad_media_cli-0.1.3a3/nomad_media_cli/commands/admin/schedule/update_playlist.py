import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the schedule the playlist is to be updated from.")
@click.option("--default-video-asset", help="The default video asset of the playlist in JSON dict format.")
@click.option("--loop-playlist", type=click.BOOL, help="Whether or not to loop the playlist.")
@click.option("--name", help="The name of the playlist.")
@click.option("--thumbnail-asset", help="The thumbnail asset of the playlist in JSON dict format.")
@click.pass_context
def update_playlist(ctx, schedule_id, default_video_asset, loop_playlist, name, thumbnail_asset):
    """Update playlist"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.update_playlist(
            schedule_id,
            validate_json(default_video_asset, "default_video_asset") if default_video_asset else None,
            loop_playlist,
            name,
            validate_json(thumbnail_asset, "thumbnail_asset") if thumbnail_asset else None
        )
        click.echo("Playlist updated successfully.")
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error updating playlist: {e}"}))
        sys.exit(1)