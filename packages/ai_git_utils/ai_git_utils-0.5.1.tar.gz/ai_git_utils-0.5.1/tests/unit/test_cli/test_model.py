"""Unit tests for model command."""
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from ai_git_utils.cli.model import model_app


@pytest.mark.unit
class TestModel:
    """Test cases for model command."""
    
    def test_add_model(self, mocker):
        """Test adding a model."""
        mocker.patch('ai_git_utils.cli.model.add_model_to_config')
        runner = CliRunner()
        
        result = runner.invoke(
            model_app,
            ["add"],
            input="test-model\ngpt-4o\nhttps://api.openai.com/v1\n0.7\nsk-test-key\n"
        )
        
        assert result.exit_code == 0
        assert "已添加并激活" in result.stdout
    
    def test_remove_model(self, mocker):
        """Test removing a model."""
        mocker.patch('ai_git_utils.cli.model.remove_model_from_config')
        runner = CliRunner()
        
        result = runner.invoke(
            model_app,
            ["remove"],
            input="test-model\n"
        )
        
        assert result.exit_code == 0
        assert "已删除" in result.stdout
    
    def test_activate_model(self, mocker):
        """Test activating a model."""
        mocker.patch('ai_git_utils.cli.model.set_active_model_in_config')
        runner = CliRunner()
        
        result = runner.invoke(
            model_app,
            ["active"],
            input="test-model\n"
        )
        
        assert result.exit_code == 0
        assert "已激活" in result.stdout
    
    def test_list_models(self, mocker):
        """Test listing models."""
        mock_config = {
            "models": {
                "model1": {"model": "gpt-4o"},
                "model2": {"model": "gpt-3.5-turbo"},
            },
            "active_model": "model1"
        }
        mocker.patch('ai_git_utils.cli.model.load_config', return_value=mock_config)
        runner = CliRunner()
        
        result = runner.invoke(model_app, ["list"])
        
        assert result.exit_code == 0
        assert "可用模型配置" in result.stdout
    
    def test_show_config(self, mocker):
        """Test showing config."""
        mock_config = {
            "models": {
                "active-model": {
                    "model": "gpt-4o",
                    "base_url": "https://api.openai.com/v1",
                    "temperature": 0.7,
                    "api_key": "sk-test-key-12345"
                }
            },
            "active_model": "active-model"
        }
        mocker.patch('ai_git_utils.cli.model.load_config', return_value=mock_config)
        runner = CliRunner()
        
        result = runner.invoke(model_app, ["show"])
        
        assert result.exit_code == 0
        assert "当前激活的模型配置" in result.stdout
    
    def test_show_config_no_models(self, mocker):
        """Test showing config when no models exist."""
        mock_config = {
            "models": {},
            "active_model": None
        }
        mocker.patch('ai_git_utils.cli.model.load_config', return_value=mock_config)
        runner = CliRunner()
        
        result = runner.invoke(model_app, ["show"])
        
        assert result.exit_code == 0
        assert "当前没有保存的模型配置" in result.stdout