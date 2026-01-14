import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--live-output-profile-group-id", required=True, help="The ID of the live output profile group.")
@click.pass_context
def get_live_output_profile_group(ctx, live_output_profile_group_id):
    """Get live output profile group"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.get_live_output_profile_group(live_output_profile_group_id)
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error getting live output profile group: {e}"}))
        sys.exit(1)