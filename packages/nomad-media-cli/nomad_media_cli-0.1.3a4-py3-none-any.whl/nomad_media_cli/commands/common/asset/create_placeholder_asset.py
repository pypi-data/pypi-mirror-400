import click
import json
import os
import sys
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--parent-id", help="The parent Asset folder ID for the placeholder Asset.")
@click.option("--url", help="The Nomad URL of the Asset folder to create the placeholder Asset for (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset folder to create the placeholder Asset for. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--asset-name", required=True, help="The visual name of the new placeholder. It can contain spaces and other characters, must contain file extension.")
@click.pass_context
def create_placeholder_asset(ctx, parent_id, url, object_key, asset_name):
    """Create placeholder asset"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide an id, url, or object-key."}))
        sys.exit(1)

    if url or object_key:       
        parent_id = get_id_from_url(ctx, url, object_key, nomad_sdk)  

    if not os.path.splitext(asset_name)[1]:
        click.echo(json.dumps({"error": "Asset name must contain file extension."}))
        sys.exit(1)

    try:
        result = nomad_sdk.create_placeholder_asset(parent_id, asset_name)
        
        if not result:
            click.echo(json.dumps({"error": f"Parent asset with id {parent_id} not found."}))
            sys.exit(1)

        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error creating placeholder asset: {e}"}))
        sys.exit(1)