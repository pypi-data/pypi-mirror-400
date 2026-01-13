"""AI-related test fixtures."""
import pytest


@pytest.fixture
def mock_openai_response():
    """Provide mock OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": '{"type": "feat", "scope": "cli", "emoji": "✨", "subject": "test feature", "fix_items": ["item1", "item2"]}'
                }
            }
        ]
    }


@pytest.fixture
def mock_openai_client(mocker):
    """Provide mock OpenAI client."""
    mock_client = mocker.MagicMock()
    mock_response = mocker.MagicMock()
    mock_response.choices = [mocker.MagicMock()]
    mock_response.choices[0].message.content = '{"type": "feat", "scope": "cli", "emoji": "✨", "subject": "test", "fix_items": []}'
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client