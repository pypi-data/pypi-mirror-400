import click
import json
import sys
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--id", help="The ID of the Asset (file or folder) to be archived.")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to be archived (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (file or folder) to be archived. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.pass_context
def archive_asset(ctx, id, url, object_key):
    """Archive asset"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide an id, url, or object-key."}))
        sys.exit(1)
        
    if url or object_key:
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)

    try:
        result = nomad_sdk.archive_asset(id)
        
        if not result:
            click.echo(json.dumps({"error": f"Asset with id {id} not found."}))
            sys.exit(1)
            
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error archiving asset: {e}"}))
        sys.exit(1)