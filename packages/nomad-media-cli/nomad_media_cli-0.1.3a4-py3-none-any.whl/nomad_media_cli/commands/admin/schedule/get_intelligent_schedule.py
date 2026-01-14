import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the intelligent schedule to be gotten.")
@click.pass_context
def get_intelligent_schedule(ctx, schedule_id):
    """Get intelligent schedule"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.get_intelligent_schedule(schedule_id)
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error getting intelligent schedule: {e}"}))
        sys.exit(1)