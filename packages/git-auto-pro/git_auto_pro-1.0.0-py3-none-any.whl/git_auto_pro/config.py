"""Configuration management module."""

import json
from pathlib import Path
from typing import Any, Optional, Dict, Union
from rich.console import Console
from rich.table import Table

console = Console()

CONFIG_FILE = Path.home() / ".git-auto-config.json"

DEFAULT_CONFIG = {
    "default_branch": "main",
    "default_commit_message": "Update files",
    "default_license": "MIT",
    "default_project_type": "python",
    "auto_push": False,
    "conventional_commits": False,
    "editor": "nano",
    "git_user_name": "",
    "git_user_email": "",
}


def load_config() -> Dict[str, Any]:
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        return {**DEFAULT_CONFIG, **config}
    except Exception as e:
        console.print(f"[yellow]Warning: Could not load config: {e}[/yellow]")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        console.print(f"[red]✗ Failed to save config: {e}[/red]")
        raise


def get_config(key: str) -> Optional[Any]:
    """Get a configuration value."""
    config = load_config()
    return config.get(key)


def set_config(key: str, value: str) -> None:
    """Set a configuration value."""
    config = load_config()
    
    # Type conversion - store as proper type
    converted_value: Union[str, bool, int] = value
    if value.lower() in ("true", "false"):
        converted_value = value.lower() == "true"
    elif value.isdigit():
        converted_value = int(value)
    
    config[key] = converted_value
    save_config(config)
    console.print(f"[green]✓ Set {key} = {converted_value}[/green]")


def list_config() -> None:
    """List all configuration values."""
    config = load_config()
    
    table = Table(title="Configuration", show_header=True)
    table.add_column("Key", style="cyan", width=30)
    table.add_column("Value", style="yellow")
    
    for key, value in sorted(config.items()):
        table.add_row(key, str(value))
    
    console.print(table)
    console.print(f"\n[dim]Config file: {CONFIG_FILE}[/dim]")


def reset_config() -> None:
    """Reset configuration to defaults."""
    save_config(DEFAULT_CONFIG)
    console.print("[green]✓ Configuration reset to defaults[/green]")


def get_default_branch() -> str:
    """Get default branch name."""
    return str(get_config("default_branch") or "main")


def get_default_license() -> str:
    """Get default license type."""
    return str(get_config("default_license") or "MIT")