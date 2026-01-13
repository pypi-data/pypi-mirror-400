"""Multi-agent system for collaborative code development."""

import asyncio
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from pathlib import Path

from .client import OllamaClient
from .types import AgentConfig, Message
from .prompt_manager import PromptManager
from .code_parser import CodeParser


class AgentStatus(Enum):
    """Agent status."""
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    WAITING = "waiting"
    DONE = "done"
    ERROR = "error"


class Agent:
    """
    Individual agent with specific role and system prompt.

    Represents a single AI agent that can perform tasks collaboratively.
    """

    def __init__(
        self,
        config: AgentConfig,
        client: OllamaClient,
        prompt_manager: Optional[PromptManager] = None
    ):
        self.config = config
        self.client = client
        self.prompt_manager = prompt_manager
        self.status = AgentStatus.IDLE
        self.conversation_history: List[Message] = []
        self.context: List[int] = []  # Ollama context for continuation

        # Initialize with system message
        self.conversation_history.append(
            Message(role="system", content=config.system_prompt)
        )

    async def think(self, user_message: str) -> str:
        """
        Process a message and generate response.

        Args:
            user_message: User input or task description

        Returns:
            Agent's response
        """
        self.status = AgentStatus.THINKING

        # Add user message to history
        self.conversation_history.append(
            Message(role="user", content=user_message)
        )

        try:
            # Use chat API for conversation
            response = await self.client.chat(
                model=self.config.model,
                messages=self.conversation_history,
                stream=False,
                options={
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens or -1,
                }
            )

            assistant_message = response["message"]["content"]

            # Add assistant response to history
            self.conversation_history.append(
                Message(role="assistant", content=assistant_message)
            )

            self.status = AgentStatus.IDLE
            return assistant_message

        except Exception as e:
            self.status = AgentStatus.ERROR
            raise RuntimeError(f"Agent {self.config.name} failed: {e}")

    async def execute_task(self, task: str) -> Dict[str, Any]:
        """
        Execute a specific task.

        Args:
            task: Task description

        Returns:
            Task result with metadata
        """
        self.status = AgentStatus.WORKING

        response = await self.think(task)

        return {
            "agent": self.config.name,
            "role": self.config.role,
            "task": task,
            "response": response,
            "status": self.status.value
        }

    def reset_conversation(self):
        """Reset conversation history but keep system prompt."""
        system_msg = self.conversation_history[0]
        self.conversation_history = [system_msg]
        self.context = []
        self.status = AgentStatus.IDLE

    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation."""
        messages = []
        for msg in self.conversation_history[1:]:  # Skip system message
            messages.append(f"{msg.role}: {msg.content[:100]}...")
        return "\n".join(messages)


class AgentOrchestrator:
    """
    Orchestrates multiple agents for collaborative work.

    Manages agent communication, task distribution, and result aggregation.
    """

    def __init__(
        self,
        client: OllamaClient,
        prompt_manager: Optional[PromptManager] = None,
        output_dir: Optional[Path] = None,
        auto_save_code: bool = True
    ):
        self.client = client
        self.prompt_manager = prompt_manager or PromptManager()
        self.agents: Dict[str, Agent] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.results: List[Dict[str, Any]] = []
        self.auto_save_code = auto_save_code
        self.code_parser = CodeParser(output_dir) if auto_save_code else None
        self.saved_files: List[Path] = []

    def register_agent(self, config: AgentConfig) -> Agent:
        """
        Register a new agent.

        Args:
            config: Agent configuration

        Returns:
            Created agent
        """
        agent = Agent(config, self.client, self.prompt_manager)
        self.agents[config.name] = agent
        return agent

    def create_coding_team(
        self,
        model: str = "llama3.2",
        specializations: Optional[List[str]] = None
    ) -> Dict[str, Agent]:
        """
        Create a team of coding agents with different specializations.

        Args:
            model: Model to use for all agents
            specializations: List of specializations (default: all)

        Returns:
            Dictionary of created agents
        """
        if specializations is None:
            specializations = ["backend", "frontend", "testing", "review"]

        team = {}
        for spec in specializations:
            config = self.prompt_manager.create_agent_config(
                name=f"{spec}_agent",
                role=f"{spec.title()} Developer",
                prompt_template=PromptManager.get_coding_agent_prompt(spec),
                model=model,
                temperature=0.7
            )
            team[spec] = self.register_agent(config)

        return team

    async def distribute_task(
        self,
        task: str,
        agent_names: Optional[List[str]] = None,
        save_code: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Distribute a task to multiple agents.

        Args:
            task: Task description
            agent_names: Specific agents to use (None = all agents)
            save_code: Override auto_save_code setting

        Returns:
            List of results from all agents
        """
        target_agents = agent_names or list(self.agents.keys())

        # Execute tasks concurrently
        tasks = []
        for agent_name in target_agents:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                tasks.append(agent.execute_task(task))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Store results and optionally save code
        should_save = save_code if save_code is not None else self.auto_save_code

        for result in results:
            if isinstance(result, Exception):
                self.results.append({
                    "error": str(result),
                    "status": "error"
                })
            else:
                self.results.append(result)

                # Auto-save code from response
                if should_save and self.code_parser and "response" in result:
                    saved = self.code_parser.save_all_code_blocks(result["response"])
                    if saved:
                        result["saved_files"] = [str(f) for f in saved]
                        self.saved_files.extend(saved)

        return self.results

    async def coordinate_workflow(
        self,
        workflow: List[Dict[str, Any]],
        on_step_complete: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a multi-step workflow with different agents.

        Args:
            workflow: List of steps with format:
                [{"agent": "agent_name", "task": "task description"}, ...]
            on_step_complete: Optional callback after each step

        Returns:
            List of results from workflow
        """
        workflow_results = []

        for i, step in enumerate(workflow):
            agent_name = step["agent"]
            task = step["task"]

            if agent_name not in self.agents:
                raise ValueError(f"Agent {agent_name} not found")

            agent = self.agents[agent_name]

            # Add context from previous steps if needed
            if i > 0 and step.get("use_context", False):
                previous_result = workflow_results[-1]
                task = f"Previous result: {previous_result['response']}\n\nYour task: {task}"

            result = await agent.execute_task(task)
            workflow_results.append(result)

            if on_step_complete:
                await on_step_complete(step, result)

        return workflow_results

    def get_agent(self, name: str) -> Optional[Agent]:
        """Get agent by name."""
        return self.agents.get(name)

    def list_agents(self) -> List[str]:
        """List all registered agents."""
        return list(self.agents.keys())

    def reset_all_agents(self):
        """Reset all agents' conversation history."""
        for agent in self.agents.values():
            agent.reset_conversation()
        self.results = []
        self.saved_files = []

    def get_saved_files(self) -> List[Path]:
        """Get list of all files saved during orchestration."""
        return self.saved_files

    def create_project_from_results(
        self,
        project_name: str = "ai_generated_project"
    ) -> Path:
        """
        Create organized project from all agent results.

        Args:
            project_name: Name of project directory

        Returns:
            Path to created project
        """
        if not self.code_parser:
            raise RuntimeError("Code parser not enabled (auto_save_code=False)")

        project_dir = self.code_parser.create_project_structure(
            self.results,
            project_name
        )

        return project_dir
