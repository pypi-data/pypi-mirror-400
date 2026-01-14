import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the schedule the intelligent playlist is to be updated.")
@click.option("--collections", help="The collections of the intelligent playlist in JSON list format.")
@click.option("--end-search-date", help="The end search date of the intelligent playlist. Format: yyyy-MM-dd.THH:MM:SS.FFFZ.")
@click.option("--end-search-duration-in-minutes", type=click.INT, help="The end search duration in minutes of the intelligent playlist.")
@click.option("--name", help="The name of the intelligent playlist.")
@click.option("--related-contents", help="The related content of the intelligent playlist in JSON list format.")
@click.option("--search-date", help="The search date of the intelligent playlist. Format: yyyy-MM-dd.THH:MM:SS.FFFZ.")
@click.option("--search-duration-in-minutes", type=click.INT, help="The search duration in minutes of the intelligent playlist.")
@click.option("--search-filter-type", type=click.INT, help="The search filter type of the intelligent playlist. Values: Random: 1, Random within a Date Range: 2, Newest: 3, Newest Not Played: 4")
@click.option("--tags", help="The tags of the intelligent playlist in JSON list format.")
@click.option("--thumbnail-asset", help="The thumbnail asset of the intelligent playlist in JSON dict format.")
@click.pass_context
def update_intelligent_playlist(ctx, schedule_id, collections, end_search_date, end_search_duration_in_minutes, name, related_contents, search_date, search_duration_in_minutes, search_filter_type, tags, thumbnail_asset):
    """Update intelligent playlist"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.update_intelligent_playlist(
            schedule_id,
            validate_json(collections, "collections") if collections else None,
            end_search_date,
            end_search_duration_in_minutes,
            name,
            validate_json(related_contents, "related_contents") if related_contents else None,
            search_date,
            search_duration_in_minutes,
            search_filter_type,
            validate_json(tags, "tags") if tags else None,
            validate_json(thumbnail_asset, "thumbnail_asset") if thumbnail_asset else None
        )
        click.echo("Intelligent playlist updated successfully.")
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error updating intelligent playlist: {e}"}))
        sys.exit(1)