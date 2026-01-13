"""Prompt building service for AI commit message generation."""
from typing import List, Tuple
from ..models.commit_message import CommitMessage


class PromptBuilder:
    """Builds prompts for AI commit message generation."""
    
    EMOJI_LIST: List[Tuple[str, str]] = [
        ("✨", "New feature"),
        ("🐛", "Fix bug"),
        ("📚", "Documentation update"),
        ("🚀", "Deploy stuff"),
        ("💄", "UI/style update"),
        ("🎨", "Improve structure/format of the code"),
        ("🔧", "Configuration modification"),
        ("🔥", "Delete code/file"),
        ("🚑", "Critical fix"),
        ("➕", "Add dependency"),
        ("⚡️", "Performance improvement"),
        ("♻️", "Refactor code"),
        ("👷", "Add or update CI build system"),
    ]
    
    def build_system_prompt(self, language: str = "English") -> str:
        """Build system prompt for AI model.
        
        Args:
            language: Output language (English/Chinese)
            
        Returns:
            Formatted system prompt string
        """
        emoji_list = "\n".join(f"- {emoji} {desc}" for emoji, desc in self.EMOJI_LIST)
        
        example = CommitMessage(
            type="fix",
            scope="cli",
            emoji="🐛",
            subject="segmentation fault in inference",
            fix_items=["fix segmentation fault in inference"],
        )
        
        return f'''
Craft clear and concise commit messages following the Conventional Commits standard format for git. 
When presented with a git diff summary, your task is to convert it into a useful commit message and add a brief description of the changes made, ensuring that lines are not longer than 74 characters. 
Your commit message should describe the nature and purpose of the changes in a comprehensive, informative, and concise manner. 
The commit message should return the json object, keep the content concise and to the point.

emoji list:

{emoji_list}

EXAMPLE JSON OUTPUT:
{self._format_example(example)}

output only the json object and answer all my questions in {language}.
'''
    
    def build_user_prompt(self, diff_output: str) -> str:
        """Build user prompt with git diff.
        
        Args:
            diff_output: Git diff output string
            
        Returns:
            Formatted user prompt string
        """
        return f"git diff summary: \n{diff_output}"
    
    def _format_example(self, example: CommitMessage) -> str:
        """Format example commit message as JSON.
        
        Args:
            example: CommitMessage instance to format
            
        Returns:
            JSON string representation
        """
        from dataclasses import asdict
        import json
        return json.dumps(asdict(example), indent=2, ensure_ascii=False)