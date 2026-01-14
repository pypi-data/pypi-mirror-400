import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--include-completed-uploads", default=True, type=click.BOOL, help="Whether to include completed uploads or not.")
@click.pass_context
def get_user_uploads(ctx, include_completed_uploads):
    """Get user uploads"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.get_user_uploads(include_completed_uploads)
        
        if not result:
            click.echo(json.dumps({"error": f"User uploads not found."}))
            sys.exit(1)
            
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error getting user uploads: {e}"}))
        sys.exit(1)