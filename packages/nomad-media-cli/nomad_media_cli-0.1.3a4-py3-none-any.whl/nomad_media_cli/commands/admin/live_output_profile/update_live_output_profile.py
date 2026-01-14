import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--live-output-id", required=True, help="The ID of the live output profile.")
@click.option("--name", help="The name of the live output profile.")
@click.option("--output-type", help="The type of the live output profile in JSON dict format.")
@click.option("--enabled", type=click.BOOL, help="Indicates if the live output profile is enabled.")
@click.option("--audio-bitrate", type=click.INT, help="The audio bitrate of the live output profile.")
@click.option("--output-stream-key", help="The output stream key of the live output profile.")
@click.option("--output-url", help="The output URL of the live output profile.")
@click.option("--secondary-output-stream-key", help="The secondary output stream key of the live output profile.")
@click.option("--secondary-url", help="The secondary URL of the live output profile.")
@click.option("--video-bitrate", type=click.INT, help="The video bitrate of the live output profile.")
@click.option("--video-bitrate-mode", help="The video bitrate mode of the live output profile. The modes are CBR and VBR.")
@click.option("--video-codec", help="The video codec of the live output profile. The codecs are H264 and H265.")
@click.option("--video-frames-per-second", type=click.INT, help="The video frames per second of the live output profile.")
@click.option("--video-height", type=click.INT, help="The video height of the live output profile.")
@click.option("--video-width", type=click.INT, help="The video width of the live output profile.")
@click.pass_context
def update_live_output_profile(ctx, live_output_id, name, output_type, enabled, audio_bitrate, output_stream_key, output_url, secondary_output_stream_key, secondary_url, video_bitrate, video_bitrate_mode, video_codec, video_frames_per_second, video_height, video_width):
    """Update live output profile"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.update_live_output_profile(
            live_output_id,
            name,
            validate_json(output_type, "output_type") if output_type else None,
            enabled,
            audio_bitrate,
            output_stream_key,
            output_url,
            secondary_output_stream_key,
            secondary_url,
            video_bitrate,
            video_bitrate_mode,
            video_codec,
            video_frames_per_second,
            video_height,
            video_width
        )
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error updating live output profile: {e}"}))
        sys.exit(1)