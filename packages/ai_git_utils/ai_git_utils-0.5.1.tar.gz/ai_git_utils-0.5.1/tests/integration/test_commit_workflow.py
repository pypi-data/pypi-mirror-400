"""Integration tests for commit workflow."""
import pytest
from pathlib import Path
from ai_git_utils.services.commit_service import CommitService


@pytest.mark.integration
@pytest.mark.requires_ai
class TestCommitWorkflow:
    """Integration tests for the complete commit workflow."""
    
    def test_full_commit_workflow(self, temp_git_repo, temp_dir, test_env_vars):
        """Test the complete commit workflow with real AI API."""
        # Create a test file with changes
        test_file = temp_dir / "test_feature.py"
        test_file.write_text("""
def new_feature():
    return "Hello, World!"

def another_function():
    pass
""")
        
        # Configure the service with test environment variables
        import os
        os.environ['OPENAI_API_KEY'] = test_env_vars['api_key']
        os.environ['OPENAI_BASE_URL'] = test_env_vars['base_url']
        os.environ['OPENAI_MODEL'] = test_env_vars['model']
        
        # Create a temporary config file
        from ai_git_utils.config_manager import CONFIG_FILE, save_config
        import tempfile
        import json
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                "models": {
                    "test-model": {
                        "model": test_env_vars['model'],
                        "base_url": test_env_vars['base_url'],
                        "temperature": test_env_vars['temperature'],
                        "api_key": test_env_vars['api_key']
                    }
                },
                "active_model": "test-model"
            }
            json.dump(config, f)
            temp_config_path = f.name
        
        # Patch CONFIG_FILE to use our temp config
        import ai_git_utils.config_manager
        original_config_file = ai_git_utils.config_manager.CONFIG_FILE
        ai_git_utils.config_manager.CONFIG_FILE = temp_config_path
        
        try:
            service = CommitService()
            
            # Prepare commit message (this will call AI API)
            commit_message = service.prepare_commit_message(str(temp_dir), None, "English")
            
            # Verify we got a commit message
            assert commit_message is not None
            assert len(commit_message) > 0
            
            # Verify the message follows conventional commits format
            assert ":" in commit_message  # Should have type(scope): format
            
            # Commit the changes
            success = service.commit_changes(str(temp_dir), commit_message)
            assert success is True
            
            # Verify the commit was created
            latest_commit = temp_git_repo.head.commit
            assert latest_commit.message.strip() == commit_message
            
        finally:
            # Cleanup
            ai_git_utils.config_manager.CONFIG_FILE = original_config_file
            import os
            if os.path.exists(temp_config_path):
                os.unlink(temp_config_path)
    
    def test_commit_workflow_with_language_chinese(self, temp_git_repo, temp_dir, test_env_vars):
        """Test commit workflow with Chinese language."""
        test_file = temp_dir / "chinese_test.py"
        test_file.write_text("def 中文函数(): pass")
        
        # Configure with test environment variables
        import os
        os.environ['OPENAI_API_KEY'] = test_env_vars['api_key']
        os.environ['OPENAI_BASE_URL'] = test_env_vars['base_url']
        os.environ['OPENAI_MODEL'] = test_env_vars['model']
        
        # Setup temporary config
        from ai_git_utils.config_manager import save_config
        import tempfile
        import json
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                "models": {
                    "test-model": {
                        "model": test_env_vars['model'],
                        "base_url": test_env_vars['base_url'],
                        "temperature": test_env_vars['temperature'],
                        "api_key": test_env_vars['api_key']
                    }
                },
                "active_model": "test-model"
            }
            json.dump(config, f)
            temp_config_path = f.name
        
        import ai_git_utils.config_manager
        original_config_file = ai_git_utils.config_manager.CONFIG_FILE
        ai_git_utils.config_manager.CONFIG_FILE = temp_config_path
        
        try:
            service = CommitService()
            commit_message = service.prepare_commit_message(str(temp_dir), None, "Chinese")
            
            assert commit_message is not None
            # The message should be in Chinese
            # (This is a basic check; actual content depends on AI response)
            
        finally:
            ai_git_utils.config_manager.CONFIG_FILE = original_config_file
            if os.path.exists(temp_config_path):
                os.unlink(temp_config_path)