import click
import json
import sys
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--id", help="The ID of the Asset (must be a video) to create the annotation for.")
@click.option("--url", help="The Nomad URL of the Asset (must be a video) to create the annotation for (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (must be a video) to create the annotation for. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--start-time-code", required=True, help="The start time code of the annotation. Format: hh:mm:ss;ff.")
@click.option("--end-time-code", help="The end time code of the annotation. Format: hh:mm:ss;ff.")
@click.option("--title", help="The title to add to the annotation.")
@click.option("--summary", help="The summary to add to the annotation.")
@click.option("--description", help="The description to add to the annotation.")
@click.pass_context
def create_annotation(ctx, id, url, object_key, start_time_code, end_time_code, title, summary, description):
    """Create annotation"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]
    
    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide an id, url, or object-key."}))
        sys.exit(1)
        
    if url or object_key:
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)

    try:
        result = nomad_sdk.create_annotation(id, start_time_code, end_time_code, title, summary, description)        
        if not result:
            click.echo(json.dumps({"error": f"Asset with id {id} not found."}))
            sys.exit(1)

        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error creating annotation: {e}"}))
        sys.exit(1)