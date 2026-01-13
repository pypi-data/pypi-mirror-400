"""README.md generator."""

from pathlib import Path
from typing import Optional
from rich.console import Console
import questionary

console = Console()


README_TEMPLATE = """# {title}

{description}

## Features

{features}

## Installation

```bash
{installation}
```

## Usage

{usage}

## Screenshots

{screenshots}

## Contributing

{contributing}

## License

This project is licensed under the {license} License - see the [LICENSE](LICENSE) file for details.

## Contact

{contact}
"""


def generate_readme(interactive: bool = True, output: str = "README.md") -> None:
    """Generate professional README.md."""
    console.print("[bold cyan]📝 Generating README.md[/bold cyan]\n")
    
    if interactive:
        title = questionary.text("Project title:", default="My Awesome Project").ask()
        description = questionary.text(
            "Project description:",
            default="A brief description of what this project does"
        ).ask()
        
        features = questionary.text(
            "Key features (comma-separated):",
            default="Feature 1, Feature 2, Feature 3"
        ).ask()
        features_list = "\n".join(f"- {f.strip()}" for f in features.split(","))
        
        installation = questionary.text(
            "Installation command:",
            default="pip install project-name"
        ).ask()
        
        usage = questionary.text(
            "Usage example:",
            default="from project import main\nmain()"
        ).ask()
        
        license_type = questionary.select(
            "License:",
            choices=["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "Other"]
        ).ask()
        
        contact = questionary.text(
            "Contact information:",
            default="Your Name - [@yourhandle](https://twitter.com/yourhandle)"
        ).ask()
    else:
        # Default values for non-interactive mode
        title = Path.cwd().name.replace("-", " ").replace("_", " ").title()
        description = "A brief description of this project"
        features_list = "- Feature 1\n- Feature 2\n- Feature 3"
        installation = "pip install package-name"
        usage = "```python\nimport package\n```"
        license_type = "MIT"
        contact = "Your Name - your.email@example.com"
    
    readme_content = README_TEMPLATE.format(
        title=title if interactive else title,
        description=description,
        features=features_list,
        installation=installation,
        usage=usage if interactive else usage,
        screenshots="Add screenshots here",
        contributing="Contributions are welcome! Please feel free to submit a Pull Request.",
        license=license_type,
        contact=contact,
    )
    
    with open(output, "w") as f:
        f.write(readme_content)
    
    console.print(f"[green]✓ README.md generated: {output}[/green]")

