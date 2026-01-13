"""Git command operations using GitPython."""

import git
from typing import Optional, List, Any
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime
import questionary

console = Console()


def get_repo() -> git.Repo:
    """Get current Git repository."""
    try:
        return git.Repo(".", search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        console.print("[red]✗ Not a git repository. Run 'git-auto init' first.[/red]")
        raise


def git_init(connect: Optional[str] = None) -> None:
    """Initialize Git repository and optionally connect to remote."""
    try:
        repo_exists = Path(".git").exists()
        
        if repo_exists:
            console.print("[yellow]Repository already initialized[/yellow]")
            repo = git.Repo(".")
        else:
            repo = git.Repo.init(".")
            console.print("[green]✓ Initialized empty Git repository[/green]")
        
        # Add remote even if repo already exists (FIXED!)
        if connect:
            try:
                # Check if remote already exists
                remotes = {remote.name: remote for remote in repo.remotes}
                
                if "origin" in remotes:
                    # Remote exists, check if URL is different
                    existing_url = remotes["origin"].url
                    if existing_url == connect:
                        console.print(f"[yellow]Remote 'origin' already set to: {connect}[/yellow]")
                    else:
                        # Update the URL
                        remotes["origin"].set_url(connect)
                        console.print(f"[green]✓ Updated remote 'origin' to: {connect}[/green]")
                else:
                    # Add new remote
                    repo.create_remote("origin", connect)
                    console.print(f"[green]✓ Added remote 'origin': {connect}[/green]")
                    
            except Exception as e:
                console.print(f"[red]✗ Failed to configure remote: {e}[/red]")
                raise
            
    except Exception as e:
        console.print(f"[red]✗ Failed to initialize repository: {e}[/red]")
        raise


def git_add(files: Optional[List[str]] = None, all: bool = False) -> None:
    """Stage files for commit."""
    try:
        repo = get_repo()
        
        if all or not files:
            # Use getattr to avoid type errors
            git_cmd = getattr(repo, 'git')
            git_cmd.add(A=True)
            console.print("[green]✓ Staged all changes[/green]")
        else:
            repo.index.add(files)
            console.print(f"[green]✓ Staged: {', '.join(files)}[/green]")
            
    except Exception as e:
        console.print(f"[red]✗ Failed to stage files: {e}[/red]")


def git_commit(message: str, conventional: bool = False, amend: bool = False) -> None:
    """Commit staged changes."""
    try:
        repo = get_repo()
        
        if conventional:
            commit_type = questionary.select(
                "Select commit type:",
                choices=[
                    "feat: A new feature",
                    "fix: A bug fix",
                    "docs: Documentation changes",
                    "style: Code style changes",
                    "refactor: Code refactoring",
                    "test: Adding tests",
                    "chore: Maintenance tasks",
                ]
            ).ask()
            
            if commit_type:
                prefix = commit_type.split(":")[0]
                message = f"{prefix}: {message}"
        
        if amend:
            git_cmd = getattr(repo, 'git')
            git_cmd.commit("--amend", "-m", message)
            console.print("[green]✓ Amended previous commit[/green]")
        else:
            repo.index.commit(message)
            console.print(f"[green]✓ Committed: {message}[/green]")
            
    except Exception as e:
        console.print(f"[red]✗ Failed to commit: {e}[/red]")


def git_push(message: Optional[str] = None, branch: str = "main", force: bool = False) -> None:
    """Push commits to remote."""
    try:
        repo = get_repo()
        git_cmd = getattr(repo, 'git')
        
        # If message provided, do add + commit + push
        if message:
            git_cmd.add(A=True)
            repo.index.commit(message)
            console.print(f"[green]✓ Committed: {message}[/green]")
        
        # Check if remote exists
        if not repo.remotes:
            console.print("[red]✗ No remote configured. Use 'git-auto init --connect <url>' first.[/red]")
            return
        
        # Push to remote
        if force:
            git_cmd.push("origin", branch, force=True)
            console.print(f"[yellow]⚠ Force pushed to {branch}[/yellow]")
        else:
            git_cmd.push("origin", branch)
            console.print(f"[green]✓ Pushed to {branch}[/green]")
            
    except Exception as e:
        console.print(f"[red]✗ Failed to push: {e}[/red]")
        console.print("[yellow]Hint: Make sure remote is configured with 'git-auto init --connect <url>'[/yellow]")


def git_pull(
    branch: Optional[str] = None, 
    rebase: bool = False,
    no_rebase: bool = False,
    ff_only: bool = False
) -> None:
    """Pull changes from remote with configurable merge strategy."""
    try:
        repo = get_repo()
        git_cmd = getattr(repo, 'git')
        
        pull_args = []
        if branch:
            pull_args.extend(["origin", branch])
        
        if rebase:
            pull_args.append("--rebase")
        elif no_rebase:
            pull_args.append("--no-rebase")
        elif ff_only:
            pull_args.append("--ff-only")
        else:
            pull_args.append("--no-rebase")
        
        git_cmd.pull(*pull_args)
        console.print("[green]✓ Pulled changes from remote[/green]")
        
    except git.GitCommandError as e:
        error_msg = str(e)
        
        if "divergent branches" in error_msg or "Need to specify how to reconcile" in error_msg:
            console.print("[red]✗ Branches have diverged[/red]")
            console.print("\n[yellow]Choose a reconciliation strategy:[/yellow]")
            console.print("  [cyan]git-auto pull --rebase[/cyan]      # Rebase your changes on top of remote")
            console.print("  [cyan]git-auto pull --no-rebase[/cyan]   # Merge remote changes (default)")
            console.print("  [cyan]git-auto pull --ff-only[/cyan]     # Only fast-forward (fails if not possible)")
        else:
            console.print(f"[red]✗ Failed to pull: {e}[/red]")
    except Exception as e:
        console.print(f"[red]✗ Failed to pull: {e}[/red]")


def git_status(short: bool = False) -> None:
    """Show working tree status."""
    try:
        repo = get_repo()
        git_cmd = getattr(repo, 'git')
        
        if short:
            status = git_cmd.status("-s")
            console.print(status)
        else:
            # Custom formatted status
            changed = [item.a_path for item in repo.index.diff(None)]
            staged = [item.a_path for item in repo.index.diff("HEAD")]
            untracked = repo.untracked_files
            
            table = Table(title="Repository Status", show_header=True)
            table.add_column("Status", style="cyan")
            table.add_column("Files", style="white")
            
            if staged:
                table.add_row("Staged", "\n".join(f"✓ {f}" for f in staged))
            if changed:
                table.add_row("Modified", "\n".join(f"M {f}" for f in changed))
            if untracked:
                table.add_row("Untracked", "\n".join(f"? {f}" for f in untracked))
            
            if not (staged or changed or untracked):
                console.print("[green]✓ Working tree clean[/green]")
            else:
                console.print(table)
                
    except Exception as e:
        console.print(f"[red]✗ Failed to get status: {e}[/red]")


def git_log(limit: int = 10, oneline: bool = False, graph: bool = False) -> None:
    """Show commit history."""
    try:
        repo = get_repo()
        git_cmd = getattr(repo, 'git')
        
        if oneline:
            log = git_cmd.log(f"--oneline", f"-{limit}")
            console.print(log)
        elif graph:
            log = git_cmd.log(f"--graph", f"--oneline", f"-{limit}")
            console.print(log)
        else:
            table = Table(title=f"Last {limit} Commits", show_header=True)
            table.add_column("Hash", style="yellow", width=8)
            table.add_column("Author", style="cyan", width=20)
            table.add_column("Date", style="green", width=20)
            table.add_column("Message", style="white")
            
            for commit in list(repo.iter_commits())[:limit]:
                date = datetime.fromtimestamp(commit.committed_date).strftime("%Y-%m-%d %H:%M")
                # Convert all fields to strings explicitly
                hash_str = str(commit.hexsha[:8])
                author_str = str(commit.author.name)
                date_str = str(date)
                message_str = str(commit.message.strip())
                
                table.add_row(hash_str, author_str, date_str, message_str)
            
            console.print(table)
            
    except Exception as e:
        console.print(f"[red]✗ Failed to show log: {e}[/red]")


def git_branch(name: Optional[str] = None, list: bool = False, remote: bool = False) -> None:
    """Create or list branches."""
    try:
        repo = get_repo()
        git_cmd = getattr(repo, 'git')
        
        if list or not name:
            branches_output = git_cmd.branch("-r" if remote else "-a")
            branches = branches_output.split("\n")
            
            table = Table(title="Branches", show_header=False)
            table.add_column("Branch", style="cyan")
            
            for branch in branches:
                branch = branch.strip()
                if branch.startswith("*"):
                    table.add_row(f"[bold green]{branch}[/bold green]")
                else:
                    table.add_row(branch)
            
            console.print(table)
        else:
            repo.create_head(name)
            console.print(f"[green]✓ Created branch: {name}[/green]")
            
    except Exception as e:
        console.print(f"[red]✗ Failed to manage branches: {e}[/red]")


def git_switch(name: str, create: bool = False) -> None:
    """Switch to a different branch."""
    try:
        repo = get_repo()
        git_cmd = getattr(repo, 'git')
        
        if create:
            git_cmd.checkout("-b", name)
            console.print(f"[green]✓ Created and switched to: {name}[/green]")
        else:
            git_cmd.checkout(name)
            console.print(f"[green]✓ Switched to: {name}[/green]")
            
    except Exception as e:
        console.print(f"[red]✗ Failed to switch branch: {e}[/red]")


def git_delete_branch(name: str, force: bool = False) -> None:
    """Delete a branch."""
    try:
        repo = get_repo()
        git_cmd = getattr(repo, 'git')
        
        if force:
            git_cmd.branch("-D", name)
        else:
            git_cmd.branch("-d", name)
        
        console.print(f"[green]✓ Deleted branch: {name}[/green]")
        
    except Exception as e:
        console.print(f"[red]✗ Failed to delete branch: {e}[/red]")


def git_stash(message: Optional[str] = None, list: bool = False) -> None:
    """Stash uncommitted changes."""
    try:
        repo = get_repo()
        git_cmd = getattr(repo, 'git')
        
        if list:
            stash_list = git_cmd.stash("list")
            stashes = stash_list.split("\n") if stash_list else []
            if stashes:
                table = Table(title="Stashes", show_header=True)
                table.add_column("Index", style="yellow", width=8)
                table.add_column("Message", style="white")
                
                for i, stash in enumerate(stashes):
                    table.add_row(str(i), stash)
                
                console.print(table)
            else:
                console.print("[yellow]No stashes found[/yellow]")
        else:
            if message:
                git_cmd.stash("push", "-m", message)
            else:
                git_cmd.stash()
            console.print("[green]✓ Changes stashed[/green]")
            
    except Exception as e:
        console.print(f"[red]✗ Failed to stash: {e}[/red]")


def git_stash_apply(index: int = 0, pop: bool = False) -> None:
    """Apply stashed changes."""
    try:
        repo = get_repo()
        git_cmd = getattr(repo, 'git')
        
        if pop:
            git_cmd.stash("pop", f"stash@{{{index}}}")
            console.print(f"[green]✓ Applied and removed stash {index}[/green]")
        else:
            git_cmd.stash("apply", f"stash@{{{index}}}")
            console.print(f"[green]✓ Applied stash {index}[/green]")
            
    except Exception as e:
        console.print(f"[red]✗ Failed to apply stash: {e}[/red]")


def git_merge(branch: str, no_ff: bool = False, squash: bool = False) -> None:
    """Merge branches."""
    try:
        repo = get_repo()
        git_cmd = getattr(repo, 'git')
        
        if squash:
            git_cmd.merge(branch, squash=True)
            console.print(f"[green]✓ Squash merged: {branch}[/green]")
        elif no_ff:
            git_cmd.merge(branch, no_ff=True)
            console.print(f"[green]✓ Merged (no fast-forward): {branch}[/green]")
        else:
            git_cmd.merge(branch)
            console.print(f"[green]✓ Merged: {branch}[/green]")
            
    except Exception as e:
        console.print(f"[red]✗ Failed to merge: {e}[/red]")


def git_clone(url: str, directory: Optional[str] = None, depth: Optional[int] = None) -> None:
    """Clone a repository."""
    try:
        kwargs: dict[str, Any] = {}
        if depth:
            kwargs["depth"] = depth
        
        target = directory if directory else url.split("/")[-1].replace(".git", "")
        
        git.Repo.clone_from(url, target, **kwargs)
        console.print(f"[green]✓ Cloned to: {target}[/green]")
        
    except Exception as e:
        console.print(f"[red]✗ Failed to clone: {e}[/red]")


def git_stats(detailed: bool = False) -> None:
    """Show repository statistics."""
    try:
        repo = get_repo()
        
        # Basic stats
        commits = list(repo.iter_commits())
        branches = list(repo.branches)
        contributors: dict[str, int] = {}
        
        for commit in commits:
            author = str(commit.author.name)
            contributors[author] = contributors.get(author, 0) + 1
        
        table = Table(title="Repository Statistics", show_header=True)
        table.add_column("Metric", style="cyan", width=25)
        table.add_column("Value", style="yellow")
        
        table.add_row("Total Commits", str(len(commits)))
        table.add_row("Total Branches", str(len(branches)))
        table.add_row("Contributors", str(len(contributors)))
        table.add_row("Current Branch", str(repo.active_branch))
        
        console.print(table)
        
        if detailed:
            # Top contributors
            contrib_table = Table(title="Top Contributors", show_header=True)
            contrib_table.add_column("Author", style="cyan")
            contrib_table.add_column("Commits", style="yellow")
            
            sorted_contributors = sorted(contributors.items(), key=lambda x: x[1], reverse=True)
            for author, count in sorted_contributors[:10]:
                contrib_table.add_row(author, str(count))
            
            console.print("\n", contrib_table)
            
    except Exception as e:
        console.print(f"[red]✗ Failed to get stats: {e}[/red]")