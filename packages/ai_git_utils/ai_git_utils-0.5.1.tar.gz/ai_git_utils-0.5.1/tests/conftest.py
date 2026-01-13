"""Global pytest configuration and fixtures."""
import os
import tempfile
from pathlib import Path
from typing import Generator
import pytest
from dotenv import load_dotenv
from git import Repo

# Load test environment variables
load_dotenv(".env.test", override=True)


@pytest.fixture(scope="session")
def test_env_vars():
    """Provide test environment variables for integration tests."""
    return {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
        "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
    }


@pytest.fixture
def temp_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    yield tmp_path


@pytest.fixture
def temp_git_repo(temp_dir: Path) -> Generator[Repo, None, None]:
    """Create a temporary git repository for testing."""
    repo = Repo.init(temp_dir)
    
    # Configure git
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()
    
    # Create initial commit
    test_file = temp_dir / "README.md"
    test_file.write_text("# Test Repository")
    repo.index.add(["README.md"])
    repo.index.commit("Initial commit")
    
    yield repo
    
    # Cleanup is handled by tmp_path fixture


@pytest.fixture
def repo_with_staged_changes(temp_git_repo: Repo, temp_dir: Path) -> Repo:
    """Create a repo with staged changes."""
    # Create a new file and stage it
    test_file = temp_dir / "new_file.py"
    test_file.write_text("print('new file')")
    temp_git_repo.index.add(["new_file.py"])
    
    return temp_git_repo


@pytest.fixture
def repo_with_unstaged_changes(temp_git_repo: Repo, temp_dir: Path) -> Repo:
    """Create a repo with unstaged changes."""
    # Modify existing file without staging
    readme_file = temp_dir / "README.md"
    readme_file.write_text("# Updated Test Repository")
    
    return temp_git_repo


@pytest.fixture
def repo_with_multiple_commits(temp_git_repo: Repo, temp_dir: Path) -> Repo:
    """Create a repo with multiple commits."""
    # First commit
    file1 = temp_dir / "file1.py"
    file1.write_text("def func1(): pass")
    temp_git_repo.index.add(["file1.py"])
    temp_git_repo.index.commit("Add file1")
    
    # Second commit
    file2 = temp_dir / "file2.py"
    file2.write_text("def func2(): pass")
    temp_git_repo.index.add(["file2.py"])
    temp_git_repo.index.commit("Add file2")
    
    return temp_git_repo


@pytest.fixture
def temp_config_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary config file for testing."""
    config_file = tmp_path / "test_config.json"
    yield config_file


@pytest.fixture
def sample_diff_output() -> str:
    """Provide sample git diff output for testing."""
    return """diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -1,5 +1,10 @@
 def hello():
-    print("Hello")
+    print("Hello, World!")
+    return True
 
 def main():
-    hello()
+    result = hello()
+    if result:
+        print("Success")
"""


@pytest.fixture
def sample_ai_response() -> dict:
    """Provide sample AI response for testing."""
    return {
        "type": "feat",
        "scope": "cli",
        "emoji": "✨",
        "subject": "add greeting enhancement",
        "fix_items": [
            "Enhanced hello() function to return boolean",
            "Added success message display in main()",
        ]
    }


@pytest.fixture
def sample_commit_message():
    """Provide sample CommitMessage object for testing."""
    from ai_git_utils.models.commit_message import CommitMessage
    
    return CommitMessage(
        type="feat",
        scope="cli",
        emoji="✨",
        subject="add greeting enhancement",
        fix_items=[
            "Enhanced hello() function to return boolean",
            "Added success message display in main()",
        ]
    )