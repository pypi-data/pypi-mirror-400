import click
import json
import sys
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--target-ids", multiple=True, help="The target ID(s) (file or folder) of the reprocess.")
@click.option("--target-urls", multiple=True, help="The target URL(s) (file or folder) (bucket::object-key) of the reprocess.")
@click.option("--target-object-keys", multiple=True, help="The target Object-key(s) (file or folder) of the reprocess. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.pass_context
def reprocess_asset(ctx, target_ids, target_urls, target_object_keys):
    """Reprocess asset"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]
    
    if not target_ids and not target_urls and not target_object_keys:
        click.echo(json.dumps({"error": "Please provide target-ids, target-urls, or target-object-keys."}))
        sys.exit(1)
        
    if not target_ids:
        target_ids = []

    if target_urls:
        target_ids.extend([get_id_from_url(ctx, url, None, nomad_sdk) for url in target_urls])
        
    if target_object_keys:
        target_ids.extend([get_id_from_url(ctx, None, object_key, nomad_sdk) for object_key in target_object_keys])

    try:
        result = nomad_sdk.reprocess_asset(target_ids)
        
        if not result or len(result) != len(target_ids):
            click.echo(json.dumps({"error": f"Asset with ids {target_ids} not found."}))
            sys.exit(1)
            
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error reprocessing asset: {e}"}))
        sys.exit(1)