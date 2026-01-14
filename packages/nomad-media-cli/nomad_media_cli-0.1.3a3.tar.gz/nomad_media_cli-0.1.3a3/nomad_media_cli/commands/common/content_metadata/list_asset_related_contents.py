from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url

import click
import json
import sys

@click.command()
@click.option("--id", help="Asset id to list the related contents for.")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to list the related contents for (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (file or folder) to list the related contents for. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.pass_context
def list_asset_related_contents(ctx, id, url, object_key):
    """List related contents"""    
    
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    if not id and not url and not object_key:
        click.echo(json.dumps({ "error": "Please provide an id, url or object-key" }))
        sys.exit(1)

    if url or object_key:
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)

    try:    
        asset_metadata = nomad_sdk.get_asset_details(id)
        
        related_contents = asset_metadata["relatedContent"]
        
        click.echo(json.dumps(related_contents, indent=4))

    except Exception as e:
        click.echo(json.dumps({ "error": f"Error listing related contents: {e}" }))
        sys.exit(1)