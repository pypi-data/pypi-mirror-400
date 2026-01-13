"""Project template generator."""

from pathlib import Path
from typing import Optional
from rich.console import Console

console = Console()


def generate_template(type: str, output: Optional[str] = None) -> None:
    """Generate project template structure."""
    console.print(f"[bold cyan]📋 Generating {type} template[/bold cyan]\n")
    
    base_path = Path(output) if output else Path(".")
    
    templates = {
        "python": generate_python_template,
        "node": generate_node_template,
        "cpp": generate_cpp_template,
        "web": generate_web_template,
        "rust": generate_rust_template,
        "go": generate_go_template,
    }
    
    generator = templates.get(type)
    if generator:
        generator(base_path)
        console.print(f"[green]✓ {type.title()} template generated[/green]")
    else:
        console.print(f"[red]✗ Unknown template type: {type}[/red]")


def generate_python_template(base_path: Path) -> None:
    """Generate Python project template."""
    # Create directory structure
    (base_path / "src").mkdir(exist_ok=True)
    (base_path / "tests").mkdir(exist_ok=True)
    (base_path / "docs").mkdir(exist_ok=True)
    
    # __init__.py
    (base_path / "src" / "__init__.py").write_text('"""Package initialization."""\n\n__version__ = "0.1.0"\n')
    
    # main.py
    (base_path / "src" / "main.py").write_text('''"""Main module."""


def main():
    """Main entry point."""
    print("Hello, World!")


if __name__ == "__main__":
    main()
''')
    
    # tests
    (base_path / "tests" / "__init__.py").write_text("")
    (base_path / "tests" / "test_main.py").write_text('''"""Tests for main module."""

import pytest
from src.main import main


def test_main():
    """Test main function."""
    main()  # Should not raise
''')
    
    # requirements.txt
    (base_path / "requirements.txt").write_text("# Add your dependencies here\n")
    
    # requirements-dev.txt
    (base_path / "requirements-dev.txt").write_text("""pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
ruff>=0.1.0
mypy>=1.5.0
""")
    
    # setup.py
    (base_path / "setup.py").write_text('''"""Setup script."""

from setuptools import setup, find_packages

setup(
    name="project-name",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.8",
)
''')


def generate_node_template(base_path: Path) -> None:
    """Generate Node.js project template."""
    # Create directory structure
    (base_path / "src").mkdir(exist_ok=True)
    (base_path / "tests").mkdir(exist_ok=True)
    (base_path / "public").mkdir(exist_ok=True)
    
    # package.json
    (base_path / "package.json").write_text('''{
  "name": "project-name",
  "version": "1.0.0",
  "description": "Project description",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "test": "jest",
    "dev": "nodemon src/index.js"
  },
  "keywords": [],
  "author": "",
  "license": "MIT",
  "devDependencies": {
    "jest": "^29.0.0",
    "nodemon": "^3.0.0"
  }
}
''')
    
    # index.js
    (base_path / "src" / "index.js").write_text('''/**
 * Main entry point
 */

function main() {
  console.log('Hello, World!');
}

main();

module.exports = { main };
''')
    
    # test
    (base_path / "tests" / "index.test.js").write_text('''const { main } = require('../src/index');

describe('Main', () => {
  test('should run without errors', () => {
    expect(() => main()).not.toThrow();
  });
});
''')


def generate_cpp_template(base_path: Path) -> None:
    """Generate C++ project template."""
    # Create directory structure
    (base_path / "src").mkdir(exist_ok=True)
    (base_path / "include").mkdir(exist_ok=True)
    (base_path / "tests").mkdir(exist_ok=True)
    (base_path / "build").mkdir(exist_ok=True)
    
    # main.cpp
    (base_path / "src" / "main.cpp").write_text('''#include <iostream>
#include "main.h"

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
''')
    
    # header
    (base_path / "include" / "main.h").write_text('''#ifndef MAIN_H
#define MAIN_H

// Function declarations

#endif // MAIN_H
''')
    
    # CMakeLists.txt
    (base_path / "CMakeLists.txt").write_text('''cmake_minimum_required(VERSION 3.10)
project(ProjectName)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

add_executable(${PROJECT_NAME} src/main.cpp)

# Tests
enable_testing()
add_subdirectory(tests)
''')


def generate_web_template(base_path: Path) -> None:
    """Generate basic web project template."""
    # Create directory structure
    (base_path / "css").mkdir(exist_ok=True)
    (base_path / "js").mkdir(exist_ok=True)
    (base_path / "img").mkdir(exist_ok=True)
    
    # index.html
    (base_path / "index.html").write_text('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Name</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header>
        <h1>Welcome to My Project</h1>
    </header>
    
    <main>
        <section>
            <h2>About</h2>
            <p>This is a sample web project.</p>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2024 Your Name</p>
    </footer>
    
    <script src="js/main.js"></script>
</body>
</html>
''')
    
    # style.css
    (base_path / "css" / "style.css").write_text('''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
}

header {
    background: #333;
    color: #fff;
    text-align: center;
    padding: 1rem;
}

main {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 2rem;
}

footer {
    background: #333;
    color: #fff;
    text-align: center;
    padding: 1rem;
    margin-top: 2rem;
}
''')
    
    # main.js
    (base_path / "js" / "main.js").write_text('''// Main JavaScript file

document.addEventListener('DOMContentLoaded', () => {
    console.log('Page loaded!');
});
''')


def generate_rust_template(base_path: Path) -> None:
    """Generate Rust project template."""
    # Create directory structure
    (base_path / "src").mkdir(exist_ok=True)
    (base_path / "tests").mkdir(exist_ok=True)
    
    # Cargo.toml
    (base_path / "Cargo.toml").write_text('''[package]
name = "project-name"
version = "0.1.0"
edition = "2021"

[dependencies]

[dev-dependencies]
''')
    
    # main.rs
    (base_path / "src" / "main.rs").write_text('''fn main() {
    println!("Hello, world!");
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
''')


def generate_go_template(base_path: Path) -> None:
    """Generate Go project template."""
    # Create directory structure
    (base_path / "cmd").mkdir(exist_ok=True)
    (base_path / "pkg").mkdir(exist_ok=True)
    (base_path / "internal").mkdir(exist_ok=True)
    
    # go.mod
    (base_path / "go.mod").write_text('''module github.com/username/project-name

go 1.21
''')
    
    # main.go
    (base_path / "cmd" / "main.go").write_text('''package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
''')
    
    # main_test.go
    (base_path / "cmd" / "main_test.go").write_text('''package main

import "testing"

func TestMain(t *testing.T) {
    // Add tests here
}
''')