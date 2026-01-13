"""
Envy CLI - Git for your .env files.

A secure environment variable management tool with encryption,
profiles, schema validation, and more.
"""

import typer
import subprocess
import os
import sys
import json
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Confirm, Prompt
from rich import print as rprint

from .crypto import EnvyCrypto, SecretMetadata
from .storage import (
    load_db, save_db,
    get_profile_secrets, set_secret, delete_secret,
    get_secret_metadata, create_profile, delete_profile,
    list_profiles, set_active_profile, get_active_profile,
    generate_env_file, parse_env_file, import_from_env_file,
    export_env_from_process, find_drift, get_all_keys, ENVY_DIR,
    get_remote, set_remote, remove_remote
)
from .utils import (
    is_envy_initialized, ensure_gitignore_entry,
    format_timestamp, format_relative_time, mask_secret,
    parse_key_value, parse_expiry, validate_profile_name,
    validate_key_name, get_shell_export_command
)

# Create CLI app
app = typer.Typer(
    name="envy",
    help="🔐 Envy: Git for your .env files - Secure environment variable management",
    add_completion=False,
    rich_markup_mode="rich"
)

# Sub-commands
profile_app = typer.Typer(help="Manage profiles (dev, prod, staging, etc.)")
team_app = typer.Typer(help="Team collaboration commands")
cloud_app = typer.Typer(help="Cloud sync commands (login, clone)")

app.add_typer(profile_app, name="profile")
app.add_typer(team_app, name="team")
app.add_typer(cloud_app, name="cloud")

console = Console()

# Cloud config
CLOUD_CONFIG_FILE = os.path.expanduser("~/.envy_cloud.json")
DEFAULT_API_URL = "https://envy-baq3.onrender.com/api"


def wait_for_server(api_url: str = None, max_retries: int = 30, retry_delay: float = 2.0) -> bool:
    """
    Wait for the server to be ready (handles cold starts on Render).
    Pings /api/health until server responds or max retries reached.
    
    Returns True if server is ready, False otherwise.
    """
    import requests
    import time
    
    if api_url is None:
        config = load_cloud_config()
        api_url = config.get("api_url", DEFAULT_API_URL)
    
    # Extract base URL (remove /api if present for health check)
    base_url = api_url.rstrip("/")
    if base_url.endswith("/api"):
        health_url = f"{base_url}/health"
    else:
        health_url = f"{base_url}/api/health"
    
    console.print("[dim]Connecting to Envy Cloud...[/dim]")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                if attempt > 0:
                    console.print("[green]✔ Server is ready![/green]")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if attempt == 0:
            console.print("[yellow]⏳ Server is starting up (cold start)...[/yellow]")
            console.print("[dim]This may take up to 60 seconds on free tier hosting.[/dim]")
        
        # Show progress every 5 attempts
        if attempt > 0 and attempt % 5 == 0:
            console.print(f"[dim]Still waiting... ({attempt * retry_delay:.0f}s elapsed)[/dim]")
        
        time.sleep(retry_delay)
    
    console.print("[red]✘ Server did not respond. Please try again later.[/red]")
    return False


def require_server_ready(api_url: str = None):
    """Check if server is ready, exit if not."""
    if not wait_for_server(api_url):
        raise typer.Exit(1)


def load_cloud_config() -> dict:
    """Load cloud authentication config."""
    if os.path.exists(CLOUD_CONFIG_FILE):
        with open(CLOUD_CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_cloud_config(config: dict):
    """Save cloud authentication config."""
    with open(CLOUD_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_cloud_token() -> Optional[str]:
    """Get saved cloud auth token."""
    config = load_cloud_config()
    return config.get("token")


def require_cloud_auth():
    """Check if logged in to cloud and exit if not."""
    token = get_cloud_token()
    if not token:
        console.print("[red]Error:[/red] Not logged in. Run [bold]envy cloud login[/bold] first.")
        raise typer.Exit(1)
    return token


def require_init():
    """Check if envy is initialized and exit if not."""
    if not is_envy_initialized():
        console.print("[red]Error:[/red] Envy not initialized. Run [bold]envy init[/bold] first.")
        raise typer.Exit(1)


# ============================================================================
# CLOUD COMMANDS
# ============================================================================

@cloud_app.command("login")
def cloud_login(
    email: Optional[str] = typer.Option(None, "--email", "-e", help="Email address"),
    api_url: str = typer.Option(DEFAULT_API_URL, "--api", help="API URL")
):
    """
    Login to Envy Cloud with your email and password.
    
    This allows you to clone environment variables from shared projects.
    """
    import requests
    
    # Check if server is ready (handles cold start)
    require_server_ready(api_url)
    
    # Prompt for email if not provided
    if not email:
        email = Prompt.ask("Email")
    
    # Prompt for password (hidden)
    password = Prompt.ask("Password", password=True)
    
    try:
        response = requests.post(
            f"{api_url}/auth/cli-login",
            json={"email": email, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data["data"]["token"]
            user = data["data"]["user"]
            
            # Save token
            save_cloud_config({
                "token": token,
                "email": user["email"],
                "name": user["name"],
                "api_url": api_url
            })
            
            console.print(Panel.fit(
                f"[green]✔ Logged in successfully![/green]\n\n"
                f"Welcome, [bold]{user['name']}[/bold] ({user['email']})\n\n"
                f"You can now use [bold]envy cloud clone[/bold] to clone projects.",
                title="🔐 Envy Cloud"
            ))
        else:
            error_msg = response.json().get("message", "Login failed")
            console.print(f"[red]{error_msg}[/red]")
            raise typer.Exit(1)
    except typer.Exit:
        raise
    except requests.exceptions.ConnectionError:
        console.print(f"[red]Error:[/red] Could not connect to {api_url}")
        console.print("Make sure the Envy server is running.")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@cloud_app.command("logout")
def cloud_logout():
    """
    Logout from Envy Cloud.
    """
    if os.path.exists(CLOUD_CONFIG_FILE):
        os.remove(CLOUD_CONFIG_FILE)
        console.print("[green]✔ Logged out successfully![/green]")
    else:
        console.print("[yellow]Not logged in.[/yellow]")


@cloud_app.command("status")
def cloud_status():
    """
    Show Envy Cloud login status.
    """
    config = load_cloud_config()
    if config.get("token"):
        console.print(Panel.fit(
            f"[green]✔ Logged in[/green]\n\n"
            f"Name: [bold]{config.get('name', 'Unknown')}[/bold]\n"
            f"Email: {config.get('email', 'Unknown')}",
            title="🔐 Envy Cloud Status"
        ))
    else:
        console.print("[yellow]Not logged in.[/yellow]")
        console.print("Run [bold]envy cloud login[/bold] to login.")


@cloud_app.command("clone")
def cloud_clone(
    project: str = typer.Argument(..., help="Project slug (e.g., my-project)"),
    environment: str = typer.Option("development", "--env", "-e", help="Environment to clone"),
    output: str = typer.Option(".env", "--output", "-o", help="Output file path")
):
    """
    Clone environment variables from a cloud project.
    
    Example: envy cloud clone my-project --env production
    """
    import requests
    
    token = require_cloud_auth()
    config = load_cloud_config()
    api_url = config.get("api_url", DEFAULT_API_URL)
    
    # Check if server is ready (handles cold start)
    require_server_ready(api_url)
    
    # Auto-initialize if not already initialized
    # Map environment names to short form
    env_map = {
        "development": "dev",
        "staging": "staging",
        "production": "prod"
    }
    local_env = env_map.get(environment, environment)
    
    if not is_envy_initialized():
        console.print("[dim]Initializing Envy...[/dim]")
        EnvyCrypto.generate_key(f"{ENVY_DIR}/master.key", use_keyring=True)
        save_db({
            "active_profile": local_env,
            "profiles": {
                "dev": {},
                "staging": {},
                "prod": {}
            },
            "metadata": {}
        })
        # Add to .gitignore with proper header
        gitignore_entries = [
            "# Envy - Secret Management",
            ".envy/master.key",
            ".envy/age.key",
            ".env",
            ".env.*",
            "!.env.example"
        ]
        for entry in gitignore_entries:
            ensure_gitignore_entry(entry)
    
    try:
        response = requests.get(
            f"{api_url}/projects/{project}/clone/{environment}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()["data"]
            
            # Write to .env file
            with open(output, "w") as f:
                f.write(f"# Cloned from {data['project']} ({data['environment']})\n")
                f.write(f"# Generated by Envy CLI\n\n")
                f.write(data["content"])
            
            var_count = len(data.get("variables", []))
            
            # Auto-import into local envy with proper metadata
            for var in data.get("variables", []):
                try:
                    crypto = EnvyCrypto()
                    encrypted_value = crypto.encrypt(var["value"])
                    metadata = SecretMetadata.create(
                        value="[encrypted]",
                        description=f"Cloned from {data['project']}"
                    )
                    set_secret(local_env, var["key"], encrypted_value, metadata)
                except Exception:
                    pass
            
            # Auto-save remote origin for push
            set_remote(data['slug'], api_url)
            
            console.print(Panel.fit(
                f"[green]✔ Cloned successfully![/green]\n\n"
                f"Project: [bold]{data['project']}[/bold]\n"
                f"Environment: [cyan]{data['environment']}[/cyan] → [cyan]{local_env}[/cyan]\n"
                f"Variables: {var_count}\n"
                f"Output: [bold]{output}[/bold]\n\n"
                f"[dim]Remote set to [bold]{data['slug']}[/bold] - use [bold]envy cloud push[/bold] to sync.[/dim]",
                title="🔐 Envy Clone"
            ))
        elif response.status_code == 401:
            console.print("[red]Error:[/red] Session expired. Please run [bold]envy cloud login[/bold] again.")
            raise typer.Exit(1)
        elif response.status_code == 403:
            console.print("[red]Error:[/red] You don't have access to this project.")
            raise typer.Exit(1)
        elif response.status_code == 404:
            console.print(f"[red]Error:[/red] Project '{project}' not found.")
            raise typer.Exit(1)
        else:
            error_msg = response.json().get("message", "Clone failed")
            console.print(f"[red]Error:[/red] {error_msg}")
            raise typer.Exit(1)
    except requests.exceptions.ConnectionError:
        console.print(f"[red]Error:[/red] Could not connect to {api_url}")
        raise typer.Exit(1)
    except Exception as e:
        if not isinstance(e, typer.Exit):
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        raise


@cloud_app.command("remote")
def cloud_remote(
    action: str = typer.Argument(None, help="Action: add, remove, or show"),
    origin: str = typer.Argument(None, help="Project slug for 'add' action")
):
    """
    Manage remote origin for push/pull operations.
    
    Examples:
        envy cloud remote              # Show current remote
        envy cloud remote show         # Show current remote
        envy cloud remote add myapp    # Set remote to 'myapp'
        envy cloud remote remove       # Remove remote
    """
    require_init()
    
    # Default to show
    if action is None or action == "show":
        remote = get_remote()
        if remote:
            console.print(Panel.fit(
                f"[green]Remote configured[/green]\n\n"
                f"Origin: [bold]{remote['origin']}[/bold]\n"
                f"Added: [dim]{remote.get('added_at', 'unknown')}[/dim]",
                title="🔗 Envy Remote"
            ))
        else:
            console.print("[dim]No remote configured.[/dim]")
            console.print("Use [bold]envy cloud remote add <project-slug>[/bold] to add a remote.")
        return
    
    if action == "add":
        if not origin:
            console.print("[red]Error:[/red] Project slug is required for 'add' action.")
            console.print("Usage: [bold]envy cloud remote add <project-slug>[/bold]")
            raise typer.Exit(1)
        
        config = load_cloud_config()
        api_url = config.get("api_url", DEFAULT_API_URL)
        set_remote(origin, api_url)
        console.print(f"[green]✔[/green] Remote set to [bold]{origin}[/bold]")
        return
    
    if action == "remove":
        remote = get_remote()
        if remote:
            remove_remote()
            console.print(f"[green]✔[/green] Remote [bold]{remote['origin']}[/bold] removed.")
        else:
            console.print("[dim]No remote to remove.[/dim]")
        return
    
    console.print(f"[red]Error:[/red] Unknown action '{action}'.")
    console.print("Valid actions: [bold]add[/bold], [bold]remove[/bold], [bold]show[/bold]")
    raise typer.Exit(1)


@cloud_app.command("push")
def cloud_push(
    profile: str = typer.Option(None, "--profile", "-p", help="Specific profile to push (default: all)"),
    force: bool = typer.Option(False, "--force", "-f", help="Force push, overwriting remote")
):
    """
    Push local environment variables to the cloud.
    
    Syncs all profiles (dev, staging, prod) or a specific profile to the remote project.
    
    Examples:
        envy cloud push                # Push all profiles
        envy cloud push -p dev         # Push only dev profile
        envy cloud push --force        # Force overwrite remote
    """
    import requests
    
    require_init()
    token = require_cloud_auth()
    
    remote = get_remote()
    if not remote:
        console.print("[red]Error:[/red] No remote configured.")
        console.print("Use [bold]envy cloud remote add <project-slug>[/bold] to set a remote.")
        raise typer.Exit(1)
    
    config = load_cloud_config()
    api_url = config.get("api_url", DEFAULT_API_URL)
    project_slug = remote["origin"]
    
    # Check if server is ready (handles cold start)
    require_server_ready(api_url)
    
    # Map local profile names to API environment names
    env_map = {
        "dev": "development",
        "staging": "staging", 
        "prod": "production"
    }
    
    db = load_db()
    profiles_to_push = [profile] if profile else list(db["profiles"].keys())
    
    crypto = EnvyCrypto()
    pushed_count = 0
    errors = []
    
    with console.status("[bold cyan]Pushing to cloud...") as status:
        for local_profile in profiles_to_push:
            if local_profile not in db["profiles"]:
                errors.append(f"Profile '{local_profile}' not found")
                continue
            
            remote_env = env_map.get(local_profile, local_profile)
            secrets = db["profiles"].get(local_profile, {})
            
            if not secrets:
                continue
            
            status.update(f"[bold cyan]Pushing {local_profile} → {remote_env}...")
            
            # Decrypt and push each variable
            for key, encrypted_value in secrets.items():
                try:
                    # Decrypt the value
                    decrypted_value = crypto.decrypt(encrypted_value)
                    
                    # Push to API with CLI source header
                    response = requests.post(
                        f"{api_url}/projects/{project_slug}/env/{remote_env}",
                        headers={
                            "Authorization": f"Bearer {token}",
                            "X-Envy-Source": "cli"
                        },
                        json={
                            "key": key,
                            "value": decrypted_value,
                            "isSecret": True,
                            "description": f"Pushed from CLI"
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json().get("data", {})
                        if data.get("changed", True):  # Default to True for backward compat
                            pushed_count += 1
                        # If changed=False, value was same, skip counting
                    elif response.status_code == 401:
                        console.print("[red]Error:[/red] Session expired. Please run [bold]envy cloud login[/bold] again.")
                        raise typer.Exit(1)
                    elif response.status_code == 403:
                        errors.append(f"No permission to edit {remote_env}")
                        break
                    else:
                        error_msg = response.json().get("message", "Push failed")
                        errors.append(f"{key}: {error_msg}")
                except Exception as e:
                    errors.append(f"{key}: {str(e)}")
    
    # Show results
    if pushed_count > 0:
        console.print(Panel.fit(
            f"[green]✔ Push complete![/green]\n\n"
            f"Remote: [bold]{project_slug}[/bold]\n"
            f"Variables changed: [cyan]{pushed_count}[/cyan]\n"
            f"Profiles: {', '.join(profiles_to_push)}",
            title="🚀 Envy Push"
        ))
    else:
        console.print(Panel.fit(
            f"[dim]No changes to push.[/dim]\n\n"
            f"Remote: [bold]{project_slug}[/bold]\n"
            f"All variables are up to date.",
            title="🚀 Envy Push"
        ))
    
    if errors:
        console.print("\n[yellow]Warnings:[/yellow]")
        for err in errors[:5]:  # Show first 5 errors
            console.print(f"  • {err}")
        if len(errors) > 5:
            console.print(f"  ... and {len(errors) - 5} more")


# ============================================================================
# CORE COMMANDS
# ============================================================================

@app.command()
def init(
    force: bool = typer.Option(False, "--force", "-f", help="Force re-initialization")
):
    """
    Initialize Envy in the current directory.
    
    Creates the .envy directory with encryption keys and default profiles.
    """
    if is_envy_initialized() and not force:
        console.print("[yellow]⚠ Envy is already initialized![/yellow]")
        console.print("Use [bold]--force[/bold] to re-initialize (this will reset your keys!).")
        return
    
    if force and is_envy_initialized():
        if not Confirm.ask("[red]This will reset your encryption keys. Continue?[/red]"):
            return
    
    # 1. Generate encryption key
    EnvyCrypto.generate_key(f"{ENVY_DIR}/master.key", use_keyring=True)
    
    # 2. Create empty database with default profiles
    save_db({
        "active_profile": "dev",
        "profiles": {
            "dev": {},
            "staging": {},
            "prod": {}
        },
        "metadata": {}
    })
    
    # 3. Add to .gitignore
    gitignore_entries = [
        "# Envy - Secret Management",
        "**/.envy/master.key",
        "**/.envy/age.key",
        "**/.envy/secrets.json",
        ".env",
        ".env.*",
        "!.env.example"
    ]
    
    for entry in gitignore_entries:
        ensure_gitignore_entry(entry)
    
    console.print(Panel.fit(
        "[green]✔ Envy initialized successfully![/green]\n\n"
        "📁 Created [bold].envy/[/bold] directory\n"
        "🔑 Generated encryption key\n"
        "📝 Default profiles: [cyan]dev[/cyan], [cyan]staging[/cyan], [cyan]prod[/cyan]\n\n"
        "[bold red]IMPORTANT:[/bold red] The master key has been added to .gitignore.\n"
        "[bold]NEVER[/bold] commit .envy/master.key to version control!",
        title="🔐 Envy"
    ))


@app.command()
def set(
    key_value: str = typer.Argument(..., help="KEY=VALUE to set"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Profile to set in"),
    expires: Optional[str] = typer.Option(None, "--expires", "-e", help="Expiration (e.g., 30d, 2w, 6m)"),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="Description of the secret")
):
    """
    Set an encrypted environment variable.
    
    Example: envy set DATABASE_URL=postgres://localhost/mydb
    """
    require_init()
    
    try:
        key, value = parse_key_value(key_value)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    # Validate key name
    valid, msg = validate_key_name(key)
    if not valid:
        console.print(f"[red]Error:[/red] {msg}")
        raise typer.Exit(1)
    
    # Use active profile if not specified
    if profile is None:
        profile = get_active_profile()
    
    # Check profile exists
    db = load_db()
    if profile not in db["profiles"]:
        console.print(f"[red]Error:[/red] Profile '{profile}' not found.")
        console.print(f"Available profiles: {', '.join(db['profiles'].keys())}")
        raise typer.Exit(1)
    
    # Encrypt and store
    crypto = EnvyCrypto()
    encrypted_value = crypto.encrypt(value)
    
    # Create metadata
    metadata = SecretMetadata.create(
        value="[encrypted]",
        expires_in_days=parse_expiry(expires) if expires else None,
        description=description
    )
    
    set_secret(profile, key, encrypted_value, metadata)
    
    console.print(f"[green]✔[/green] Set [cyan]{key}[/cyan] in [magenta]{profile}[/magenta]")
    
    if expires:
        console.print(f"  ⏰ Expires in {expires}")


@app.command()
def get(
    key: str = typer.Argument(..., help="Key to retrieve"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Profile to get from"),
    show: bool = typer.Option(False, "--show", "-s", help="Show the actual value (not masked)")
):
    """
    Get an environment variable value.
    """
    require_init()
    
    if profile is None:
        profile = get_active_profile()
    
    db = load_db()
    if profile not in db["profiles"]:
        console.print(f"[red]Error:[/red] Profile '{profile}' not found.")
        raise typer.Exit(1)
    
    if key not in db["profiles"][profile]:
        console.print(f"[red]Error:[/red] Key '{key}' not found in profile '{profile}'.")
        raise typer.Exit(1)
    
    crypto = EnvyCrypto()
    try:
        value = crypto.decrypt(db["profiles"][profile][key])
    except Exception:
        console.print(f"[red]Error:[/red] Failed to decrypt '{key}'. Key mismatch?")
        raise typer.Exit(1)
    
    if show:
        console.print(value)
    else:
        console.print(f"[cyan]{key}[/cyan]={mask_secret(value)}")
        console.print("[dim]Use --show to see the actual value[/dim]")


@app.command()
def delete(
    key: str = typer.Argument(..., help="Key to delete"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Profile to delete from"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation")
):
    """
    Delete an environment variable.
    """
    require_init()
    
    if profile is None:
        profile = get_active_profile()
    
    if not force:
        if not Confirm.ask(f"Delete [cyan]{key}[/cyan] from [magenta]{profile}[/magenta]?"):
            return
    
    if delete_secret(profile, key):
        console.print(f"[green]✔[/green] Deleted [cyan]{key}[/cyan] from [magenta]{profile}[/magenta]")
    else:
        console.print(f"[red]Error:[/red] Key '{key}' not found in profile '{profile}'.")
        raise typer.Exit(1)


@app.command()
def view(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Profile to view"),
    show: bool = typer.Option(False, "--show", "-s", help="Show actual values (not masked)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON")
):
    """
    View all secrets in a profile.
    """
    require_init()
    
    if profile is None:
        profile = get_active_profile()
    
    db = load_db()
    if profile not in db["profiles"]:
        console.print(f"[red]Error:[/red] Profile '{profile}' not found.")
        raise typer.Exit(1)
    
    crypto = EnvyCrypto()
    secrets = db["profiles"][profile]
    
    if not secrets:
        console.print(f"[yellow]No secrets in profile '{profile}'[/yellow]")
        return
    
    if json_output:
        import json
        decrypted = {}
        for k, v in secrets.items():
            try:
                decrypted[k] = crypto.decrypt(v) if show else "[encrypted]"
            except Exception:
                decrypted[k] = "[decryption failed]"
        console.print(json.dumps(decrypted, indent=2))
        return
    
    table = Table(title=f"🔐 Profile: {profile}", show_header=True)
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    table.add_column("Status", style="dim")
    
    metadata_dict = db.get("metadata", {}).get(profile, {})
    
    for key, encrypted_val in sorted(secrets.items()):
        try:
            value = crypto.decrypt(encrypted_val)
            display_value = value if show else mask_secret(value)
        except Exception:
            display_value = "[red]decryption failed[/red]"
        
        # Check metadata for expiry/staleness
        status = ""
        meta = metadata_dict.get(key, {})
        if meta:
            if SecretMetadata.is_expired(meta):
                status = "⚠️ EXPIRED"
            elif SecretMetadata.is_stale(meta):
                status = "🔄 Stale"
            else:
                days_left = SecretMetadata.days_until_expiry(meta)
                if days_left is not None and days_left <= 7:
                    status = f"⏰ {days_left}d left"
        
        table.add_row(key, display_value, status)
    
    console.print(table)
    
    if not show:
        console.print("\n[dim]Use --show to reveal actual values[/dim]")


@app.command()
def run(
    profile: str = typer.Argument(..., help="Profile to use"),
    command: List[str] = typer.Argument(..., help="Command to run (after --)")
):
    """
    Run a command with secrets injected into the environment.
    
    Example: envy run prod -- npm start
    
    This is the GOLD STANDARD for security - secrets live in memory, not on disk!
    """
    require_init()
    
    db = load_db()
    if profile not in db["profiles"]:
        console.print(f"[red]Error:[/red] Profile '{profile}' not found.")
        raise typer.Exit(1)
    
    crypto = EnvyCrypto()
    
    # Decrypt all secrets for this profile
    env_vars = os.environ.copy()
    secrets = db["profiles"][profile]
    decrypted_secrets = {}
    
    for k, v in secrets.items():
        try:
            decrypted_secrets[k] = crypto.decrypt(v)
            env_vars[k] = decrypted_secrets[k]
        except Exception:
            console.print(f"[red]Error:[/red] Failed to decrypt {k}. Key mismatch?")
            raise typer.Exit(1)
    
    # Check for expired secrets
    metadata_dict = db.get("metadata", {}).get(profile, {})
    expired = []
    expiring_soon = []
    
    for key in secrets.keys():
        meta = metadata_dict.get(key, {})
        if meta:
            if SecretMetadata.is_expired(meta):
                expired.append(key)
            else:
                days_left = SecretMetadata.days_until_expiry(meta)
                if days_left is not None and days_left <= 7:
                    expiring_soon.append((key, days_left))
    
    if expired:
        console.print(f"[yellow]⚠ Warning: Expired secrets: {', '.join(expired)}[/yellow]")
    
    if expiring_soon:
        for key, days in expiring_soon:
            console.print(f"[yellow]⏰ {key} expires in {days} days[/yellow]")
    
    # Run the subprocess
    console.print(f"[dim]Running in '{profile}' environment with {len(secrets)} secrets...[/dim]\n")
    
    try:
        result = subprocess.run(command, env=env_vars)
        raise typer.Exit(result.returncode)
    except FileNotFoundError:
        console.print(f"[red]Error:[/red] Command not found: {command[0]}")
        raise typer.Exit(1)


@app.command()
def export(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Profile to export"),
    output: str = typer.Option(".env", "--output", "-o", help="Output file path"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing file")
):
    """
    Generate a .env file from encrypted secrets.
    
    ⚠️  WARNING: This creates a plaintext file! Use 'envy run' for better security.
    """
    require_init()
    
    if profile is None:
        profile = get_active_profile()
    
    if os.path.exists(output) and not force:
        if not Confirm.ask(f"[yellow]File '{output}' exists. Overwrite?[/yellow]"):
            return
    
    db = load_db()
    if profile not in db["profiles"]:
        console.print(f"[red]Error:[/red] Profile '{profile}' not found.")
        raise typer.Exit(1)
    
    crypto = EnvyCrypto()
    secrets = db["profiles"][profile]
    
    decrypted = {}
    for k, v in secrets.items():
        try:
            decrypted[k] = crypto.decrypt(v)
        except Exception:
            console.print(f"[red]Error:[/red] Failed to decrypt {k}")
            raise typer.Exit(1)
    
    generate_env_file(decrypted, output, profile)
    
    console.print(f"[green]✔[/green] Exported {len(decrypted)} variables to [bold]{output}[/bold]")
    console.print("[yellow]⚠ Remember: This file contains plaintext secrets![/yellow]")
    console.print("[dim]Consider using 'envy run' instead for better security.[/dim]")


@app.command(name="import")
def import_env(
    file_path: str = typer.Argument(".env", help="Path to .env file to import"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Profile to import into"),
    merge: bool = typer.Option(False, "--merge", "-m", help="Merge with existing secrets")
):
    """
    Import variables from a .env file.
    """
    require_init()
    
    if not os.path.exists(file_path):
        console.print(f"[red]Error:[/red] File '{file_path}' not found.")
        raise typer.Exit(1)
    
    if profile is None:
        profile = get_active_profile()
    
    db = load_db()
    if profile not in db["profiles"]:
        console.print(f"[red]Error:[/red] Profile '{profile}' not found.")
        raise typer.Exit(1)
    
    env_vars = import_from_env_file(file_path)
    
    if not env_vars:
        console.print("[yellow]No variables found in file.[/yellow]")
        return
    
    if not merge and db["profiles"][profile]:
        if not Confirm.ask(f"[yellow]Profile '{profile}' has existing secrets. Replace all?[/yellow]"):
            console.print("Use [bold]--merge[/bold] to merge instead.")
            return
        db["profiles"][profile] = {}
    
    crypto = EnvyCrypto()
    imported = 0
    
    for key, value in env_vars.items():
        encrypted = crypto.encrypt(value)
        set_secret(profile, key, encrypted)
        imported += 1
    
    console.print(f"[green]✔[/green] Imported {imported} variables into [magenta]{profile}[/magenta]")


@app.command()
def capture(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Profile to capture into"),
    filter_prefix: Optional[str] = typer.Option(None, "--filter", "-f", help="Only capture vars with this prefix"),
    exclude_system: bool = typer.Option(True, "--exclude-system/--include-system", help="Exclude system variables")
):
    """
    Capture current process environment variables into a profile.
    
    Useful for importing from your current shell session.
    """
    require_init()
    
    if profile is None:
        profile = get_active_profile()
    
    db = load_db()
    if profile not in db["profiles"]:
        console.print(f"[red]Error:[/red] Profile '{profile}' not found.")
        raise typer.Exit(1)
    
    env_vars = export_env_from_process()
    
    # System variables to exclude
    system_vars = {
        'PATH', 'HOME', 'USER', 'SHELL', 'TERM', 'LANG', 'LC_ALL',
        'PWD', 'OLDPWD', 'HOSTNAME', 'LOGNAME', 'DISPLAY', 'EDITOR',
        'SYSTEMROOT', 'WINDIR', 'PROGRAMFILES', 'APPDATA', 'LOCALAPPDATA',
        'TEMP', 'TMP', 'COMPUTERNAME', 'USERNAME', 'USERPROFILE',
        'HOMEDRIVE', 'HOMEPATH', 'COMSPEC', 'OS', 'PROCESSOR_ARCHITECTURE',
        'NUMBER_OF_PROCESSORS', 'PATHEXT', 'PSModulePath'
    }
    
    crypto = EnvyCrypto()
    captured = 0
    
    for key, value in env_vars.items():
        # Filter by prefix if specified
        if filter_prefix and not key.startswith(filter_prefix):
            continue
        
        # Exclude system variables
        if exclude_system and key.upper() in system_vars:
            continue
        
        encrypted = crypto.encrypt(value)
        set_secret(profile, key, encrypted)
        captured += 1
    
    console.print(f"[green]✔[/green] Captured {captured} variables into [magenta]{profile}[/magenta]")


@app.command()
def diff(
    source: str = typer.Argument("dev", help="Source profile"),
    target: str = typer.Argument("prod", help="Target profile"),
    show_values: bool = typer.Option(False, "--show", "-s", help="Show actual values")
):
    """
    Show differences between two profiles (Drift Detection).
    
    Example: envy diff dev prod
    
    Helps prevent "It worked on my machine" errors!
    """
    require_init()
    
    db = load_db()
    
    for p in [source, target]:
        if p not in db["profiles"]:
            console.print(f"[red]Error:[/red] Profile '{p}' not found.")
            raise typer.Exit(1)
    
    drift = find_drift(source, target)
    crypto = EnvyCrypto() if show_values else None
    
    # Missing in target (potential problems in prod!)
    if drift["missing_in_target"]:
        console.print(f"\n[red]⚠ Keys in [bold]{source}[/bold] but MISSING in [bold]{target}[/bold]:[/red]")
        for key in sorted(drift["missing_in_target"]):
            if show_values and crypto:
                val = crypto.decrypt(db["profiles"][source][key])
                console.print(f"  [red]- {key}[/red] = {mask_secret(val)}")
            else:
                console.print(f"  [red]- {key}[/red]")
    
    # Missing in source
    if drift["missing_in_source"]:
        console.print(f"\n[yellow]Keys in [bold]{target}[/bold] but not in [bold]{source}[/bold]:[/yellow]")
        for key in sorted(drift["missing_in_source"]):
            console.print(f"  [yellow]+ {key}[/yellow]")
    
    # Common keys
    if drift["common"]:
        console.print(f"\n[green]✔ Keys present in both profiles: {len(drift['common'])}[/green]")
        if show_values:
            for key in sorted(drift["common"]):
                src_val = crypto.decrypt(db["profiles"][source][key])
                tgt_val = crypto.decrypt(db["profiles"][target][key])
                if src_val != tgt_val:
                    console.print(f"  [cyan]{key}[/cyan]: values differ")
    
    if not drift["missing_in_target"] and not drift["missing_in_source"]:
        console.print("\n[green]✔ No drift detected! Profiles are in sync.[/green]")
    elif drift["missing_in_target"]:
        console.print(f"\n[red]⚠ WARNING: {len(drift['missing_in_target'])} keys missing in {target}![/red]")
        console.print("[dim]These could cause production failures.[/dim]")


@app.command()
def check(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Profile to check")
):
    """
    Check for expired or stale secrets (Secret Rotation Reminders).
    """
    require_init()
    
    if profile is None:
        profile = get_active_profile()
    
    db = load_db()
    if profile not in db["profiles"]:
        console.print(f"[red]Error:[/red] Profile '{profile}' not found.")
        raise typer.Exit(1)
    
    metadata_dict = db.get("metadata", {}).get(profile, {})
    
    expired = []
    expiring_soon = []
    stale = []
    
    for key in db["profiles"][profile].keys():
        meta = metadata_dict.get(key, {})
        if meta:
            if SecretMetadata.is_expired(meta):
                expired.append(key)
            elif SecretMetadata.days_until_expiry(meta) is not None:
                days = SecretMetadata.days_until_expiry(meta)
                if days <= 30:
                    expiring_soon.append((key, days))
            
            if SecretMetadata.is_stale(meta):
                stale.append(key)
    
    console.print(Panel.fit(f"🔍 Secret Health Check: {profile}", style="bold"))
    
    if expired:
        console.print("\n[red]❌ EXPIRED SECRETS:[/red]")
        for key in expired:
            console.print(f"  • {key}")
    
    if expiring_soon:
        console.print("\n[yellow]⏰ EXPIRING SOON:[/yellow]")
        for key, days in sorted(expiring_soon, key=lambda x: x[1]):
            console.print(f"  • {key} ({days} days left)")
    
    if stale:
        console.print("\n[blue]🔄 STALE SECRETS (>90 days old):[/blue]")
        for key in stale:
            console.print(f"  • {key}")
    
    if not expired and not expiring_soon and not stale:
        console.print("\n[green]✔ All secrets are healthy![/green]")
    
    total_issues = len(expired) + len(expiring_soon) + len(stale)
    if total_issues > 0:
        raise typer.Exit(1)


# ============================================================================
# PROFILE COMMANDS
# ============================================================================

@profile_app.command("list")
def profile_list():
    """List all profiles."""
    require_init()
    
    profiles = list_profiles()
    active = get_active_profile()
    
    console.print("\n[bold]📁 Profiles:[/bold]\n")
    
    db = load_db()
    for p in profiles:
        count = len(db["profiles"].get(p, {}))
        marker = "[green]● active[/green]" if p == active else ""
        console.print(f"  {p} ({count} secrets) {marker}")


@profile_app.command("create")
def profile_create(
    name: str = typer.Argument(..., help="Name of the new profile")
):
    """Create a new profile."""
    require_init()
    
    valid, msg = validate_profile_name(name)
    if not valid:
        console.print(f"[red]Error:[/red] {msg}")
        raise typer.Exit(1)
    
    if create_profile(name):
        console.print(f"[green]✔[/green] Created profile [magenta]{name}[/magenta]")
    else:
        console.print(f"[yellow]Profile '{name}' already exists.[/yellow]")


@profile_app.command("delete")
def profile_delete(
    name: str = typer.Argument(..., help="Name of the profile to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation")
):
    """Delete a profile."""
    require_init()
    
    if name == get_active_profile():
        console.print("[red]Error:[/red] Cannot delete the active profile.")
        raise typer.Exit(1)
    
    if not force:
        if not Confirm.ask(f"[red]Delete profile '{name}' and all its secrets?[/red]"):
            return
    
    if delete_profile(name):
        console.print(f"[green]✔[/green] Deleted profile [magenta]{name}[/magenta]")
    else:
        console.print(f"[red]Error:[/red] Profile '{name}' not found.")
        raise typer.Exit(1)


@profile_app.command("switch")
def profile_switch(
    name: str = typer.Argument(..., help="Profile to switch to")
):
    """Switch the active profile."""
    require_init()
    
    if set_active_profile(name):
        console.print(f"[green]✔[/green] Switched to profile [magenta]{name}[/magenta]")
    else:
        console.print(f"[red]Error:[/red] Profile '{name}' not found.")
        raise typer.Exit(1)


@profile_app.command("copy")
def profile_copy(
    source: str = typer.Argument(..., help="Source profile"),
    target: str = typer.Argument(..., help="Target profile (will be created)")
):
    """Copy all secrets from one profile to another."""
    require_init()
    
    db = load_db()
    
    if source not in db["profiles"]:
        console.print(f"[red]Error:[/red] Source profile '{source}' not found.")
        raise typer.Exit(1)
    
    if target in db["profiles"]:
        if not Confirm.ask(f"[yellow]Profile '{target}' exists. Overwrite?[/yellow]"):
            return
    
    db["profiles"][target] = db["profiles"][source].copy()
    
    # Copy metadata too
    if "metadata" in db and source in db["metadata"]:
        db["metadata"][target] = db["metadata"][source].copy()
    
    save_db(db)
    
    count = len(db["profiles"][target])
    console.print(f"[green]✔[/green] Copied {count} secrets from [magenta]{source}[/magenta] to [magenta]{target}[/magenta]")


# ============================================================================
# TEAM COMMANDS
# ============================================================================

@team_app.command("list")
def team_list():
    """List team members for the current project."""
    import requests
    
    require_init()
    token = require_cloud_auth()
    
    remote = get_remote()
    if not remote:
        console.print("[red]Error:[/red] No remote configured.")
        console.print("Use [bold]envy cloud remote add <project-slug>[/bold] to set a remote.")
        raise typer.Exit(1)
    
    config = load_cloud_config()
    api_url = config.get("api_url", DEFAULT_API_URL)
    project_slug = remote["origin"]
    
    # Check if server is ready (handles cold start)
    require_server_ready(api_url)
    
    try:
        response = requests.get(
            f"{api_url}/projects/{project_slug}/team",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()["data"]
            team = data.get("team", [])
            
            if not team:
                console.print("[yellow]No team members found.[/yellow]")
                return
            
            table = Table(title=f"👥 Team Members - {project_slug}", show_header=True)
            table.add_column("Name", style="cyan")
            table.add_column("Email", style="dim")
            table.add_column("Role", style="green")
            table.add_column("Added", style="dim")
            
            for member in team:
                user = member.get("user", {})
                name = user.get("name", "Unknown")
                email = user.get("email", "")
                role = member.get("role", "member")
                added = format_relative_time(member.get("addedAt", ""))
                table.add_row(name, email, role.title(), added)
            
            console.print(table)
        
        elif response.status_code == 404:
            console.print(f"[red]Error:[/red] Project '{project_slug}' not found.")
            raise typer.Exit(1)
        
        elif response.status_code == 403:
            console.print("[red]Error:[/red] You don't have access to this project.")
            raise typer.Exit(1)
        
        else:
            error = response.json().get("message", "Unknown error")
            console.print(f"[red]Error:[/red] {error}")
            raise typer.Exit(1)
            
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error:[/red] Failed to connect to API: {e}")
        raise typer.Exit(1)


# ============================================================================
# UTILITY COMMANDS
# ============================================================================

@app.command()
def shell(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Profile to export")
):
    """
    Print shell export commands for secrets.
    
    Usage: eval $(envy shell)
    """
    require_init()
    
    if profile is None:
        profile = get_active_profile()
    
    db = load_db()
    if profile not in db["profiles"]:
        console.print(f"[red]Error:[/red] Profile '{profile}' not found.", err=True)
        raise typer.Exit(1)
    
    crypto = EnvyCrypto()
    secrets = db["profiles"][profile]
    
    for key, encrypted_val in secrets.items():
        try:
            value = crypto.decrypt(encrypted_val)
            print(get_shell_export_command(key, value))
        except Exception:
            pass


@app.command()
def status():
    """Show Envy status and summary."""
    if not is_envy_initialized():
        console.print("[yellow]Envy is not initialized in this directory.[/yellow]")
        console.print("Run [bold]envy init[/bold] to get started.")
        return
    
    db = load_db()
    schema = load_schema()
    active = get_active_profile()
    
    console.print(Panel.fit(
        f"[bold]🔐 Envy Status[/bold]\n\n"
        f"Active Profile: [cyan]{active}[/cyan]\n"
        f"Total Profiles: {len(db.get('profiles', {}))}\n"
        f"Schema Variables: {len(schema.get('variables', {}))}\n"
        f"Secrets in Active: {len(db.get('profiles', {}).get(active, {}))}",
        title="Status"
    ))
    
    # Show all profiles summary
    table = Table(show_header=True, header_style="bold")
    table.add_column("Profile")
    table.add_column("Secrets", justify="right")
    table.add_column("Status")
    
    for p_name, p_secrets in db.get("profiles", {}).items():
        status = "[green]● active[/green]" if p_name == active else ""
        table.add_row(p_name, str(len(p_secrets)), status)
    
    console.print(table)


@app.command()
def version():
    """Show Envy version."""
    from . import __version__
    console.print(f"Envy v{__version__}")


if __name__ == "__main__":
    app()
