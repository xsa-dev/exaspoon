"""
Base Persona Class

This module defines the base persona class that all specific personas should inherit from.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import json


class PersonaIdentity(BaseModel):
    """Persona identity configuration"""
    description: str
    archetype: str
    core_principles: List[str]


class SpeechStyle(BaseModel):
    """Speech style configuration"""
    tone: str
    style: str
    avoids: List[str]
    preferred_phrases: List[str]


class PersonaBehavior(BaseModel):
    """Behavior configuration"""
    goals: List[str]
    actions: Dict[str, str]


class PersonaExamples(BaseModel):
    """Example responses for different situations"""
    greetings: List[str]
    analysis_responses: List[str]
    optimization_responses: List[str]


class PersonaConfig(BaseModel):
    """Complete persona configuration"""
    role: str
    identity: PersonaIdentity
    speech_style: SpeechStyle
    behavior: PersonaBehavior
    examples: PersonaExamples


class BasePersona(ABC):
    """Base class for all personas"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.name = self.__class__.__name__.replace('Persona', '').lower()
        self.config = self._load_config(config)
        
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """Return persona configuration dictionary"""
        pass
    
    def _load_config(self, config: Optional[Dict[str, Any]] = None) -> PersonaConfig:
        """Load and validate persona configuration"""
        if config is None:
            config = self.get_config()
        
        return PersonaConfig(**config)
    
    def get_system_prompt(self) -> str:
        """Generate system prompt from persona configuration"""
        cfg = self.config
        
        prompt = f"""You are {self.name.title()}, {cfg.role}. {cfg.identity.description}.

Your principles:
{chr(10).join(f"- {principle}" for principle in cfg.identity.core_principles)}

Your style: {cfg.speech_style.tone}. {cfg.speech_style.style}.

Your goals:
{chr(10).join(f"- {goal}" for goal in cfg.behavior.goals)}

Remember: {cfg.speech_style.preferred_phrases[0] if cfg.speech_style.preferred_phrases else "Be precise and helpful"}."""
        
        return prompt
    
    def get_greeting(self) -> str:
        """Get a random greeting from persona examples"""
        import random
        return random.choice(self.config.examples.greetings)
    
    def get_analysis_response(self) -> str:
        """Get a random analysis response template"""
        import random
        return random.choice(self.config.examples.analysis_responses)
    
    def get_optimization_response(self) -> str:
        """Get a random optimization response template"""
        import random
        return random.choice(self.config.examples.optimization_responses)
    
    def format_response(self, content: str, response_type: str = "general") -> str:
        """Format response according to persona style"""
        if response_type == "greeting":
            return self.get_greeting()
        elif response_type == "analysis":
            template = self.get_analysis_response()
            return f"{template} {content}"
        elif response_type == "optimization":
            template = self.get_optimization_response()
            return f"{template} {content}"
        else:
            # Apply persona style to general responses
            return content
    
    def validate_config(self) -> bool:
        """Validate persona configuration"""
        try:
            # This will raise pydantic.ValidationError if invalid
            PersonaConfig(**self.get_config())
            return True
        except Exception:
            return False