"""Unit tests for utils module."""
import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path


@pytest.mark.unit
class TestUtils:
    """Test cases for utility functions."""
    
    def test_edit_commit_message_with_mock_editor(self, tmp_path: Path, mocker):
        """Test edit_commit_message with mocked editor."""
        from ai_git_utils.utils import edit_commit_message
        
        initial_message = "Initial commit message"
        edited_message = "Edited commit message"
        
        # Mock subprocess.run to simulate editor
        mock_run = mocker.patch('ai_git_utils.utils.subprocess.run')
        
        # Mock file operations
        mock_temp_file = tmp_path / "test_edit.tmp"
        mock_temp_file.write_text(edited_message)
        
        with patch('ai_git_utils.utils.tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.return_value.__enter__.return_value.name = str(mock_temp_file)
            mock_temp.return_value.__exit__.return_value = None
            
            result = edit_commit_message(initial_message)
            
            assert result == edited_message
            mock_run.assert_called_once()
    
    def test_edit_commit_message_editor_not_found(self, tmp_path: Path, mocker):
        """Test edit_commit_message when editor is not found."""
        from ai_git_utils.utils import edit_commit_message
        
        initial_message = "Initial commit message"
        
        # Mock shutil.which to return None (editor not found)
        mocker.patch('ai_git_utils.utils.shutil.which', return_value=None)
        mocker.patch.dict('os.environ', {'EDITOR': ''}, clear=True)
        
        # Mock tempfile to avoid actual file creation
        with patch('ai_git_utils.utils.tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.return_value.__enter__.return_value.name = str(tmp_path / "test.tmp")
            mock_temp.return_value.__exit__.return_value = None
            
            # Mock os.unlink to avoid FileNotFoundError
            mocker.patch('ai_git_utils.utils.os.unlink')
            
            result = edit_commit_message(initial_message)
            
            # Should return initial message when editor not found
            assert result == initial_message
    
    def test_edit_commit_message_editor_error(self, tmp_path: Path, mocker):
        """Test edit_commit_message when editor exits with error."""
        from ai_git_utils.utils import edit_commit_message
        from subprocess import CalledProcessError
        
        initial_message = "Initial commit message"
        
        # Mock subprocess.run to raise CalledProcessError
        mock_run = mocker.patch(
            'ai_git_utils.utils.subprocess.run',
            side_effect=CalledProcessError(1, 'vim')
        )
        
        # Mock tempfile to avoid actual file creation
        with patch('ai_git_utils.utils.tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.return_value.__enter__.return_value.name = str(tmp_path / "test.tmp")
            mock_temp.return_value.__exit__.return_value = None
            
            # Mock os.unlink to avoid FileNotFoundError
            mocker.patch('ai_git_utils.utils.os.unlink')
            
            result = edit_commit_message(initial_message)
            
            # Should return initial message when editor fails
            assert result == initial_message