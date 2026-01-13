"""Version command implementation."""
import typer
from .. import __version__


def version():
    """显示当前软件版本"""
    typer.echo(f"AI Git Utils V{__version__}")