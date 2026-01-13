"""Abstract model provider interface for offline models."""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any, Optional, List
from enum import Enum

from .types import Message


class ModelType(Enum):
    """Supported model types."""
    OLLAMA = "ollama"
    LLAMA_CPP = "llama_cpp"
    TRANSFORMERS = "transformers"
    GGUF = "gguf"
    CUSTOM = "custom"


class ModelProvider(ABC):
    """
    Abstract base class for model providers.

    Allows plugging in different offline model backends (Ollama, llama.cpp, etc.)
    """

    def __init__(self, model_type: ModelType):
        self.model_type = model_type

    @abstractmethod
    async def initialize(self, **kwargs):
        """Initialize the model provider."""
        pass

    @abstractmethod
    async def shutdown(self):
        """Cleanup and shutdown the provider."""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> str | AsyncIterator[str]:
        """
        Generate text from prompt.

        Args:
            prompt: User prompt
            system: System prompt
            stream: Whether to stream responses
            **kwargs: Provider-specific options

        Returns:
            Generated text or stream of text chunks
        """
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        stream: bool = False,
        **kwargs
    ) -> str | AsyncIterator[str]:
        """
        Chat completion with message history.

        Args:
            messages: Conversation history
            stream: Whether to stream responses
            **kwargs: Provider-specific options

        Returns:
            Generated response or stream
        """
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """List available models."""
        pass

    @abstractmethod
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        pass


class OllamaProvider(ModelProvider):
    """Ollama model provider implementation."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        super().__init__(ModelType.OLLAMA)
        self.base_url = base_url
        self._client = None

    async def initialize(self, **kwargs):
        """Initialize Ollama client."""
        from .client import OllamaClient

        self._client = OllamaClient(
            base_url=self.base_url,
            **kwargs
        )
        await self._client.__aenter__()

    async def shutdown(self):
        """Shutdown Ollama client."""
        if self._client:
            await self._client.__aexit__(None, None, None)

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        stream: bool = False,
        model: str = "llama3.2",
        **kwargs
    ) -> str | AsyncIterator[str]:
        """Generate using Ollama."""
        if not self._client:
            raise RuntimeError("Provider not initialized")

        result = await self._client.generate(
            model=model,
            prompt=prompt,
            system=system,
            stream=stream,
            **kwargs
        )

        if stream:
            async def stream_text():
                async for chunk in result:
                    if not chunk.done:
                        yield chunk.response

            return stream_text()
        else:
            return result.response

    async def chat(
        self,
        messages: List[Message],
        stream: bool = False,
        model: str = "llama3.2",
        **kwargs
    ) -> str | AsyncIterator[str]:
        """Chat using Ollama."""
        if not self._client:
            raise RuntimeError("Provider not initialized")

        result = await self._client.chat(
            model=model,
            messages=messages,
            stream=stream,
            **kwargs
        )

        if stream:
            async def stream_text():
                async for chunk in result:
                    if "message" in chunk:
                        yield chunk["message"]["content"]

            return stream_text()
        else:
            return result["message"]["content"]

    async def list_models(self) -> List[str]:
        """List Ollama models."""
        if not self._client:
            raise RuntimeError("Provider not initialized")

        result = await self._client.list_models()
        return [model["name"] for model in result.get("models", [])]

    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get Ollama model info."""
        if not self._client:
            raise RuntimeError("Provider not initialized")

        return await self._client.show_model(model_name)


class LlamaCppProvider(ModelProvider):
    """llama.cpp model provider (for direct GGUF model loading)."""

    def __init__(self, model_path: str):
        super().__init__(ModelType.LLAMA_CPP)
        self.model_path = model_path
        self._model = None

    async def initialize(self, **kwargs):
        """Initialize llama.cpp model."""
        try:
            from llama_cpp import Llama

            # Load model in executor to avoid blocking
            import asyncio
            loop = asyncio.get_event_loop()

            self._model = await loop.run_in_executor(
                None,
                lambda: Llama(
                    model_path=self.model_path,
                    n_ctx=kwargs.get("n_ctx", 4096),
                    n_gpu_layers=kwargs.get("n_gpu_layers", -1),  # Use GPU if available
                    verbose=kwargs.get("verbose", False)
                )
            )

        except ImportError:
            raise ImportError("llama-cpp-python not installed. Install with: pip install llama-cpp-python")

    async def shutdown(self):
        """Cleanup llama.cpp model."""
        self._model = None

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> str | AsyncIterator[str]:
        """Generate using llama.cpp."""
        if not self._model:
            raise RuntimeError("Provider not initialized")

        full_prompt = prompt
        if system:
            full_prompt = f"System: {system}\n\nUser: {prompt}\n\nAssistant:"

        import asyncio
        loop = asyncio.get_event_loop()

        if stream:
            async def stream_text():
                output = await loop.run_in_executor(
                    None,
                    lambda: self._model(
                        full_prompt,
                        max_tokens=kwargs.get("max_tokens", 512),
                        temperature=kwargs.get("temperature", 0.7),
                        stream=True
                    )
                )

                for chunk in output:
                    yield chunk["choices"][0]["text"]

            return stream_text()
        else:
            output = await loop.run_in_executor(
                None,
                lambda: self._model(
                    full_prompt,
                    max_tokens=kwargs.get("max_tokens", 512),
                    temperature=kwargs.get("temperature", 0.7)
                )
            )
            return output["choices"][0]["text"]

    async def chat(
        self,
        messages: List[Message],
        stream: bool = False,
        **kwargs
    ) -> str | AsyncIterator[str]:
        """Chat using llama.cpp."""
        if not self._model:
            raise RuntimeError("Provider not initialized")

        # Convert messages to prompt format
        prompt_parts = []
        for msg in messages:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}")

        prompt = "\n\n".join(prompt_parts) + "\n\nAssistant:"

        return await self.generate(prompt, stream=stream, **kwargs)

    async def list_models(self) -> List[str]:
        """List loaded model."""
        if self._model:
            return [self.model_path]
        return []

    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get model info."""
        return {
            "model_path": self.model_path,
            "type": "llama.cpp",
            "loaded": self._model is not None
        }


class ModelRegistry:
    """
    Registry for managing multiple model providers.

    Allows switching between different offline models seamlessly.
    """

    def __init__(self):
        self._providers: Dict[str, ModelProvider] = {}
        self._active_provider: Optional[str] = None

    def register_provider(self, name: str, provider: ModelProvider):
        """Register a model provider."""
        self._providers[name] = provider

    async def initialize_provider(self, name: str, **kwargs):
        """Initialize a specific provider."""
        if name not in self._providers:
            raise ValueError(f"Provider {name} not registered")

        await self._providers[name].initialize(**kwargs)

    def set_active_provider(self, name: str):
        """Set the active provider."""
        if name not in self._providers:
            raise ValueError(f"Provider {name} not registered")

        self._active_provider = name

    def get_active_provider(self) -> Optional[ModelProvider]:
        """Get the currently active provider."""
        if self._active_provider:
            return self._providers[self._active_provider]
        return None

    def get_provider(self, name: str) -> Optional[ModelProvider]:
        """Get a specific provider."""
        return self._providers.get(name)

    def list_providers(self) -> List[str]:
        """List all registered providers."""
        return list(self._providers.keys())

    async def shutdown_all(self):
        """Shutdown all providers."""
        for provider in self._providers.values():
            try:
                await provider.shutdown()
            except Exception as e:
                print(f"Error shutting down provider: {e}")


# Convenience function to create a registry with common providers
async def create_standard_registry(
    ollama_url: str = "http://localhost:11434",
    llama_cpp_model: Optional[str] = None
) -> ModelRegistry:
    """
    Create a model registry with standard providers.

    Args:
        ollama_url: Ollama API URL
        llama_cpp_model: Path to GGUF model for llama.cpp (optional)

    Returns:
        Initialized ModelRegistry
    """
    registry = ModelRegistry()

    # Register Ollama provider
    ollama = OllamaProvider(base_url=ollama_url)
    registry.register_provider("ollama", ollama)
    await registry.initialize_provider("ollama")

    # Register llama.cpp provider if model path provided
    if llama_cpp_model:
        llamacpp = LlamaCppProvider(model_path=llama_cpp_model)
        registry.register_provider("llama_cpp", llamacpp)
        await registry.initialize_provider("llama_cpp")

    # Set Ollama as default
    registry.set_active_provider("ollama")

    return registry
