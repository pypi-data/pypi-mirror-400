import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--live-operator-id", required=True, help="The ID of the live operator.")
@click.option("--related-content-id", multiple=True, help="The related content IDs of the live operator.")
@click.option("--tag-id", multiple=True, help="The tag IDs of the live operator.")
@click.pass_context
def complete_segment(ctx, live_operator_id, related_content_id, tag_id):
    """Complete segment"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.complete_segment(live_operator_id, related_content_id, tag_id)
        
        if not result:
            click.echo(json.dumps({"error": f"Live operator with id {live_operator_id} not found."}))
            sys.exit(1)
            
        click.echo("Segment completed successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error completing segment: {e}"}))
        sys.exit(1)