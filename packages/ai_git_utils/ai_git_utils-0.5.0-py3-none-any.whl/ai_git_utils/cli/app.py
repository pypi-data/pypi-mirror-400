"""Main CLI application entry point."""
import typer
from .commit import commit
from .diff import diff_app
from .log import log
from .model import model_app
from .version import version

app = typer.Typer()

# Register commands
app.command()(commit)
app.command()(log)
app.command()(version)
app.add_typer(model_app, name="model", help="管理AI模型")
app.add_typer(diff_app, name="diff", help="查看代码更改")