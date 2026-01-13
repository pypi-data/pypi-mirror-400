"""Model management command implementation."""
import typer
from rich.console import Console
from rich.table import Table
from ..config_manager import (
    add_model_to_config,
    remove_model_from_config,
    set_active_model_in_config,
    load_config,
)

model_app = typer.Typer()
console = Console()


@model_app.command("add")
def add_model(
    name: str = typer.Option(..., prompt=True),
    model: str = typer.Option(..., prompt=True),
    base_url: str = typer.Option(..., prompt=True),
    temperature: float = typer.Option(..., prompt=True),
    api_key: str = typer.Option(..., prompt=True),
):
    """添加新的模型配置"""
    model_config = {
        "model": model,
        "base_url": base_url,
        "temperature": temperature,
        "api_key": api_key,
    }
    add_model_to_config(name, model_config)
    typer.echo(f"模型 '{name}' 已添加并激活。")


@model_app.command("remove")
def remove_model(name: str = typer.Option(..., prompt=True)):
    """删除指定的模型配置"""
    remove_model_from_config(name)
    typer.echo(f"模型 '{name}' 已删除。")


@model_app.command("active")
def activate_model(name: str = typer.Option(..., prompt=True)):
    """激活指定的模型配置"""
    set_active_model_in_config(name)
    typer.echo(f"模型 '{name}' 已激活。")


@model_app.command("list")
def list_models():
    """列出所有可用的模型配置"""
    config = load_config()
    active_model = config["active_model"]

    table = Table(title="可用模型配置")
    table.add_column("模型名称", style="cyan")
    table.add_column("状态", style="magenta")

    for name in config["models"]:
        status = "激活" if name == active_model else ""
        table.add_row(name, status)

    console.print(table)


@model_app.command("show")
def show_config():
    """显示当前的模型配置"""
    config = load_config()
    active_model = config["active_model"]

    if not config["models"]:
        typer.echo("当前没有保存的模型配置。请运行 'aigit model add' 命令添加模型。")
        return

    table = Table(title=f"当前激活的模型配置: {active_model}")
    table.add_column("配置项", style="cyan", no_wrap=True)
    table.add_column("值", style="magenta")

    active_config = config["models"].get(active_model, {})
    for key, value in active_config.items():
        if key == "api_key" and value:
            value = value[:4] + "*" * (len(value) - 4)
        table.add_row(key, str(value))

    console.print(table)