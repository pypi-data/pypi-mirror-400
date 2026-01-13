"""Unit tests for AIService."""
import pytest
from unittest.mock import Mock, patch
from ai_git_utils.services.ai_service import AIService
from ai_git_utils.models.commit_message import CommitMessage


class TestAIService:
    """Test cases for AIService."""

    def test_generate_commit_message_success(self):
        """Test successful commit message generation."""
        with patch('ai_git_utils.services.ai_service.OpenAI') as mock_openai:
            # Mock the OpenAI client and response
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '{"type": "feat", "scope": "cli", "subject": "Add new feature", "emoji": "✨", "fix_items": []}'
            mock_client.chat.completions.create.return_value = mock_response
            
            with patch('ai_git_utils.services.ai_service.get_active_model') as mock_get_model:
                mock_get_model.return_value = {
                    'base_url': 'https://api.openai.com/v1',
                    'api_key': 'test-key',
                    'model': 'gpt-4',
                    'temperature': 0.7
                }
                
                service = AIService()
                result = service.generate_commit_message("test diff", "English")
                
                assert isinstance(result, CommitMessage)
                assert result.type == "feat"
                assert result.scope == "cli"
                assert result.subject == "Add new feature"

    def test_generate_commit_message_no_active_model(self):
        """Test error when no active model is configured."""
        with patch('ai_git_utils.services.ai_service.get_active_model') as mock_get_model:
            mock_get_model.return_value = None
            
            service = AIService()
            
            with pytest.raises(ValueError, match="No active model configured"):
                service.generate_commit_message("test diff", "English")

    def test_parse_response_invalid_json(self):
        """Test error handling for invalid JSON response."""
        service = AIService()
        
        with pytest.raises(RuntimeError, match="Failed to parse AI response"):
            service._parse_response("invalid json")

    def test_parse_response_success(self):
        """Test successful response parsing."""
        service = AIService()
        
        json_str = '{"type": "fix", "scope": "api", "subject": "Fix bug", "emoji": "🐛", "fix_items": []}'
        result = service._parse_response(json_str)
        
        assert isinstance(result, CommitMessage)
        assert result.type == "fix"
        assert result.scope == "api"
        assert result.subject == "Fix bug"