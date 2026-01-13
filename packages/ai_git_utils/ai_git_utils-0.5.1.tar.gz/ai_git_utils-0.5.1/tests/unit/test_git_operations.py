"""Unit tests for git_operations module."""
import pytest
from git import Repo
from pathlib import Path


@pytest.mark.unit
class TestGitOperations:
    """Test cases for git_operations functions."""
    
    def test_get_git_diff_staged(self, repo_with_staged_changes: Repo):
        """Test getting git diff for staged changes."""
        from ai_git_utils.git_operations import get_git_diff
        
        diff = get_git_diff(repo_with_staged_changes, staged=True)
        
        assert diff is not None
        assert "new_file.py" in diff
    
    def test_get_git_diff_unstaged(self, repo_with_unstaged_changes: Repo):
        """Test getting git diff for unstaged changes."""
        from ai_git_utils.git_operations import get_git_diff
        
        diff = get_git_diff(repo_with_unstaged_changes, staged=False)
        
        assert diff is not None
        assert "README.md" in diff
    
    def test_get_git_diff_specific_file(self, temp_git_repo: Repo, temp_dir: Path):
        """Test getting git diff for a specific file."""
        from ai_git_utils.git_operations import get_git_diff
        
        # Create and modify a specific file
        test_file = temp_dir / "specific.py"
        test_file.write_text("original")
        temp_git_repo.index.add(["specific.py"])
        temp_git_repo.index.commit("Add specific.py")
        
        test_file.write_text("modified")
        
        diff = get_git_diff(temp_git_repo, staged=False, file_path="specific.py")
        
        assert "specific.py" in diff
    
    def test_commit_changes(self, temp_git_repo: Repo):
        """Test committing changes."""
        from ai_git_utils.git_operations import commit_changes
        
        commit_message = "Test commit message"
        commit_changes(temp_git_repo, commit_message)
        
        # Verify commit was created
        latest_commit = temp_git_repo.head.commit
        assert latest_commit.message.strip() == commit_message
    
    def test_get_commit_diff(self, repo_with_multiple_commits: Repo):
        """Test getting diff for a specific commit."""
        from ai_git_utils.git_operations import get_commit_diff
        
        # Get diff of the second commit
        commit_hash = repo_with_multiple_commits.head.commit.hexsha
        diff = get_commit_diff(repo_with_multiple_commits, commit_hash)
        
        assert diff is not None
        assert "file2.py" in diff