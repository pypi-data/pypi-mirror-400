import click
import json
import sys
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--id", multiple=True, help="The ID(s) of the Assets to be copied")
@click.option("--url", multiple=True, help="The Nomad URL(s) of the Asset (file or folder) to copy the Assets for (bucket::object-key).")
@click.option("--object-key", multiple=True, help="Object-key(s) of the Asset (file or folder) to copy the Assets for. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--destination-folder-id", required=True, help="The destination folder ID of the Assets.")
@click.option("--batch-action", help="The actions to be performed. Format: {'id': id, description: description}.")
@click.option("--content-definition-id", help="The content definition ID of the Assets.")
@click.option("--schema-name", help="The schema name of the Assets.")
@click.option("--resolver-exempt", type=click.BOOL, help="The resolver exempt of the Assets.")
@click.pass_context
def copy_asset(ctx, id, url, object_key, destination_folder_id, batch_action, content_definition_id, schema_name, resolver_exempt):
    """Copy asset"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]
    
    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide an id, url, or object-key."}))
        sys.exit(1)
        
    id = list(id) if id else []
        
    if url:
        id.extend([get_id_from_url(ctx, url, None, nomad_sdk) for url in url])
    
    if object_key:
        id.extend([get_id_from_url(ctx, None, object_key, nomad_sdk) for object_key in object_key])

    try:
        result = nomad_sdk.copy_asset(
            id,
            destination_folder_id,
            validate_json(batch_action, "batch_action") if batch_action else None,
            content_definition_id,
            schema_name,
            resolver_exempt
        )
        
        if not result:
            click.echo(json.dumps({"error": f"Asset with id {id} not found."}))
            sys.exit(1)
            
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error copying asset: {e}"}))
        sys.exit(1)