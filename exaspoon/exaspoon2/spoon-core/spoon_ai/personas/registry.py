"""
Persona Registry and Manager

This module provides the persona registry and manager system for handling
multiple personas and switching between them.
"""

from typing import Dict, Type, Optional, List
import logging
from .base import BasePersona
from .exaspoon import ExaSpoonPersona

logger = logging.getLogger(__name__)


class PersonaRegistry:
    """Registry for managing available personas"""
    
    def __init__(self):
        self._personas: Dict[str, Type[BasePersona]] = {}
        self._register_default_personas()
    
    def _register_default_personas(self):
        """Register default personas"""
        self.register("exaspoon", ExaSpoonPersona)
    
    def register(self, name: str, persona_class: Type[BasePersona]):
        """Register a persona class"""
        if not issubclass(persona_class, BasePersona):
            raise ValueError(f"Persona class must inherit from BasePersona")
        
        self._personas[name.lower()] = persona_class
        logger.info(f"Registered persona: {name}")
    
    def get_persona_class(self, name: str) -> Optional[Type[BasePersona]]:
        """Get persona class by name"""
        return self._personas.get(name.lower())
    
    def list_available_personas(self) -> List[str]:
        """List all registered persona names"""
        return list(self._personas.keys())
    
    def list_personas(self) -> List[str]:
        """List all registered persona names (alias for list_available_personas)"""
        return self.list_available_personas()
    
    def create_persona(self, name: str, config: Optional[Dict] = None) -> Optional[BasePersona]:
        """Create a persona instance"""
        persona_class = self.get_persona_class(name)
        if persona_class:
            return persona_class(config)
        return None


class PersonaManager:
    """Manager for handling persona instances and switching"""
    
    def __init__(self, registry: Optional[PersonaRegistry] = None):
        self.registry = registry or PersonaRegistry()
        self._current_persona: Optional[BasePersona] = None
        self._persona_instances: Dict[str, BasePersona] = {}
    
    def set_persona(self, name: str, config: Optional[Dict] = None) -> bool:
        """Set the current persona"""
        try:
            # Check if we already have an instance
            if name in self._persona_instances:
                self._current_persona = self._persona_instances[name]
                logger.info(f"Switched to existing persona: {name}")
                return True
            
            # Create new instance
            persona = self.registry.create_persona(name, config)
            if persona:
                self._current_persona = persona
                self._persona_instances[name] = persona
                logger.info(f"Created and set new persona: {name}")
                return True
            else:
                logger.error(f"Persona not found: {name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to set persona {name}: {e}")
            return False
    
    def get_current_persona(self) -> Optional[BasePersona]:
        """Get the current persona"""
        return self._current_persona
    
    def get_system_prompt(self) -> str:
        """Get system prompt from current persona"""
        if self._current_persona:
            return self._current_persona.get_system_prompt()
        return "You are a helpful AI assistant."
    
    def format_response(self, content: str, response_type: str = "general") -> str:
        """Format response using current persona"""
        if self._current_persona:
            return self._current_persona.format_response(content, response_type)
        return content
    
    def list_available_personas(self) -> List[str]:
        """List all available personas"""
        return self.registry.list_personas()
    
    def get_persona_info(self, name: str) -> Optional[Dict]:
        """Get information about a specific persona"""
        persona_class = self.registry.get_persona_class(name)
        if persona_class:
            try:
                temp_persona = persona_class()
                return {
                    "name": name,
                    "role": temp_persona.config.role,
                    "description": temp_persona.config.identity.description,
                    "archetype": temp_persona.config.identity.archetype,
                    "tone": temp_persona.config.speech_style.tone
                }
            except Exception as e:
                logger.error(f"Failed to get persona info for {name}: {e}")
        return None


# Global persona manager instance
persona_manager = PersonaManager()