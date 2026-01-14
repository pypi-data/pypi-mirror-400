import click
import json
import sys

from nomad_media_cli.helpers.get_contents_by_name import get_contents_by_name
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--id", help="The ID of the Asset (file or folder) to register.")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to register (bucket::object-key).")
@click.option("--parent-id", help="The ID of the parent Asset.")
@click.option("--display-object-key", help="The display Object-key of the Asset to register.")
@click.option("--bucket-name", required=True, help="The bucket name of the Asset to register.")
@click.option("--object-key", required=True, help="The object key of the Asset to register.")
@click.option("--e-tag", help="The eTag of the Asset to register.")
@click.option("--tag-names", multiple=True, help="The tag name(s) of the Asset to register.")
@click.option("--tag-ids", multiple=True, help="The tag id(s) of the Asset to register.")
@click.option("--collection-names", multiple=True, help="The collection(s) of the Asset to register.")
@click.option("--collection-ids", multiple=True, help="The collection id(s) of the Asset to register.")
@click.option("--related-content-ids", multiple=True, help="The related content id(s) of the Asset to register.")
@click.option("--sequencer", help="The sequencer of the Asset to register.")
@click.option("--asset-status", help="The Asset status of the Asset to register.")
@click.option("--storage-class", help="The storage class of the Asset to register.")
@click.option("--asset-type", help="The Asset type of the Asset to register.")
@click.option("--content-length", type=click.INT, help="The content length of the Asset to register.")
@click.option("--storage-event-name", help="The storage event name of the Asset to register.")
@click.option("--created-date", help="The created date of the Asset to register.")
@click.option("--storage-source-ip-address", help="The storage source IP address of the Asset to register.")
@click.option("--start-media-processor", is_flag=True, help="The start media processor of the Asset to register.")
@click.option("--delete-missing-asset", is_flag=True, help="The delete missing Asset of the Asset to register.")
@click.pass_context
def register_asset(ctx, id, url, parent_id, display_object_key, bucket_name, object_key, e_tag, tag_names, tag_ids, 
                   collection_names, collection_ids, related_content_ids, sequencer, asset_status, storage_class, asset_type, 
                   content_length, storage_event_name, created_date, storage_source_ip_address, start_media_processor, 
                   delete_missing_asset):
    """Register asset"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    if url:       
        id = get_id_from_url(ctx, url, None, nomad_sdk)

    tags = tag_ids if tag_ids else []
    if tag_names:
        tag_props = get_contents_by_name(ctx, tag_names, "tag", nomad_sdk)
        tags += [tag["id"] for tag in tag_props]
        
    collections = collection_ids if collection_ids else []
    if collection_names:
        collection_props = get_contents_by_name(ctx, collection_names, "collection", nomad_sdk)
        collections += [collection["id"] for collection in collection_props]
            
    try:
        result = nomad_sdk.register_asset(
            id,
            parent_id,
            display_object_key,
            bucket_name,
            object_key,
            e_tag,
            tags if tags else None,
            collections if collections else None,
            related_content_ids,
            sequencer,
            asset_status,
            storage_class,
            asset_type,
            content_length,
            storage_event_name,
            created_date,
            storage_source_ip_address,
            start_media_processor,
            delete_missing_asset
        )
        
        if not result:
            click.echo(json.dumps({"error": f"Asset with id {id} not found."}))
            sys.exit(1)
            
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error registering asset: {e}"}))
        sys.exit(1)