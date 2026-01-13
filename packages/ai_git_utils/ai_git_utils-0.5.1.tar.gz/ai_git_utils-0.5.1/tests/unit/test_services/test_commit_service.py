"""Unit tests for CommitService."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from ai_git_utils.services.commit_service import CommitService
from ai_git_utils.models.commit_message import CommitMessage


class TestCommitService:
    """Test cases for CommitService."""

    def test_prepare_commit_message_success(self):
        """Test successful commit message preparation."""
        with patch('ai_git_utils.services.commit_service.Repo') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            
            with patch('ai_git_utils.services.commit_service.get_git_diff') as mock_get_diff:
                mock_get_diff.return_value = "test diff output"
                
                with patch('ai_git_utils.services.commit_service.edit_commit_message') as mock_edit:
                    mock_edit.return_value = "feat: test commit"
                    
                    with patch.object(CommitService, '__init__', lambda self: None):
                        service = CommitService()
                        service.ai_service = Mock()
                        
                        mock_commit_message = CommitMessage(
                            type="feat",
                            scope="test",
                            subject="test commit",
                            emoji="✨",
                            fix_items=[]
                        )
                        service.ai_service.generate_commit_message.return_value = mock_commit_message
                        
                        result = service.prepare_commit_message(".", None, "English")
                        
                        assert result == "feat: test commit"
                        mock_repo.git.add.assert_called_once_with('.')
                        mock_get_diff.assert_called_once_with(mock_repo, True, None)
                        mock_edit.assert_called_once()

    def test_prepare_commit_message_no_changes(self):
        """Test commit message preparation when no changes detected."""
        with patch('ai_git_utils.services.commit_service.Repo') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            
            with patch('ai_git_utils.services.commit_service.get_git_diff') as mock_get_diff:
                mock_get_diff.return_value = ""
                
                with patch.object(CommitService, '__init__', lambda self: None):
                    service = CommitService()
                    service.ai_service = Mock()
                    
                    result = service.prepare_commit_message(".", None, "English")
                    
                    assert result is None

    def test_commit_changes_success(self):
        """Test successful commit changes."""
        with patch('ai_git_utils.services.commit_service.Repo') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            
            with patch('ai_git_utils.services.commit_service.commit_changes') as mock_commit:
                service = CommitService()
                
                result = service.commit_changes(".", "test commit message")
                
                assert result is True
                mock_commit.assert_called_once_with(mock_repo, "test commit message")