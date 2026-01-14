import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--live-output-id", required=True, help="The ID of the live output profile.")
@click.pass_context
def delete_live_output_profile(ctx, live_output_id):
    """Delete live output profile"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.delete_live_output_profile(live_output_id)
        click.echo("Live output profile deleted successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error deleting live output profile: {e}"}))
        sys.exit(1)