"""Unit tests for config_manager module."""
import pytest
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


@pytest.mark.unit
class TestConfigManager:
    """Test cases for config_manager functions."""
    
    @pytest.fixture
    def mock_config_file(self, tmp_path: Path):
        """Create a mock config file."""
        config_file = tmp_path / "test_config.json"
        config_data = {
            "models": {
                "test-model": {
                    "model": "gpt-4o",
                    "base_url": "https://api.openai.com/v1",
                    "temperature": 0.7,
                    "api_key": "sk-test"
                }
            },
            "active_model": "test-model"
        }
        config_file.write_text(json.dumps(config_data))
        return config_file
    
    def test_load_config_with_file(self, mock_config_file):
        """Test loading config when file exists."""
        with patch('ai_git_utils.config_manager.CONFIG_FILE', str(mock_config_file)):
            from ai_git_utils.config_manager import load_config
            
            config = load_config()
            
            assert "models" in config
            assert "active_model" in config
            assert config["active_model"] == "test-model"
    
    def test_load_config_without_file(self, tmp_path):
        """Test loading config when file doesn't exist."""
        non_existent_file = tmp_path / "non_existent.json"
        
        with patch('ai_git_utils.config_manager.CONFIG_FILE', str(non_existent_file)):
            from ai_git_utils.config_manager import load_config
            
            config = load_config()
            
            assert config == {"models": {}, "active_model": None}
    
    def test_save_config(self, tmp_path):
        """Test saving config to file."""
        config_file = tmp_path / "test_save.json"
        
        with patch('ai_git_utils.config_manager.CONFIG_FILE', str(config_file)):
            from ai_git_utils.config_manager import save_config
            
            test_config = {"models": {}, "active_model": None}
            save_config(test_config)
            
            assert config_file.exists()
            with open(config_file, "r") as f:
                saved_config = json.load(f)
            assert saved_config == test_config
    
    def test_add_model_to_config(self, tmp_path):
        """Test adding a model to config."""
        config_file = tmp_path / "test_add.json"
        
        with patch('ai_git_utils.config_manager.CONFIG_FILE', str(config_file)):
            from ai_git_utils.config_manager import add_model_to_config, load_config
            
            model_config = {
                "model": "gpt-4o",
                "base_url": "https://api.openai.com/v1",
                "temperature": 0.7,
                "api_key": "sk-test"
            }
            
            add_model_to_config("new-model", model_config)
            
            config = load_config()
            assert "new-model" in config["models"]
            assert config["active_model"] == "new-model"
    
    def test_remove_model_from_config(self, tmp_path):
        """Test removing a model from config."""
        config_file = tmp_path / "test_remove.json"
        
        with patch('ai_git_utils.config_manager.CONFIG_FILE', str(config_file)):
            from ai_git_utils.config_manager import (
                add_model_to_config,
                remove_model_from_config,
                load_config
            )
            
            model_config = {
                "model": "gpt-4o",
                "base_url": "https://api.openai.com/v1",
                "temperature": 0.7,
                "api_key": "sk-test"
            }
            
            add_model_to_config("to-remove", model_config)
            remove_model_from_config("to-remove")
            
            config = load_config()
            assert "to-remove" not in config["models"]
    
    def test_set_active_model_in_config(self, tmp_path):
        """Test setting active model in config."""
        config_file = tmp_path / "test_active.json"
        
        with patch('ai_git_utils.config_manager.CONFIG_FILE', str(config_file)):
            from ai_git_utils.config_manager import (
                add_model_to_config,
                set_active_model_in_config,
                load_config
            )
            
            model_config = {
                "model": "gpt-4o",
                "base_url": "https://api.openai.com/v1",
                "temperature": 0.7,
                "api_key": "sk-test"
            }
            
            add_model_to_config("model1", model_config)
            add_model_to_config("model2", model_config)
            set_active_model_in_config("model2")
            
            config = load_config()
            assert config["active_model"] == "model2"
    
    def test_get_active_model(self, tmp_path):
        """Test getting active model config."""
        config_file = tmp_path / "test_get.json"
        
        with patch('ai_git_utils.config_manager.CONFIG_FILE', str(config_file)):
            from ai_git_utils.config_manager import (
                add_model_to_config,
                get_active_model
            )
            
            model_config = {
                "model": "gpt-4o",
                "base_url": "https://api.openai.com/v1",
                "temperature": 0.7,
                "api_key": "sk-test"
            }
            
            add_model_to_config("active-model", model_config)
            
            active = get_active_model()
            assert active["model"] == "gpt-4o"
            assert active["api_key"] == "sk-test"