from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseMusicGenModel(ABC):
    """Base class for all music generation models."""

    def __init__(self, model_name: str, config: Optional[Dict[str, Any]] = None):
        self.model_name = model_name
        self.config = config or {}
        self._model = None
    
    @abstractmethod
    def load_model(self):
        """Load the music generation model."""
        pass

    @abstractmethod
    def generate_music(self, prompt: str, **kwargs) -> Any:
        """Generate music based on the given prompt."""
        pass

