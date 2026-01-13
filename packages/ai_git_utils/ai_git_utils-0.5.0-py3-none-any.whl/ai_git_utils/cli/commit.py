"""Commit command implementation."""
import typer
from typing import Optional
from git.exc import InvalidGitRepositoryError, GitCommandError
from ..services.commit_service import CommitService
from ..config_manager import get_active_model


def commit(
    file_path: Optional[str] = typer.Option(None, "--file", "-f", help="指定文件路径"),
    language: str = typer.Option("English", "--lang", "-l", help="设置语言（English/Chinese）"),
):
    """
    使用 AI 智能生成代码更改信息
    """
    active_config = get_active_model()
    if not active_config:
        typer.echo("错误：未找到激活的模型配置。请先运行 'aigit model add' 或 'aigit model active' 命令。")
        raise typer.Exit(code=1)
    
    try:
        service = CommitService()
        
        # Prepare commit message
        commit_message = service.prepare_commit_message(".", file_path, language)
        
        if commit_message is None:
            typer.echo("没有检测到更改。")
            return
        
        # Show the edited commit message
        typer.echo("\n编辑后的提交信息：")
        typer.echo(commit_message)
        
        # Ask for confirmation
        if typer.confirm("\n确认提交这些更改？"):
            service.commit_changes(".", commit_message)
            typer.echo("更改已成功提交！")
        else:
            typer.echo("提交已取消。")
            
    except InvalidGitRepositoryError:
        typer.echo("错误：当前目录不是有效的Git仓库。", err=True)
    except GitCommandError as e:
        typer.echo(f"Git命令执行错误：{str(e)}", err=True)
    except Exception as e:
        typer.echo(f"错误：{str(e)}", err=True)
        raise typer.Exit(code=1)