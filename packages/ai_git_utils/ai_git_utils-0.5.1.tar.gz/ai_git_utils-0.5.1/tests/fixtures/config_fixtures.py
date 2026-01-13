"""Configuration-related test fixtures."""
import pytest
import json
from pathlib import Path


@pytest.fixture
def sample_model_config() -> dict:
    """Provide sample model configuration."""
    return {
        "model": "gpt-4o",
        "base_url": "https://api.openai.com/v1",
        "temperature": 0.7,
        "api_key": "sk-test-key-12345",
    }


@pytest.fixture
def sample_config_dict(sample_model_config: dict) -> dict:
    """Provide sample configuration dictionary."""
    return {
        "models": {
            "test-model": sample_model_config,
            "another-model": {
                "model": "gpt-3.5-turbo",
                "base_url": "https://api.openai.com/v1",
                "temperature": 0.5,
                "api_key": "sk-another-key",
            }
        },
        "active_model": "test-model",
    }


@pytest.fixture
def config_file_with_data(temp_config_file: Path, sample_config_dict: dict) -> Path:
    """Create a config file with sample data."""
    temp_config_file.write_text(json.dumps(sample_config_dict, indent=2))
    return temp_config_file