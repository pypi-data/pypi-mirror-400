"""Commit message data model."""
from dataclasses import dataclass
from typing import List


@dataclass
class CommitMessage:
    """Represents a structured commit message following Conventional Commits.
    
    Attributes:
        type: The type of change (e.g., feat, fix, docs)
        scope: The scope of the change (e.g., cli, api, ui)
        emoji: An emoji representing the type of change
        subject: A short description of the change
        fix_items: A list of detailed changes made
    """
    type: str
    scope: str
    emoji: str
    subject: str
    fix_items: List[str]
    
    def to_string(self) -> str:
        """Convert commit message to string format.
        
        Returns:
            Formatted commit message string
        """
        items = "\n".join(f"- {item}" for item in self.fix_items)
        return f"{self.type}({self.scope}): {self.emoji} {self.subject}\n\n{items}"