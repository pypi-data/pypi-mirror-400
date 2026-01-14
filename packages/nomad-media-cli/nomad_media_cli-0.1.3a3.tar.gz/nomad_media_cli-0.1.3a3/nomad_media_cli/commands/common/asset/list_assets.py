from nomad_media_cli.helpers.utils import initialize_sdk, get_config

import click
import json
import sys
import traceback

@click.command()
@click.option("--id", help="Asset ID, collection id, or saved search id to list the assets for")
@click.option("--url", help="The Nomad URL of the Asset (file or folder) to list the assets for (bucket::object-key).")
@click.option("--object-key", help="Object-key of the Asset (file or folder) to list the assets for. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--page-size", default=100, type=click.INT, help="Number of items to return per page. Default is 100.")
@click.option("--page-offset", default=0, type=click.INT, help="Offset of the page. Default is 0. The recommendation is to use page-token instead of page-offset.")
@click.option("--page-offset-token", help="Token to get the next page. Cannot be used with page-offset. This value is returned in a previous list-assets API call.")
@click.option("--order-by", default="title", help="Field to order by. Default is title.")
@click.option("--order-by-type", default="ascending", type=click.Choice(["asc", "desc", "ascending", "descending"]), help="Order type (asc, desc, ascending, descending). Default is ascending.")
@click.option("-r", "--recursive", is_flag=True, help="List assets recursively.")
@click.pass_context
def list_assets(ctx, id, url, object_key, page_size, page_offset, page_offset_token, order_by, order_by_type, recursive):
    """List assets"""
    
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]
    config = ctx.obj["config"]
    
    if not id and not url and not object_key:
        click.echo(json.dumps({"error": "Please provide an id, url, or object-key."}))
        sys.exit(1)

    if page_size and page_size not in range(1, 1000):
        click.echo(json.dumps({ "error": "Page size must be between 1 and 999." }))
        sys.exit(1)
        
    if page_offset and page_offset < 0:
        click.echo(json.dumps({ "error": "Page offset must be greater than or equal to 0." }))
        sys.exit(1)
        
    if page_offset and page_offset_token:
        click.echo(json.dumps({ "error": "Please provide either a page offset or a page offset token." }))
        sys.exit(1)
        
    if page_offset_token:
        try:
            page_offset_token = page_offset_token.replace('\\n', '').replace('\\"', '"')
            page_offset = page_offset_token
        except json.JSONDecodeError:
            click.echo(json.dumps({ "error": "Invalid page offset token." }))
            sys.exit(1)
        
    if order_by_type and (order_by_type == "asc" or order_by_type == "desc"):
        order_by_type += "ending"

    try:        
        filter = None
        if id:
            asset = nomad_sdk.get_asset_details(id)
            if not asset:
                click.echo(json.dumps({ "error": f"Asset with id {id} not found." }))
                sys.exit(1)        

            filter = [{
                "fieldName": "id",
                "operator": "equals",
                "values": id
            }]
        elif url or object_key:
            if url and "::" not in url:
                click.echo(json.dumps({ "error": "Please provide a valid path or set the default bucket." }))               
                sys.exit(1)
            if object_key:
                if "bucket" in config:
                    url = f"{config["bucket"]}::{object_key}"
                else:
                    click.echo(json.dumps({ "error": "Please set bucket using `set-bucket` or use url." }))
                    sys.exit(1)

            filter = [{
                "fieldName": "url",
                "operator": "equals",
                "values": url
            }]
        else:
            click.echo(json.dumps({ "error": "Please provide an id or path." }))
            sys.exit(1)
            
        sort_field = None
        sort_field = [{
            "fieldName": order_by,
            "sortType": order_by_type
        }]

        asset_properties_results = nomad_sdk.search(None, None, None, filter, None,
            None, None, None, None, None, None, None, None, None, None)
        
        if "items" not in asset_properties_results:
            click.echo(json.dumps(asset_properties_results))
            sys.exit(1)

        asset_properties = asset_properties_results["items"]
            
        results = []
        if asset_properties[0]["identifiers"]["assetTypeDisplay"] == "Folder":
            if recursive:
                filter = [{
                    "fieldName": "uuidSearchField",
                    "operator": "equals",
                    "values": asset_properties[0]["id"]
                }]           
            else:
                filter = [{
                    "fieldName": "parentId",
                    "operator": "equals",
                    "values": asset_properties[0]["id"]
                }]     

            folder_results = nomad_sdk.search(None, page_offset, page_size, filter, sort_field, 
                [
                    { "name": "id" },
                    { "name": "identifiers.name" },
                    { "name": "identifiers.url" },
                    { "name": "identifiers.fullUrl" },
                    { "name": "identifiers.assetTypeDisplay" },
                    { "name": "identifiers.mediaTypeDisplay" },
                    { "name": "identifiers.contentLength" },
                    { "name": "identifiers.displayPath" }
                ], None, None, None, None, None, None, None, None, None)
            
            results = folder_results
        else:
            results = nomad_sdk.search(None, page_offset, page_size, filter, sort_field, 
                [
                    { "name": "id" },
                    { "name": "identifiers.name" },
                    { "name": "identifiers.url" },
                    { "name": "identifiers.fullUrl" },
                    { "name": "identifiers.assetTypeDisplay" },
                    { "name": "identifiers.mediaTypeDisplay" },
                    { "name": "identifiers.contentLength" },
                    { "name": "identifiers.displayPath" }
                ], None, None, None, None, None, None, None, None, None)

        if "items" not in results:
            click.echo(json.dumps(results))
            sys.exit(1)

        filtered_result_items = [
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
                "fullUrl": x["identifiers"].get("fullUrl")
            }
            for x in results["items"]
        ]
        
        results["items"] = filtered_result_items

        result_str = json.dumps(results, indent=4, ensure_ascii=False)
        result_str = result_str.replace("False", "false").replace("True", "true")
        click.echo(result_str.encode("utf-8", errors="replace").decode())
    
    except Exception as e:
        click.echo(json.dumps({ "error": f"Error listing assets: {e}" }))
        sys.exit(1)