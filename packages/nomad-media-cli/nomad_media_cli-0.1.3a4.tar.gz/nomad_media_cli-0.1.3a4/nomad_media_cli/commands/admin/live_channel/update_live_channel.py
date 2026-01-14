import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--live-channel-id", required=True, help="The ID of the live channel.")
@click.option("--name", help="The name of the live channel.")
@click.option("--thumbnail-image-id", help="The thumbnail image ID of the live channel.")
@click.option("--archive-folder-asset-id", help="The archive folder asset ID of the live channel.")
@click.option("--enable-high-availability", type=click.BOOL, help="Indicates if the live channel is enabled for high availability.")
@click.option("--enable-live-clipping", type=click.BOOL, help="Indicates if the live channel is enabled for live clipping.")
@click.option("--is-secure-output", required=True, type=click.BOOL, help="Indicates if the live channel is secure output.")
@click.option("--is-output-screenshot", required=True, type=click.BOOL, help="Indicates if the live channel is output screenshot.")
@click.option("--channel-type", help="The type of the live channel. The types are External, IVS, Normal, and Realtime.")
@click.option("--external-service-api-url", help="The external service API URL of the live channel. Only required if the type is External.")
@click.option("--security-groups", help="The security groups of the live channel in JSON list format.")
@click.pass_context
def update_live_channel(ctx, live_channel_id, name, thumbnail_image_id, archive_folder_asset_id, enable_high_availability, enable_live_clipping, is_secure_output, is_output_screenshot, channel_type, external_service_api_url, security_groups):
    """Update live channel"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.update_live_channel(
            live_channel_id,
            name,
            thumbnail_image_id,
            archive_folder_asset_id,
            enable_high_availability,
            enable_live_clipping,
            is_secure_output,
            is_output_screenshot,
            channel_type,
            external_service_api_url,
            validate_json(security_groups, "security_groups") if security_groups else None
        )
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error updating live channel: {e}"}))
    sys.exit(1)