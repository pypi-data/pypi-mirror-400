"""Unit tests for diff command."""
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from ai_git_utils.cli.diff import diff_app


@pytest.mark.unit
class TestDiff:
    """Test cases for diff command."""
    
    def test_diff_current_no_changes(self, mocker, temp_git_repo):
        """Test diff current command when there are no changes."""
        # Mock get_git_diff to return None
        mocker.patch('ai_git_utils.cli.diff.get_git_diff', return_value=None)
        runner = CliRunner()
        
        result = runner.invoke(diff_app, ["current"])
        
        assert "没有检测到更改" in result.stdout
    
    def test_diff_current_with_changes(self, mocker, temp_git_repo):
        """Test diff current command with changes."""
        # Mock get_git_diff to return diff output
        mock_diff = "diff --git a/file.py b/file.py\n+ new line"
        mocker.patch('ai_git_utils.cli.diff.get_git_diff', return_value=mock_diff)
        mocker.patch('ai_git_utils.cli.diff.beautify_diff')
        runner = CliRunner()
        
        result = runner.invoke(diff_app, ["current"])
        
        assert result.exit_code == 0
    
    def test_diff_commit(self, mocker, temp_git_repo):
        """Test diff commit command."""
        # Mock get_commit_diff to return diff output
        mock_diff = "diff --git a/file.py b/file.py\n+ new line"
        mocker.patch('ai_git_utils.cli.diff.get_commit_diff', return_value=mock_diff)
        mocker.patch('ai_git_utils.cli.diff.beautify_diff')
        runner = CliRunner()
        
        result = runner.invoke(diff_app, ["commit", "abc123"])
        
        assert result.exit_code == 0