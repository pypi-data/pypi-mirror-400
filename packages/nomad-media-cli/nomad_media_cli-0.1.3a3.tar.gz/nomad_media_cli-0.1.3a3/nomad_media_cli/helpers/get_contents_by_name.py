import click
import json
import sys

from nomad_media_cli.helpers.get_content_definition_id import get_content_definition_id

def get_contents_by_name(ctx, content_names, content_definition_name, nomad_sdk):
    """Get the content definition ID from the content definition name"""
    
    matching_contents = []
    offset = 0
    content_definition_id = get_content_definition_id(ctx, content_definition_name.capitalize())
    remaining_content_names = set(content_names)
    
    while remaining_content_names:
        contents = nomad_sdk.search(None, offset, None, [{
            "fieldName": "contentDefinitionId",
            "operator": "equals",
            "values": content_definition_id
        }], None, None, None, None, None, None, None, None, None, None, None)
        
        if len(contents["items"]) == 0:
            break

        for content in contents["items"]:
            if not remaining_content_names:
                break
            
            content_title = content.get("title")
            if content_title in remaining_content_names:
                matching_contents.append(content)
                remaining_content_names.remove(content_title)
                
        offset += 1
        
    if remaining_content_names:
        click.echo(json.dumps({ "error": f"contents not found: {remaining_content_names}" }))
        sys.exit(1)

    return matching_contents