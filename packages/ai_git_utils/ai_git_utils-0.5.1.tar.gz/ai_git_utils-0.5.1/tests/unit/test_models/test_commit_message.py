"""Unit tests for CommitMessage model."""
import pytest
from ai_git_utils.models.commit_message import CommitMessage


@pytest.mark.unit
class TestCommitMessage:
    """Test cases for CommitMessage dataclass."""
    
    def test_commit_message_initialization(self):
        """Test that CommitMessage can be initialized with all fields."""
        commit_msg = CommitMessage(
            type="feat",
            scope="cli",
            emoji="✨",
            subject="add new feature",
            fix_items=["item1", "item2"]
        )
        
        assert commit_msg.type == "feat"
        assert commit_msg.scope == "cli"
        assert commit_msg.emoji == "✨"
        assert commit_msg.subject == "add new feature"
        assert commit_msg.fix_items == ["item1", "item2"]
    
    def test_to_string_format(self):
        """Test that to_string() formats the message correctly."""
        commit_msg = CommitMessage(
            type="fix",
            scope="api",
            emoji="🐛",
            subject="fix critical bug",
            fix_items=["fix null pointer", "add error handling"]
        )
        
        result = commit_msg.to_string()
        
        assert "fix(api): 🐛 fix critical bug" in result
        assert "- fix null pointer" in result
        assert "- add error handling" in result
    
    def test_to_string_empty_fix_items(self):
        """Test to_string() with empty fix_items list."""
        commit_msg = CommitMessage(
            type="docs",
            scope="readme",
            emoji="📚",
            subject="update documentation",
            fix_items=[]
        )
        
        result = commit_msg.to_string()
        
        assert "docs(readme): 📚 update documentation" in result
        assert result.endswith("\n\n")  # Empty items section
    
    def test_commit_message_with_special_characters(self):
        """Test CommitMessage with special characters in subject."""
        commit_msg = CommitMessage(
            type="feat",
            scope="ui",
            emoji="💄",
            subject="add <button> element & update CSS",
            fix_items=["add button", "update styles"]
        )
        
        result = commit_msg.to_string()
        
        assert "feat(ui): 💄 add <button> element & update CSS" in result