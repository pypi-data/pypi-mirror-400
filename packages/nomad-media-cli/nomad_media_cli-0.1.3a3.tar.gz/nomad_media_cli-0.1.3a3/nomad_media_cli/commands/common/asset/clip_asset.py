import click
import json
import sys

from nomad_media_cli.helpers.get_contents_by_name import get_contents_by_name
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.validate_json import validate_json

@click.command()
@click.option("--id", help="The ID of the Asset (must be a video) to clip.")
@click.option("--url", help="The Nomad URL of the Asset (must be a video) to clip (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (must be a video) to clip. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--start-time-code", required=True, help="The start time code of the Asset to clip. Format: hh:mm:ss;ff.")
@click.option("--end-time-code", required=True, help="The end time code of the Asset to clip. Format: hh:mm:ss;ff.")
@click.option("--title", required=True, help="The title to add to the Asset to clip.")
@click.option("--output-folder-id", required=True, help="The output folder ID to add to the Asset to clip.")
@click.option("--tag-names", multiple=True, help="The tag name(s) to add to the Asset to clip.")
@click.option("--tag-ids", multiple=True, help="The tag id(s) to add to the Asset to clip.")
@click.option("--collection-names", multiple=True, help="The collection name(s) to add to the Asset to clip.")
@click.option("--collection-ids", multiple=True, help="The collection id(s) to add to the Asset to clip.")
@click.option("--related-content-ids", multiple=True, help="The related content id(s) to add to the Asset to clip.")
@click.option("--video-bitrate", type=click.INT, help="The video bitrate to add to the Asset to clip.")
@click.option("--audio-tracks", help="The audio tracks to add to the Asset to clip in JSON list format.")
@click.pass_context
def clip_asset(ctx, id, url, object_key, start_time_code, end_time_code, title, output_folder_id, tag_names, 
               tag_ids, collection_names, collection_ids, related_content_ids, video_bitrate, audio_tracks):
    """Clip asset"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]
    
    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide an id, url, or object-key."}))
        sys.exit(1)
        
    if url or object_key:
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)
        
    tags = [{"id": tag_id} for tag_id in tag_ids] if tag_ids else None
    if tag_names:
        tag_props = get_contents_by_name(ctx, tag_names, "tag", nomad_sdk)
        if tag_ids:
            tags += tag_props
            
    collections = [{"id": collection_id} for collection_id in collection_ids] if collection_ids else None
    if collection_names:
        collection_props = get_contents_by_name(ctx, collection_names, "collection", nomad_sdk)
        if collection_ids:
            collections += collection_props
            
    if related_content_ids:
        related_contents = [{"id": related_content_id} for related_content_id in related_content_ids]
    else:
        related_contents = None

    try:
        result = nomad_sdk.clip_asset(
            id,
            start_time_code,
            end_time_code,
            title,
            output_folder_id,
            tags,
            collections,
            related_contents,
            video_bitrate,
            [validate_json(audio_track, "audio_tracks") for audio_track in audio_tracks] if audio_tracks else None
        )

        if not result:          
            click.echo(json.dumps({"error": f"Asset with id {id} not found."}))
            sys.exit(1)        

        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error clipping asset: {e}"}))
        sys.exit(1)