"""AI service for generating commit messages."""
from openai import OpenAI
from ..models.commit_message import CommitMessage
from ..config_manager import get_active_model
from .prompt_builder import PromptBuilder


class AIService:
    """Service for interacting with AI models."""
    
    def __init__(self):
        """Initialize AI service."""
        self.prompt_builder = PromptBuilder()
    
    def generate_commit_message(
        self,
        diff_output: str,
        language: str = "English"
    ) -> CommitMessage:
        """
        Generate commit message from git diff using AI.
        
        Args:
            diff_output: Git diff output
            language: Output language (English/Chinese)
            
        Returns:
            Generated CommitMessage object
            
        Raises:
            ValueError: If no active model is configured
            RuntimeError: If AI API call fails
        """
        model_config = get_active_model()
        if not model_config:
            raise ValueError("No active model configured")
        
        system_prompt = self.prompt_builder.build_system_prompt(language)
        user_prompt = self.prompt_builder.build_user_prompt(diff_output)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        client = OpenAI(
            base_url=model_config.get('base_url'),
            api_key=model_config.get('api_key'),
        )
        
        response = client.chat.completions.create(
            extra_headers={"X-Title": "AIGit"},
            extra_body={},
            model=model_config.get('model'),
            messages=messages,
            temperature=model_config.get('temperature'),
            response_format={'type': 'json_object'}
        )
        
        return self._parse_response(response.choices[0].message.content)
    
    def _parse_response(self, response_text: str) -> CommitMessage:
        """
        Parse AI response into CommitMessage.
        
        Args:
            response_text: JSON response from AI
            
        Returns:
            CommitMessage object
            
        Raises:
            RuntimeError: If response cannot be parsed as JSON
        """
        import json
        try:
            data = json.loads(response_text)
            return CommitMessage(**data)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse AI response: {e}")