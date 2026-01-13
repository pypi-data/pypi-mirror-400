"""Configuration data models."""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ModelConfig:
    """AI model configuration.
    
    Attributes:
        model: The model identifier (e.g., gpt-4o)
        base_url: The base URL for the API endpoint
        temperature: The temperature parameter for the model
        api_key: The API key for authentication
    """
    model: str
    base_url: str
    temperature: float
    api_key: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelConfig":
        """Create ModelConfig from dictionary.
        
        Args:
            data: Dictionary containing model configuration
            
        Returns:
            ModelConfig instance
        """
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ModelConfig to dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "api_key": self.api_key,
        }