import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the playlist to be deleted.")
@click.pass_context
def delete_playlist(ctx, schedule_id):
    """Delete playlist"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.delete_playlist(schedule_id)
        click.echo("Playlist deleted successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error deleting playlist: {e}"}))
        sys.exit(1)