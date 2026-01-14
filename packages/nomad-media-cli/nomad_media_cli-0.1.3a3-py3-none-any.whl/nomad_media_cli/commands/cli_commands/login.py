from nomad_media_pip.src.nomad_sdk import Nomad_SDK
from nomad_media_cli.helpers.utils import get_config

import click
import json
import sys

@click.command()
@click.option("--username", help="Username for authentication")
@click.option("--password", help="Password for authentication")
@click.option("--api-key", help="API Key for authentication")
@click.option("--sso-provider", help="SSO Provider for authentication")
@click.option("--sso-code", help="SSO Code for authentication")
@click.option("--sso-state", help="SSO State for authentication")
@click.option("--sso-session-state", help="SSO Session State for authentication")
@click.option("--sso-redirect-url", help="SSO Redirect URL for authentication. Make sure to quote the URL.")
@click.pass_context
def login(ctx, username, password, api_key, sso_provider, sso_code, sso_state, sso_session_state, sso_redirect_url):
    """Login to the service"""

    get_config(ctx)

    config = ctx.obj["config"]
    config_path = ctx.obj["config_path"]

    try:
        login_config = config.copy()
        
        if username:
            login_config["username"] = username
        if password:
            login_config["password"] = password
        if api_key:
            login_config["apiKey"] = api_key
        if sso_provider:
            login_config["ssoProvider"] = sso_provider
        if sso_code:
            login_config["ssoCode"] = sso_code
        if sso_state:
            login_config["ssoState"] = sso_state
        if sso_session_state:
            login_config["ssoSessionState"] = sso_session_state
        if sso_redirect_url:
            login_config["ssoRedirectUrl"] = sso_redirect_url
        
        nomad_sdk = Nomad_SDK(login_config)
            
        config["token"] = nomad_sdk.token
        config["refresh_token_val"] = nomad_sdk.refresh_token_val
        config["expiration_seconds"] = nomad_sdk.expiration_seconds
        config["id"] = nomad_sdk.id
        
        with open(config_path, "w") as file:
            json.dump(config, file, indent=4)

        click.echo(json.dumps({ "message": "Successfully logged in." }))
            
    except Exception as e:
        click.echo(json.dumps({ "error": f"Error logging in: Invalid credentials" }))
        sys.exit(1)