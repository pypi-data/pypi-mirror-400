import click
import json
import sys

def validate_json(json_string, field_name):
    try:
        return json.loads(json_string)
    except Exception as e:
        click.echo(json.dumps({ "error": f"Error parsing JSON for {field_name}: {e}" }))
        sys.exit(1)