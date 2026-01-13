"""gitignore generator."""

from typing import Optional
from rich.console import Console
import questionary

console = Console()


GITIGNORE_TEMPLATES = {
    "python": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Jupyter
.ipynb_checkpoints
""",
    
    "node": """# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.yarn-integrity

# Build
dist/
build/
*.tsbuildinfo

# Environment
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDEs
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Testing
coverage/
.nyc_output

# Logs
logs
*.log
""",
    
    "web": """# Dependencies
node_modules/

# Build
dist/
build/
*.map

# Environment
.env
.env.local

# IDEs
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
""",
}


def generate_gitignore(template: Optional[str] = None) -> None:
    """Generate .gitignore file."""
    console.print("[bold cyan]🚫 Generating .gitignore[/bold cyan]\n")
    
    if not template:
        template = questionary.select(
            "Select template:",
            choices=list(GITIGNORE_TEMPLATES.keys()) + ["Custom"]
        ).ask()
    
    if template == "Custom":
        patterns = questionary.text(
            "Enter patterns (comma-separated):",
            default="*.log, .env, node_modules/"
        ).ask()
        content = "\n".join(p.strip() for p in patterns.split(","))
    else:
        content = GITIGNORE_TEMPLATES.get(
            template if template else "python",
            ""
        ) 
    
    with open(".gitignore", "w") as f:
        f.write(content)
    
    console.print("[green]✓ .gitignore generated[/green]")
