import click
import sys, json

def get_content_definition_id(ctx, content_definition_name):
    """Get the content definition ID from the content definition name"""
    nomad_sdk = ctx.obj["nomad_sdk"]

    config = ctx.obj["config"]   

    if config["apiType"] == "admin":
        content_definitions = nomad_sdk.get_content_definitions(None, None, None, None, None)
        content_definition = next(filter(lambda x: x["properties"]["title"] == content_definition_name.capitalize(), content_definitions["items"]), None)
    
        if not content_definition:
            click.echo(json.dumps({ "error": "Content definition not found." }))
            sys.exit(1) 
    
        return content_definition["contentDefinitionId"]
    elif content_definition_name.lower() in ["collection", "tag"]:
        portal_json = nomad_sdk.misc_function("config/ea1d7060-6291-46b8-9468-135e7b94021b/portal.json", "GET", None, True)
        content_definition_id = portal_json[f"{content_definition_name.lower()}ContentDefinitionId"]
        return content_definition_id
    else:
        click.echo(json.dumps({ "error": "Cannot use content definition name for portal API unless it is collection or tag." }))
        sys.exit(1)
        
