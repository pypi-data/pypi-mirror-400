"""
Init command - Create a new project structure and generate development files
"""

import sys
from pathlib import Path
from typing import Optional

from infoman.cli.scaffold import ProjectScaffold


def init_project(project_name: Optional[str] = None, target_dir: Optional[str] = None) -> int:
    """
    Initialize a new project with standard structure

    Args:
        project_name: Name of the project (optional, will prompt if not provided)
        target_dir: Target directory (optional, defaults to current directory)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Get project name from argument or prompt
    if not project_name:
        try:
            project_name = input("Enter project name: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            return 1

    if not project_name:
        print("Error: Project name cannot be empty")
        return 1

    # Validate project name
    if not project_name.replace("-", "").replace("_", "").isalnum():
        print("Error: Project name can only contain letters, numbers, hyphens, and underscores")
        return 1

    # Parse target directory
    target_path = Path(target_dir) / project_name if target_dir else None

    try:
        # Create scaffold generator
        scaffold = ProjectScaffold(project_name, target_path)

        # Generate project structure
        scaffold.generate()

        return 0

    except FileExistsError as e:
        print(f"Error: {e}")
        print("Please choose a different project name or remove the existing directory.")
        return 1

    except PermissionError as e:
        print(f"Error: Permission denied - {e}")
        return 1

    except Exception as e:
        print(f"Error: Failed to create project - {e}")
        return 1


def generate_makefile(project_name: Optional[str] = None, force: bool = False) -> int:
    """
    Generate Makefile for existing project

    Args:
        project_name: Project name (optional, defaults to current directory name)
        force: Overwrite existing Makefile

    Returns:
        Exit code (0 for success, 1 for error)
    """
    import os

    # Get project name
    if not project_name:
        project_name = Path.cwd().name

    # Check if Makefile exists
    makefile_path = Path.cwd() / "Makefile"
    if makefile_path.exists() and not force:
        print(f"Error: Makefile already exists")
        print(f"Use --force to overwrite")
        return 1

    # Read template
    template_path = Path(__file__).parent.parent / "templates" / "Makefile.template"
    try:
        template_content = template_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: Template not found at {template_path}")
        return 1

    # Replace placeholder
    makefile_content = template_content.replace("{{PROJECT_NAME}}", project_name)

    # Write Makefile
    try:
        makefile_path.write_text(makefile_content, encoding="utf-8")
        print(f"✓ Makefile created successfully!")
        print(f"\nProject: {project_name}")
        print(f"\nRun 'make help' to see available commands.")
        return 0
    except Exception as e:
        print(f"Error: Failed to create Makefile - {e}")
        return 1


def main() -> None:
    """Main entry point for CLI"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Infoman CLI - Project scaffolding and development tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  init        Create a new project with full structure
  makefile    Generate Makefile for existing project

Examples:
  infomankit init                       # Interactive mode
  infomankit init my-project            # Create project named 'my-project'
  infomankit init my-app --dir /tmp     # Create in specific directory

  infomankit makefile                   # Generate Makefile in current directory
  infomankit makefile --force           # Overwrite existing Makefile
  infomankit makefile --name my-app     # Set project name

For more information, visit: https://github.com/infoman-lib/infoman-pykit
        """,
    )

    parser.add_argument(
        "command",
        choices=["init", "makefile"],
        help="Command to execute",
    )

    parser.add_argument(
        "project_name",
        nargs="?",
        help="Name of the project (for init command)",
    )

    parser.add_argument(
        "--dir",
        "-d",
        dest="target_dir",
        help="Target directory (for init command, default: current directory)",
    )

    parser.add_argument(
        "--name",
        "-n",
        dest="makefile_name",
        help="Project name (for makefile command, default: current directory name)",
    )

    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force overwrite existing files (for makefile command)",
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="infomankit 0.3.15",
    )

    args = parser.parse_args()

    if args.command == "init":
        exit_code = init_project(args.project_name, args.target_dir)
        sys.exit(exit_code)
    elif args.command == "makefile":
        exit_code = generate_makefile(args.makefile_name, args.force)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
