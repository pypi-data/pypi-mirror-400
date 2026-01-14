import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--live-operator-id", required=True, help="The ID of the live operator.")
@click.option("--preroll-asset-id", help="The preroll asset ID of the live operator.")
@click.option("--postroll-asset-id", help="The postroll asset ID of the live operator.")
@click.option("--live-input-id", help="The live input ID of the live operator.")
@click.option("--related-content-id", multiple=True, help="The related content IDs of the live operator.")
@click.option("--tag-id", multiple=True, help="The tag IDs of the live operator.")
@click.pass_context
def start_broadcast(ctx, live_operator_id, preroll_asset_id, postroll_asset_id, live_input_id, related_content_id, tag_id):
    """Start broadcast"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.start_broadcast(live_operator_id, preroll_asset_id, postroll_asset_id, live_input_id,
                                  related_content_id, tag_id)
        
        if not result:
            click.echo(json.dumps({"error": f"Live operator with id {live_operator_id} not found."}))
            sys.exit(1)
            
        click.echo("Broadcast started successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error starting broadcast: {e}"}))
        sys.exit(1)