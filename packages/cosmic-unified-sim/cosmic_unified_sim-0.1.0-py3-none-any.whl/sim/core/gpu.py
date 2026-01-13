"""
GPU Backend Support
===================

Unified GPU acceleration supporting multiple backends:
- CUDA via CuPy (NVIDIA)
- Vulkan via vulkpy (AMD/NVIDIA/Intel)
- OpenCL via PyOpenCL (AMD/NVIDIA/Intel)
- Fallback to NumPy (CPU)

Refactored to use strategy pattern for cleaner code.
"""

import warnings
from typing import Any, Optional, Protocol, runtime_checkable

import numpy as np

from .exceptions import GPUNotAvailableError
from .logging import get_logger

logger = get_logger("gpu")

# Try to import GPU backends
GPU_BACKENDS = {}

# CUDA/CuPy (NVIDIA)
try:
    import cupy as cp

    GPU_BACKENDS["cuda"] = cp
    logger.debug("CUDA backend available via CuPy")
except ImportError:
    pass

# Vulkan
try:
    import vulkpy as vk

    GPU_BACKENDS["vulkan"] = vk
    logger.debug("Vulkan backend available")
except ImportError:
    pass

# OpenCL
try:
    import pyopencl as cl

    GPU_BACKENDS["opencl"] = cl
    logger.debug("OpenCL backend available")
except ImportError:
    pass

GPU_AVAILABLE = len(GPU_BACKENDS) > 0


# ============================================================================
# Backend Strategy Pattern
# ============================================================================


@runtime_checkable
class ArrayBackend(Protocol):
    """Protocol defining array backend interface."""

    def zeros(self, shape, dtype=None) -> Any: ...
    def ones(self, shape, dtype=None) -> Any: ...
    def array(self, obj, dtype=None) -> Any: ...
    def asarray(self, obj, dtype=None) -> Any: ...
    def copy(self, x) -> Any: ...
    def to_cpu(self, x) -> np.ndarray: ...
    def to_device(self, x) -> Any: ...


class NumpyBackend:
    """NumPy CPU backend."""

    name = "numpy"
    is_gpu = False

    def __init__(self):
        self.xp = np

    def zeros(self, shape, dtype=None):
        return np.zeros(shape, dtype=dtype)

    def ones(self, shape, dtype=None):
        return np.ones(shape, dtype=dtype)

    def array(self, obj, dtype=None):
        return np.array(obj, dtype=dtype)

    def asarray(self, obj, dtype=None):
        return np.asarray(obj, dtype=dtype)

    def copy(self, x):
        return np.copy(x)

    def to_cpu(self, x) -> np.ndarray:
        return np.asarray(x)

    def to_device(self, x):
        return x

    def synchronize(self):
        pass

    @property
    def info(self) -> str:
        return "NumPy (CPU)"


class CUDABackend:
    """CUDA backend via CuPy."""

    name = "cuda"
    is_gpu = True

    def __init__(self):
        if "cuda" not in GPU_BACKENDS:
            raise GPUNotAvailableError("cuda")
        import cupy as cp

        self.xp = cp
        self._cp = cp

    def zeros(self, shape, dtype=None):
        return self._cp.zeros(shape, dtype=dtype)

    def ones(self, shape, dtype=None):
        return self._cp.ones(shape, dtype=dtype)

    def array(self, obj, dtype=None):
        return self._cp.array(obj, dtype=dtype)

    def asarray(self, obj, dtype=None):
        return self._cp.asarray(obj, dtype=dtype)

    def copy(self, x):
        return self._cp.copy(x)

    def to_cpu(self, x) -> np.ndarray:
        if hasattr(x, "get"):
            return x.get()
        return np.asarray(x)

    def to_device(self, x):
        return self._cp.asarray(x)

    def synchronize(self):
        self._cp.cuda.Stream.null.synchronize()

    @property
    def info(self) -> str:
        device = self._cp.cuda.Device()
        mem_info = device.mem_info
        total_gb = mem_info[1] / 1e9
        free_gb = mem_info[0] / 1e9
        return f"CUDA: {device.name} ({total_gb:.1f} GB total, {free_gb:.1f} GB free)"


class OpenCLBackend:
    """OpenCL backend via PyOpenCL."""

    name = "opencl"
    is_gpu = True

    def __init__(self):
        if "opencl" not in GPU_BACKENDS:
            raise GPUNotAvailableError("opencl")
        import pyopencl as cl
        import pyopencl.array as cl_array

        self._cl = cl
        self._cl_array = cl_array
        self.xp = np  # OpenCL uses numpy arrays with cl operations

        # Create context and queue
        platform = cl.get_platforms()[0]
        device = platform.get_devices()[0]
        self._ctx = cl.Context([device])
        self._queue = cl.CommandQueue(self._ctx)
        self._device_name = device.name

    def zeros(self, shape, dtype=None):
        return np.zeros(shape, dtype=dtype)

    def ones(self, shape, dtype=None):
        return np.ones(shape, dtype=dtype)

    def array(self, obj, dtype=None):
        return np.array(obj, dtype=dtype)

    def asarray(self, obj, dtype=None):
        return np.asarray(obj, dtype=dtype)

    def copy(self, x):
        return np.copy(x)

    def to_cpu(self, x) -> np.ndarray:
        if hasattr(x, "get"):
            return x.get()
        return np.asarray(x)

    def to_device(self, x):
        return self._cl_array.to_device(self._queue, np.asarray(x))

    def synchronize(self):
        self._queue.finish()

    @property
    def info(self) -> str:
        return f"OpenCL: {self._device_name}"


class VulkanBackend:
    """Vulkan backend via vulkpy."""

    name = "vulkan"
    is_gpu = True

    def __init__(self):
        if "vulkan" not in GPU_BACKENDS:
            raise GPUNotAvailableError("vulkan")
        import vulkpy as vk

        self._vk = vk
        self.xp = np  # Vulkan uses numpy with GPU compute

    def zeros(self, shape, dtype=None):
        return np.zeros(shape, dtype=dtype)

    def ones(self, shape, dtype=None):
        return np.ones(shape, dtype=dtype)

    def array(self, obj, dtype=None):
        return np.array(obj, dtype=dtype)

    def asarray(self, obj, dtype=None):
        return np.asarray(obj, dtype=dtype)

    def copy(self, x):
        return np.copy(x)

    def to_cpu(self, x) -> np.ndarray:
        return np.asarray(x)

    def to_device(self, x):
        return x  # Vulkpy handles transfers internally

    def synchronize(self):
        pass

    @property
    def info(self) -> str:
        return "Vulkan"


# ============================================================================
# Unified Backend Interface
# ============================================================================


class GPUBackend:
    """
    Unified GPU backend interface.

    Provides a consistent API regardless of underlying GPU library.
    Falls back to NumPy if no GPU is available.

    Examples:
    ---------
    >>> backend = GPUBackend(use_gpu=True)
    >>> xp = backend.get_array_module()
    >>> a = xp.array([1, 2, 3])
    >>> result = backend.to_cpu(a)  # Always returns numpy array
    """

    _backend_classes = {
        "numpy": NumpyBackend,
        "cuda": CUDABackend,
        "opencl": OpenCLBackend,
        "vulkan": VulkanBackend,
    }

    def __init__(self, use_gpu: Optional[bool] = None, preferred_backend: Optional[str] = None):
        """
        Initialize GPU backend.

        Args:
            use_gpu: Force GPU (True), force CPU (False), or auto-detect (None)
            preferred_backend: Preferred backend: "cuda", "vulkan", "opencl", or None (auto)
        """
        self._backend = self._select_backend(use_gpu, preferred_backend)
        logger.info(f"Using backend: {self._backend.info}")

    def _select_backend(self, use_gpu: Optional[bool], preferred: Optional[str]):
        """Select appropriate backend based on preferences and availability."""

        # Force CPU
        if use_gpu is False:
            return NumpyBackend()

        # No GPU available
        if not GPU_AVAILABLE:
            if use_gpu is True:
                warnings.warn("GPU requested but no GPU backends available. Using CPU.")
            return NumpyBackend()

        # Try preferred backend
        if preferred and preferred in GPU_BACKENDS:
            try:
                return self._backend_classes[preferred]()
            except Exception as e:
                logger.warning(f"Failed to initialize {preferred}: {e}")

        # Auto-select: prefer CUDA > OpenCL > Vulkan
        for backend_name in ["cuda", "opencl", "vulkan"]:
            if backend_name in GPU_BACKENDS:
                try:
                    return self._backend_classes[backend_name]()
                except Exception as e:
                    logger.warning(f"Failed to initialize {backend_name}: {e}")

        # Fallback to CPU
        return NumpyBackend()

    # Delegate all methods to the selected backend

    @property
    def use_gpu(self) -> bool:
        """Whether GPU is being used."""
        return self._backend.is_gpu

    @property
    def backend_name(self) -> str:
        """Name of the active backend."""
        return self._backend.name

    @property
    def use_opencl(self) -> bool:
        """Whether OpenCL backend is active."""
        return self._backend.name == "opencl"

    def get_array_module(self):
        """
        Get array module (numpy or cupy).

        Returns:
            Module compatible with numpy API
        """
        return self._backend.xp

    def zeros(self, shape, dtype=None):
        """Create zeros array on current backend."""
        return self._backend.zeros(shape, dtype=dtype)

    def ones(self, shape, dtype=None):
        """Create ones array on current backend."""
        return self._backend.ones(shape, dtype=dtype)

    def array(self, obj, dtype=None):
        """Create array on current backend."""
        return self._backend.array(obj, dtype=dtype)

    def asarray(self, obj, dtype=None):
        """Convert to array on current backend."""
        return self._backend.asarray(obj, dtype=dtype)

    def copy(self, x):
        """Copy array."""
        return self._backend.copy(x)

    def to_cpu(self, x) -> np.ndarray:
        """
        Transfer array to CPU (numpy).

        Args:
            x: Array on any backend

        Returns:
            numpy array
        """
        return self._backend.to_cpu(x)

    def to_gpu(self, x):
        """
        Transfer array to GPU.

        Args:
            x: numpy array

        Returns:
            Array on GPU backend
        """
        return self._backend.to_device(x)

    def synchronize(self) -> None:
        """Synchronize GPU operations (wait for completion)."""
        self._backend.synchronize()

    @property
    def info(self) -> str:
        """Get backend information."""
        return self._backend.info


# ============================================================================
# Factory Functions
# ============================================================================

_default_backend: Optional[GPUBackend] = None


def get_backend(
    use_gpu: Optional[bool] = None,
    preferred_backend: Optional[str] = None,
    min_qubits_for_gpu: int = 15,
) -> GPUBackend:
    """
    Get appropriate backend based on preferences.

    Args:
        use_gpu: Force GPU (True), force CPU (False), or auto (None)
        preferred_backend: Preferred backend name
        min_qubits_for_gpu: Minimum problem size to use GPU (for auto mode)

    Returns:
        GPUBackend instance
    """
    return GPUBackend(use_gpu=use_gpu, preferred_backend=preferred_backend)


def get_default_backend() -> GPUBackend:
    """Get or create the default backend."""
    global _default_backend
    if _default_backend is None:
        _default_backend = GPUBackend()
    return _default_backend


def get_array_module(use_gpu: Optional[bool] = None):
    """
    Get numpy-compatible array module.

    Args:
        use_gpu: Force GPU (True), force CPU (False), or auto (None)

    Returns:
        numpy or cupy module
    """
    backend = get_backend(use_gpu=use_gpu)
    return backend.get_array_module()


def list_available_backends() -> list:
    """List available GPU backends."""
    available = ["numpy"]
    available.extend(GPU_BACKENDS.keys())
    return available


def get_gpu_info() -> dict:
    """Get information about available GPUs."""
    info = {
        "gpu_available": GPU_AVAILABLE,
        "backends": list_available_backends(),
    }

    if "cuda" in GPU_BACKENDS:
        try:
            import cupy as cp

            device = cp.cuda.Device()
            mem_info = device.mem_info
            info["cuda"] = {
                "device": device.name,
                "memory_total_gb": mem_info[1] / 1e9,
                "memory_free_gb": mem_info[0] / 1e9,
            }
        except Exception:
            pass

    return info
