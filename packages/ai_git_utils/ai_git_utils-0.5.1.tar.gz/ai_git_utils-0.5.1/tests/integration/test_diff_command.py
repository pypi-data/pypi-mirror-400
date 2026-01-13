"""Integration tests for diff command."""
import pytest
from pathlib import Path
from typer.testing import CliRunner
from ai_git_utils.cli.app import app


@pytest.mark.integration
class TestDiffCommand:
    """Integration tests for diff command."""
    
    def test_diff_current_with_real_changes(self, temp_git_repo, temp_dir, monkeypatch):
        """Test diff current command with real file changes."""
        # Create a test file
        test_file = temp_dir / "test.py"
        test_file.write_text("def test(): pass")
        temp_git_repo.index.add(["test.py"])
        temp_git_repo.index.commit("Initial commit")
        
        # Modify the file
        test_file.write_text("def test(): return 'hello'")
        
        monkeypatch.chdir(temp_dir)
        
        runner = CliRunner()
        result = runner.invoke(app, ["diff", "current"])
        
        assert result.exit_code == 0
    
    def test_diff_commit_with_real_commit(self, temp_git_repo, temp_dir, monkeypatch):
        """Test diff commit command with real commit."""
        # Create and commit a file
        test_file = temp_dir / "test.py"
        test_file.write_text("def test(): pass")
        temp_git_repo.index.add(["test.py"])
        commit = temp_git_repo.index.commit("Initial commit")
        
        # Modify the file and commit again
        test_file.write_text("def test(): return 'hello'")
        temp_git_repo.index.add(["test.py"])
        temp_git_repo.index.commit("Second commit")
        
        monkeypatch.chdir(temp_dir)
        
        runner = CliRunner()
        result = runner.invoke(app, ["diff", "commit", commit.hexsha[:7]])
        
        assert result.exit_code == 0
    
    def test_diff_current_no_changes(self, temp_git_repo, temp_dir, monkeypatch):
        """Test diff current command when there are no changes."""
        monkeypatch.chdir(temp_dir)
        
        runner = CliRunner()
        result = runner.invoke(app, ["diff", "current"])
        
        assert result.exit_code == 0
        assert "没有检测到更改" in result.stdout