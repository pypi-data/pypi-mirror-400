import click
import json
import sys
from nomad_media_cli.helpers.get_id_from_url import get_id_from_url
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--target-ids", multiple=True, help="The target ID(s) of the Asset (file or folder) to start the workflow for.") 
@click.option("--target-urls", multiple=True, help="The Nomad URL(s) of the Asset (file or folder) to start the workflow for (bucket::object-key).")
@click.option("--target-object-keys", multiple=True, help="Object-key(s) of the Asset (file or folder) to start the workflow for. This option assumes the default bucket that was previously set with the `set-bucket` command.")
@click.option("--action-arguments", required=True, help="The action arguments to start the workflow with.")
@click.pass_context
def start_workflow(ctx, action_arguments, target_ids, target_urls, target_object_keys):
    """Start workflow"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    if not target_ids and not target_urls and not target_object_keys:
        click.echo(json.dumps({"error": "Please provide target ids, urls, or object-keys."}))
        sys.exit(1)
        
    if not target_ids:
        target_ids = []
        
    if target_urls:
        target_ids.extend([get_id_from_url(ctx, url, None, nomad_sdk) for url in target_urls])
        
    if target_object_keys:
        target_ids.extend([get_id_from_url(ctx, None, object_key, nomad_sdk) for object_key in target_object_keys])   

    try:
        action_args = json.loads(action_arguments.strip().replace("'", '"'))
    except Exception as e:
        click.echo(json.dumps({"error": f"Error parsing action arguments: {e}"}))
        sys.exit(1)

    try:
        result = nomad_sdk.start_workflow(action_args, target_ids)
        
        if not result:
            click.echo(json.dumps({"error": f"Error starting workflow."}))
            sys.exit(1)
            
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error starting workflow: {e}"}))
        sys.exit(1)