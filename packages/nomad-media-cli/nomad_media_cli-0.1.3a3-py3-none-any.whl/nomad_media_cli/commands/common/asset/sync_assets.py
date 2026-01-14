import click
import json
import os
import signal
import sys
import threading
import time
import unicodedata
from concurrent.futures import as_completed, FIRST_COMPLETED, ThreadPoolExecutor, wait
from nomad_media_cli.commands.admin.asset_upload.upload_assets import upload_assets
from nomad_media_cli.commands.common.asset.delete_asset import delete_asset
from nomad_media_cli.commands.common.asset.download_assets import download_assets
from nomad_media_cli.commands.common.asset.get_asset_details import get_asset_details
from nomad_media_cli.commands.common.asset.list_assets import list_assets
from nomad_media_cli.helpers.capture_click_output import capture_click_output
from nomad_media_cli.helpers.utils import initialize_sdk
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url

shutdown_requested = False

@click.command()
@click.option("--id", help="The ID of the Asset folder to be synced.")
@click.option("--url", help="The Nomad URL of the Asset folder to be synced (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset folder to be synced. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--sync-direction", required=True, type=click.Choice(["local-to-nomad", "nomad-to-local"]), help="Direction of the sync.")
@click.option("--local-path", required=True, help="Source path for the sync.")
@click.option("--threads", default=4, type=click.INT, help="Number of threads to use for the sync.")
@click.option("--include-empty-folders", is_flag=True, help="Include empty folders in the sync.")
@click.option("--poll-interval", type=click.INT, help="Polling interval in seconds. When set, the sync will run continuously until interrupted.")
@click.pass_context

def sync_assets(ctx, id, url, object_key, sync_direction, local_path, threads, include_empty_folders, poll_interval):
    """Sync assets between Nomad and local storage."""
    global shutdown_requested
    
    # sys.stdout = open('output.txt', 'w')
    # sys.stderr = open('error.txt', 'w')
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide an id, url, or object-key."}))
        sys.exit(1)

    if url or object_key:
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)

    response = nomad_sdk.get_asset(id)
    if not response:
        click.echo(json.dumps({"error": f"Asset folder not found: {id}."}))
        sys.exit(1)

    if response["assetType"] != 1:
        click.echo(json.dumps({"error": "Asset must be a folder."}))
        sys.exit(1)

    # Checks if the path is a directory
    if not os.path.isdir(local_path):
        click.echo(json.dumps({"error": "Local path must be a directory."}))
        sys.exit(1)
        
    if poll_interval:
        click.echo(f"Starting continuous sync with {poll_interval} second intervals. Press Ctrl+C to stop.")

        def signal_handler(sig, frame):
            global shutdown_requested
            shutdown_requested = True
            click.echo("\nShutdown requested. Completing current operation...")

        signal.signal(signal.SIGINT, signal_handler)

        sync_count = 0
        error_count = 0

        try:
            while not shutdown_requested:
                sync_count += 1
                click.echo(f"Starting sync iteration {sync_count}...")

                success = perform_sync(ctx, id, response, local_path, sync_direction, threads, include_empty_folders)
                
                if shutdown_requested:
                    click.echo("Shutdown requested during sync operation.")
                    break
                
                if not success:
                    error_count += 1
                    if error_count >= 5:
                        click.echo("Too many consecutive errors. Stopping sync.")
                        break
                else:
                    error_count = 0

                click.echo(f"Waiting {poll_interval} seconds before next sync...")
                for i in range(poll_interval):
                    if shutdown_requested:
                        break
                    time.sleep(1)

        except KeyboardInterrupt:
            shutdown_requested = True
            click.echo(f"\nSync interrupted by user after {sync_count} iterations.")
        except Exception as e:
            click.echo(json.dumps({"error": f"Unexpected error in continuous sync: {e}"}))
            sys.exit(1)
        finally:
            click.echo("Sync stopped gracefully.")
    else:
        try:
            perform_sync(ctx, id, response, local_path, sync_direction, threads, include_empty_folders)
        except KeyboardInterrupt:
            click.echo("\nSync interrupted by user.")
            sys.exit(0)

def perform_sync(ctx, id, response, local_path, sync_direction, threads, include_empty_folders):
    global shutdown_requested
    
    try:
        if shutdown_requested:
            return False
            
        differences = check_dir_structure(ctx, id, response["objectKey"], local_path, sync_direction, threads, include_empty_folders)
        
        if shutdown_requested:
            return False
        
        if differences:
            try:
                check_differences(ctx, differences, sync_direction, local_path, id, include_empty_folders)
                click.echo(f"Sync completed successfully at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                return True
            except Exception as sync_error:
                click.echo(json.dumps({"error": f"Error during sync operations: {sync_error}"}))
                return False
        else:
            click.echo(f"No differences found - everything is in sync at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            return True
    except Exception as e:
        click.echo(json.dumps({"error": f"Error during sync: {e}"}))
        return False
    
def check_differences(ctx, differences, sync_direction, source, id, include_empty_folders):
    global shutdown_requested
    
    for dif_key, difference_info in differences.items():
        if shutdown_requested:
            click.echo("Sync interrupted. Some operations may not be completed.")
            break
            
        try:
            if "missing" not in difference_info:
                for key, value in difference_info.items():
                    def get_files(file_dict, files, path=""):
                        if isinstance(file_dict["value"], dict):
                            if all(isinstance(val, str) for val in file_dict["value"].values()):
                                file_dict["value"]["path"] = path + file_dict["key"]
                                files[file_dict["key"]] = file_dict["value"]
                            else:
                                for sub_key, sub_value in file_dict["value"].items():
                                    get_files({"key": sub_key, "value": sub_value}, files, path + file_dict["key"] + "/")
                    
                    files = {}
                    get_files({"key": key, "value": value}, files, dif_key + "/")
                    check_differences(ctx, files, sync_direction, source, id, include_empty_folders)    
                continue          

            if sync_direction == "local-to-nomad":
                if difference_info["missing"] == "nomad":
                    file_path = os.path.join(source, difference_info["path"])
                    capture_click_output(ctx, upload_assets, id=id, source=file_path, recursive=True)
                else:
                    capture_click_output(ctx, delete_asset, id=difference_info["id"])
            elif sync_direction == "nomad-to-local":
                if difference_info["missing"] == "local":
                    asset_info = capture_click_output(ctx, get_asset_details, id=difference_info["id"])
                    if asset_info.get("error"):
                        click.echo(f"Skipping asset {dif_key} {difference_info['id']}: not found")
                        continue
                    elif asset_info["properties"]["statusName"] != "Available":
                        click.echo(f"Skipping asset {dif_key} {difference_info['id']}: not available.")
                        continue

                    file_path = os.path.join(source, difference_info['path'])
                    parent_dir = os.path.dirname(file_path)

                    if not os.path.exists(parent_dir):
                        os.makedirs(parent_dir, exist_ok=True)
                    try:
                        capture_click_output(ctx, download_assets, id=difference_info["id"], 
                            destination=parent_dir, include_empty_folders=include_empty_folders, recursive=True)
                    except PermissionError as e:
                        msg = f"Permission denied: Cannot write to {parent_dir}. Please check folder permissions. ({e})"
                        try:
                            click.echo(msg, file=sys.__stderr__)
                        except Exception:
                            print(msg, file=sys.__stderr__)
                        continue
                    except ValueError as e:
                        msg = f"I/O error: {e}. This may be due to a closed or unavailable stderr/stdout."
                        try:
                            click.echo(msg, file=sys.__stderr__)
                        except Exception:
                            print(msg, file=sys.__stderr__)
                        continue
                    except Exception as e:
                        msg = f"Skipping download for asset {dif_key} {difference_info['id']}: {asset_info['properties'].get('statusName')} {e}"
                        try:
                            click.echo(msg, file=sys.__stderr__)
                        except Exception:
                            print(msg, file=sys.__stderr__)
                        continue
                else:
                    file_path = os.path.join(source, difference_info["path"])
                    if os.path.isdir(file_path):
                        os.rmdir(file_path)
                    else:
                        os.remove(file_path)
        except Exception as e:
            click.echo(json.dumps({"error": f"Error processing differences: {e}"}))
            raise e

def get_total_asset_list(ctx, dir_id, threads):
    page_offset = 0
    dir_assets = []
    lock = threading.Lock()
    stop_event = threading.Event()
    
    def get_assets(dir_id, page_offset):
        for _ in range(3):
            list_assets_result = capture_click_output(ctx, list_assets, id=dir_id, page_size=100, page_offset=page_offset, recursive=True)
            if list_assets_result and "items" in list_assets_result:
                return list_assets_result["items"]
        else:
            raise Exception("Failed to retrieve assets after 3 attempts.")
    try:
        first_result = get_assets(dir_id, page_offset)
        if len(first_result) < 100:
            return first_result
        dir_assets.extend(first_result)
        page_offset += 1        

        with ThreadPoolExecutor(max_workers=threads) as executor:
            while not stop_event.is_set():
                futures = []
                current_offset = page_offset
                for i in range(threads):
                    futures.append(executor.submit(get_assets, dir_id, current_offset + i))
                
                batch_results = []
                for future in as_completed(futures):
                    try:
                        items = future.result()
                        batch_results.append(items)
                    except Exception as e:
                        click.echo(json.dumps({"error": f"Error retrieving assets: {e}"}))
                        stop_event.set()
                        break
                    
                with lock:
                    for items in batch_results:
                        dir_assets.extend(items)

                if any(len(items) == 0 for items in batch_results):
                    stop_event.set()
                    break

                page_offset += threads

        return dir_assets
    except Exception as e:
        return(e)

def check_dir_structure(ctx, id, nom_path, path, sync_direction, threads, include_empty_folders):
    try:
        nomad_structure = get_nomad_structure(ctx, id, nom_path, threads)
        local_structure = get_local_structure(path)
    except Exception as e:
        click.echo(json.dumps({"error": f"Error checking directory structure: {e}"}))
        sys.exit(1)

    return compare_structs(nomad_structure["sub_dirs"], local_structure["sub_dirs"], sync_direction, include_empty_folders)

def normalize_name(name):
    return unicodedata.normalize("NFC", name) if name else name

def compare_structs(nomad_struct, local_struct, sync_direction, include_empty_folders, current_path=""):
    differences = {}

    nomad_lookup = {normalize_name(item["name"]): item for item in nomad_struct}
    local_lookup = {normalize_name(item["name"]): item for item in local_struct}
    all_keys = set(nomad_lookup.keys()).union(set(local_lookup.keys()))

    for key in all_keys:
        asset_path = os.path.join(current_path, key) if current_path else key

        nomad_asset = nomad_lookup.get(key)
        local_asset = local_lookup.get(key)

        nomad_type = nomad_asset.get("file_type") if nomad_asset else None
        if not nomad_type and nomad_asset:
            nomad_type = nomad_asset.get("assetTypeDisplay")
        local_type = local_asset.get("file_type") if local_asset else None

        nomad_is_dir = nomad_type == "Folder"
        local_is_dir = local_type == "Folder"
        nomad_is_file = nomad_type == "File"
        local_is_file = local_type == "File"

        if nomad_asset and local_asset and nomad_is_file and local_is_file:
            continue

        # If both exist and both are folders, recurse
        if nomad_asset and local_asset and nomad_is_dir and local_is_dir:
            nested_diff = compare_structs(
                nomad_asset.get("sub_dirs", []),
                local_asset.get("sub_dirs", []),
                sync_direction,
                include_empty_folders,
                asset_path
            )
            if nested_diff:
                differences[key] = nested_diff
            continue

        # If missing on one side, add difference
        if not nomad_asset:
            if not include_empty_folders and local_type == "Folder" and local_asset.get("sub_dirs", []) == []:
                continue
            differences[key] = {"missing": "nomad", "path": asset_path}
        elif not local_asset:
            # For nomad folder: if it has sub_dirs, do not include the folder itself as a difference and do not include its id
            if nomad_is_dir:
                sub_dirs = nomad_asset.get("sub_dirs", [])
                if sub_dirs:
                    nested_diff = compare_structs(
                        sub_dirs,
                        [],
                        sync_direction,
                        include_empty_folders,
                        asset_path
                    )
                    if nested_diff:
                        differences[key] = nested_diff
                    continue
                else:
                    # Only include the folder as missing if it has no sub_dirs
                    differences[key] = {
                        "missing": "local",
                        "path": asset_path,
                        "file_type": nomad_type
                    }
                    continue
            # For files, include as missing
            differences[key] = {
                "missing": "local",
                "path": asset_path,
                "id": nomad_asset.get("id"),
                "file_type": nomad_type
            }
        # If types mismatch (file vs folder), treat as difference
        elif nomad_type != local_type:
            differences[key] = {
                "type_mismatch": True,
                "nomad_type": nomad_type,
                "local_type": local_type,
                "path": asset_path,
                "id": nomad_asset.get("id")
            }

    return differences


def get_nomad_structure(ctx, asset_id, path, threads):
    assets = get_total_asset_list(ctx, asset_id, threads)
    
    root_asset_name = path.strip("/").split("/")[-1]
    root = {"id": asset_id, "name": root_asset_name, "file_type": "Folder", "sub_dirs": []}
    
    def add_asset_to_structure(structure, parts, asset):
        try:
            if not parts or parts[0] == "":
                return

            current_part = normalize_name(parts[0])
            remaining_parts = [normalize_name(p) for p in parts[1:]]

            sub_dir = next((d for d in structure["sub_dirs"] if d["name"] == current_part), None)

            if not sub_dir: 
                sub_dir = {
                    "id": None, 
                    "name": current_part, 
                    "file_type": asset["assetTypeDisplay"] if not remaining_parts else "Folder", 
                    "sub_dirs": []
                }
                structure["sub_dirs"].append(sub_dir)

            if not remaining_parts:
                sub_dir.update({
                    "id": asset["id"]
                })
            else:
                add_asset_to_structure(sub_dir, remaining_parts, asset)
        except Exception as e:
            click.echo(json.dumps({"error": f"Error adding asset to structure: {e}"}))
            raise e

    def sort_sub_dirs(sub_dirs):
        # Folders first, then files, both sorted by name
        sub_dirs.sort(key=lambda d: (d["file_type"] != "Folder", d["name"]))
        for d in sub_dirs:
            if d["file_type"] == "Folder" and d["sub_dirs"]:
                sort_sub_dirs(d["sub_dirs"])
    
    # Process each asset
    try:
        for asset in assets:
            # Split the asset's URL into parts relative to the root path
            display_path = asset["displayPath"]
            if len(display_path.split(path)) < 2:
                continue
            relative_path = display_path.split(path, 1)[1].lstrip("/")
            parts = relative_path.split("/")

            # Add the asset to the structure
            add_asset_to_structure(root, parts, asset)

        sort_sub_dirs(root["sub_dirs"])
        return root
    except Exception as e:
        click.echo(json.dumps({"error": f"Error processing assets: {e}"}))
        raise e

def get_local_structure(path):
    structure = {"name": normalize_name(os.path.basename(path)), "file_type": "Folder", "sub_dirs": []}
    path = os.path.abspath(path)

    for root, dirs, files in os.walk(path):
        rel_path = os.path.relpath(root, path)
        
        if rel_path == ".":
            current_level = structure
        else:
            current_level = structure
            parts = [normalize_name(part) for part in rel_path.split(os.sep)]
            for part in parts:
                for sub_dir in current_level["sub_dirs"]:
                    if sub_dir["name"] == part:
                        current_level = sub_dir
                        break
        
        for dir_name in dirs:
            sub_dir = {"name": normalize_name(dir_name), "file_type": "Folder", "sub_dirs": []}
            current_level["sub_dirs"].append(sub_dir)
        
        for file_name in files:
            file_entry = {"name": normalize_name(file_name), "file_type": "File", "sub_dirs": []}
            current_level["sub_dirs"].append(file_entry)
    
    return structure