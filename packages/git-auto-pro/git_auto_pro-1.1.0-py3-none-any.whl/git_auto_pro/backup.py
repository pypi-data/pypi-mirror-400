"""Repository backup and restore module."""

import shutil
import tarfile
from pathlib import Path
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def create_backup(output: Optional[str] = None) -> None:
    """Create repository backup."""
    console.print("[bold cyan]💾 Creating repository backup[/bold cyan]\n")
    
    try:
        # Get repository name
        repo_name = Path.cwd().name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if not output:
            output = f"{repo_name}_backup_{timestamp}.tar.gz"
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating backup...", total=None)
            
            # Create tar archive
            with tarfile.open(output, "w:gz") as tar:

                for item in Path.cwd().iterdir():
                    if item.name != ".git":
                        tar.add(item, arcname=item.name)
                

                git_dir = Path(".git")
                if git_dir.exists():
                    for item in ["config", "HEAD", "refs", "hooks"]:
                        git_item = git_dir / item
                        if git_item.exists():
                            tar.add(git_item, arcname=f".git/{item}")
            
            progress.update(task, description="Backup complete!")
        
        backup_size = Path(output).stat().st_size / (1024 * 1024)  # MB
        console.print(f"[green]✓ Backup created: {output}[/green]")
        console.print(f"[cyan]Size: {backup_size:.2f} MB[/cyan]")
        
    except Exception as e:
        console.print(f"[red]✗ Backup failed: {e}[/red]")


def restore_backup(backup_path: str) -> None:
    """Restore from backup."""
    console.print(f"[bold cyan]♻️ Restoring from backup: {backup_path}[/bold cyan]\n")
    
    if not Path(backup_path).exists():
        console.print(f"[red]✗ Backup file not found: {backup_path}[/red]")
        return
    
    try:
        # Create restore directory
        restore_dir = Path.cwd() / "restored"
        restore_dir.mkdir(exist_ok=True)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Extracting backup...", total=None)
            
            # Extract tar archive
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(restore_dir)
            
            progress.update(task, description="Restore complete!")
        
        console.print(f"[green]✓ Backup restored to: {restore_dir}[/green]")
        
    except Exception as e:
        console.print(f"[red]✗ Restore failed: {e}[/red]")