# init-python-package

Minimal, distribution-ready Python package scaffolding.  
Generate projects that are instantly installable with pip and publishable to PyPI.

init-python-package helps you bootstrap Python projects with a ready-to-publish structure:
- Editable install support (`pip install -e .`)
- PyPI-compliant metadata (`pyproject.toml`, SPDX license, README`)
- Preconfigured tests, scripts, and notebooks

## Features
- Generates a complete PyPI-ready package structure
- Includes `README.md`, `LICENSE`, and `pyproject.toml`
- IDE-neutral `.gitignore` for clean collaboration
- Modular design for optional flows and diagnostics
- Emphasis on reproducibility and auditability

## Installation

Clone the repository and set up your environment:

```bash
git clone https://github.com/your-username/init-python-package.git
cd init-python-package
./setup_env.sh        # or setup_env.bat on Windows
pip install -e .
```

Alternatively, users can manually create and activate a virtual environment if they prefer.

## 📦 Usage

Run directly from your terminal:

```bash
init-python-package my_new_package
```

Argument ```my_new_package``` is the full path to the generated package. If you omit the path arg, the tool runs in **interactive mode** and prompts you for the package location.

---

This creates a new folder with a complete Python package structure, including:
- Metadata (`pyproject.toml`, `README.md`, `LICENSE`)
- Importable package directory (`my_new_package/`)
- CLI entry point (`my_new_package/main.py`)
- Test scaffolding (`tests/`)
- Supporting folders (`scripts/`, `notebooks/`, `data/`)

## 🗂️ Generated Package Structure

```text
my_new_package/
├── my_new_package/           # Importable Python package
│   ├── __init__.py           # Includes dynamic version
│   ├── main.py               # CLI entry point
│   └── tools/                # Helper modules
├── tests/                    # pytest-ready test folder
├── scripts/                  # Example scripts
├── notebooks/                # Example notebooks
├── data/                     # Data folder
├── README.md                 # PyPI-ready long description
├── LICENSE                   # Apache-2.0 license
├── pyproject.toml            # Build metadata
├── .gitignore
├── requirements.txt
├── setup_env.bat / .sh       # Optional environment setup
```

## Project Intent

The goal of this project is to make starting a new Python package as simple and reliable as possible.  
Instead of piecing together configuration files, metadata, and test scaffolding by hand,  
`init-python-package` generates a complete, distribution-ready structure that you can install locally  
with `pip` and publish directly to PyPI.

By using this scaffolding, you can:
- Begin coding immediately without worrying about packaging details.  
- Validate that your project installs cleanly in a fresh environment.  
- Ensure reproducibility with standardized metadata and licensing.  
- Share your work confidently, knowing the structure meets PyPI requirements.

This project is shared publicly in support of the Python open‑source community,  
with the hope that it will be useful for learners, researchers, and developers alike.  
Contributions are welcome, though please note that pull requests may not be actively reviewed.

## Author

George Cutter

## Disclaimer

This software is provided **“as is”**, without warranty of any kind.  
The author assumes no responsibility for errors, omissions, or outcomes resulting from its use.  
Users are encouraged to validate results independently and adapt workflows to their own requirements.  
This project is intended for educational and research purposes and should not be used as a substitute for professional advice in regulated domains (e.g., medical, legal, financial).

## License

This project is licensed under the **Apache License 2.0**.  
You may use, modify, and distribute this software under the terms of the Apache License.  
See the [LICENSE](LICENSE) file for the full text.