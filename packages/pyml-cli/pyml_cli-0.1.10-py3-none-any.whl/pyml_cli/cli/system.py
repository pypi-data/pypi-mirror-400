"""CLI for interacting with system tools.

Because pyml relies heavily on the presence of anaconda,
we look for environment variables such as:

- `CONDA_EXE`
- `CONDA_PYTHON_EXE`
- `CONDA_PREFIX`
- `anaconda`
"""

import typer
from sh import bash, curl, which

app = typer.Typer()


@app.command()
def status():
    """Report status for tools that we expect to have installed.

    We check for the presence of:

    1. A `pixi` installation.
    2. A `homebrew` installation.
    3. The presence of a .pypirc file.
    """
    check_pixi()


def check_pixi():
    """Check that `pixi` is installed."""
    out = which("pixi")
    if out:
        location = out.strip("\n")
        print(f"✅ pixi found at {location}! 🎉")
    else:
        print(
            "❌ pixi not found. "
            "Please follow instructions at https://pixi.sh/install.sh to install pixi."
        )


@app.command()
def init():
    """Bootstrap user's system with necessary programs."""
    install_pixi()


def install_pixi():
    """Install conda onto a user's system."""
    # curl -fsSL https://pixi.sh/install.sh | bash
    curl("-fsSL", "https://pixi.sh/install.sh", "-o", "/tmp/install_pixi.sh")
    bash("/tmp/install_pixi.sh")


def install_homebrew():
    """Install homebrew onto a user's system."""
    pass
