import click
import json
import sys
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--id", help="The ID of the Asset (must be a video) to delete the asset ad break for.")
@click.option("--url", help="The Nomad URL of the Asset (must be a video) to delete the asset ad break for (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (must be a video) to delete the asset ad break for. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--ad-break-id", required=True, help="The ID of the ad break.")
@click.pass_context
def delete_asset_ad_break(ctx, id, url, object_key, ad_break_id):
    """Delete asset ad break"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide an id, url, or object-key."}))
        sys.exit(1)

    if url or object_key:       
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)  
        
    try:
        result = nomad_sdk.delete_asset_ad_break(id, ad_break_id)
        
        if not result:
            click.echo(json.dumps({"error": f"Asset ad break with id {ad_break_id} not found."}))
            sys.exit(1)

        click.echo(result)

    except Exception as e:
        click.echo(json.dumps({"error": f"Error deleting asset ad break: {e}"}))
        sys.exit(1)