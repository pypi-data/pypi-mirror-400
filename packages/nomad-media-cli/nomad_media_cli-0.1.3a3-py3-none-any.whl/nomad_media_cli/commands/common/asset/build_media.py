import click
import json
import sys

from nomad_media_cli.helpers.get_contents_by_name import get_contents_by_name
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--source-ids", multiple=True, help=(
        "The source ID(s) of the Asset(s) (file or folder) to build. Format: " 
        "[{'sourceAssetId': 'source-asset-id', 'startTimeCode': 'start-time-code', 'endTimeCode': 'end-time-code'}]. "
        "Both startTimeCode and endTimeCode are optional."
    ))
@click.option("--source-urls", multiple=True, help=(
        "The source URL(s) of Asset(s) (file or folder) to build (bucket::object-key). Format:"
        "[{'url': 'source-url', 'startTimeCode': 'start-time-code', 'endTimeCode': 'end-time-code'}]. "
        "Both startTimeCode and endTimeCode are optional."
    ))
@click.option("--source-object-keys", multiple=True, help=(
        "The source Object-key(s) of the Asset(s) (file or folder) to build. Format: "
        "[{'objectKey': 'source-object-key', 'startTimeCode': 'start-time-code', 'endTimeCode': 'end-time-code'}]. "
        "Both startTimeCode and endTimeCode are optional."
        "This option assumes the default bucket that was previously set with the `set-bucket` command."
    ))
@click.option("--title", help="The title to add to the Asset(s) to build.")
@click.option("--tag-names", multiple=True, help="The tag name(s) to add to the Asset(s) to build.")
@click.option("--tag-ids", multiple=True, help="The tag id(s) to add to the Asset(s) to build.")
@click.option("--collection-names", multiple=True, help="The collection name(s) to add to the Asset(s) to build.")
@click.option("--collection-ids", multiple=True, help="The collection id(s) to add to the Asset(s) to build.")
@click.option("--related-content-ids", multiple=True, help="The related content id(s) to add to the Asset(s) to build.")
@click.option("--destination-folder-id", required=True, help="The destination folder ID to add to the Asset(s) to build.")
@click.option("--video-bitrate", type=click.INT, help="The video bitrate to add to the Asset(s) to build.")
@click.option("--audio-tracks", multiple=True, help="The audio tracks to add to the Asset(s) to build in JSON list format.")
@click.pass_context
def build_media(ctx, source_ids, source_urls, source_object_keys, title, tag_names, tag_ids, collection_names, collection_ids, 
                related_content_ids, destination_folder_id, video_bitrate, audio_tracks):
    """Build media"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]
    
    if not source_ids and not source_urls and not source_object_keys:
        click.echo(json.dumps({"error": "Please provide source-ids, source-urls, or source-object-keys."}))
        sys.exit(1)
        
    if not source_ids:
        source_ids = []
    else:
        sources = []
        for source_id in source_ids:
            source = validate_json(source_id, "source_ids")
            sources.append({
                "sourceAssetId": source.get("sourceAssetId"),
                "start_time_code": source.get("startTimeCode"),
                "end_time_code": source.get("endTimeCode")
            })
        source_ids = sources
            
    if source_urls:
        for source in source_urls:
            source = validate_json(source, "source_urls")
            url = source.get("url")
            start_time_code = source.get("start_time_code")
            end_time_code = source.get("end_time_code")
            asset_id = get_id_from_url(ctx, url, None, nomad_sdk)
            source_ids.append({
                "sourceAssetId": asset_id,
                "start_time_code": start_time_code,
                "end_time_code": end_time_code
            })

    if source_object_keys:
        for source in source_object_keys:
            source = validate_json(source, "source_object_keys")
            object_key = source.get("object_key")
            start_time_code = source.get("start_time_code")
            end_time_code = source.get("end_time_code")
            asset_id = get_id_from_url(ctx, None, object_key, nomad_sdk)
            source_ids.append({
                "sourceAssetId": asset_id,
                "start_time_code": start_time_code,
                "end_time_code": end_time_code
            })
            
    tags = [{"id": tag_id} for tag_id in tag_ids] if tag_ids else []
    if tag_names:
        tag_props = get_contents_by_name(ctx, tag_names, "tag", nomad_sdk)
        tags += tag_props
        
    collections = [{"id": collection_id} for collection_id in collection_ids] if collection_ids else []
    if collection_names:
        collection_props = get_contents_by_name(ctx, collection_names, "collection", nomad_sdk)
        collections += collection_props
        
    if related_content_ids:
        related_contents = [{"id": related_content_id} for related_content_id in related_content_ids]
    else:
        related_contents = None

    try:
        nomad_sdk.build_media(
            source_ids,
            title,
            tags if tags else None,
            collections if collections else None,
            related_contents,
            destination_folder_id,
            video_bitrate,
            [validate_json(audio_track, "audio_tracks") for audio_track in audio_tracks] if audio_tracks else None
        )
        click.echo("Media built successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error building media: {e}"}))
        sys.exit(1)