import click
import json
import sys
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--id", help="The ID of the Asset to update.")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to update (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (file or folder) to update. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--display-name", help="The display name of the Asset.")
@click.option("--display-date", help="The display date of the Asset.")
@click.option("--available-start-date", help="The available start date of the Asset.")
@click.option("--available-end-date", help="The available end date of the Asset.")
@click.option("--custom-properties", help="The custom properties of the Asset. Format: {'prop1': 'value1', 'prop2': 'value2'}.")
@click.pass_context
def update_asset(ctx, id, url, object_key, display_name, display_date, available_start_date, 
                 available_end_date, custom_properties):
    """Update asset"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide an id, url, or object-key."}))
        sys.exit(1)

    if url or object_key:       
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)

    try:
        result = nomad_sdk.update_asset(
            id,
            display_name,
            display_date,
            available_start_date,
            available_end_date,
            validate_json(custom_properties, "custom_properties") if custom_properties else None
        )
        
        if not result:
            click.echo(json.dumps({"error": f"Asset with id {id} not found."}))
            sys.exit(1)
            
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error updating asset: {e}"}))
        sys.exit(1)