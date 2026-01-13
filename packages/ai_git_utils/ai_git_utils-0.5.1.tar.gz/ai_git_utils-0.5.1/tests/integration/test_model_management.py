"""Integration tests for model management."""
import pytest
import json
import tempfile
import os
from pathlib import Path


@pytest.mark.integration
class TestModelManagement:
    """Integration tests for model management functionality."""
    
    def test_add_and_activate_model(self):
        """Test adding and activating a model."""
        from ai_git_utils.config_manager import (
            add_model_to_config,
            set_active_model_in_config,
            get_active_model,
            load_config
        )
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_config_path = f.name
            # Initialize with empty config
            json.dump({"models": {}, "active_model": None}, f)
        
        import ai_git_utils.config_manager
        original_config_file = ai_git_utils.config_manager.CONFIG_FILE
        ai_git_utils.config_manager.CONFIG_FILE = temp_config_path
        
        try:
            # Add a model
            model_config = {
                "model": "gpt-4o",
                "base_url": "https://api.openai.com/v1",
                "temperature": 0.7,
                "api_key": "sk-test-key"
            }
            add_model_to_config("test-model", model_config)
            
            # Verify model was added
            config = load_config()
            assert "test-model" in config["models"]
            assert config["active_model"] == "test-model"
            
            # Add another model
            model_config2 = {
                "model": "gpt-3.5-turbo",
                "base_url": "https://api.openai.com/v1",
                "temperature": 0.5,
                "api_key": "sk-test-key-2"
            }
            add_model_to_config("test-model-2", model_config2)
            
            # Activate the second model
            set_active_model_in_config("test-model-2")
            
            # Verify activation
            config = load_config()
            assert config["active_model"] == "test-model-2"
            
            # Verify get_active_model returns correct config
            active = get_active_model()
            assert active["model"] == "gpt-3.5-turbo"
            
        finally:
            ai_git_utils.config_manager.CONFIG_FILE = original_config_file
            if os.path.exists(temp_config_path):
                os.unlink(temp_config_path)
    
    def test_remove_model(self):
        """Test removing a model."""
        from ai_git_utils.config_manager import (
            add_model_to_config,
            remove_model_from_config,
            load_config
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_config_path = f.name
            # Initialize with empty config
            json.dump({"models": {}, "active_model": None}, f)
        
        import ai_git_utils.config_manager
        original_config_file = ai_git_utils.config_manager.CONFIG_FILE
        ai_git_utils.config_manager.CONFIG_FILE = temp_config_path
        
        try:
            # Add models
            model_config = {
                "model": "gpt-4o",
                "base_url": "https://api.openai.com/v1",
                "temperature": 0.7,
                "api_key": "sk-test-key"
            }
            add_model_to_config("to-remove", model_config)
            
            # Remove the model
            remove_model_from_config("to-remove")
            
            # Verify removal
            config = load_config()
            assert "to-remove" not in config["models"]
            
        finally:
            ai_git_utils.config_manager.CONFIG_FILE = original_config_file
            if os.path.exists(temp_config_path):
                os.unlink(temp_config_path)