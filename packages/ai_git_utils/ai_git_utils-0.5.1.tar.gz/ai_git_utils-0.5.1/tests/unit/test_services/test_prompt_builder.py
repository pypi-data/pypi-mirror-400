"""Unit tests for PromptBuilder service."""
import pytest
from ai_git_utils.services.prompt_builder import PromptBuilder


@pytest.mark.unit
class TestPromptBuilder:
    """Test cases for PromptBuilder service."""
    
    def test_build_system_prompt_english(self):
        """Test building system prompt in English."""
        builder = PromptBuilder()
        prompt = builder.build_system_prompt("English")
        
        assert "Conventional Commits" in prompt
        assert "emoji list" in prompt
        assert "answer all my questions in English" in prompt
        assert "✨" in prompt
        assert "🐛" in prompt
    
    def test_build_system_prompt_chinese(self):
        """Test building system prompt in Chinese."""
        builder = PromptBuilder()
        prompt = builder.build_system_prompt("Chinese")
        
        assert "Conventional Commits" in prompt
        assert "emoji list" in prompt
        assert "answer all my questions in Chinese" in prompt
    
    def test_build_user_prompt(self):
        """Test building user prompt with diff output."""
        builder = PromptBuilder()
        diff = "diff --git a/file.py b/file.py\n+ new line"
        prompt = builder.build_user_prompt(diff)
        
        assert "git diff summary" in prompt
        assert diff in prompt
    
    def test_emoji_list_contains_all_emojis(self):
        """Test that EMOJI_LIST contains all expected emojis."""
        builder = PromptBuilder()
        expected_emojis = ["✨", "🐛", "📚", "🚀", "💄", "🎨", "🔧", "🔥", "🚑", "➕", "⚡️", "♻️", "👷"]
        
        actual_emojis = [emoji for emoji, _ in builder.EMOJI_LIST]
        
        for emoji in expected_emojis:
            assert emoji in actual_emojis