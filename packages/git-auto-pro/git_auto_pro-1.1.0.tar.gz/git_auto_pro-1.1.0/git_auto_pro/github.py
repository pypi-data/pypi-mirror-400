"""GitHub API integration module."""

import requests
import keyring
from pathlib import Path
import json
from typing import Optional, List, Dict
from rich.console import Console
from rich.prompt import Prompt, Confirm
import questionary

console = Console()

SERVICE_NAME = "git-auto-pro"
TOKEN_KEY = "github-token"


TOKEN_FILE = Path.home() / ".git-auto-token.json"


def _use_file_storage() -> bool:
    """Check if we should use file-based storage."""
    try:

        keyring.get_keyring()

        test_service = "git-auto-test"
        try:
            keyring.set_password(test_service, "test", "test")
            keyring.delete_password(test_service, "test")
            return False
        except Exception:
            return True
    except Exception:
        return True


def get_stored_token() -> Optional[str]:
    """Retrieve stored GitHub token from keyring or file."""

    if not _use_file_storage():
        try:
            token = keyring.get_password(SERVICE_NAME, TOKEN_KEY)
            if token:
                return token
        except Exception as e:
            console.print(f"[yellow]Warning: Keyring access failed: {e}[/yellow]")
    

    if TOKEN_FILE.exists():
        try:
            data = json.loads(TOKEN_FILE.read_text())
            return data.get("token")
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read token file: {e}[/yellow]")
    
    return None


def store_token(token: str) -> None:
    """Store GitHub token in keyring or file."""
    use_file = _use_file_storage()
    
    if use_file:

        console.print("[yellow]⚠️  Keyring not available, using file-based storage[/yellow]")
        console.print(f"[dim]Token will be stored in: {TOKEN_FILE}[/dim]")
        
        try:
            TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = {"token": token}
            TOKEN_FILE.write_text(json.dumps(data, indent=2))

            try:
                TOKEN_FILE.chmod(0o600)
            except Exception:
                pass
            console.print("[green]✓ Token stored securely in file[/green]")
        except Exception as e:
            console.print(f"[red]✗ Failed to store token: {e}[/red]")
            raise
    else:

        try:
            keyring.set_password(SERVICE_NAME, TOKEN_KEY, token)
            console.print("[green]✓ Token stored securely in keyring[/green]")
        except Exception as e:
            console.print(f"[red]✗ Failed to store token in keyring: {e}[/red]")

            console.print("[yellow]Falling back to file storage...[/yellow]")
            TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = {"token": token}
            TOKEN_FILE.write_text(json.dumps(data, indent=2))
            try:
                TOKEN_FILE.chmod(0o600)
            except Exception:
                pass
            console.print("[green]✓ Token stored in file[/green]")


def validate_token(token: str) -> bool:
    """Validate GitHub token using API."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get("https://api.github.com/user", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            console.print(f"[green]✓ Authenticated as: {user_data['login']}[/green]")
            return True
        else:
            console.print(f"[red]✗ Invalid token: {response.status_code}[/red]")
            return False
    except Exception as e:
        console.print(f"[red]✗ Validation failed: {e}[/red]")
        return False


def login_github(token: Optional[str] = None) -> None:
    """Login to GitHub using Personal Access Token."""
    console.print("[bold cyan]🔐 GitHub Authentication[/bold cyan]\n")
    
    if not token:
        console.print("To create a token, visit: https://github.com/settings/tokens")
        console.print("Required scopes: repo, workflow, admin:org\n")
        token = Prompt.ask("Enter your GitHub Personal Access Token", password=True)
    
    if not token:
        console.print("[red]✗ No token provided[/red]")
        return
    
    if validate_token(token):
        store_token(token)
        console.print("[bold green]✓ Login successful![/bold green]")
    else:
        console.print("[red]✗ Login failed[/red]")


def get_authenticated_session() -> requests.Session:
    """Get authenticated requests session."""
    token = get_stored_token()
    if not token:
        console.print("[red]✗ Not authenticated. Run 'git-auto login' first.[/red]")
        raise ValueError("Not authenticated")
    
    session = requests.Session()
    session.headers.update({
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    })
    return session


def get_current_user() -> Dict:
    """Get current authenticated user information."""
    session = get_authenticated_session()
    response = session.get("https://api.github.com/user")
    response.raise_for_status()
    return response.json()


def create_github_repo(
    name: str,
    private: bool = False,
    description: Optional[str] = None,
    homepage: Optional[str] = None,
    topics: Optional[List[str]] = None,
    auto_init: bool = False,
) -> Dict:
    """Create a new GitHub repository."""
    console.print(f"[bold cyan]📦 Creating repository: {name}[/bold cyan]\n")
    
    session = get_authenticated_session()
    user = get_current_user()
    
    data = {
        "name": name,
        "private": private,
        "auto_init": auto_init,
    }
    
    if description:
        data["description"] = description
    if homepage:
        data["homepage"] = homepage
    
    try:
        response = session.post("https://api.github.com/user/repos", json=data)
        response.raise_for_status()
        repo_data = response.json()
        
        console.print(f"[green]✓ Repository created: {repo_data['html_url']}[/green]")
        

        if topics:
            topics_response = session.put(
                f"https://api.github.com/repos/{user['login']}/{name}/topics",
                json={"names": topics},
                headers={"Accept": "application/vnd.github.mercy-preview+json"}
            )
            if topics_response.status_code == 200:
                console.print(f"[green]✓ Topics added: {', '.join(topics)}[/green]")
        
        return repo_data
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            console.print(f"[red]✗ Repository '{name}' already exists[/red]")
        else:
            console.print(f"[red]✗ Failed to create repository: {e}[/red]")
        raise


def add_collaborator(
    username: str,
    repo: Optional[str] = None,
    permission: str = "push"
) -> None:
    """Add a collaborator to a repository."""
    session = get_authenticated_session()
    user = get_current_user()
    
    if not repo:

        import git
        try:
            repo_obj = git.Repo(".")

            remotes = getattr(repo_obj, 'remotes')
            origin = getattr(remotes, 'origin')
            remote_url = origin.url
            repo = remote_url.split("/")[-1].replace(".git", "")
        except:
            console.print("[red]✗ Could not detect repository. Use --repo option.[/red]")
            return
    
    console.print(f"[cyan]Adding {username} as collaborator to {repo}...[/cyan]")
    
    try:
        response = session.put(
            f"https://api.github.com/repos/{user['login']}/{repo}/collaborators/{username}",
            json={"permission": permission}
        )
        response.raise_for_status()
        console.print(f"[green]✓ Collaborator added: {username} ({permission})[/green]")
    except Exception as e:
        console.print(f"[red]✗ Failed to add collaborator: {e}[/red]")


def protect_branch(
    branch: str = "main",
    repo: Optional[str] = None
) -> None:
    """Setup branch protection rules."""
    session = get_authenticated_session()
    user = get_current_user()
    
    if not repo:

        import git
        try:
            repo_obj = git.Repo(".")

            remotes = getattr(repo_obj, 'remotes')
            origin = getattr(remotes, 'origin')
            remote_url = origin.url
            repo = remote_url.split("/")[-1].replace(".git", "")
        except:
            console.print("[red]✗ Could not detect repository. Use --repo option.[/red]")
            return
    
    console.print(f"[cyan]Setting up protection for branch '{branch}'...[/cyan]")
    
    protection_data = {
        "required_status_checks": None,
        "enforce_admins": False,
        "required_pull_request_reviews": {
            "dismissal_restrictions": {},
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": False,
            "required_approving_review_count": 1
        },
        "restrictions": None
    }
    
    try:
        response = session.put(
            f"https://api.github.com/repos/{user['login']}/{repo}/branches/{branch}/protection",
            json=protection_data,
            headers={"Accept": "application/vnd.github.luke-cage-preview+json"}
        )
        response.raise_for_status()
        console.print(f"[green]✓ Branch protection enabled for '{branch}'[/green]")
    except Exception as e:
        console.print(f"[red]✗ Failed to protect branch: {e}[/red]")


def clear_stored_token() -> None:
    """Clear stored token (for logout/reset)."""

    if not _use_file_storage():
        try:
            keyring.delete_password(SERVICE_NAME, TOKEN_KEY)
            console.print("[green]✓ Token cleared from keyring[/green]")
            return
        except Exception:
            pass
    

    if TOKEN_FILE.exists():
        try:
            TOKEN_FILE.unlink()
            console.print("[green]✓ Token cleared from file[/green]")
        except Exception as e:
            console.print(f"[red]✗ Failed to clear token: {e}[/red]")