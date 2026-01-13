"""Unit tests for commit command."""
import pytest
from typer.testing import CliRunner
from unittest.mock import Mock, patch
from ai_git_utils.cli.app import app
from git.exc import InvalidGitRepositoryError, GitCommandError


class TestCommitCommand:
    """Test cases for commit command."""

    def test_commit_no_active_model(self):
        """Test commit command when no active model is configured."""
        runner = CliRunner()
        
        with patch('ai_git_utils.cli.commit.get_active_model') as mock_get_model:
            mock_get_model.return_value = None
            
            result = runner.invoke(app, ["commit"])
            
            assert result.exit_code == 1
            assert "未找到激活的模型配置" in result.stdout

    def test_commit_invalid_git_repo(self):
        """Test commit command when not in a git repository."""
        runner = CliRunner()
        
        with patch('ai_git_utils.cli.commit.get_active_model') as mock_get_model:
            mock_get_model.return_value = {
                'base_url': 'https://api.openai.com/v1',
                'api_key': 'test-key',
                'model': 'gpt-4',
                'temperature': 0.7
            }
            
            with patch('ai_git_utils.cli.commit.CommitService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                mock_service.prepare_commit_message.side_effect = InvalidGitRepositoryError()
                
                result = runner.invoke(app, ["commit"])
                
                assert "当前目录不是有效的Git仓库" in result.stderr

    def test_commit_git_command_error(self):
        """Test commit command when git command fails."""
        runner = CliRunner()
        
        with patch('ai_git_utils.cli.commit.get_active_model') as mock_get_model:
            mock_get_model.return_value = {
                'base_url': 'https://api.openai.com/v1',
                'api_key': 'test-key',
                'model': 'gpt-4',
                'temperature': 0.7
            }
            
            with patch('ai_git_utils.cli.commit.CommitService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                mock_service.prepare_commit_message.side_effect = GitCommandError("git error")
                
                result = runner.invoke(app, ["commit"])
                
                assert "Git命令执行错误" in result.stderr

    def test_commit_no_changes(self):
        """Test commit command when no changes detected."""
        runner = CliRunner()
        
        with patch('ai_git_utils.cli.commit.get_active_model') as mock_get_model:
            mock_get_model.return_value = {
                'base_url': 'https://api.openai.com/v1',
                'api_key': 'test-key',
                'model': 'gpt-4',
                'temperature': 0.7
            }
            
            with patch('ai_git_utils.cli.commit.CommitService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                mock_service.prepare_commit_message.return_value = None
                
                result = runner.invoke(app, ["commit"])
                
                assert "没有检测到更改" in result.stdout

    def test_commit_with_file_path(self):
        """Test commit command with specific file path."""
        runner = CliRunner()
        
        with patch('ai_git_utils.cli.commit.get_active_model') as mock_get_model:
            mock_get_model.return_value = {
                'base_url': 'https://api.openai.com/v1',
                'api_key': 'test-key',
                'model': 'gpt-4',
                'temperature': 0.7
            }
            
            with patch('ai_git_utils.cli.commit.CommitService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                mock_service.prepare_commit_message.return_value = "feat: test commit"
                
                result = runner.invoke(app, ["commit", "--file", "test.py"])
                
                mock_service.prepare_commit_message.assert_called_once_with(".", "test.py", "English")

    def test_commit_with_language_chinese(self):
        """Test commit command with Chinese language."""
        runner = CliRunner()
        
        with patch('ai_git_utils.cli.commit.get_active_model') as mock_get_model:
            mock_get_model.return_value = {
                'base_url': 'https://api.openai.com/v1',
                'api_key': 'test-key',
                'model': 'gpt-4',
                'temperature': 0.7
            }
            
            with patch('ai_git_utils.cli.commit.CommitService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                mock_service.prepare_commit_message.return_value = "feat: 测试提交"
                
                result = runner.invoke(app, ["commit", "--lang", "Chinese"])
                
                mock_service.prepare_commit_message.assert_called_once_with(".", None, "Chinese")