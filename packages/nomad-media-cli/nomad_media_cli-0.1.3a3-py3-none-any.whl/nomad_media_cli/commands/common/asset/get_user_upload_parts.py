import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--upload-id", required=True, help="The ID of the upload to get the user upload parts for.")
@click.pass_context
def get_user_upload_parts(ctx, upload_id):
    """Get user upload parts"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.get_user_upload_parts(upload_id)
        
        if not result:
            click.echo(json.dumps({"error": f"User upload parts for upload with id {upload_id} not found."}))
            sys.exit(1)
            
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error getting user upload parts: {e}"}))
        sys.exit(1)