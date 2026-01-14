import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.get_content_definition_id import get_content_definition_id
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url

@click.command()
@click.option("--id", help="The ID of the content.")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to add the tag to (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (file or folder) to add the tag to. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--tag-name", help="The name of the tag.")
@click.option("--tag-id", help="The ID of the tag.")
@click.pass_context
def add_asset_tag(ctx, id, url, object_key, tag_name, tag_id):
    """Add tag to content"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]
    
    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide either an id, url or object-key"}))
        sys.exit(1)

    if url or object_key:
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)

    try:
        offset = 0
        tag_content_definition_id = get_content_definition_id(ctx, "Tag")
        while not tag_id:
            tags = nomad_sdk.search(None, offset, None, [{
                "fieldName": "contentDefinitionId",
                "operator": "equals",
                "values": tag_content_definition_id
            }], None, None, None, None, None, None, None, None, None, None, None)
            
            if len(tags["items"]) == 0:
                break
            
            for tag in tags["items"]:
                if tag.get("title") == tag_name:
                    tag_id = tag["id"]
                    break

            offset += 1

        result = nomad_sdk.add_tag_or_collection("tag", id, "asset", tag_name, tag_id, not tag_id)
        if not result:
            click.echo(json.dumps({ "error": "Error adding tag." }))
            sys.exit(1)
        7
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error adding tag: {e}"}))
        sys.exit(1)