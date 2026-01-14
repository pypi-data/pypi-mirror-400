import click
import json
import sys

from nomad_media_cli.helpers.get_contents_by_name import get_contents_by_name
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--id", help="The ID of the Asset (file or folder) to record the Asset tracking beacon for.")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to record the Asset tracking beacon for (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (file or folder) to record the Asset tracking beacon for. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--tracking-event", required=True, help="The tracking event of the Asset tracking beacon.")
@click.option("--live-channel-name", help="The live channel name of the Asset tracking beacon.")
@click.option("--live-channel-id", help="The live channel ID of the Asset tracking beacon. If this value is provided, it ignores the live channel name.")
@click.option("--content-id", help="Optional content ID to track along with required Asset ID.")
@click.option("--second", required=True, type=click.INT, help="Second mark into the video/ad.")
@click.pass_context
def records_asset_tracking_beacon(ctx, id, url, object_key, tracking_event, live_channel_name, live_channel_id, content_id, second):
    """Record asset tracking beacon"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide an id, url, or object-key."}))
        sys.exit(1)

    if url or object_key:       
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)  
        
    if not live_channel_id and not live_channel_name:
        click.echo(json.dumps({"error": "Please provide a live channel ID or name."}))
        sys.exit(1)
        
    if live_channel_name:
        live_channel_id = get_contents_by_name(ctx, [live_channel_name], "live_channel", nomad_sdk)[0]["id"]

    try:
        nomad_sdk.records_asset_tracking_beacon(id, tracking_event, live_channel_id, content_id, second)
        click.echo("Asset tracking beacon recorded successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error recording asset tracking beacon: {e}"}))
        sys.exit(1)