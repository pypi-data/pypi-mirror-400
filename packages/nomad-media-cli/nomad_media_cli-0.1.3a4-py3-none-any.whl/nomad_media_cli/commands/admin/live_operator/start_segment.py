import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--live-operator-id", required=True, help="The ID of the live operator.")
@click.pass_context
def start_segment(ctx, live_operator_id):
    """Start segment"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.start_segment(live_operator_id)
        click.echo("Segment started successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error starting segment: {e}"}))
        sys.exit(1)