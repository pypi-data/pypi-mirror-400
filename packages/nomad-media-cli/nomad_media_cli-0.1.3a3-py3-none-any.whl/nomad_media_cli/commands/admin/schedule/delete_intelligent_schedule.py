import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the intelligent schedule to be deleted.")
@click.pass_context
def delete_intelligent_schedule(ctx, schedule_id):
    """Delete intelligent schedule"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.delete_intelligent_schedule(schedule_id)
        click.echo("Intelligent schedule deleted successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error deleting intelligent schedule: {e}"}))
        sys.exit(1)