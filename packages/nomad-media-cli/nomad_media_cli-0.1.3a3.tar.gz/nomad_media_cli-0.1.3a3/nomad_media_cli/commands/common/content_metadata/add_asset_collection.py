import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.get_content_definition_id import get_content_definition_id
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url

@click.command()
@click.option("--id", help="The ID of the content.")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to add the collection to (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (file or folder) to add the collection to. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--collection-name", help="The name of the collection.")
@click.option("--collection-id", help="The ID of the collection.")
@click.pass_context
def add_asset_collection(ctx, id, url, object_key, collection_name, collection_id):
    """Add collection to content"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]
    
    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide either an id, url or object-key"}))
        sys.exit(1)

    if url or object_key:
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)

    try:
        offset = 0
        collection_content_definition_id = get_content_definition_id(ctx, "Collection")
        while not collection_id:
            collections = nomad_sdk.search(None, offset, None, [{
                "fieldName": "contentDefinitionId",
                "operator": "equals",
                "values": collection_content_definition_id
            }], None, None, None, None, None, None, None, None, None, None, None)
            
            if len(collections["items"]) == 0:
                break
            
            for collection in collections["items"]:
                if collection.get("title") == collection_name:
                    collection_id = collection["id"]
                    break
                
            offset += 1

        result = nomad_sdk.add_tag_or_collection("collection", id, "asset", collection_name, collection_id, not collection_id)
        if not result:
            click.echo(json.dumps({ "error": "Error adding collection." }))
            sys.exit(1)
            
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error adding collection: {e}"}))
        sys.exit(1)