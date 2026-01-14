import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--content-id", help="The content id of the event to update. None for create.")
@click.option("--content-definition-id", required=True, help="The content definition id of the event.")
@click.option("--name", help="The name of the event.")
@click.option("--start-datetime", required=True, help="The start date time of the event.")
@click.option("--end-datetime", required=True, help="The end date time of the event.")
@click.option("--event-type", required=True, help="The event type of the event in JSON dict format.")
@click.option("--series", help="The series of the event in JSON dict format.")
@click.option("--is-disabled", type=click.BOOL, help="Whether the event is disabled.")
@click.option("--override-series-properties", required=True, type=click.BOOL, help="Whether to override the series properties.")
@click.option("--series-properties", help="The properties of the event in JSON dict format.")
@click.pass_context
def create_and_update_event(ctx, content_id, content_definition_id, name, start_datetime, end_datetime, event_type, series, is_disabled, override_series_properties, series_properties):
    """Create and update event"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.create_and_update_event(
            content_id,
            content_definition_id,
            name,
            start_datetime,
            end_datetime,
            validate_json(event_type, "event_type"),
            validate_json(series, "series") if series else None,
            is_disabled,
            override_series_properties,
            validate_json(series_properties, "series_properties") if series_properties else None
        )
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error creating and updating event: {e}"}))
        sys.exit(1)