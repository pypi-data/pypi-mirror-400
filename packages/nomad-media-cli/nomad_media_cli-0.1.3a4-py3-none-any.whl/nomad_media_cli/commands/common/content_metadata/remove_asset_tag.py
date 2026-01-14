import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url

@click.command()
@click.option("--id", help="The id of the asset.")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to remove the tag from (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (file or folder) to remove the tag from. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--tag-id", required=True, help="The id of the tag.")
@click.pass_context
def remove_asset_tag(ctx, id, url, object_key, tag_id):
    """Remove tag from asset"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]
    
    if not id and not url and not object_key:
        click.echo(json.dumps({ "error": "Please provide an id, url or object-key" }))
        return

    if url or object_key:
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)

    try:
        result = nomad_sdk.remove_tag_or_collection("tag", id, "asset", tag_id)
        if not result:
            click.echo(json.dumps({ "error": "Error removing tag from asset." }))
            sys.exit(1)
        
        click.echo(json.dumps({ "message": "tag removed from asset." }))
    except Exception as e:
        click.echo(json.dumps({ "error": f"Error removing tag from asset: {e}" }))