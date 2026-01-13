"""Project initialization CLI."""

import os
from pathlib import Path

from cookiecutter.main import cookiecutter
from loguru import logger
from sh import git
from typer import Typer

app = Typer()

PROJECT_TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "project"


@app.command()
def init():
    """Initialize project from template."""
    output_dir = cookiecutter(str(PROJECT_TEMPLATE_DIR.resolve()))

    if output_dir:
        project_path = Path(output_dir)
        try:
            os.chdir(project_path)
            git("init", "-b", "main")
            logger.info(f"✓ Initialized git repository in {project_path}")
        except Exception as e:
            print(f"⚠ Git initialization failed: {e} - skipping git initialization")
