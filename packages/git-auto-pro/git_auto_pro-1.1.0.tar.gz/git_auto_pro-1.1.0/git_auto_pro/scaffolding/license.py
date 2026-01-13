"""LICENSE generator."""

from datetime import datetime
from typing import Optional
from rich.console import Console
import questionary

console = Console()


LICENSE_TEMPLATES = {
    "MIT": """MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",
    
    "Apache-2.0": """Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Copyright {year} {author}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
""",
    
    "GPL-3.0": """GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) {year} {author}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
""",
}


def generate_license(
    type: Optional[str] = None,
    author: Optional[str] = None,
    year: Optional[int] = None,
) -> None:
    """Generate LICENSE file."""
    console.print("[bold cyan]⚖️ Generating LICENSE[/bold cyan]\n")
    
    if not type:
        type = questionary.select(
            "Select license type:",
            choices=list(LICENSE_TEMPLATES.keys()) + ["Custom"]
        ).ask()
    
    if type == "Custom":
        console.print("[yellow]Please create your custom LICENSE file manually[/yellow]")
        return
    
    if not author:
        author = questionary.text("Author name:", default="Your Name").ask()
    
    if not year:
        year = datetime.now().year
    
    license_template = LICENSE_TEMPLATES.get(
        type if type else "MIT",
        LICENSE_TEMPLATES["MIT"]
    )
    license_content = license_template.format(year=year, author=author)
    
    with open("LICENSE", "w") as f:
        f.write(license_content)
    
    console.print(f"[green]✓ LICENSE generated: {type}[/green]")

