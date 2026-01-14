import click
from click import style

import os
from platformdirs import user_config_dir
import sys

from nomad_media_cli.commands.cli_commands.init import init
from nomad_media_cli.commands.cli_commands.list_config_path import list_config_path
from nomad_media_cli.commands.cli_commands.login import login
from nomad_media_cli.commands.cli_commands.logout import logout
from nomad_media_cli.commands.cli_commands.update_config import update_config

from nomad_media_cli.commands.admin.asset_upload.upload_assets import upload_assets

from nomad_media_cli.commands.common.asset.archive_asset import archive_asset
from nomad_media_cli.commands.common.asset.build_media import build_media
from nomad_media_cli.commands.common.asset.clip_asset import clip_asset
from nomad_media_cli.commands.common.asset.copy_asset import copy_asset
from nomad_media_cli.commands.common.asset.create_annotation import create_annotation
from nomad_media_cli.commands.common.asset.create_asset_ad_break import create_asset_ad_break
from nomad_media_cli.commands.common.asset.create_folder_asset import create_folder_asset
from nomad_media_cli.commands.common.asset.create_placeholder_asset import create_placeholder_asset
from nomad_media_cli.commands.common.asset.create_screenshot_at_timecode import create_screenshot_at_timecode
from nomad_media_cli.commands.common.asset.delete_annotation import delete_annotation
from nomad_media_cli.commands.common.asset.delete_asset_ad_break import delete_asset_ad_break
from nomad_media_cli.commands.common.asset.delete_asset import delete_asset
from nomad_media_cli.commands.common.asset.download_assets import download_assets
from nomad_media_cli.commands.common.asset.duplicate_asset import duplicate_asset
from nomad_media_cli.commands.common.asset.get_annotations import get_annotations
from nomad_media_cli.commands.common.asset.get_asset_ad_breaks import get_asset_ad_breaks
from nomad_media_cli.commands.common.asset.get_asset_child_nodes import get_asset_child_nodes
from nomad_media_cli.commands.common.asset.get_asset_details import get_asset_details
from nomad_media_cli.commands.common.asset.get_asset_manifest_with_cookies import get_asset_manifest_with_cookies
from nomad_media_cli.commands.common.asset.get_asset_metadata_summary import get_asset_metadata_summary
from nomad_media_cli.commands.common.asset.get_asset_parent_folders import get_asset_parent_folders
from nomad_media_cli.commands.common.asset.get_asset_screenshot_details import get_asset_screenshot_details
from nomad_media_cli.commands.common.asset.get_asset_segment_details import get_asset_segment_details
from nomad_media_cli.commands.common.asset.get_asset import get_asset
from nomad_media_cli.commands.common.asset.get_user_upload_parts import get_user_upload_parts
from nomad_media_cli.commands.common.asset.get_user_uploads import get_user_uploads
from nomad_media_cli.commands.common.asset.import_annotations import import_annotations
from nomad_media_cli.commands.common.asset.index_asset import index_asset
from nomad_media_cli.commands.common.asset.list_assets import list_assets
from nomad_media_cli.commands.common.asset.list_buckets import list_buckets
from nomad_media_cli.commands.common.asset.local_restore_asset import local_restore_asset
from nomad_media_cli.commands.common.asset.move_asset import move_asset
from nomad_media_cli.commands.common.asset.records_asset_tracking_beacon import records_asset_tracking_beacon
from nomad_media_cli.commands.common.asset.register_asset import register_asset
from nomad_media_cli.commands.common.asset.reprocess_asset import reprocess_asset
from nomad_media_cli.commands.common.asset.restore_asset import restore_asset
from nomad_media_cli.commands.common.asset.set_default_bucket import set_default_bucket
from nomad_media_cli.commands.common.asset.share_asset import share_asset
from nomad_media_cli.commands.common.asset.start_workflow import start_workflow
from nomad_media_cli.commands.common.asset.sync_assets import sync_assets
from nomad_media_cli.commands.common.asset.transcribe_asset import transcribe_asset
from nomad_media_cli.commands.common.asset.update_annotation import update_annotation
from nomad_media_cli.commands.common.asset.update_asset_ad_break import update_asset_ad_break
from nomad_media_cli.commands.common.asset.update_asset_language import update_asset_language
from nomad_media_cli.commands.common.asset.update_asset import update_asset

from nomad_media_cli.commands.common.content_metadata.add_asset_collection import add_asset_collection
from nomad_media_cli.commands.common.content_metadata.add_asset_properties import add_asset_properties
from nomad_media_cli.commands.common.content_metadata.add_asset_related_content import add_asset_related_content
from nomad_media_cli.commands.common.content_metadata.add_asset_tag import add_asset_tag
from nomad_media_cli.commands.common.content_metadata.list_asset_collections import list_asset_collections
from nomad_media_cli.commands.common.content_metadata.list_asset_related_contents import list_asset_related_contents
from nomad_media_cli.commands.common.content_metadata.list_asset_tags import list_asset_tags
from nomad_media_cli.commands.common.content_metadata.remove_asset_collection import remove_asset_collection
from nomad_media_cli.commands.common.content_metadata.remove_asset_related_content import remove_asset_related_content
from nomad_media_cli.commands.common.content_metadata.remove_asset_tag import remove_asset_tag

from nomad_media_cli.commands.common.search.get_content_definition_contents import get_content_definition_contents

from nomad_media_cli.helpers.check_token import check_token

# Set the configuration directory and path
CONFIG_DIR = user_config_dir("nomad_media_cli")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

@click.group()
@click.option("--config-path", default=CONFIG_PATH, help="Path to the configuration file (optional)")
@click.pass_context
def cli(ctx, config_path):
    """Nomad Media CLI"""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path

def add_command(command):
    #@click.command(name=command.name)
    #@click.pass_context
    #def wrapper(ctx, *args, **kwargs):
    #    with click.progressbar(length=100, label=f"Running {command.name}...", file=sys.stderr) as progress:
    #        result = ctx.invoke(command, *args, **kwargs)
    #        progress.update(100)
    #        progress.finish()  
    #    return result       

    return cli.add_command(command)   
    
# CLI_Commands
add_command(init)
add_command(list_config_path)
add_command(login)
add_command(logout)
add_command(update_config)

# Admin
# Asset Upload
add_command(upload_assets)

# Common
# Asset
add_command(archive_asset)
add_command(build_media)
add_command(clip_asset)
add_command(copy_asset)
add_command(create_annotation)
add_command(create_asset_ad_break)
add_command(create_folder_asset)
add_command(create_placeholder_asset)
add_command(create_screenshot_at_timecode)
add_command(delete_annotation)
add_command(delete_asset_ad_break)
add_command(delete_asset)
add_command(download_assets)
add_command(duplicate_asset)
add_command(get_annotations)
add_command(get_asset_ad_breaks)
add_command(get_asset_child_nodes)
add_command(get_asset_details)
add_command(get_asset_manifest_with_cookies)
add_command(get_asset_metadata_summary)
add_command(get_asset_parent_folders)
add_command(get_asset_screenshot_details)
add_command(get_asset_segment_details)
add_command(get_asset)
add_command(get_user_upload_parts)
add_command(get_user_uploads)
add_command(import_annotations)
add_command(index_asset)
add_command(list_assets)
add_command(list_buckets)
add_command(local_restore_asset)
add_command(move_asset)
add_command(records_asset_tracking_beacon)
add_command(register_asset)
add_command(reprocess_asset)
add_command(restore_asset)
add_command(set_default_bucket)
add_command(share_asset)
add_command(start_workflow)
add_command(sync_assets)
add_command(transcribe_asset)
add_command(update_annotation)
add_command(update_asset_ad_break)
add_command(update_asset_language)
add_command(update_asset)

# Content Metadata
add_command(add_asset_collection)
add_command(add_asset_properties)
add_command(add_asset_related_content)
add_command(add_asset_tag)
add_command(list_asset_collections)
add_command(list_asset_tags)
add_command(list_asset_related_contents)
add_command(remove_asset_collection)
add_command(remove_asset_related_content)
add_command(remove_asset_tag)

# Search
add_command(get_content_definition_contents)

@cli.result_callback()
@click.pass_context
def process(ctx, *args, **kwargs):
    if ctx.obj.get("nomad_sdk"):
        check_token(ctx.obj["config_path"], ctx.obj["nomad_sdk"])

if __name__ == "__main__":
    cli(obj={})
