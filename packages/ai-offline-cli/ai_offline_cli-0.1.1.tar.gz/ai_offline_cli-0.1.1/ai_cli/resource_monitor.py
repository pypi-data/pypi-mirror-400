"""Resource monitoring for efficient PC resource management."""

import psutil
import asyncio
from typing import Optional, Dict, Any

from .types import ResourceUsage


class ResourceMonitor:
    """Monitor system resources (CPU, RAM, GPU)."""

    def __init__(self, check_interval: float = 1.0):
        self.check_interval = check_interval
        self._task: Optional[asyncio.Task] = None
        self._current_usage: Optional[ResourceUsage] = None
        self._running = False

    async def start(self):
        """Start monitoring resources."""
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())

    async def stop(self):
        """Stop monitoring resources."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _monitor_loop(self):
        """Background monitoring loop."""
        while self._running:
            try:
                self._current_usage = await self._collect_usage()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error monitoring resources: {e}")
                await asyncio.sleep(self.check_interval)

    async def _collect_usage(self) -> ResourceUsage:
        """Collect current resource usage."""
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        cpu_percent = await loop.run_in_executor(None, psutil.cpu_percent, 0.1)

        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024 ** 3)

        # Try to get GPU info if available
        gpu_usage = await self._get_gpu_usage()

        return ResourceUsage(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_available_gb=memory_available_gb,
            gpu_usage=gpu_usage
        )

    async def _get_gpu_usage(self) -> Optional[Dict[str, Any]]:
        """Get GPU usage if available (NVIDIA, AMD, Apple Silicon)."""
        try:
            # Try NVIDIA first
            import pynvml
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()

            gpus = []
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)

                gpus.append({
                    "id": i,
                    "name": name,
                    "memory_used_gb": memory_info.used / (1024 ** 3),
                    "memory_total_gb": memory_info.total / (1024 ** 3),
                    "memory_percent": (memory_info.used / memory_info.total) * 100,
                    "gpu_percent": utilization.gpu
                })

            pynvml.nvmlShutdown()
            return {"type": "nvidia", "devices": gpus}

        except (ImportError, Exception):
            # NVIDIA not available, try Apple Silicon
            try:
                # For macOS with Apple Silicon
                import subprocess
                result = subprocess.run(
                    ["system_profiler", "SPDisplaysDataType"],
                    capture_output=True,
                    text=True
                )
                if "Apple" in result.stdout:
                    return {"type": "apple_silicon", "available": True}
            except Exception:
                pass

        return None

    async def get_current_usage(self) -> ResourceUsage:
        """Get current resource usage."""
        if self._current_usage:
            return self._current_usage
        return await self._collect_usage()

    def should_throttle(self, cpu_threshold: float = 90.0, memory_threshold: float = 90.0) -> bool:
        """Check if we should throttle requests based on resource usage."""
        if not self._current_usage:
            return False

        return (
            self._current_usage.cpu_percent > cpu_threshold or
            self._current_usage.memory_percent > memory_threshold
        )
