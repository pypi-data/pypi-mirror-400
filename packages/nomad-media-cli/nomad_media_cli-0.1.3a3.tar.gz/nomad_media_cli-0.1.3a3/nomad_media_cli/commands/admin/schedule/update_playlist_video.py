import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--playlist-id", required=True, help="The ID of the schedule the playlist video is to be updated from.")
@click.option("--item-id", required=True, help="The ID of the item to be updated.")
@click.option("--asset", help="The asset of the playlist video in JSON dict format.")
@click.pass_context
def update_playlist_video(ctx, playlist_id, item_id, asset):
    """Update playlist video"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.update_playlist_video(
            playlist_id,
            item_id,
            validate_json(asset, "asset") if asset else None
        )
        click.echo("Playlist video updated successfully.")
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error updating playlist video: {e}"}))
        sys.exit(1)