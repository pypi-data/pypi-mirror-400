import click
import json
import os
import sys
import logging
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
from nomad_media_cli.commands.common.asset.list_assets import list_assets
from nomad_media_cli.helpers.capture_click_output import capture_click_output
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk

BATCH_SIZE = 100

@click.command()
@click.option("--source", required=True, help="Local OS file or folder path specifying the files or folders to upload. For example: file.jpg or folderName/file.jpg or just folderName.")
@click.option("--id", help="Nomad ID of the Asset Folder to upload the source file(s) and/or folder(s) into.")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to list the assets for (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (file or folder) to list the assets for. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--num-files", default=3, type=click.INT, help="Number of concurrent files to upload.")
@click.option("-r", "--recursive", is_flag=True, help="Recursively upload a folder.")
@click.pass_context
def upload_assets(ctx, source, id, url, object_key, num_files, recursive):
    """Upload assets with batching and multiprocessing."""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    if not os.path.exists(source):
        click.echo(json.dumps({"error": "Source path does not exist."}))
        sys.exit(1)

    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide an id, url, or object-key."}))
        sys.exit(1)

    if url or object_key:
        id = get_id_from_url(ctx, url, object_key, nomad_sdk)

    response = nomad_sdk.get_asset(id)
    if not response:
        click.echo(json.dumps({"error": f"Parent folder not found: {id}."}))
        sys.exit(1)

    if response["assetType"] != 1:
        click.echo(json.dumps({"error": "Asset must be a folder."}))
        sys.exit(1)

    try:
        files_to_upload = []
        if os.path.isdir(source):
            if not recursive:
                click.echo(json.dumps({"error": "Please use the --recursive option to upload directories."}))
                sys.exit(1)
            source_name = os.path.basename(source)
            folder_id = find_folder_id(id, source_name, 1, nomad_sdk)                  

            folder_id_map = {source: folder_id}
            
            for root, dirs, files in os.walk(source):
                folder_name = os.path.basename(root)
                folder_id = folder_id_map.get(root)

                if not folder_id:
                    parent_folder_id = folder_id_map[os.path.dirname(root)]

                    folder_id = find_folder_id(parent_folder_id, folder_name, 1, nomad_sdk)

                    folder_id_map[root] = folder_id

                for name in files:
                    if find_folder_id(folder_id, name, 2, nomad_sdk):
                        continue

                    file_path = os.path.normpath(os.path.join(root, name))

                    if sys.platform == "win32":
                        file_path = f"\\\\?\\{os.path.abspath(file_path)}"
                        
                    if os.path.getsize(file_path) == 0:
                        continue
                    
                    files_to_upload.append((file_path, folder_id))
        else:
            if os.path.getsize(source) == 0:
                click.echo(json.dumps({"error": "File is empty."}))
                sys.exit(1)
            files_to_upload.append((source, id))

        # Process files in batches
        assets = []
        exit_code = 0
        for i in range(0, len(files_to_upload), BATCH_SIZE):
            batch = files_to_upload[i:i + BATCH_SIZE]
            batch_assets, batch_exit_code = upload_files(ctx, batch, num_files, nomad_sdk)
            assets.extend(batch_assets)
            if batch_exit_code == 1:
                exit_code = 1
                
        click.echo(json.dumps(assets))
        sys.exit(exit_code)

    except Exception as e:
        exec_type, exec_value, exec_tb = sys.exc_info()
        click.echo(json.dumps({"error": f"Error uploading assets: {e}"}))
        sys.exit(1)

def upload_files(ctx, batch, num_files, nomad_sdk):
    """
    Upload files in a single process using multithreading.
    """
    assets = []
    exit_code = 0 

    with ThreadPoolExecutor(max_workers=num_files) as executor:
        futures = []
        for file_path, folder_id in batch:
            future = executor.submit(upload_asset, file_path, folder_id, nomad_sdk)
            futures.append(future)
        for future in as_completed(futures):
            response = future.result()
            if response:
                list_assets_response = capture_click_output(
                    ctx,
                    list_assets,
                    id=response
                )
                assets.append(list_assets_response["items"][0])
            else:
                assets.append({"file": file_path, "uploadStatus": "Failed", "uploadErrorMessage": "Error uploading asset."})
                exit_code = 1
                
    return assets, exit_code


def upload_asset(file_path, folder_id, nomad_sdk):
    """
    Retry logic for uploading a file.
    """
    try:
        asset_id = nomad_sdk.upload_asset(None, None, None, "replace", file_path, folder_id, None)
        if not asset_id:
            raise Exception("Error uploading asset.")
        return asset_id
    except Exception as e:
        return None
    
def find_folder_id(parent_id, folder_name, asset_type, nomad_sdk):
    offset = 0
    folder_id = None
    while True:
        nomad_folders = nomad_sdk.search(None, offset, None,
            [
                {
                    "fieldName": "parentId",
                    "operator": "equals",
                    "values": parent_id
                },
                {
                    "fieldName": "assetType",
                    "operator": "equals",
                    "values": asset_type
                }
            ],
            None, None, None, None, None, None, None, None, None, None, None)                     

        if len(nomad_folders["items"]) == 0:
            break

        folder = next((nomad_folder for nomad_folder in nomad_folders["items"] if nomad_folder["title"] == folder_name), None)
        if folder:
            folder_id = folder["id"]
            break

        offset += 1
        
    if not folder_id and asset_type == 1:
        folder = nomad_sdk.create_folder_asset(parent_id, folder_name)
        folder_id = folder["id"]
        
    return folder_id