import click
import json
import sys

from nomad_media_cli.helpers.get_contents_by_name import get_contents_by_name
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--id", help="The ID of the asset to update the ad break for.")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to update the ad break for (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (file or folder) to update the ad break for. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--ad-break-id", required=True, help="The ID of the ad break.")
@click.option("--time-code", help="The time code of the asset ad break. Format: hh:mm:ss;ff.")
@click.option("--tag-names", multiple=True, help="The tag name(s) of the asset ad break.")
@click.option("--tag-ids", multiple=True, help="The tag id(s) of the asset ad break.")
@click.option("--label-names", multiple=True, help="The label name(s) of the asset ad break.")
@click.option("--label-ids", multiple=True, help="The label id(s) of the asset ad break.")
@click.pass_context
def update_asset_ad_break(ctx, id, url, object_key, ad_break_id, time_code, tag_names, tag_ids, label_names, label_ids):
    """Update asset ad break"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide an id, url, or object-key."}))
        sys.exit(1)

    if url or object_key:       
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)
        

    tags = [{"id": tag_id} for tag_id in tag_ids] if tag_ids else []
    if tag_names:
        tag_props = get_contents_by_name(ctx, tag_names, "tag", nomad_sdk)
        tags += tag_props        

    labels = [{"id": label_id} for label_id in label_ids] if label_ids else []
    if label_names:
        label_props = get_contents_by_name(ctx, label_names, "label", nomad_sdk)
        labels += label_props
            
    try:
        result = nomad_sdk.update_asset_ad_break(
            id,
            ad_break_id,
            time_code,
            tags if tags else None,
            labels if labels else None
        )
        
        if not result:
            click.echo(json.dumps({"error": f"Asset ad break with id {ad_break_id} not found."}))
            sys.exit(1)
            
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error updating asset ad break: {e}"}))
        sys.exit(1)