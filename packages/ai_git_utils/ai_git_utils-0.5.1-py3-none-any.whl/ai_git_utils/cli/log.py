"""Log command implementation."""
import typer
from datetime import datetime
from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError
from rich.console import Console
from rich.table import Table

console = Console()


def log(
    limit: int = typer.Option(10, "--limit", "-n", help="显示的提交数量"),
    since: str = typer.Option(None, "--since", "-s", help="显示指定日期之后的提交，格式：YYYY-MM-DD"),
    until: str = typer.Option(None, "--until", "-u", help="显示指定日期之前的提交，格式：YYYY-MM-DD"),
):
    """美观地显示git log"""
    try:
        repo = Repo(".")
        commits = repo.iter_commits()

        if since:
            since_date = datetime.strptime(since, "%Y-%m-%d")
            commits = filter(lambda c: c.committed_datetime > since_date, commits)

        if until:
            until_date = datetime.strptime(until, "%Y-%m-%d")
            commits = filter(lambda c: c.committed_datetime < until_date, commits)

        table = Table(title="Git Log")
        table.add_column("提交哈希", style="cyan", no_wrap=True)
        table.add_column("作者", style="magenta")
        table.add_column("日期", style="green")
        table.add_column("提交信息", style="yellow")

        for _commit in list(commits)[:limit]:
            table.add_row(
                _commit.hexsha[:7],
                _commit.author.name,
                _commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                _commit.message.split("\n")[0],
            )

        console.print(table)

    except InvalidGitRepositoryError:
        typer.echo("错误：当前目录不是有效的Git仓库。", err=True)
    except GitCommandError as e:
        typer.echo(f"Git命令执行错误：{str(e)}", err=True)