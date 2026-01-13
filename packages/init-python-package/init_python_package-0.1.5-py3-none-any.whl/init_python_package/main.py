from pathlib import Path
from init_python_package.tools.scaffold import scaffold_structure
from init_python_package.tools.headers import write_python_files_with_header
from init_python_package.tools.metadata import write_metadata
from init_python_package.tools.tools import write_tools
from init_python_package.tools.pyproject_gen import write_pyproject_toml
from init_python_package.tools.readme_gen import write_readme_md
from init_python_package.tools.license_gen import write_license_file

def run_initializer(project_root: Path) -> None:
    """Perform the full package scaffolding in the given project_root."""
    project_root.mkdir(parents=True, exist_ok=False)
    pkgname = project_root.name.lower().replace("-", "_")

    try:
        scaffold_structure(project_root, pkgname)
        write_tools(project_root, pkgname)
        write_metadata(project_root, pkgname)
        write_python_files_with_header(project_root, pkgname)
        write_pyproject_toml(project_root, pkgname)
        write_readme_md(project_root, pkgname)
        write_license_file(project_root)

    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        raise
    else:
        print(f"✅ Package '{pkgname}' initialized successfully at {project_root}")

def cli() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Initialize a new Python package scaffold")
    parser.add_argument("target", nargs="?", help="Target directory for the new package")
    parser.add_argument("--interactive", action="store_true",
                        help="Prompt for target path instead of passing as argument")
    args = parser.parse_args()

    if args.interactive or args.target is None:
        project_path_input = input("Enter the full path where you want to create the new package: ").strip()
        project_root = Path(project_path_input)
    else:
        project_root = Path(args.target)

    run_initializer(project_root)

if __name__ == "__main__":
    cli()

