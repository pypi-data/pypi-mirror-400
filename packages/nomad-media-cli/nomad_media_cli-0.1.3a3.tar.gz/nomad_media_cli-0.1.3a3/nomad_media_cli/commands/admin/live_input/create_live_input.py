import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--name", help="The name of the live input.")
@click.option("--source", help="The source of the live input.")
@click.option("--input-type", help="The type of the live input. The types are RTMP_PULL, RTMP_PUSH, RTP_PUSH, UDP_PUSH and URL_PULL.")
@click.option("--is-standard", type=click.BOOL, help="Indicates if the live input is standard.")
@click.option("--video-asset-id", help="The video asset ID of the live input.")
@click.option("--destinations", required=True, help="The destinations of the live input in JSON list format.")
@click.option("--sources", help="The sources of the live input in JSON list format.")
@click.pass_context
def create_live_input(ctx, name, source, input_type, is_standard, video_asset_id, destinations, sources):
    """Create live input"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.create_live_input(
            name,
            source,
            input_type,
            is_standard,
            video_asset_id,
            validate_json(destinations, "destinations"),
            validate_json(sources, "sources") if sources else None
        )
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error creating live input: {e}"}))
        sys.exit(1)