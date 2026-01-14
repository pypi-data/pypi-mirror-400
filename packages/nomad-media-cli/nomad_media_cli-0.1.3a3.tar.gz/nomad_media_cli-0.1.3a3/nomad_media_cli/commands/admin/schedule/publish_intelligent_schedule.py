import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the schedule to be published.")
@click.option("--number-of-locked-days", required=True, type=click.INT, help="The number of locked days of the intelligent schedule.")
@click.pass_context
def publish_intelligent_schedule(ctx, schedule_id, number_of_locked_days):
    """Publish intelligent schedule"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.publish_intelligent_schedule(schedule_id, number_of_locked_days)
        click.echo("Intelligent schedule published successfully.")
        click.echo(result)

    except Exception as e:
        click.echo(json.dumps({"error": f"Error publishing intelligent schedule: {e}"}))
        sys.exit(1)