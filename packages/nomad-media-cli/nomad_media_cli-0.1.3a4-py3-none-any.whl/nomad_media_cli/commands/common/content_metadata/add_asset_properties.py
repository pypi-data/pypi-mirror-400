import click
import json
import sys
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--id", help="The id of the asset.")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to add the tag to (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (file or folder) to add the tag to. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--name", help="The display name of the asset.")
@click.option("--date", help="The display date of the asset.")
@click.option("--properties", help="The custom properties of the asset. Must be in JSON format. Example: '{\"key\": \"value\"}'")
@click.pass_context
def add_asset_properties(ctx, id, url, object_key, name, date, properties):
    """Add custom properties to asset"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]
        
    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide either an id, url or object-key"}))
        sys.exit(1)

    if url or object_key:
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)

    try:
        try:
            if properties:
                properties = validate_json(properties, "properties")
        except:
            click.echo(json.dumps({ "error": "Custom properties must be in JSON format." }))
            sys.exit(1)    

        result = nomad_sdk.add_custom_properties(id, name, date, properties)
        if not result:
            click.echo(json.dumps({ "error": "Error adding custom properties to asset." }))
            sys.exit(1)
        click.echo(json.dumps({ "message": "Custom properties added to asset." }))
    except Exception as e:
        click.echo(json.dumps({ "error": f"Error adding custom properties to asset." }))