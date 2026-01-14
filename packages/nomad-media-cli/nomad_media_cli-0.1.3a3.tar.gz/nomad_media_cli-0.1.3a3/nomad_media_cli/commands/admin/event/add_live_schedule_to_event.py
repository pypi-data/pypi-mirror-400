import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--event-id", required=True, help="The ID of the event to add the live schedule to.")
@click.option("--slate-video", help="The slate video ID of the event in JSON dict format.")
@click.option("--preroll-video", help="The preroll video of the event in JSON dict format.")
@click.option("--postroll-video", help="The postroll video of the event in JSON dict format.")
@click.option("--is-secure-output", type=click.BOOL, help="Whether the event is secure output.")
@click.option("--archive-folder", help="The archive folder of the event in JSON dict format.")
@click.option("--primary-live-input", help="The live input A ID of the event in JSON dict format.")
@click.option("--backup-live-input", help="The live input B ID of the event in JSON dict format.")
@click.option("--primary-livestream-input-url", help="The primary live stream URL of the event.")
@click.option("--backup-livestream-input-url", help="The backup live stream URL of the event.")
@click.option("--external-output-profiles", help="The external output profiles of the event in JSON list format.")
@click.option("--status", help="Current status of the Live Channel Settings configuration in JSON dict format.")
@click.option("--status-message", help="The status message of the event.")
@click.option("--live-channel", help="The live channel of the event in JSON dict format.")
@click.option("--override-settings", type=click.BOOL, help="Whether to override the settings of the event.")
@click.option("--output-profile-group", help="The output profile group of the event in JSON dict format.")
@click.pass_context
def add_live_schedule_to_event(ctx, event_id, slate_video, preroll_video, postroll_video, is_secure_output, archive_folder, 
                               primary_live_input, backup_live_input, primary_livestream_input_url, backup_livestream_input_url, 
                               external_output_profiles, status, status_message, live_channel, override_settings, 
                               output_profile_group):
    """Add live schedule to event"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.add_live_schedule_to_event(
            event_id,
            validate_json(slate_video, "slate_video") if slate_video else None,
            validate_json(preroll_video, "preroll_video") if preroll_video else None,
            validate_json(postroll_video, "postroll_video") if postroll_video else None,
            is_secure_output,
            validate_json(archive_folder, "archive_folder") if archive_folder else None,
            validate_json(primary_live_input, "primary_live_input") if primary_live_input else None,
            validate_json(backup_live_input, "backup_live_input") if backup_live_input else None,
            primary_livestream_input_url,
            backup_livestream_input_url,
            validate_json(external_output_profiles, "external_output_profiles") if external_output_profiles else None,
            validate_json(status, "status") if status else None,
            status_message,
            validate_json(live_channel, "live_channel") if live_channel else None,
            override_settings,
            validate_json(output_profile_group, "output_profile_group") if output_profile_group else None
        )
        click.echo("Live schedule added to event successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error adding live schedule to event: {e}"}))
        sys.exit(1)