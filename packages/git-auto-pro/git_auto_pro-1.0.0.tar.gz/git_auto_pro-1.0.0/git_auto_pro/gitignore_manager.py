
"""Interactive .gitignore file manager."""

from pathlib import Path
from typing import List, Set
import questionary
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

console = Console()


def get_all_files(directory: Path = Path("."), max_depth: int = 3) -> List[Path]:
    """Get all files in directory recursively."""
    all_files = []
    
    def scan_dir(path: Path, depth: int = 0):
        if depth > max_depth:
            return
        
        try:
            for item in path.iterdir():
                # Skip .git directory
                if item.name == ".git":
                    continue
                    
                if item.is_file():
                    all_files.append(item.relative_to(directory))
                elif item.is_dir():
                    scan_dir(item, depth + 1)
        except PermissionError:
            pass
    
    scan_dir(directory)
    return sorted(all_files)


def load_gitignore() -> Set[str]:
    """Load existing .gitignore patterns."""
    gitignore_file = Path(".gitignore")
    if not gitignore_file.exists():
        return set()
    
    patterns = set()
    with open(gitignore_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.add(line)
    
    return patterns


def save_gitignore(patterns: Set[str]) -> None:
    """Save .gitignore patterns."""
    gitignore_file = Path(".gitignore")
    
    # Read existing content to preserve comments
    existing_content = ""
    if gitignore_file.exists():
        with open(gitignore_file, "r") as f:
            existing_content = f.read()
    
    # Write new patterns
    with open(gitignore_file, "w") as f:
        # Keep header comments if they exist
        if existing_content and existing_content.startswith("#"):
            lines = existing_content.split("\n")
            for line in lines:
                if line.startswith("#"):
                    f.write(line + "\n")
                else:
                    break
            f.write("\n")
        
        # Write patterns
        for pattern in sorted(patterns):
            f.write(pattern + "\n")
    
    console.print(f"[green]✓ Saved {len(patterns)} patterns to .gitignore[/green]")


def display_file_tree(files: List[Path], ignored: Set[str]) -> None:
    """Display files in a tree structure."""
    tree = Tree("📁 Project Files")
    
    # Group by directory
    dirs = {}
    for file in files[:50]:  # Limit to first 50 for display
        parts = file.parts
        if len(parts) == 1:

            status = "🚫" if should_ignore(file, ignored) else "✅"
            tree.add(f"{status} {file}")
        else:
            # File in directory
            dir_name = parts[0]
            if dir_name not in dirs:
                dirs[dir_name] = tree.add(f"📂 {dir_name}/")
            
            status = "🚫" if should_ignore(file, ignored) else "✅"
            dirs[dir_name].add(f"{status} {'/'.join(parts[1:])}")
    
    console.print(tree)


def should_ignore(file: Path, patterns: Set[str]) -> bool:
    """Check if file matches any ignore pattern."""
    file_str = str(file)
    
    for pattern in patterns:
        # Simple pattern matching
        if pattern.endswith("/"):
            # Directory pattern
            if file_str.startswith(pattern.rstrip("/")):
                return True
        elif pattern.startswith("*"):
            # Extension pattern
            if file_str.endswith(pattern[1:]):
                return True
        elif pattern in file_str:

            return True
    
    return False


def interactive_gitignore_manager() -> None:
    """Interactive .gitignore file manager."""
    console.print("[bold cyan]📝 Interactive .gitignore Manager[/bold cyan]\n")
    
    # Load existing patterns
    ignored_patterns = load_gitignore()
    console.print(f"Loaded {len(ignored_patterns)} existing patterns\n")
    
    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "📋 View all files (with ignore status)",
                "➕ Add files/patterns to ignore",
                "➖ Remove patterns from ignore",
                "🎯 Browse and select files to ignore",
                "📊 Show current .gitignore",
                "🧹 Clean: Remove ignored files from git",
                "💾 Save and exit",
                "❌ Exit without saving",
            ]
        ).ask()
        
        if not choice:
            break
        
        if "View all files" in choice:
            view_files_with_status(ignored_patterns)
        
        elif "Add files/patterns" in choice:
            add_patterns(ignored_patterns)
        
        elif "Remove patterns" in choice:
            remove_patterns(ignored_patterns)
        
        elif "Browse and select" in choice:
            browse_and_select(ignored_patterns)
        
        elif "Show current" in choice:
            show_current_gitignore(ignored_patterns)
        
        elif "Clean: Remove" in choice:
            clean_ignored_files()
        
        elif "Save and exit" in choice:
            save_gitignore(ignored_patterns)
            console.print("[bold green]✓ Changes saved![/bold green]")
            break
        
        elif "Exit without saving" in choice:
            confirm = questionary.confirm("Exit without saving changes?").ask()
            if confirm:
                console.print("[yellow]Changes discarded[/yellow]")
                break


def view_files_with_status(ignored: Set[str]) -> None:
    """View all files with their ignore status."""
    console.print("\n[cyan]📁 Project Files:[/cyan]\n")
    
    files = get_all_files()
    
    if not files:
        console.print("[yellow]No files found[/yellow]")
        return
    
    table = Table(show_header=True)
    table.add_column("Status", style="cyan", width=8)
    table.add_column("File", style="white")
    table.add_column("Reason", style="dim")
    
    for file in files[:100]:  # Limit to 100 files
        if should_ignore(file, ignored):
            status = "🚫 Ignored"
            reason = get_ignore_reason(file, ignored)
        else:
            status = "✅ Tracked"
            reason = ""
        
        table.add_row(status, str(file), reason)
    
    console.print(table)
    
    if len(files) > 100:
        console.print(f"\n[dim]... and {len(files) - 100} more files[/dim]")
    
    input("\nPress Enter to continue...")


def get_ignore_reason(file: Path, patterns: Set[str]) -> str:
    """Get the pattern that causes file to be ignored."""
    file_str = str(file)
    
    for pattern in patterns:
        if pattern.endswith("/") and file_str.startswith(pattern.rstrip("/")):
            return f"matches: {pattern}"
        elif pattern.startswith("*") and file_str.endswith(pattern[1:]):
            return f"matches: {pattern}"
        elif pattern in file_str:
            return f"matches: {pattern}"
    
    return ""


def add_patterns(ignored: Set[str]) -> None:
    """Add new patterns to ignore."""
    console.print("\n[cyan]➕ Add Patterns to .gitignore[/cyan]\n")
    
    pattern_type = questionary.select(
        "What would you like to add?",
        choices=[
            "📁 Folder (e.g., node_modules/)",
            "📄 File extension (e.g., *.pyc)",
            "📝 Specific file (e.g., config.local.py)",
            "🎯 Custom pattern",
            "📦 Common presets (Python, Node, etc.)",
        ]
    ).ask()
    
    if "Folder" in pattern_type:
        folder = questionary.text("Folder name (will add trailing /):").ask()
        if folder:
            pattern = folder if folder.endswith("/") else folder + "/"
            ignored.add(pattern)
            console.print(f"[green]✓ Added: {pattern}[/green]")
    
    elif "File extension" in pattern_type:
        ext = questionary.text("Extension (e.g., pyc, log):").ask()
        if ext:
            pattern = f"*.{ext}" if not ext.startswith("*.") else ext
            ignored.add(pattern)
            console.print(f"[green]✓ Added: {pattern}[/green]")
    
    elif "Specific file" in pattern_type:
        filename = questionary.text("File name or path:").ask()
        if filename:
            ignored.add(filename)
            console.print(f"[green]✓ Added: {filename}[/green]")
    
    elif "Custom pattern" in pattern_type:
        pattern = questionary.text("Enter pattern:").ask()
        if pattern:
            ignored.add(pattern)
            console.print(f"[green]✓ Added: {pattern}[/green]")
    
    elif "Common presets" in pattern_type:
        add_preset(ignored)


def add_preset(ignored: Set[str]) -> None:
    """Add common preset patterns."""
    presets = {
        "Python": ["__pycache__/", "*.py[cod]", "*.so", ".Python", "*.egg-info/", 
                   "dist/", "build/", ".pytest_cache/", ".coverage", "venv/", "env/"],
        "Node.js": ["node_modules/", "npm-debug.log", "*.tsbuildinfo", "dist/", ".env"],
        "Build artifacts": ["*.o", "*.a", "*.lib", "*.dll", "*.exe", "*.out"],
        "IDEs": [".vscode/", ".idea/", "*.swp", "*.swo", ".DS_Store"],
        "Logs": ["*.log", "logs/"],
    }
    
    preset = questionary.select(
        "Select preset:",
        choices=list(presets.keys())
    ).ask()
    
    if preset:
        patterns = presets[preset]
        for pattern in patterns:
            ignored.add(pattern)
        console.print(f"[green]✓ Added {len(patterns)} patterns from {preset} preset[/green]")


def remove_patterns(ignored: Set[str]) -> None:
    """Remove patterns from ignore list."""
    if not ignored:
        console.print("[yellow]No patterns to remove[/yellow]")
        return
    
    patterns_to_remove = questionary.checkbox(
        "Select patterns to remove:",
        choices=sorted(ignored)
    ).ask()
    
    if patterns_to_remove:
        for pattern in patterns_to_remove:
            ignored.discard(pattern)
        console.print(f"[green]✓ Removed {len(patterns_to_remove)} patterns[/green]")


def browse_and_select(ignored: Set[str]) -> None:
    """Browse files and select which to ignore."""
    console.print("\n[cyan]🎯 Browse and Select Files[/cyan]\n")
    
    files = get_all_files()
    

    tracked_files = [f for f in files if not should_ignore(f, ignored)]
    
    if not tracked_files:
        console.print("[yellow]All files are already ignored[/yellow]")
        return
    
    # Show in groups
    file_choices = [str(f) for f in tracked_files[:200]]  # Limit to 200
    
    selected = questionary.checkbox(
        "Select files/folders to ignore:",
        choices=file_choices
    ).ask()
    
    if selected:
        for item in selected:
            ignored.add(item)
        console.print(f"[green]✓ Added {len(selected)} items to ignore[/green]")


def show_current_gitignore(ignored: Set[str]) -> None:
    """Show current .gitignore patterns."""
    console.print("\n[cyan]📊 Current .gitignore Patterns:[/cyan]\n")
    
    if not ignored:
        console.print("[yellow]No patterns defined[/yellow]")
    else:
        table = Table(show_header=True)
        table.add_column("#", style="dim", width=5)
        table.add_column("Pattern", style="cyan")
        table.add_column("Type", style="yellow")
        
        for i, pattern in enumerate(sorted(ignored), 1):
            if pattern.endswith("/"):
                ptype = "Folder"
            elif pattern.startswith("*"):
                ptype = "Extension"
            else:
                ptype = "File/Pattern"
            
            table.add_row(str(i), pattern, ptype)
        
        console.print(table)
    
    input("\nPress Enter to continue...")


def clean_ignored_files() -> None:
    """Remove ignored files from git tracking."""
    console.print("\n[yellow]⚠️  This will remove ignored files from git tracking[/yellow]")
    console.print("[dim]Files will remain on disk but won't be tracked[/dim]\n")
    
    confirm = questionary.confirm("Continue?").ask()
    
    if confirm:
        import subprocess
        try:

            result = subprocess.run(
                ["git", "rm", "-r", "--cached", "."],
                capture_output=True,
                text=True
            )
            
            # Re-add everything (respecting .gitignore)
            subprocess.run(["git", "add", "."])
            
            console.print("[green]✓ Cleaned ignored files from git[/green]")
            console.print("[dim]Run 'git-auto commit' to save changes[/dim]")
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")





