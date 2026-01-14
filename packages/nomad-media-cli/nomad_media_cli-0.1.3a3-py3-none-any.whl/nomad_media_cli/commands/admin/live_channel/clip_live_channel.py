import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--live-channel-id", required=True, help="The ID of the live channel to clip.")
@click.option("--start-time-code", help="The start time code of the live channel to clip.")
@click.option("--end-time-code", help="The end time code of the live channel to clip.")
@click.option("--title", help="The title of the live channel to clip.")
@click.option("--output-folder-id", required=True, help="The output folder ID of the live channel to clip.")
@click.option("--tags", help="The tags of the live channel to clip in JSON list format.")
@click.option("--collections", help="The collections of the live channel to clip in JSON list format.")
@click.option("--related-contents", help="The related contents of the live channel to clip in JSON list format.")
@click.option("--video-bitrate", type=click.INT, help="The video bitrate of the live channel to clip.")
@click.option("--audio-tracks", help="The audio tracks of the live channel to clip in JSON list format.")
@click.pass_context
def clip_live_channel(ctx, live_channel_id, start_time_code, end_time_code, title, output_folder_id, tags, collections, related_contents, video_bitrate, audio_tracks):
    """Clip live channel"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.clip_live_channel(
            live_channel_id,
            start_time_code,
            end_time_code,
            title,
            output_folder_id,
            validate_json(tags, "tags") if tags else None,
            validate_json(collections, "collections") if collections else None,
            validate_json(related_contents, "related_contents") if related_contents else None,
            video_bitrate,
            validate_json(audio_tracks, "audio_tracks") if audio_tracks else None
        )
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error clipping live channel: {e}"}))
        sys.exit(1)