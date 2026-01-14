import click
import json
import os
import platform
import re
import sys
import threading
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
from nomad_media_cli.helpers.capture_click_output import capture_click_output
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.commands.common.search.search import search
from nomad_media_cli.commands.common.asset.get_asset_details import get_asset_details

@click.command()
@click.option("--id", help="Asset ID, collection id, or saved search id to list the assets for.")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to download the archive for (bucket::object-key).")
@click.option("--object-key", help="Object-key only of the Asset (file or folder) to download the archive for. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--destination", default = ".", help="Local OS folder path specifying the location to download into. If this is not specified then it assumes the current folder")
@click.option("--threads", default=3, type=click.INT, help="The number of simultaneous downloads to perform. Default is 3.")
@click.option("--include-empty-folders", is_flag=True, help="Include empty folders in the download.")
@click.option("--download-proxy", is_flag=True, help="Download the assets using a proxy.")
@click.option("--template-name", help="The template name of the proxy to use for downloading the assets. This is only applicable if --download-proxy is set.")
@click.option("-r", "--recursive", is_flag=True, help="Download the assets in the subfolders also.")
@click.pass_context
def download_assets(ctx, id, url, object_key, destination, threads, include_empty_folders, download_proxy, template_name, recursive):
    """Download archive asset"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    if not id and not url and not object_key:
        click.echo(json.dumps({ "error": "Please provide an id, url or object-key" }))
        sys.exit(1)
        
    if url or object_key:
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)

    try:
        if not os.path.exists(destination):
            click.echo(json.dumps({ "error": f"Destination path {destination} does not exist." }))
            sys.exit(1)
            
        if not os.path.isdir(destination):
            click.echo(json.dumps({ "error": f"Destination path {destination} is not a directory." }))
            sys.exit(1)
            
        try:
            test_file = os.path.join(destination, "test")
            with open(test_file, "w") as f:
                pass
            os.remove(test_file)
        except Exception as e:
            click.echo(json.dumps({ "error": f"Destination path {destination} is not writable." }))
            sys.exit(1)

        offset = 0
        filtered_assets = []
        while True:
            assets = get_assets(nomad_sdk, id, offset, download_proxy, template_name)

            if not assets or assets["totalItemCount"] == 0:
                break
                
            asset_items = assets["items"]

            if download_proxy and template_name:
                filtered_asset_items = []
                for asset in asset_items:
                    template_found = False
                    for relatedVideo in asset["identifiers"].get("relatedVideos", []):
                        if relatedVideo.get("templateName") == template_name:
                            asset["identifiers"]["proxyUrl"] = relatedVideo.get("fullUrl")
                            template_found = True
                            break
                        
                    for relatedAudio in asset["identifiers"].get("relatedAudios", []):
                        if relatedAudio.get("templateName") == template_name:
                            asset["identifiers"]["proxyUrl"] = relatedAudio.get("fullUrl")
                            template_found = True
                            break

                    if template_found:
                        filtered_assets.append(asset)
                        
                asset_items = filtered_asset_items

            else:
                for asset in asset_items:
                    if not include_empty_folders:
                        if not asset["identifiers"].get("assetTypeDisplay"):
                            continue
                        if asset["identifiers"]["assetTypeDisplay"] == "Folder":
                            if asset["assetStats"]["totalContentLength"] == 0:
                                continue

                    filtered_assets.append(asset)
                    
            offset += 1
        
        if len(filtered_assets) == 0:
            click.echo(json.dumps({ "error": f"No assets found for id {id}" }))
            sys.exit(1)

        download_assets_exec(ctx, filtered_assets, destination, threads, download_proxy, template_name, recursive)

        if not include_empty_folders:
            # Remove empty folders created during download due to error
            for root, dirs, files in os.walk(destination, topdown=False):
                for dir in dirs:
                    try:
                        dir_path = os.path.join(root, dir)
                        if not os.listdir(dir_path):
                            os.rmdir(dir_path)
                    except Exception as e:
                        continue
                    
    except Exception as e:           
        click.echo(json.dumps({"error": f"Error downloading asset: {e}"}))
        sys.exit(1)
        
def download_assets_exec(ctx, assets, destination, threads, download_proxy, template_name, recursive):
    """Download assets in batches of 100"""
    is_folder_asset = assets[0]["identifiers"]["assetTypeDisplay"] == "Folder"
    asset_name = assets[0]["identifiers"]["displayName"]
    asset_date = assets[0]["identifiers"].get("displayDate")
    display_path = assets[0]["identifiers"]["displayPath"]
    
    if is_folder_asset:
        destination = os.path.join(destination, sanitize_path(asset_name))
        os.makedirs(destination, exist_ok=True)
        
    num_file_assets = len([asset for asset in assets if asset["identifiers"]["assetTypeDisplay"] == "File"])    

    progress_counter = threading.Lock()
    progress = {'current': 0}
    for batch_num in range(0, len(assets), 100):
        batch = assets[batch_num:batch_num + 100]
        download_batch(ctx, batch, threads, download_proxy, template_name, is_folder_asset, asset_name, 
                       asset_date, display_path, destination, num_file_assets, batch_num, recursive, progress, progress_counter)

    for asset in assets:
        if "fullUrl" in asset["identifiers"]:
            del asset["identifiers"]["fullUrl"]
            
    print_assets(assets)
    
def download_batch(ctx, batch, threads, download_proxy, template_name, is_folder_asset, asset_name, 
                   asset_date, display_path, destination, num_file_assets, batch_num, recursive, 
                   progress, progress_counter):
    
    print_lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for idx, asset in enumerate(batch):
            executor.submit(download_asset, ctx, asset, download_proxy, template_name, 
                            is_folder_asset, asset_name, asset_date, display_path, destination, 
                            num_file_assets, recursive, print_lock, progress, progress_counter)

def download_asset(ctx, asset, download_proxy, template_name, is_folder_asset, 
                   asset_name, asset_date, display_path, destination, num_file_assets, 
                   recursive, print_lock=None, progress=None, progress_counter=None):

    if download_proxy:
        if template_name:
            url = asset["identifiers"].get("proxyUrl")
        else:
            try:
                content_type = asset["identifiers"]["mediaTypeDisplay"]
                if content_type == "Video":
                    url = asset["identifiers"]["previewVideoFullUrl"]
                elif content_type == "Audio":
                    url = asset["identifiers"]["previewAudioFullUrl"]
                    asset_name = f"{os.path.splitext(asset_name)[0]}.mp3"
                elif content_type == "Image":
                    url = asset["identifiers"]["previewImageFullUrl"]
                else:
                    url = asset["identifiers"]["fullUrl"]
            except KeyError:
                url = asset["identifiers"]["fullUrl"]

        url_extension = get_extension_from_url(url)
        asset_name = f"{os.path.splitext(asset_name)[0]}{url_extension}"
        asset["identifiers"]["proxyUrl"] = url
    else:
        url = asset["identifiers"]["fullUrl"]    

    if is_folder_asset:
        id_path = display_path
        asset_path = asset["identifiers"]["displayPath"]
        path = asset_path.replace(id_path, "").strip("/")
        path = sanitize_path(path)
    else:
        path = sanitize_path(asset_name)

    # is folder
    if not url:
        if not recursive:
            return
        os.makedirs(f"{destination}/{path}", exist_ok=True)
    else:
        if destination:
            if os.sep in path:
                paths = path.split(os.sep)
                full_path = destination
                for path_sep in paths[:-1]:
                    full_path = os.path.join(full_path, path_sep)
                    if not os.path.exists(full_path):
                        os.makedirs(full_path, exist_ok=True)
                path = os.path.join(full_path, paths[-1])
                
                # Windows path length limit workaround
                if sys.platform == "win32":
                    path = f"\\\\?\\{os.path.abspath(path)}" 
            else:
                path = os.path.join(destination, path)     

        asset_name = os.path.basename(path)
        show_progress = True
        if os.path.exists(path):
            show_progress = False
        if show_progress and progress is not None and progress_counter is not None:
            with progress_counter:
                progress['current'] += 1
                progress_str = f"({progress['current']}/{num_file_assets}) Downloading {asset_name}"
        else:
            progress_str = f"Downloading {asset_name}"
        if print_lock:
            with print_lock:
                print(progress_str, file=sys.stderr)
        else:
            print(progress_str, file=sys.stderr)
        if os.path.exists(path):
            if print_lock:
                with print_lock:
                    print(f"Skipping {asset_name} as it already exists", file=sys.stderr)
            else:
                print(f"Skipping {asset_name} as it already exists", file=sys.stderr)
            asset["downloadStatus"] = "Skipped"
            return
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path), exist_ok=True)

        retries = 3
        for _ in range(retries):
            try:                
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                asset["downloadStatus"] = "Downloaded"
                break

            except Exception as e:
                asset["downloadStatus"] = "Failed"
                asset["downloadErrorMessage"] = str(e)
                
        if asset["downloadStatus"] == "Failed":
            return
                
        if response.status_code == 200:
            with open(path, "wb") as f:
                f.write(response.content)

            asset["downloadStatus"] = "Downloaded"

            try:
                if not asset_date:
                    return
                
                if asset_date.endswith('Z'):
                    asset_date_clean = asset_date[:-1]  # Remove the 'Z'
                else:
                    asset_date_clean = asset_date
                
                if "." in asset_date_clean:
                    asset_date_clean = asset_date_clean.split('.')[0]
                
                sys_time = datetime.strptime(asset_date_clean, "%Y-%m-%dT%H:%M:%S").timestamp()
                os.utime(path, (sys_time, sys_time))
            except Exception as e:
                if print_lock:
                    with print_lock:
                        print(f"Error setting file time for {asset_name}: {e}", file=sys.stderr)
                else:
                    print(f"Error setting file time for {asset_name}: {e}", file=sys.stderr)
        else:
            asset["downloadStatus"] = "Failed"
            downloadErrorMessage = None
            try:
                root = ET.fromstring(response.text)
                error_code = root.find("Code").text
                error_message = root.find("Message").text
                downloadErrorMessage = f"{error_code}: {error_message}"
            except ET.ParseError:
                downloadErrorMessage = response.text
                
            asset["downloadErrorMessage"] = downloadErrorMessage

    
def sanitize_path(path):
    """Sanitize the path by replacing invalid characters with underscores (_)."""

    if path.endswith("/"):
        path = path[:-1]

    if get_target_os(path) == "Windows":
        invalid_chars = r'[<>:"\\|?*]'
    
    sanitized_path_parts = []
    for part in path.split(os.sep):
        sanitized_part = re.sub(invalid_chars, "_", part)
        sanitized_path_parts.append(sanitized_part)
        
    sanitized_path = os.sep.join(sanitized_path_parts)

    return os.path.normpath(sanitized_path)

def get_target_os(path):
    """Get the target OS for the path."""
    if platform.system() == "Windows" or platform.system() == "Microsoft":
        return "Windows"
    
    abs_path = os.path.abspath(path)
    
    if abs_path.startswith("/mnt/") or abs_path.startswith("/media/"):
        return "Windows"
    
    return "Unix"

def get_assets(nomad_sdk, id, offset, download_proxy, template_name):
    filter = [{
        "fieldName": "uuidSearchField",
        "operator": "equals",
        "values": id
    }]

    if download_proxy and template_name:
        filter.append({
            "fieldName": "identifiers.mediaTypeDisplay",
            "operator": 2,
            "values": ["Audio", "Video"]
        })

    sort_field = [{
        "fieldName": "url",
        "sortType": "ascending"
    }]
     
    return nomad_sdk.search(None, offset, None, filter, sort_field, None, None, None, None, None, None, None, None, None, None)

def print_assets(assets):
    filtered_assets = [
        {
            "id": x["id"],
            "lastModifiedDate": x["lastModifiedDate"],
            "createdDate": x["createdDate"],
            "assetTypeDisplay": x["identifiers"]["assetTypeDisplay"],
            "mediaTypeDisplay": x["identifiers"].get("mediaTypeDisplay"),
            "name": x["identifiers"].get("name"),
            "contentLength": x["identifiers"].get("contentLength"),
            "displayPath": x["identifiers"].get("displayPath"),
            "url": x["identifiers"].get("url"),
            "fullUrl": x["identifiers"].get("fullUrl"),
            "proxyUrl": x["identifiers"].get("proxyUrl"),
            "downloadStatus": x.get("downloadStatus"),
        }
        for x in assets
    ]
    
    click.echo(json.dumps(filtered_assets, indent=4))

def get_extension_from_url(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    _, extension = os.path.splitext(path)
    return extension