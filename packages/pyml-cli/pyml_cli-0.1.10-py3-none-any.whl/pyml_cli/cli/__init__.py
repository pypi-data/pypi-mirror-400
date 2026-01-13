"""Initialize the CLI package."""

from pathlib import Path

import typer
import yaml

from ..version import __version__
from .project import init
from .system import status

app = typer.Typer(pretty_exceptions_show_locals=False)

app.command()(init)
app.command()(status)

@app.command()
def configure(
    name: str = typer.Option(..., help="Your name", prompt=True),
    email: str = typer.Option(..., help="Your email address", prompt=True),
    github_username: str = typer.Option("", help="Your GitHub username", prompt=True),
    twitter_username: str = typer.Option("", help="Your Twitter username", prompt=True),
    linkedin_username: str = typer.Option(
        "", help="Your LinkedIn username", prompt=True
    ),
):
    """Initial configuration for pyml.

    :param name: Your name.
    :param email: Your email address.
    :param github_username: Your GitHub username.
    :param twitter_username: Your Twitter username.
    :param linkedin_username: Your LinkedIn username.
    """
    info = dict(
        name=name,
        email=email,
        github_username=github_username,
        twitter_username=twitter_username,
        linkedin_username=linkedin_username,
    )
    config_file_path = Path.home() / ".pyml.yaml"
    with config_file_path.open("w+") as f:
        f.write(yaml.dump(info))


@app.command()
def version():
    """Print the current version of pyml."""
    print(__version__)
