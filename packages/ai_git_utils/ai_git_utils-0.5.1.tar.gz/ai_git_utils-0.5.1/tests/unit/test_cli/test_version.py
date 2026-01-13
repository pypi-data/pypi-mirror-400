"""Unit tests for version command."""
import pytest
from ai_git_utils.cli.version import version


@pytest.mark.unit
class TestVersion:
    """Test cases for version command."""
    
    def test_version_command(self, capsys):
        """Test version command displays correct version."""
        version()
        
        captured = capsys.readouterr()
        assert "AI Git Utils" in captured.out
        assert "V" in captured.out