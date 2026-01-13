"""Integration tests for log command."""
import pytest
from pathlib import Path
from datetime import datetime
from typer.testing import CliRunner
from ai_git_utils.cli.app import app


@pytest.mark.integration
class TestLogCommand:
    """Integration tests for log command."""
    
    def test_log_default(self, temp_git_repo, temp_dir, monkeypatch):
        """Test log command with default parameters."""
        # Create some commits
        test_file = temp_dir / "test.py"
        test_file.write_text("def test(): pass")
        temp_git_repo.index.add(["test.py"])
        temp_git_repo.index.commit("Initial commit")
        
        test_file.write_text("def test(): return 'hello'")
        temp_git_repo.index.add(["test.py"])
        temp_git_repo.index.commit("Add return value")
        
        # Change to temp directory
        monkeypatch.chdir(temp_dir)
        
        runner = CliRunner()
        result = runner.invoke(app, ["log"])
        
        assert result.exit_code == 0
        assert "Git Log" in result.stdout
        assert "Initial commit" in result.stdout
        assert "Add return value" in result.stdout
    
    def test_log_with_limit(self, temp_git_repo, temp_dir, monkeypatch):
        """Test log command with limit parameter."""
        # Create multiple commits
        test_file = temp_dir / "test.py"
        for i in range(5):
            test_file.write_text(f"def test(): return {i}")
            temp_git_repo.index.add(["test.py"])
            temp_git_repo.index.commit(f"Commit {i}")
        
        monkeypatch.chdir(temp_dir)
        
        runner = CliRunner()
        result = runner.invoke(app, ["log", "--limit", "3"])
        
        assert result.exit_code == 0
        assert "Git Log" in result.stdout
        # Should only show 3 commits
        assert result.stdout.count("Commit") == 3
    
    def test_log_empty_repository(self, temp_git_repo, temp_dir, monkeypatch):
        """Test log command when repository has no commits."""
        # Don't create any commits, just initial one from fixture
        monkeypatch.chdir(temp_dir)
        
        runner = CliRunner()
        result = runner.invoke(app, ["log"])
        
        assert result.exit_code == 0
        assert "Git Log" in result.stdout
    
    def test_log_multiline_message(self, temp_git_repo, temp_dir, monkeypatch):
        """Test log command with multiline commit messages."""
        test_file = temp_dir / "test.py"
        test_file.write_text("def test(): pass")
        temp_git_repo.index.add(["test.py"])
        
        # Create commit with multiline message
        message = """feat: add new feature

This is a detailed description
with multiple lines

- Point 1
- Point 2"""
        
        temp_git_repo.index.commit(message)
        
        monkeypatch.chdir(temp_dir)
        
        runner = CliRunner()
        result = runner.invoke(app, ["log"])
        
        assert result.exit_code == 0
        assert "Git Log" in result.stdout
        # Should show only first line
        assert "feat: add new feature" in result.stdout
        # Should not show detailed description
        assert "This is a detailed description" not in result.stdout
    
    def test_log_shows_author(self, temp_git_repo, temp_dir, monkeypatch):
        """Test that log command shows author information."""
        test_file = temp_dir / "test.py"
        test_file.write_text("def test(): pass")
        temp_git_repo.index.add(["test.py"])
        temp_git_repo.index.commit("Test commit")
        
        monkeypatch.chdir(temp_dir)
        
        runner = CliRunner()
        result = runner.invoke(app, ["log"])
        
        assert result.exit_code == 0
        assert "Git Log" in result.stdout
        # Should show author column header
        assert "作者" in result.stdout
    
    def test_log_shows_date(self, temp_git_repo, temp_dir, monkeypatch):
        """Test that log command shows commit date."""
        test_file = temp_dir / "test.py"
        test_file.write_text("def test(): pass")
        temp_git_repo.index.add(["test.py"])
        temp_git_repo.index.commit("Test commit")
        
        monkeypatch.chdir(temp_dir)
        
        runner = CliRunner()
        result = runner.invoke(app, ["log"])
        
        assert result.exit_code == 0
        assert "Git Log" in result.stdout
        # Should show date column header
        assert "日期" in result.stdout
        # Should show actual date
        assert datetime.now().strftime("%Y") in result.stdout
    
    def test_log_shows_commit_hash(self, temp_git_repo, temp_dir, monkeypatch):
        """Test that log command shows commit hash."""
        test_file = temp_dir / "test.py"
        test_file.write_text("def test(): pass")
        temp_git_repo.index.add(["test.py"])
        temp_git_repo.index.commit("Test commit")
        
        monkeypatch.chdir(temp_dir)
        
        runner = CliRunner()
        result = runner.invoke(app, ["log"])
        
        assert result.exit_code == 0
        assert "Git Log" in result.stdout
        # Should show commit hash column header
        assert "提交哈希" in result.stdout
        # Should show actual hash (7 characters)
        # Check that there's a line with exactly 7 characters (the hash)
        lines = result.stdout.split('\n')
        hash_lines = [line.strip() for line in lines if len(line.strip()) == 7]
        assert len(hash_lines) > 0