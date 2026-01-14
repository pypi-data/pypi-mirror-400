from nomad_media_cli.helpers.utils import initialize_sdk
import click
import json
import sys

@click.command()
@click.option("--content-id", required=True, help="The ID of the content.")
@click.option("--content-definition-id", required=True, help="The ID of the content definition.")
@click.option("--sort_column", default=None, help="The sort column.")
@click.option("--is-desc", default=None, type=click.BOOL, help="The is descending flag.")
@click.option("--page-index", default=None, type=click.INT, help="The page index.")
@click.option("--size-index", default=None, type=click.INT, help="The size index.")
@click.pass_context
def get_content_user_track(ctx, content_id, content_definition_id, sort_column, is_desc, page_index, size_index):
    """Get the user track for a content"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.get_content_user_track(content_id, content_definition_id, sort_column, is_desc, page_index, size_index)
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({ "error": f"Error getting content user track: {e}" }))
        sys.exit(1)