"""Diff command implementation."""
import typer
from typing import Optional
from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError
from ..git_operations import get_git_diff, get_commit_diff
from ..utils import beautify_diff

diff_app = typer.Typer()


@diff_app.command("current")
def diff(
    file_path: Optional[str] = typer.Option(None, "--file", "-f", help="指定文件路径"),
):
    """查看代码更改"""
    try:
        repo = Repo(".")
        repo.git.add('.')
        diff_output = get_git_diff(repo, True, file_path)

        if not diff_output:
            typer.echo("没有检测到更改。")
        else:
            beautify_diff(diff_output)

    except InvalidGitRepositoryError:
        typer.echo("错误：当前目录不是有效的Git仓库。", err=True)
    except GitCommandError as e:
        typer.echo(f"Git命令执行错误：{str(e)}", err=True)


@diff_app.command("commit")
def commit_diff(commit_hash: str = typer.Argument(..., help="指定的commit哈希值")):
    """显示指定commit的diff"""
    try:
        repo = Repo(".")
        diff_output = get_commit_diff(repo, commit_hash)
        beautify_diff(diff_output)
    except InvalidGitRepositoryError:
        typer.echo("错误：当前目录不是有效的Git仓库。", err=True)
    except GitCommandError as e:
        typer.echo(f"Git命令执行错误：{str(e)}", err=True)