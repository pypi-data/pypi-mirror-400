from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url

import click
import json
import sys

@click.command()
@click.option("--id", help="Asset id to list the collections for.")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to list the collections for (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (file or folder) to list the collections for. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.pass_context
def list_asset_collections(ctx, id, url, object_key):
    """List collections"""    
    
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    if not id and not url and not object_key:
        click.echo(json.dumps({ "error": "Please provide an id, url or object-key" }))
        sys.exit(1)
        
    if url or object_key:
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)

    try:    
        asset_metadata = nomad_sdk.get_asset_details(id)
        
        collections = asset_metadata["collections"]
        collections = [collection["description"] for collection in collections]
        
        click.echo(json.dumps(collections, indent=4))

    except Exception as e:
        click.echo(json.dumps({ "error": f"Error listing collections: {e}" }))
        sys.exit(1)