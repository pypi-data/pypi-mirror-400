import click
import os
import asyncio
import webbrowser
from functools import wraps
from ..api_client import get_api_client
from ..config_manager import config_manager

def require_login(f):
    """Decorator to enforce login."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = config_manager.get_token()
        if not token:
            click.echo("Error: You must be logged in to run this command.")
            click.echo("Run 'onecoder login' first.")
            return
        return f(*args, **kwargs)
    return wrapper

def require_feature(feature_name):
    """Decorator to enforce feature entitlements."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = config_manager.get_token()
            if not token:
                 click.secho("Error: You must be logged in to access this feature.", fg="red")
                 return
            
            entitlements = config_manager.get_entitlements()
            
            if feature_name not in entitlements:
                click.secho(f"Error: Feature '{feature_name}' is not enabled for your account.", fg="red")
                click.echo("Upgrade your plan at: https://onecoder.dev/upgrade")
                return
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

from ..constants import GITHUB_CLIENT_ID

@click.command()
def login():
    """Authenticates with OneCoder via GitHub."""
    
    async def get_url():
        try:
            client = get_api_client()
            return await client.get_github_auth_url()
        except Exception as e:
            raise e

    try:
        auth_url = asyncio.run(get_url())
    except Exception as e:
        click.secho(f"Error fetching auth URL from API: {e}", fg="red")
        click.secho("Fallback: Using local configuration if available.", fg="yellow")
        client_id = GITHUB_CLIENT_ID
        auth_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&scope=user:email"

    click.echo("To authenticate, please visit the following URL in your browser:")
    click.echo(f"\n  {auth_url}\n")
    click.secho("Note: If you haven't installed the OneCoder GitHub App yet, please do so from the App Profile page.", fg="yellow")
    
    if click.confirm("Open browser automatically?", default=True):
        webbrowser.open(auth_url)
    
    code = click.prompt("Enter the authorization code provided by GitHub")
    
    async def do_login():
        try:
            client = get_api_client()
            result = await client.login_with_github(code)
            config_manager.set_token(result["token"])
            config_manager.set_user(result["user"])
            
            # Fetch entitlements immediately after login
            client.set_token(result["token"])
            sub_info = await client.get_subscription_info()
            config_manager.set_entitlements(sub_info.get("entitlements", []))
            
            click.echo(f"Successfully logged in as {result['user']['username']}!")
            click.echo(f"Plan: {sub_info.get('planName', 'Free Tier')}")
            
            if "github" in result and result["github"].get("expiresIn"):
                 click.echo(f"  (Token expires in {result['github']['expiresIn']} seconds)")
                 
        except Exception as e:
            import logging
            logging.exception("Login process failed")
            click.echo(f"Error: Login failed: {e}")

    asyncio.run(do_login())

@click.command()
def logout():
    """Logs out of OneCoder."""
    config_manager.clear_token()
    config_manager.set_entitlements([])
    click.echo("Successfully logged out.")

@click.command()
def whoami():
    """Shows the currently authenticated user and their entitlements."""
    user = config_manager.get_user()
    if user:
        token = config_manager.get_token()
        entitlements = config_manager.get_entitlements()
        
        click.secho(f"Logged in as: {user['username']}", fg="green")
        if entitlements:
            click.echo(f"Active Features: {', '.join(entitlements)}")
        else:
            click.echo("Current Plan: Free Tier")
            
        if token:
            click.echo(f"Token: {token[:10]}...{token[-10:]}")
    else:
        click.echo("Not logged in.")
