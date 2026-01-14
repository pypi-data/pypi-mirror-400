import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the intelligent playlist to be deleted.")
@click.pass_context
def delete_intelligent_playlist(ctx, schedule_id):
    """Delete intelligent playlist"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.delete_intelligent_playlist(schedule_id)
        click.echo("Intelligent playlist deleted successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error deleting intelligent playlist: {e}"}))
        sys.exit(1)