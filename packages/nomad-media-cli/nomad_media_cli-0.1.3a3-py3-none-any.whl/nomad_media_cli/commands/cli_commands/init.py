from nomad_media_cli.commands.cli_commands.login import login

import click
import json
import os

@click.command()
@click.option("--service-api-url", required=True, help="API URL for the service")
@click.option("--api-type", default="admin", type=click.Choice(['admin', 'portal']), help="API type [admin|portal]. Default is admin")
@click.option("--debug", default=False, type=click.BOOL, help="Enable debug mode. Default is false")
@click.option("--username", help="Username credential")
@click.option("--password", help="Password credential")
@click.option("--api-key", help="API Key credential")
@click.option("--sso-provider", help="SSO Provider credential")
@click.option("--sso-code", help="SSO Code credential")
@click.option("--sso-state", help="SSO State credential")
@click.option("--sso-session-state", help="SSO Session State credential")
@click.option("--sso-redirect-url", help="SSO Redirect URL credential. Make sure use quotes for the URL.")

@click.pass_context
def init(ctx, service_api_url, api_type, debug, username, password, api_key, sso_provider, sso_code, sso_state, sso_session_state, sso_redirect_url):
    """Initialize the SDK and save configuration"""
    
    config_path = ctx.obj["config_path"]
    config_dir = os.path.dirname(config_path)
    os.makedirs(config_dir, exist_ok=True)
    
    if not service_api_url.startswith("https://"):
        service_api_url = f"https://{service_api_url}"
        
    debug = debug or False
    
    config = {
        "serviceApiUrl": service_api_url,
        "apiType": api_type,
        "debugMode": debug,
        "disableLogging": not debug
    }
    
    try:
        with open(config_path, "w") as file:
            json.dump(config, file, indent=4)
            
        if not username and not password and not api_key and not sso_provider and not sso_code and not sso_state and not sso_session_state and not sso_redirect_url:
            click.echo(json.dumps({ "message": "Successfully initialized the CLI" }))
            
        if username or password or api_key or sso_provider or sso_code or sso_state or sso_session_state or sso_redirect_url:
            ctx.invoke(login, username=username, password=password, api_key=api_key, sso_provider=sso_provider, sso_code=sso_code, sso_state=sso_state, sso_session_state=sso_session_state, sso_redirect_url=sso_redirect_url)
            
    except Exception as e:
        click.echo(json.dumps({ "error": f"Error saving configuration: {e}" }))