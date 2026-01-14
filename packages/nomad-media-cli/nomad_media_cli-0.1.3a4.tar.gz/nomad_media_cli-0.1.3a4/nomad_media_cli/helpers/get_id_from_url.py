import click
import json
import sys

def get_id_from_url(ctx, url, object_key, nomad_sdk):
    if url and "::" not in url:
        click.echo(json.dumps({ "error": "Please provide a valid path or set the default bucket." }))               
        sys.exit(1)
    elif object_key:
        if "bucket" in ctx.obj["config"]:
            url = f"{ctx.obj["config"]["bucket"]}::{object_key}/"
        else:
            click.echo(json.dumps({ "error": "Please set bucket using `set-bucket` or use url." }))
            sys.exit(1)

    url_search_results = nomad_sdk.search(None, None, None, [{
        "fieldName": "url",
        "operator": "equals",
        "values": url
    }], None, None, None, None, None, None, None, None, None, None, None)
    
    if not url_search_results or len(url_search_results["items"]) == 0:
        click.echo(json.dumps({ "error": f"URL {url} not found." }))
        sys.exit(1)
        
    for item in url_search_results["items"]:
        if item["identifiers"]["url"] == url:
            return item["id"]
    
    click.echo(json.dumps({ "error": f"Asset with url {url} not found." }))
    sys.exit(1)