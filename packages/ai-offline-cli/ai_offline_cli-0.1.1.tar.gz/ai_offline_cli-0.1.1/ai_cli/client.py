"""Low-level Ollama HTTP client with resource management."""

import httpx
import json
from typing import AsyncIterator, Dict, Any, Optional
from contextlib import asynccontextmanager

from .resource_monitor import ResourceMonitor
from .types import Message, GenerateRequest, GenerateResponse


class OllamaClient:
    """Low-level asynchronous client for Ollama API with resource control."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: float = 120.0,
        max_connections: int = 10,
        enable_resource_monitoring: bool = True
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._max_connections = max_connections
        self._resource_monitor = ResourceMonitor() if enable_resource_monitoring else None

    async def __aenter__(self):
        """Async context manager entry."""
        limits = httpx.Limits(
            max_keepalive_connections=self._max_connections,
            max_connections=self._max_connections,
            keepalive_expiry=30.0
        )

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout),
            limits=limits,
            http2=True  # Use HTTP/2 for better performance
        )

        if self._resource_monitor:
            await self._resource_monitor.start()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._resource_monitor:
            await self._resource_monitor.stop()

        if self._client:
            await self._client.aclose()

    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        template: Optional[str] = None,
        context: Optional[list[int]] = None,
        stream: bool = False,
        options: Optional[Dict[str, Any]] = None,
    ) -> GenerateResponse | AsyncIterator[GenerateResponse]:
        """
        Low-level generate request to Ollama.

        Args:
            model: Model name
            prompt: User prompt
            system: System prompt (application/vnd.ollama.image.system)
            template: Custom template
            context: Context from previous generation
            stream: Stream response
            options: Model options (temperature, top_p, etc.)
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
        }

        if system:
            payload["system"] = system
        if template:
            payload["template"] = template
        if context:
            payload["context"] = context
        if options:
            payload["options"] = options

        # Check resources before making request
        if self._resource_monitor:
            resources = await self._resource_monitor.get_current_usage()
            if resources.memory_percent > 90:
                raise ResourceWarning(f"Memory usage too high: {resources.memory_percent}%")

        if stream:
            return self._stream_generate(payload)
        else:
            response = await self._client.post("/api/generate", json=payload)
            response.raise_for_status()
            return GenerateResponse(**response.json())

    async def _stream_generate(self, payload: Dict[str, Any]) -> AsyncIterator[GenerateResponse]:
        """Stream generate responses."""
        async with self._client.stream("POST", "/api/generate", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    data = json.loads(line)
                    yield GenerateResponse(**data)

    async def chat(
        self,
        model: str,
        messages: list[Message],
        stream: bool = False,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any] | AsyncIterator[Dict[str, Any]]:
        """
        Low-level chat request with message history.

        Args:
            model: Model name
            messages: List of messages with role and content
            stream: Stream response
            options: Model options
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        payload = {
            "model": model,
            "messages": [msg.model_dump() for msg in messages],
            "stream": stream,
        }

        if options:
            payload["options"] = options

        if stream:
            return self._stream_chat(payload)
        else:
            response = await self._client.post("/api/chat", json=payload)
            response.raise_for_status()
            return response.json()

    async def _stream_chat(self, payload: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """Stream chat responses."""
        async with self._client.stream("POST", "/api/chat", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    yield json.loads(line)

    async def list_models(self) -> Dict[str, Any]:
        """List available models."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        response = await self._client.get("/api/tags")
        response.raise_for_status()
        return response.json()

    async def show_model(self, model: str) -> Dict[str, Any]:
        """Show model information including system prompt."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        response = await self._client.post("/api/show", json={"name": model})
        response.raise_for_status()
        return response.json()

    async def create_model(
        self,
        name: str,
        modelfile: str,
        stream: bool = False
    ) -> Dict[str, Any] | AsyncIterator[Dict[str, Any]]:
        """
        Create a custom model with specific system prompt.

        Args:
            name: Model name
            modelfile: Modelfile content (includes SYSTEM, TEMPLATE, etc.)
            stream: Stream creation progress
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        payload = {
            "name": name,
            "modelfile": modelfile,
            "stream": stream
        }

        if stream:
            return self._stream_create(payload)
        else:
            response = await self._client.post("/api/create", json=payload)
            response.raise_for_status()
            return response.json()

    async def _stream_create(self, payload: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """Stream model creation progress."""
        async with self._client.stream("POST", "/api/create", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    yield json.loads(line)

    async def delete_model(self, name: str) -> Dict[str, Any]:
        """Delete a model."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        response = await self._client.delete("/api/delete", json={"name": name})
        response.raise_for_status()
        return response.json()

    def get_resource_usage(self) -> Optional[Dict[str, Any]]:
        """Get current resource usage."""
        if self._resource_monitor:
            import asyncio
            loop = asyncio.get_event_loop()
            resources = loop.run_until_complete(self._resource_monitor.get_current_usage())
            return resources.model_dump()
        return None
