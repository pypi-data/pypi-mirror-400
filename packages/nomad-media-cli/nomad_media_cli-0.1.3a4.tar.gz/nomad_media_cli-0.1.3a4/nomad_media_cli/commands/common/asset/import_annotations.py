import click
import json
import sys
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--id", help="The ID of the Asset (must be a video) to import the annotations for.")
@click.option("--url", help="The Nomad URL of the Asset (must be a video) to import the annotations for (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (must be a video) to import the annotations for. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--annotations", multiple=True, required=True, help=(
        "The annotations to import. Format: "
        '{"start-time-code": "hh:mm:ss;ff", "end-time-code": "hh:mm:ss;ff"}'
        "Both start-time-code and end-time-code are optional."
    ))
@click.pass_context
def import_annotations(ctx, id, url, object_key, annotations):
    """Import annotations"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide an id, url, or object-key."}))
        sys.exit(1)

    if url or object_key:       
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)  

    annotations_json = [validate_json(annotation, "annotations") for annotation in annotations]

    try:
        nomad_sdk.import_annotations(id, annotations_json)
            
        click.echo("Annotations imported successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error importing annotations: {e}"}))
        sys.exit(1)