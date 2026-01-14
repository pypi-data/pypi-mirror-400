import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--content-management-type", type=click.INT, help="The type of content management to get. 1; None, 2; DataSelector, 3; FormSelector")
@click.option("--sort-column", help="The column to sort by.")
@click.option("--is-desc", type=click.BOOL, help="Whether to sort descending.")
@click.option("--page-index", type=click.INT, help="The page index to get.")
@click.option("--page-size", type=click.INT, help="The page size to get.")
@click.pass_context
def get_content_definitions(ctx, content_management_type, sort_column, is_desc, page_index, page_size):
    """Get content definitions"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        if content_management_type:
            if content_management_type < 1 or content_management_type > 3:
                click.echo(json.dumps({"error": "Content management type must be 1, 2, or 3."}))
                sys.exit(1)     

        result = nomad_sdk.get_content_definitions(content_management_type, sort_column, is_desc, page_index, page_size)
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error getting content definitions: {e}"}))
        sys.exit(1)