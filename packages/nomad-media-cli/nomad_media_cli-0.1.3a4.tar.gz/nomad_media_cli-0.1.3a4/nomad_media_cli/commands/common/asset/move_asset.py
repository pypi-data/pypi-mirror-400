import click
import json
import sys
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--id", help="The ID of the Asset (file or folder) to move.")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to move (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (file or folder) to move. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--destination-folder-id", required=True, help="The destination folder ID of the move.")
@click.option("--name", help="The name of the Asset when moved.")
@click.option("--batch-action", help="The batch action of the move. Format: {'id': id, description: description}.")
@click.option("--content-definition-id", help="The content definition ID of the move.")
@click.option("--schema-name", help="The schema name of the move.")
@click.option("--resolver-exempt", type=click.BOOL, help="The resolver exempt of the move.")
@click.pass_context
def move_asset(ctx, id, url, object_key, destination_folder_id, name, batch_action, 
                content_definition_id, schema_name, resolver_exempt):
    """Move asset"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]


    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide an id, url, or object-key."}))
        sys.exit(1)

    if url or object_key:       
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)  

    try:
        result = nomad_sdk.move_asset(
            id,
            destination_folder_id,
            name,
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
        click.echo(json.dumps({"error": f"Error moving asset: {e}"}))
        sys.exit(1)