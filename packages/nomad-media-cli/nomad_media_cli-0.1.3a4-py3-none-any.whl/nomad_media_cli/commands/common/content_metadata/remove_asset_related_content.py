import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url

@click.command()
@click.option("--id", help="The id of the asset.")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to remove the related content from (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (file or folder) to remove the related content from. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--related-content-id", required=True, help="The id of the related content.")
@click.pass_context
def remove_asset_related_content(ctx, id, url, object_key, related_content_id):
    """Remove related content to asset"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]
    
    if not id and not url and not object_key:
        click.echo(json.dumps({ "error": "Please provide an id, url or object-key" }))
        sys.exit(1)

    if url or object_key:
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)

    try:
        result = nomad_sdk.delete_related_content(id, related_content_id, "asset")
        if not result:
            click.echo(json.dumps({ "error": "Error removing related content to asset." }))
            sys.exit(1)
            
        click.echo(json.dumps({ "message": "Related content removed to asset." }))
    except Exception as e:
        click.echo(json.dumps({ "error": f"Error removing related content to asset: {e}" }))