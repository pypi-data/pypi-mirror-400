import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--content-id", required=True, help="The ID of the event to delete.")
@click.option("--content-definition-id", required=True, help="The content definition ID of the event to delete.")
@click.pass_context
def delete_event(ctx, content_id, content_definition_id):
    """Delete event"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.delete_event(content_id, content_definition_id)
        click.echo("Event deleted successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error deleting event: {e}"}))
        sys.exit(1)