import click
import json
import sys
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--id", help="The ID of the Asset (file or folder) to get the Asset child nodes for.")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to get the Asset child nodes for (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (file or folder) to get the Asset child nodes for. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--folder-id", help="The ID of the folder the Asset is in.")
@click.option("--sort-column", help="The column to sort by.")
@click.option("--is-desc", type=click.BOOL, help="Whether the sort is descending or not.")
@click.option("--page-index", type=click.INT, help="The page index of the Asset child nodes.")
@click.option("--page-size", type=click.INT, help="The page size of the Asset child nodes.")
@click.pass_context
def get_asset_child_nodes(ctx, id, url, object_key, folder_id, sort_column, is_desc, page_index, page_size):
    """Get asset child nodes"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide an id, url, or object-key."}))
        sys.exit(1)

    if url or object_key:       
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)  

    try:
        result = nomad_sdk.get_asset_child_nodes(id, folder_id, sort_column, is_desc, page_index, page_size)

        if not result:
            click.echo(json.dumps({"error": f"Asset child nodes for asset with id {id} not found."}))
            sys.exit(1)

        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error getting asset child nodes: {e}"}))
        sys.exit(1)