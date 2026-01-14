import click
import json
import sys
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--id", help="The ID of the Asset (file or folder) to get the manifest with cookies for.")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to get the manifest with cookies for (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (file or folder) to get the manifest with cookies for. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--cookie-id", required=True, help="The ID of the cookie.")
@click.pass_context
def get_asset_manifest_with_cookies(ctx, id, url, object_key, cookie_id):
    """Get asset manifest with cookies"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide an id, url, or object-key."}))
        sys.exit(1)

    if url or object_key:       
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)  

    try:
        result = nomad_sdk.get_asset_manifest_with_cookies(id, cookie_id)

        if not result:
            click.echo(json.dumps({"error": f"Asset manifest with cookies for asset with id {id} not found."}))
            sys.exit(1)
            
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error getting asset manifest with cookies: {e}"}))
        sys.exit(1)