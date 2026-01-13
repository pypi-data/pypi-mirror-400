"""Low-level AI CLI for multi-agent development with offline models."""

__version__ = "0.1.0"

from .client import OllamaClient
from .agent import Agent, AgentOrchestrator
from .models import ModelProvider
from .code_parser import CodeParser, CodeOrganizer

__all__ = [
    "OllamaClient",
    "Agent",
    "AgentOrchestrator",
    "ModelProvider",
    "CodeParser",
    "CodeOrganizer",
]
