"""Commit service for handling git commit operations."""
from typing import Optional
from git import Repo
from ..git_operations import get_git_diff, commit_changes
from ..utils import edit_commit_message
from .ai_service import AIService


class CommitService:
    """Service for handling commit operations."""
    
    def __init__(self):
        """Initialize commit service."""
        self.ai_service = AIService()
    
    def prepare_commit_message(
        self,
        repo_path: str = ".",
        file_path: Optional[str] = None,
        language: str = "English"
    ) -> Optional[str]:
        """
        Prepare commit message with AI-generated content.
        
        Args:
            repo_path: Path to git repository
            file_path: Optional specific file path
            language: Output language for commit message
            
        Returns:
            Edited commit message string, or None if no changes detected
            
        Raises:
            InvalidGitRepositoryError: If not a valid git repository
            GitCommandError: If git command fails
            RuntimeError: If AI service fails
        """
        repo = Repo(repo_path)
        repo.git.add('.')
        
        diff_output = get_git_diff(repo, True, file_path)
        
        if not diff_output:
            print("No changes detected.")
            return None
        
        # Generate commit message using AI
        commit_message = self.ai_service.generate_commit_message(
            diff_output,
            language
        )
        
        # Format and edit commit message
        initial_message = commit_message.to_string()
        edited_message = edit_commit_message(initial_message)
        
        return edited_message
    
    def commit_changes(
        self,
        repo_path: str = ".",
        commit_message: str = ""
    ) -> bool:
        """
        Commit changes with the given message.
        
        Args:
            repo_path: Path to git repository
            commit_message: Commit message to use
            
        Returns:
            True if commit was successful
            
        Raises:
            InvalidGitRepositoryError: If not a valid git repository
            GitCommandError: If git command fails
        """
        repo = Repo(repo_path)
        commit_changes(repo, commit_message)
        return True