"""Type definitions for AI CLI."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message."""
    role: str = Field(..., description="Role: system, user, or assistant")
    content: str = Field(..., description="Message content")
    images: Optional[List[str]] = Field(None, description="Image data (base64)")


class GenerateRequest(BaseModel):
    """Generate request parameters."""
    model: str
    prompt: str
    system: Optional[str] = None
    template: Optional[str] = None
    context: Optional[List[int]] = None
    stream: bool = False
    raw: bool = False
    options: Optional[Dict[str, Any]] = None


class GenerateResponse(BaseModel):
    """Generate response."""
    model: str
    created_at: str
    response: str
    done: bool
    context: Optional[List[int]] = None
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None


class ResourceUsage(BaseModel):
    """System resource usage."""
    cpu_percent: float = Field(..., description="CPU usage percentage")
    memory_percent: float = Field(..., description="Memory usage percentage")
    memory_available_gb: float = Field(..., description="Available memory in GB")
    gpu_usage: Optional[Dict[str, Any]] = Field(None, description="GPU usage if available")


class AgentConfig(BaseModel):
    """Agent configuration."""
    name: str = Field(..., description="Agent name")
    role: str = Field(..., description="Agent role description")
    system_prompt: str = Field(..., description="System prompt for agent")
    model: str = Field(default="llama3.2", description="Model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, description="Max tokens to generate")

    def to_modelfile(self) -> str:
        """Generate Modelfile for this agent configuration."""
        lines = [
            f"FROM {self.model}",
            f"SYSTEM {self.system_prompt}",
            f"PARAMETER temperature {self.temperature}",
        ]

        if self.max_tokens:
            lines.append(f"PARAMETER num_predict {self.max_tokens}")

        return "\n".join(lines)
