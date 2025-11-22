"""
Persona System for Spoon AI Agents

This module provides a flexible persona system that allows agents to adopt
different personalities, communication styles, and behavioral patterns.
"""

from .base import BasePersona
from .registry import PersonaRegistry, PersonaManager
from .exaspoon import ExaSpoonPersona

__all__ = [
    'BasePersona',
    'PersonaRegistry', 
    'PersonaManager',
    'ExaSpoonPersona'
]