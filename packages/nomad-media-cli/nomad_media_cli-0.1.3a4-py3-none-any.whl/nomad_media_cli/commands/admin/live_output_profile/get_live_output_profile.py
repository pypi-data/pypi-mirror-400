import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--live-output-id", required=True, help="The ID of the live output profile.")
@click.pass_context
def get_live_output_profile(ctx, live_output_id):
    """Get live output profile"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.get_live_output_profile(live_output_id)
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error getting live output profile: {e}"}))
        sys.exit(1)