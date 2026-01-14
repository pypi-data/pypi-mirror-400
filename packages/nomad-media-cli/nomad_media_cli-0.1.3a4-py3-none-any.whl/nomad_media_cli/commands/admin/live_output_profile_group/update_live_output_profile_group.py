import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--live-output-profile-group-id", required=True, help="The ID of the live output profile group.")
@click.option("--name", help="The name of the live output profile group.")
@click.option("--is-enabled", type=click.BOOL, help="Indicates if the live output profile group is enabled.")
@click.option("--manifest-type", help="The manifest type of the live output profile group. The types are HLS, DASH, and BOTH.")
@click.option("--is-default-group", type=click.BOOL, help="Indicates if the live output profile group is the default group.")
@click.option("--live-output-type", help="The type of the live output profile group in JSON list format.")
@click.option("--archive-live-output-profile", help="The archive live output profile of the live output profile group in JSON list format.")
@click.option("--live-output-profile", help="The live output profile of the live output profile group in JSON list format.")
@click.pass_context
def update_live_output_profile_group(ctx, live_output_profile_group_id, name, is_enabled, manifest_type, is_default_group, live_output_type, archive_live_output_profile, live_output_profile):
    """Update live output profile group"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.update_live_output_profile_group(
            live_output_profile_group_id,
            name,
            is_enabled,
            manifest_type,
            is_default_group,
            validate_json(live_output_type, "live_output_type") if live_output_type else None,
            validate_json(archive_live_output_profile, "archive_live_output_profile") if archive_live_output_profile else None,
            validate_json(live_output_profile, "live_output_profile") if live_output_profile else None
        )
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error updating live output profile group: {e}"}))
        sys.exit(1)