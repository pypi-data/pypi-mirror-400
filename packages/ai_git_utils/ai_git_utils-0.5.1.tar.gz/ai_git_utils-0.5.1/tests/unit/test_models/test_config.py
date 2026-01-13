"""Unit tests for ModelConfig model."""
import pytest
from ai_git_utils.models.config import ModelConfig


@pytest.mark.unit
class TestModelConfig:
    """Test cases for ModelConfig dataclass."""
    
    def test_model_config_initialization(self):
        """Test that ModelConfig can be initialized with all fields."""
        config = ModelConfig(
            model="gpt-4o",
            base_url="https://api.openai.com/v1",
            temperature=0.7,
            api_key="sk-test-key"
        )
        
        assert config.model == "gpt-4o"
        assert config.base_url == "https://api.openai.com/v1"
        assert config.temperature == 0.7
        assert config.api_key == "sk-test-key"
    
    def test_from_dict(self):
        """Test creating ModelConfig from dictionary."""
        data = {
            "model": "gpt-3.5-turbo",
            "base_url": "https://api.openai.com/v1",
            "temperature": 0.5,
            "api_key": "sk-another-key"
        }
        
        config = ModelConfig.from_dict(data)
        
        assert isinstance(config, ModelConfig)
        assert config.model == "gpt-3.5-turbo"
        assert config.temperature == 0.5
    
    def test_to_dict(self):
        """Test converting ModelConfig to dictionary."""
        config = ModelConfig(
            model="gpt-4o",
            base_url="https://api.openai.com/v1",
            temperature=0.7,
            api_key="sk-test-key"
        )
        
        result = config.to_dict()
        
        assert isinstance(result, dict)
        assert result["model"] == "gpt-4o"
        assert result["base_url"] == "https://api.openai.com/v1"
        assert result["temperature"] == 0.7
        assert result["api_key"] == "sk-test-key"
    
    def test_from_dict_to_dict_roundtrip(self):
        """Test that from_dict and to_dict are inverse operations."""
        original_data = {
            "model": "gpt-4o",
            "base_url": "https://api.openai.com/v1",
            "temperature": 0.7,
            "api_key": "sk-test-key"
        }
        
        config = ModelConfig.from_dict(original_data)
        result_data = config.to_dict()
        
        assert result_data == original_data