"""System prompt manager for multi-agent control."""

from typing import Dict, Optional, List
from pathlib import Path
import json

from .types import AgentConfig


class PromptManager:
    """
    Manages system prompts (application/vnd.ollama.image.system) for agents.

    Provides centralized control over agent system prompts for collaborative work.
    """

    def __init__(self, prompts_dir: Optional[Path] = None):
        self.prompts_dir = prompts_dir or Path.home() / ".ai-cli" / "prompts"
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self._prompts: Dict[str, str] = {}
        self._load_prompts()

    def _load_prompts(self):
        """Load saved prompts from disk."""
        prompts_file = self.prompts_dir / "prompts.json"
        if prompts_file.exists():
            with open(prompts_file, "r", encoding="utf-8") as f:
                self._prompts = json.load(f)

    def _save_prompts(self):
        """Save prompts to disk."""
        prompts_file = self.prompts_dir / "prompts.json"
        with open(prompts_file, "w", encoding="utf-8") as f:
            json.dump(self._prompts, f, indent=2, ensure_ascii=False)

    def register_prompt(self, name: str, system_prompt: str):
        """
        Register a new system prompt.

        Args:
            name: Prompt identifier
            system_prompt: System prompt content
        """
        self._prompts[name] = system_prompt
        self._save_prompts()

    def get_prompt(self, name: str) -> Optional[str]:
        """Get a registered system prompt."""
        return self._prompts.get(name)

    def list_prompts(self) -> List[str]:
        """List all registered prompt names."""
        return list(self._prompts.keys())

    def delete_prompt(self, name: str):
        """Delete a registered prompt."""
        if name in self._prompts:
            del self._prompts[name]
            self._save_prompts()

    def create_agent_config(
        self,
        name: str,
        role: str,
        prompt_template: str,
        model: str = "llama3.2",
        temperature: float = 0.7,
        **kwargs
    ) -> AgentConfig:
        """
        Create agent configuration with system prompt.

        Args:
            name: Agent name
            role: Agent role description
            prompt_template: Template for system prompt
            model: Model name
            temperature: Temperature parameter
            **kwargs: Additional prompt variables

        Returns:
            AgentConfig with formatted system prompt
        """
        system_prompt = prompt_template.format(role=role, **kwargs)

        config = AgentConfig(
            name=name,
            role=role,
            system_prompt=system_prompt,
            model=model,
            temperature=temperature
        )

        # Save this configuration
        self.register_prompt(f"agent_{name}", system_prompt)

        return config

    @staticmethod
    def get_coding_agent_prompt(specialization: str = "general") -> str:
        """
        Get pre-defined coding agent prompt.

        Args:
            specialization: Agent specialization (general, backend, frontend, testing, review)
        """
        base_prompt = """You are a professional software developer working collaboratively with other AI agents.

Your role: {specialization}

Guidelines:
1. Write clean, maintainable, and well-documented code
2. Follow best practices and coding standards
3. Communicate clearly with other agents about your work
4. Ask for clarification when requirements are unclear
5. Test your code thoroughly
6. Consider edge cases and error handling

When working with other agents:
- Clearly state what you're working on
- Share relevant context and decisions
- Review and provide constructive feedback
- Coordinate to avoid conflicts
"""

        specializations = {
            "general": "General-purpose software development",
            "backend": "Backend development - APIs, databases, business logic",
            "frontend": "Frontend development - UI/UX, components, user interactions",
            "testing": "Testing and quality assurance - unit tests, integration tests, test coverage",
            "review": "Code review and architecture - review code quality, suggest improvements",
            "devops": "DevOps and infrastructure - deployment, CI/CD, monitoring",
        }

        spec_text = specializations.get(specialization, specializations["general"])
        return base_prompt.format(specialization=spec_text)

    @staticmethod
    def get_orchestrator_prompt() -> str:
        """Get prompt for orchestrator agent that coordinates other agents."""
        return """You are an orchestrator agent coordinating multiple AI agents for collaborative software development.

Your responsibilities:
1. Analyze tasks and break them into subtasks
2. Assign subtasks to appropriate specialized agents
3. Coordinate agent communication and workflow
4. Resolve conflicts and ensure consistency
5. Integrate work from multiple agents
6. Maintain project coherence and quality

Communication protocol:
- Assign clear, specific tasks to agents
- Monitor progress and provide guidance
- Facilitate information sharing between agents
- Make final decisions on conflicting approaches
- Ensure all agents understand the overall goal

Always think about:
- Task dependencies and execution order
- Resource allocation and efficiency
- Code consistency across agents
- Integration points between components
"""
