import click
import json

@click.command()
@click.pass_context
def list_config_path(ctx):
    """List the configuration path"""
    
    click.echo(json.dumps({ "path": ctx.obj["config_path"] }))