#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
"""
GPU/Device utilities with support for CUDA, MPS (Apple Silicon), and CPU.

Uses a backend pattern to provide device-agnostic GPU operations.
Each backend (NvidiaGPU, AppleGPU, NoGPU) implements the GPUBackend interface.
"""
import math
import os
import time
import torch
import logging
from abc import ABC, abstractmethod

try:
    import psutil
except ImportError:
    psutil = None

logger = logging.getLogger(__name__)


# ============================================================================
# Backend Abstract Base Class
# ============================================================================

class GPUBackend(ABC):
    """Abstract base class for GPU/device backends."""
    
    @abstractmethod
    def get_device(self) -> torch.device:
        """Get the torch device."""
        pass
    
    @abstractmethod
    def get_device_type(self) -> str:
        """Get device type as string."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available."""
        pass
    
    @abstractmethod
    def get_memory_allocated(self) -> float:
        """Get allocated memory in GB."""
        pass
    
    @abstractmethod
    def get_memory_reserved(self) -> float:
        """Get reserved memory in GB."""
        pass
    
    @abstractmethod
    def get_max_memory_allocated(self) -> float:
        """Get peak allocated memory in GB."""
        pass
    
    @abstractmethod
    def get_max_memory_reserved(self) -> float:
        """Get peak reserved memory in GB."""
        pass
    
    @abstractmethod
    def empty_cache(self):
        """Clear memory cache."""
        pass
    
    @abstractmethod
    def synchronize(self):
        """Synchronize device operations."""
        pass
    
    @abstractmethod
    def reset_peak_memory_stats(self):
        """Reset peak memory statistics."""
        pass
    
    @abstractmethod
    def reset_accumulated_memory_stats(self):
        """Reset accumulated memory statistics (CUDA only, no-op for others)."""
        pass
    
    @abstractmethod
    def ipc_collect(self):
        """Collect IPC (inter-process communication) memory (CUDA only, no-op for others)."""
        pass
    
    @abstractmethod
    def set_seed(self, seed: int):
        """Set random seed for device operations."""
        pass
    
    @abstractmethod
    def get_memory_summary(self, abbreviated: bool = True) -> str:
        """Get memory summary string (empty string if not supported)."""
        pass
    
    @abstractmethod
    def get_memory_snapshot(self) -> list:
        """Get memory snapshot list (empty list if not supported)."""
        pass
    
    @abstractmethod
    def get_device_properties(self, device_id: int = 0):
        """Get device properties (returns None if not supported)."""
        pass
    
    @abstractmethod
    def get_current_device_id(self) -> int:
        """Get current device ID (returns 0 if not supported)."""
        pass
    
    @abstractmethod
    def get_max_batch_size(
        self,
        requested_batch_size: int,
        n_cols: int = 0,
        n_attention_heads: int = 16,
        has_relationship_features: bool = False,
        ops_per_pair: int = 1,  # Default 1 (fusion mode); 9 if unfused
        min_batch_size: int = 32,
    ) -> int:
        """
        Calculate the maximum safe batch size for this device.
        
        Handles device-specific constraints like MPS INT_MAX limits.
        
        Args:
            requested_batch_size: The batch size you want to use
            n_cols: Number of columns in the dataset
            n_attention_heads: Number of attention heads in transformer
            has_relationship_features: Whether relationship features are enabled
            ops_per_pair: Number of relationship operations per column pair
            min_batch_size: Minimum viable batch size
        
        Returns:
            Safe batch size (<= requested_batch_size, >= min_batch_size)
        """
        pass
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.get_device_type()})"


# ============================================================================
# CUDA Backend (NVIDIA GPUs)
# ============================================================================

class NvidiaGPU(GPUBackend):
    """NVIDIA CUDA GPU backend."""
    
    def __init__(self):
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available")
        self._device = torch.device("cuda")
        logger.debug("🖥️  Initialized NVIDIA CUDA GPU backend")
    
    def get_device(self) -> torch.device:
        return self._device
    
    def get_device_type(self) -> str:
        return "cuda"
    
    def is_available(self) -> bool:
        return torch.cuda.is_available()
    
    def get_memory_allocated(self) -> float:
        return torch.cuda.memory_allocated() / (1024**3)
    
    def get_memory_reserved(self) -> float:
        return torch.cuda.memory_reserved() / (1024**3)
    
    def get_max_memory_allocated(self) -> float:
        return torch.cuda.max_memory_allocated() / (1024**3)
    
    def get_max_memory_reserved(self) -> float:
        return torch.cuda.max_memory_reserved() / (1024**3)
    
    def empty_cache(self):
        torch.cuda.empty_cache()
    
    def synchronize(self):
        torch.cuda.synchronize()
    
    def reset_peak_memory_stats(self):
        torch.cuda.reset_peak_memory_stats()
    
    def reset_accumulated_memory_stats(self):
        torch.cuda.reset_accumulated_memory_stats()
    
    def ipc_collect(self):
        torch.cuda.ipc_collect()
    
    def set_seed(self, seed: int):
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    
    def get_memory_summary(self, abbreviated: bool = True) -> str:
        return torch.cuda.memory_summary(abbreviated=abbreviated)
    
    def get_memory_snapshot(self) -> dict:
        return torch.cuda.memory_snapshot()
    
    def get_device_properties(self, device_id: int = 0):
        return torch.cuda.get_device_properties(device_id)
    
    def get_current_device_id(self) -> int:
        return torch.cuda.current_device()
    
    def get_max_batch_size(
        self,
        requested_batch_size: int,
        n_cols: int = 0,
        n_attention_heads: int = 16,
        has_relationship_features: bool = False,
        ops_per_pair: int = 1,  # Default 1 (fusion mode); 9 if unfused
        min_batch_size: int = 32,
    ) -> int:
        """
        Calculate maximum safe batch size for CUDA based on available GPU memory.
        
        Memory estimation for embedding space training:
        - Column encodings: batch × n_cols × d_model × 4 bytes (forward + backward = 2x)
        - Attention matrices: batch × heads × n_cols × n_cols × 4 bytes × n_layers
        - InfoNCE similarity matrix: batch × batch × 4 bytes (per mask split)
        - Optimizer states: ~2x model memory for AdamW
        - Safety margin: 25% headroom
        
        With gradient checkpointing enabled, attention memory is reduced by ~n_layers.
        """
        if n_cols == 0:
            # No column info - fall back to requested size
            return requested_batch_size
        
        try:
            # Get available GPU memory
            device_id = torch.cuda.current_device()
            props = torch.cuda.get_device_properties(device_id)
            total_memory_gb = props.total_memory / (1024**3)
            
            # Reserve memory already allocated + some for model
            allocated_gb = torch.cuda.memory_allocated(device_id) / (1024**3)
            
            # Use 70% of total memory as target (30% safety margin)
            # This accounts for: fragmentation, PyTorch overhead, CUDA driver
            available_gb = total_memory_gb * 0.70 - allocated_gb
            available_gb = max(1.0, available_gb)  # At least 1GB available
            
            # Constants for estimation (d_model=256, n_layers=3 typical)
            d_model = 256
            bytes_per_float = 4  # float32 (BF16 reduces this but we use conservative estimate)
            
            # Estimate memory per sample (in GB)
            # 1. Column encodings forward + backward: n_cols × d_model × 4 bytes × 2
            col_encoding_per_sample = (n_cols * d_model * bytes_per_float * 2) / (1024**3)
            
            # 2. Attention per sample (with gradient checkpointing, reduced by n_layers)
            # Attention: heads × n_cols × n_cols per layer
            # With checkpointing: only store 1 layer's activations at a time
            attention_per_sample = (n_attention_heads * n_cols * n_cols * bytes_per_float) / (1024**3)
            
            # 3. InfoNCE loss creates batch×batch similarity matrices
            # This scales with batch_size, so we need to solve iteratively
            # Rough estimate: batch × d_model × 4 bytes for similarity computation
            infonce_per_sample = (d_model * bytes_per_float * 4) / (1024**3)  # ~4x for intermediate tensors
            
            # Total per-sample memory (GB)
            mem_per_sample = col_encoding_per_sample + attention_per_sample + infonce_per_sample
            
            # For many columns (100+), attention dominates
            if n_cols >= 100:
                # Additional scaling factor for large column counts
                # Empirically, 147 cols uses ~180 MB per sample at batch_size=512
                # That's 93 GB / 512 = 0.18 GB per sample
                mem_per_sample = max(mem_per_sample, 0.15)  # At least 150 MB per sample for 100+ cols
            
            # Calculate max batch size
            max_batch = int(available_gb / mem_per_sample)
            
            # Round down to power of 2 for GPU efficiency
            if max_batch >= 2:
                max_batch = 2 ** int(math.log2(max_batch))
            
            # Apply constraints
            max_batch = max(min_batch_size, min(requested_batch_size, max_batch))
            
            if max_batch < requested_batch_size:
                logger.warning(
                    f"🔋 CUDA memory limit: batch_size {requested_batch_size} → {max_batch} "
                    f"(GPU: {total_memory_gb:.1f} GB, {n_cols} cols, ~{mem_per_sample*1000:.1f} MB/sample)"
                )
            else:
                logger.info(
                    f"✅ CUDA batch_size={max_batch} fits in memory "
                    f"(GPU: {total_memory_gb:.1f} GB, {n_cols} cols, est. {max_batch * mem_per_sample:.1f} GB)"
                )
            
            return max_batch
            
        except Exception as e:
            logger.warning(f"⚠️  CUDA memory estimation failed: {e}, using requested batch_size={requested_batch_size}")
            return requested_batch_size


# ============================================================================
# MPS Backend (Apple Silicon GPUs)
# ============================================================================

class AppleGPU(GPUBackend):
    """Apple Metal Performance Shaders (MPS) GPU backend."""

    _BYTES_IN_GB = 1024 ** 3

    def __init__(self):
        if not getattr(torch.backends, "mps", None):
            raise RuntimeError(
                "PyTorch was not built with MPS support (torch.backends.mps is missing)."
            )
        if not torch.backends.mps.is_available():
            raise RuntimeError(
                "MPS is not available on this machine (requires Apple Silicon + MPS driver)."
            )

        self._device = torch.device("mps")
        # Track our own notion of "peak" since MPS doesn't expose it.
        self._peak_allocated_bytes = 0
        self._peak_reserved_bytes = 0

        logger.info("⚡ Initialized Apple MPS GPU backend")

    # ---- Core device info ----

    def get_device(self) -> torch.device:
        return self._device

    def get_device_type(self) -> str:
        return "mps"

    def is_available(self) -> bool:
        return torch.backends.mps.is_available()

    # ---- Internals ----

    def _bytes_to_gb(self, n: int) -> float:
        return float(n) / self._BYTES_IN_GB

    def _update_peaks(self, allocated_bytes: int, reserved_bytes: int) -> None:
        if allocated_bytes > self._peak_allocated_bytes:
            self._peak_allocated_bytes = allocated_bytes
        if reserved_bytes > self._peak_reserved_bytes:
            self._peak_reserved_bytes = reserved_bytes

    def _current_alloc_and_reserved_bytes(self) -> tuple[int, int]:
        alloc = int(torch.mps.current_allocated_memory())
        reserved = int(torch.mps.driver_allocated_memory())
        # Update peaks on every observation
        self._update_peaks(alloc, reserved)
        return alloc, reserved

    # ---- Memory API ----

    def get_memory_allocated(self) -> float:
        alloc_bytes, _ = self._current_alloc_and_reserved_bytes()
        return self._bytes_to_gb(alloc_bytes)

    def get_memory_reserved(self) -> float:
        _, reserved_bytes = self._current_alloc_and_reserved_bytes()
        return self._bytes_to_gb(reserved_bytes)

    def get_max_memory_allocated(self) -> float:
        # Our own tracked peak since backend init or last reset.
        return self._bytes_to_gb(self._peak_allocated_bytes)

    def get_max_memory_reserved(self) -> float:
        return self._bytes_to_gb(self._peak_reserved_bytes)

    # ---- Memory / execution control ----

    def empty_cache(self):
        torch.mps.empty_cache()

    def synchronize(self):
        torch.mps.synchronize()

    def reset_peak_memory_stats(self):
        """
        For CUDA this resets internal counters; for MPS we just reset our own
        tracked peaks. Semantics are close enough for dev.
        """
        self._peak_allocated_bytes = 0
        self._peak_reserved_bytes = 0
    
    def reset_accumulated_memory_stats(self):
        """No-op for MPS (CUDA-specific function)."""
        pass
    
    def ipc_collect(self):
        """No-op for MPS (CUDA-specific function)."""
        pass

    def set_seed(self, seed: int):
        # No torch.mps.manual_seed; torch.manual_seed covers MPS.
        torch.manual_seed(seed)

    # ---- Diagnostics / reporting ----

    def get_memory_summary(self, abbreviated: bool = True) -> str:
        alloc_bytes, reserved_bytes = self._current_alloc_and_reserved_bytes()
        alloc_gb = self._bytes_to_gb(alloc_bytes)
        reserved_gb = self._bytes_to_gb(reserved_bytes)
        peak_alloc_gb = self.get_max_memory_allocated()
        peak_reserved_gb = self.get_max_memory_reserved()

        if abbreviated:
            return (
                "MPS memory: "
                f"allocated={alloc_gb:.3f} GB, "
                f"reserved={reserved_gb:.3f} GB, "
                f"peak_alloc={peak_alloc_gb:.3f} GB, "
                f"peak_reserved={peak_reserved_gb:.3f} GB"
            )
        else:
            return (
                "MPS memory summary\n"
                f"  allocated (current): {alloc_gb:.3f} GB\n"
                f"  reserved (current):  {reserved_gb:.3f} GB\n"
                f"  peak allocated:      {peak_alloc_gb:.3f} GB\n"
                f"  peak reserved:       {peak_reserved_gb:.3f} GB\n"
                "  NOTE: peaks are tracked in Python, not by MPS itself.\n"
            )

    def get_memory_snapshot(self) -> list:
        # MPS doesn't expose detailed allocation snapshots like CUDA.
        # Return empty list so consuming code can safely iterate.
        # The detailed memory info is available via get_memory_summary() instead.
        return []

    # ---- Device properties ----

    def get_device_properties(self, device_id: int = 0):
        return {
            "name": "Apple MPS",
            "index": device_id,
            "type": "mps",
            "total_memory": None,  # not exposed
        }

    def get_current_device_id(self) -> int:
        return 0
    
    def get_max_batch_size(
        self,
        requested_batch_size: int,
        n_cols: int = 0,
        n_attention_heads: int = 16,
        has_relationship_features: bool = False,
        ops_per_pair: int = 1,  # Default 1 (fusion mode); 9 if unfused
        min_batch_size: int = 32,
    ) -> int:
        """
        MPS has INT_MAX constraint on tensor dimensions.
        
        With relationship features, the attention matrix can exceed INT_MAX:
        - seq_len = 1 (CLS) + n_cols + n_pairs * ops_per_pair
        - attention shape: (batch * n_heads, seq_len, seq_len)
        - If batch * n_heads * seq_len^2 > INT_MAX → crash with:
          "NDArray dimension length > INT_MAX"
        """
        max_batch = requested_batch_size
        
        if has_relationship_features and n_cols > 0:
            # Calculate sequence length with relationship tokens
            n_pairs = n_cols * (n_cols - 1) // 2
            seq_len = 1 + n_cols + n_pairs * ops_per_pair
            
            # Calculate max safe batch size: batch * n_heads * seq_len^2 <= INT_MAX
            INT_MAX = 2**31 - 1
            mps_max = INT_MAX // (n_attention_heads * seq_len * seq_len)
            
            # Round down to power of 2 for GPU efficiency
            if mps_max > 0:
                mps_max = 2 ** int(math.log2(mps_max))
                mps_max = max(min_batch_size, mps_max)
            else:
                mps_max = min_batch_size
            
            if mps_max < max_batch:
                logger.warning("=" * 80)
                logger.warning("⚠️  MPS BATCH SIZE LIMIT: Reducing batch size to prevent INT_MAX overflow")
                logger.warning(f"   Relationship features create {n_pairs * ops_per_pair} extra tokens")
                logger.warning(f"   Total sequence length: {seq_len} (1 CLS + {n_cols} cols + {n_pairs * ops_per_pair} rel tokens)")
                logger.warning(f"   Attention matrix elements: batch × {n_attention_heads} heads × {seq_len}² = very large")
                logger.warning(f"   Max safe batch size for MPS: {mps_max}")
                logger.warning(f"   Reducing batch_size: {requested_batch_size} → {mps_max}")
                logger.warning("=" * 80)
                max_batch = mps_max
        
        return max(min_batch_size, max_batch)

    def __repr__(self) -> str:
        return f"<AppleGPU device={self._device}>"


# ============================================================================
# CPU Backend (No GPU)
# ============================================================================

class NoGPU(GPUBackend):
    """CPU-only backend (no accelerator). Tracks system RAM instead of GPU RAM."""

    _BYTES_IN_GB = 1024 ** 3

    def __init__(self):
        self._device = torch.device("cpu")
        logger.info("💻 Initialized CPU backend (no GPU / accelerator)")

        # Track "peaks" for parity with GPU backends
        self._peak_used_ram_bytes = 0

    # ---- Core device info ----

    def get_device(self) -> torch.device:
        return self._device

    def get_device_type(self) -> str:
        return "cpu"

    def is_available(self) -> bool:
        return True

    # ---- Memory tracking (system RAM) ----

    def _bytes_to_gb(self, n: int) -> float:
        return float(n) / self._BYTES_IN_GB

    def _update_peak(self, used_bytes: int):
        if used_bytes > self._peak_used_ram_bytes:
            self._peak_used_ram_bytes = used_bytes

    def _current_ram_bytes(self) -> int:
        if psutil is None:
            return 0
        used = psutil.virtual_memory().used
        self._update_peak(used)
        return used

    def get_memory_allocated(self) -> float:
        """Return **used system RAM**, matching CUDA/MPS GB units."""
        return self._bytes_to_gb(self._current_ram_bytes())

    def get_memory_reserved(self) -> float:
        """For CPU, 'reserved' is just total RAM."""
        if psutil is None:
            return 0.0
        total = psutil.virtual_memory().total
        return self._bytes_to_gb(total)

    def get_max_memory_allocated(self) -> float:
        return self._bytes_to_gb(self._peak_used_ram_bytes)

    def get_max_memory_reserved(self) -> float:
        return self.get_memory_reserved()

    # ---- Execution / cache control ----

    def empty_cache(self):
        pass  # No CPU caching equivalent

    def synchronize(self):
        pass  # CPU ops are synchronous

    def reset_peak_memory_stats(self):
        self._peak_used_ram_bytes = 0
    
    def reset_accumulated_memory_stats(self):
        """No-op for CPU (CUDA-specific function)."""
        pass
    
    def ipc_collect(self):
        """No-op for CPU (CUDA-specific function)."""
        pass

    def set_seed(self, seed: int):
        torch.manual_seed(seed)

    # ---- Diagnostics ----

    def get_memory_summary(self, abbreviated: bool = True) -> str:
        if psutil is None:
            return "CPU RAM: psutil not available"
        
        vm = psutil.virtual_memory()
        used = self._bytes_to_gb(vm.used)
        avail = self._bytes_to_gb(vm.available)
        total = self._bytes_to_gb(vm.total)
        peak = self.get_max_memory_allocated()

        if abbreviated:
            return (
                f"CPU RAM: used={used:.3f} GB, available={avail:.3f} GB, peak={peak:.3f} GB"
            )
        else:
            return (
                "CPU RAM summary\n"
                f"  used:      {used:.3f} GB\n"
                f"  available: {avail:.3f} GB\n"
                f"  total:     {total:.3f} GB\n"
                f"  peak used: {peak:.3f} GB\n"
            )

    def get_memory_snapshot(self) -> list:
        # Return list with single summary dict for compatibility with consuming code
        # (which expects a list of allocation dicts like CUDA provides)
        if psutil is None:
            return []
        
        vm = psutil.virtual_memory()
        return [{
            "backend": "cpu",
            "used_bytes": vm.used,
            "available_bytes": vm.available,
            "total_bytes": vm.total,
            "used_gb": self._bytes_to_gb(vm.used),
            "available_gb": self._bytes_to_gb(vm.available),
            "total_gb": self._bytes_to_gb(vm.total),
            "peak_used_gb": self.get_max_memory_allocated(),
        }]

    # ---- Device props ----

    def get_device_properties(self, device_id: int = 0):
        if psutil is None:
            return {
                "name": "CPU",
                "index": device_id,
                "type": "cpu",
                "total_memory_gb": None,
            }
        
        vm = psutil.virtual_memory()
        return {
            "name": "CPU",
            "index": device_id,
            "type": "cpu",
            "total_memory_gb": self._bytes_to_gb(vm.total),
        }

    def get_current_device_id(self) -> int:
        return 0
    
    def get_max_batch_size(
        self,
        requested_batch_size: int,
        n_cols: int = 0,
        n_attention_heads: int = 16,
        has_relationship_features: bool = False,
        ops_per_pair: int = 1,  # Default 1 (fusion mode); 9 if unfused
        min_batch_size: int = 32,
    ) -> int:
        """CPU has no special batch size constraints."""
        return requested_batch_size

    def __repr__(self) -> str:
        return "<NoGPU device=cpu>"


# ============================================================================
# Backend Factory & Global Instance
# ============================================================================

def _detect_backend() -> GPUBackend:
    """Auto-detect and create the appropriate GPU backend."""
    if torch.cuda.is_available():
        return NvidiaGPU()
    elif torch.backends.mps.is_available():
        return AppleGPU()
    else:
        return NoGPU()


# Global backend instance
_backend: GPUBackend = None


def _get_backend() -> GPUBackend:
    """Get the current backend, initializing if needed."""
    global _backend
    if _backend is None:
        _backend = _detect_backend()
    return _backend


def set_backend_cpu():
    """Force CPU backend."""
    global _backend
    _backend = NoGPU()


def set_backend_gpu():
    """Force GPU backend (CUDA or MPS)."""
    global _backend
    if torch.cuda.is_available():
        _backend = NvidiaGPU()
    elif torch.backends.mps.is_available():
        _backend = AppleGPU()
    else:
        raise RuntimeError("No GPU available. Cannot set GPU backend.")


def reset_backend():
    """Reset to auto-detected backend."""
    global _backend
    _backend = _detect_backend()


# ============================================================================
# Public API - delegates to current backend
# ============================================================================

def get_device() -> torch.device:
    """Get the current torch device."""
    return _get_backend().get_device()


def get_device_type() -> str:
    """Get device type as string ('cuda', 'mps', or 'cpu')."""
    return _get_backend().get_device_type()


def is_gpu_available() -> bool:
    """Check if any GPU (CUDA or MPS) is available."""
    # CRITICAL: If /sphere/CPU_SP exists, force CPU mode for single predictor training
    if os.path.exists('/sphere/CPU_SP'):
        return False
    backend = _get_backend()
    return backend.is_available() and backend.get_device_type() != "cpu"


def is_cuda_available() -> bool:
    """Check if CUDA GPU is available."""
    return torch.cuda.is_available()


def is_mps_available() -> bool:
    """Check if MPS (Apple Silicon) GPU is available."""
    return torch.backends.mps.is_available()


def get_max_batch_size(
    requested_batch_size: int,
    n_cols: int = 0,
    n_attention_heads: int = 16,
    has_relationship_features: bool = False,
    ops_per_pair: int = 1,  # Default 1 (fusion mode); 9 if unfused
    min_batch_size: int = 32,
) -> int:
    """
    Calculate the maximum safe batch size for the current GPU device.
    
    This is the SINGLE function to call for batch size limits. It handles:
    - MPS (Apple Silicon): INT_MAX overflow in attention computation
    - CUDA: Memory constraints (future)
    - CPU: No constraints
    
    Call this instead of scattering GPU-specific batch size logic throughout the codebase.
    
    Args:
        requested_batch_size: The batch size you want to use
        n_cols: Number of columns in the dataset (needed for MPS with relationship features)
        n_attention_heads: Number of attention heads in transformer (default: 16)
        has_relationship_features: Whether relationship features are enabled
        ops_per_pair: Number of relationship operations per column pair (default: 8)
        min_batch_size: Minimum viable batch size (default: 32 for InfoNCE)
    
    Returns:
        Safe batch size (<= requested_batch_size, >= min_batch_size)
    """
    return _get_backend().get_max_batch_size(
        requested_batch_size=requested_batch_size,
        n_cols=n_cols,
        n_attention_heads=n_attention_heads,
        has_relationship_features=has_relationship_features,
        ops_per_pair=ops_per_pair,
        min_batch_size=min_batch_size,
    )


def get_gpu_memory_allocated() -> float:
    """Get allocated GPU memory in GB (0.0 if not supported)."""
    return _get_backend().get_memory_allocated()


def get_gpu_memory_reserved() -> float:
    """Get reserved GPU memory in GB (0.0 if not supported)."""
    return _get_backend().get_memory_reserved()


def get_max_gpu_memory_allocated() -> float:
    """Get peak allocated GPU memory in GB (0.0 if not supported)."""
    return _get_backend().get_max_memory_allocated()


def get_max_gpu_memory_reserved() -> float:
    """Get peak reserved GPU memory in GB (0.0 if not supported)."""
    return _get_backend().get_max_memory_reserved()


def empty_gpu_cache():
    """Clear GPU memory cache (no-op if not supported)."""
    _get_backend().empty_cache()


INT_MAX = 2**31 - 1


def check_mps_dimension_safe(tensor: torch.Tensor, context: str = "") -> bool:
    """
    Check if a tensor has any dimension > INT_MAX (MPS limit).
    
    Call this before operations that MPS might choke on.
    
    Args:
        tensor: The tensor to check
        context: Description of where this check is happening (for debug output)
    
    Returns:
        True if safe, False if any dimension exceeds INT_MAX
    
    Raises:
        ValueError if any dimension exceeds INT_MAX (with detailed debug info)
    """
    for dim_idx, dim_size in enumerate(tensor.shape):
        if dim_size > INT_MAX:
            msg = (
                f"💥 MPS INT_MAX OVERFLOW at {context}\n"
                f"   Tensor shape: {tensor.shape}\n"
                f"   Dimension {dim_idx} = {dim_size:,} > INT_MAX ({INT_MAX:,})\n"
                f"   Total elements: {tensor.numel():,}\n"
                f"   Dtype: {tensor.dtype}, Device: {tensor.device}"
            )
            logger.error(msg)
            raise ValueError(msg)
    
    # Also check numel() since some ops flatten internally
    numel = tensor.numel()
    if numel > INT_MAX:
        msg = (
            f"💥 MPS INT_MAX OVERFLOW (numel) at {context}\n"
            f"   Tensor shape: {tensor.shape}\n"
            f"   numel() = {numel:,} > INT_MAX ({INT_MAX:,})\n"
            f"   This may fail if the tensor gets flattened\n"
            f"   Dtype: {tensor.dtype}, Device: {tensor.device}"
        )
        logger.warning(msg)
        # Don't raise - just warn, since not all ops flatten
    
    return True


def debug_mps_tensor_shapes(*tensors_with_names):
    """
    Debug utility: print tensor shapes and check for INT_MAX violations.
    
    Usage:
        debug_mps_tensor_shapes(
            ("x after view", x),
            ("attention_weights", attn),
            ("output", out),
        )
    """
    logger.info("=" * 80)
    logger.info("🔍 MPS TENSOR SHAPE DEBUG:")
    for name, tensor in tensors_with_names:
        if tensor is None:
            logger.info(f"   {name}: None")
            continue
        shape_str = str(tensor.shape)
        numel = tensor.numel()
        max_dim = max(tensor.shape) if tensor.shape else 0
        warning = " ⚠️ EXCEEDS INT_MAX!" if max_dim > INT_MAX or numel > INT_MAX else ""
        logger.info(f"   {name}: shape={shape_str}, numel={numel:,}, max_dim={max_dim:,}{warning}")
    logger.info("=" * 80)


def synchronize_gpu():
    """Synchronize GPU operations (no-op if not supported)."""
    _get_backend().synchronize()


def reset_gpu_peak_memory_stats():
    """Reset GPU peak memory statistics (no-op if not supported)."""
    _get_backend().reset_peak_memory_stats()


def reset_gpu_accumulated_memory_stats():
    """Reset GPU accumulated memory statistics (CUDA only, no-op for others)."""
    _get_backend().reset_accumulated_memory_stats()


def ipc_collect_gpu():
    """Collect IPC memory (CUDA only, no-op for others)."""
    _get_backend().ipc_collect()


def aggressive_clear_gpu_cache(iterations: int = 3, do_gc: bool = True):
    """
    Aggressively clear GPU cache with multiple iterations and optional garbage collection.
    
    This function handles all GPU type checking internally - no need to check is_gpu_available()
    or is_cuda_available() before calling. Works with CUDA, MPS, and other backends.
    
    Args:
        iterations: Number of cache clear iterations (default: 3)
        do_gc: Whether to run garbage collection between iterations (default: True)
    
    Returns:
        Dict with memory stats after clearing, or None if GPU not available
    """
    import gc
    
    if not is_gpu_available():
        return None
    
    backend = _get_backend()
    results = {}
    
    for i in range(iterations):
        if do_gc:
            gc.collect()
        
        backend.empty_cache()
        backend.ipc_collect()  # CUDA-specific, no-op on MPS/CPU
        backend.synchronize()
        
        # Get memory stats after this iteration
        allocated = backend.get_memory_allocated()
        reserved = backend.get_memory_reserved()
        results[f'after_iteration_{i+1}'] = {
            'allocated_gb': allocated,
            'reserved_gb': reserved
        }
    
    # Try to reset stats (CUDA-specific, no-op on MPS/CPU)
    try:
        backend.reset_peak_memory_stats()
        backend.reset_accumulated_memory_stats()
    except Exception:
        pass
    
    # Final stats
    results['final'] = {
        'allocated_gb': backend.get_memory_allocated(),
        'reserved_gb': backend.get_memory_reserved(),
        'max_allocated_gb': backend.get_max_memory_allocated(),
        'max_reserved_gb': backend.get_max_memory_reserved()
    }
    
    return results


def set_gpu_seed(seed: int):
    """Set random seed for GPU operations."""
    _get_backend().set_seed(seed)


def get_gpu_memory_summary(abbreviated: bool = True) -> str:
    """Get GPU memory summary string (empty string if not supported)."""
    return _get_backend().get_memory_summary(abbreviated=abbreviated)


def get_gpu_memory_snapshot() -> dict:
    """Get GPU memory snapshot dict (empty dict if not supported)."""
    return _get_backend().get_memory_snapshot()


def get_gpu_device_properties(device_id: int = 0):
    """Get GPU device properties (returns None if not supported)."""
    return _get_backend().get_device_properties(device_id)


def get_gpu_current_device_id() -> int:
    """Get current GPU device ID (returns 0 if not supported)."""
    return _get_backend().get_current_device_id()


def get_backend_name() -> str:
    """Get the name of the current backend."""
    return _get_backend().__class__.__name__


def get_gpu_device_count() -> int:
    """Get the number of GPU devices available (CUDA only, returns 1 for MPS/CPU)."""
    backend = _get_backend()
    if isinstance(backend, NvidiaGPU):
        return torch.cuda.device_count()
    elif is_gpu_available():
        # MPS only has 1 device
        return 1
    else:
        # CPU
        return 0


def get_gpu_device_name(device_id: int = 0) -> str:
    """
    Get the name of a GPU device.
    
    Args:
        device_id: Device ID (only meaningful for CUDA)
        
    Returns:
        Device name string, or empty string if not available
    """
    backend = _get_backend()
    if isinstance(backend, NvidiaGPU):
        return torch.cuda.get_device_name(device_id)
    elif isinstance(backend, AppleGPU):
        # MPS doesn't expose device name, but we know it's Apple Silicon
        return "Apple M-series GPU (MPS)"
    else:
        return "CPU"


def log_gpu_memory(
    prefix: str = "",
    level: str = "info",
    log_func=None
) -> dict:
    """
    Log GPU memory stats in a consistent format across all GPU types.
    
    This function handles all GPU type checking internally - works with CUDA, MPS, and CPU.
    On CUDA, logs allocated/reserved/free memory. On MPS/CPU, returns early with empty dict.
    
    Args:
        prefix: Prefix string for the log message (e.g., "BEFORE FORWARD [e=5, b=2]")
        level: Log level - "info", "debug", "warning", "error" (default: "info")
        log_func: Optional custom logger function (default: uses module logger)
        
    Returns:
        dict with memory stats: {'allocated_gb', 'reserved_gb', 'total_gb', 'free_gb'}
        Empty dict if CUDA not available (MPS/CPU don't have equivalent memory APIs)
    
    Example:
        log_gpu_memory("BEFORE FORWARD [e=5, b=2]", level="debug")
        # Output: "📊 GPU MEMORY: BEFORE FORWARD [e=5, b=2]: Alloc=2.34GB, Reserved=3.12GB, Free=10.54GB"
    """
    # Only works on CUDA - MPS/CPU don't have equivalent memory tracking APIs
    if not is_cuda_available():
        return {}
    
    if log_func is None:
        log_func = getattr(logger, level, logger.info)
    
    try:
        backend = _get_backend()
        device_idx = backend.get_current_device_id()
        device_props = backend.get_device_properties(device_idx)
        
        if device_props is None:
            return {}
        
        total_gb = device_props.total_memory / (1024**3)
        allocated_gb = backend.get_memory_allocated()
        reserved_gb = backend.get_memory_reserved()
        free_gb = total_gb - reserved_gb
        
        msg = f"📊 GPU MEMORY: {prefix}: Alloc={allocated_gb:.2f}GB, Reserved={reserved_gb:.2f}GB, Free={free_gb:.2f}GB"
        log_func(msg)
        
        return {
            'allocated_gb': allocated_gb,
            'reserved_gb': reserved_gb,
            'total_gb': total_gb,
            'free_gb': free_gb
        }
    except Exception as ex:
        logger.debug(f"Unable to log GPU memory stats: {ex}")
        return {}


def log_gpu_memory_detailed(
    prefix: str = "",
    model=None,
    level: str = "error",
    log_func=None
) -> dict:
    """
    Log detailed GPU memory breakdown with model size estimation.
    
    This is for error/diagnostic contexts where you need maximum detail about memory usage.
    Only works on CUDA - returns empty dict on MPS/CPU.
    
    Args:
        prefix: Prefix for log messages (e.g., "OOM ERROR CONTEXT")
        model: Optional PyTorch model to estimate parameter/gradient memory usage
        level: Log level - "info", "debug", "warning", "error" (default: "error")
        log_func: Optional custom logger function (default: uses module logger at specified level)
        
    Returns:
        dict with detailed memory stats or empty dict if CUDA not available
        
    Example:
        log_gpu_memory_detailed("OOM ERROR CONTEXT", model=self.encoder, level="error")
    """
    if not is_cuda_available():
        return {}
    
    if log_func is None:
        log_func = getattr(logger, level, logger.error)
    
    try:
        backend = _get_backend()
        device_idx = backend.get_current_device_id()
        device_props = backend.get_device_properties(device_idx)
        
        if device_props is None:
            return {}
        
        total_gb = device_props.total_memory / (1024**3)
        allocated_gb = backend.get_memory_allocated()
        reserved_gb = backend.get_memory_reserved()
        max_allocated_gb = backend.get_max_memory_allocated()
        free_gb = total_gb - reserved_gb
        
        log_func(f"   📊 GPU MEMORY BREAKDOWN: {prefix}")
        log_func(f"      GPU: {device_props.name}")
        log_func(f"      Total:     {total_gb:.2f} GiB")
        log_func(f"      Allocated: {allocated_gb:.2f} GiB ({allocated_gb/total_gb*100:.1f}%)")
        log_func(f"      Reserved:  {reserved_gb:.2f} GiB ({reserved_gb/total_gb*100:.1f}%)")
        log_func(f"      Peak:      {max_allocated_gb:.2f} GiB ({max_allocated_gb/total_gb*100:.1f}%)")
        log_func(f"      Free:      {free_gb:.2f} GiB ({free_gb/total_gb*100:.1f}%)")
        
        result = {
            'total_gb': total_gb,
            'allocated_gb': allocated_gb,
            'reserved_gb': reserved_gb,
            'max_allocated_gb': max_allocated_gb,
            'free_gb': free_gb,
            'device_name': device_props.name
        }
        
        # Estimate model size if provided
        if model is not None:
            try:
                model_params = sum(p.numel() * p.element_size() for p in model.parameters())
                model_grads = sum(p.numel() * p.element_size() for p in model.parameters() if p.grad is not None)
                model_gb = (model_params + model_grads) / (1024**3)
                log_func(f"      Model:     ~{model_gb:.2f} GiB (params + grads)")
                result['model_gb'] = model_gb
                
                # Estimate activations
                activations_gb = allocated_gb - model_gb
                if activations_gb > 0:
                    log_func(f"      Activations: ~{activations_gb:.2f} GiB (batch tensors, intermediate results)")
                    result['activations_gb'] = activations_gb
            except Exception as model_err:
                logger.debug(f"Could not estimate model memory: {model_err}")
        
        return result
        
    except Exception as ex:
        logger.debug(f"Could not get detailed GPU memory stats: {ex}")
        return {}


def move_to_cpu_if_needed(tensor: torch.Tensor, detach: bool = True) -> torch.Tensor:
    """
    Move tensor to CPU if it's on a GPU device (CUDA, MPS, etc.).
    
    Args:
        tensor: PyTorch tensor (may be on any device)
        detach: If True, detach from computation graph before moving
        
    Returns:
        Tensor on CPU (or original tensor if already on CPU)
    """
    if tensor.device.type != 'cpu':
        if detach:
            return tensor.detach().cpu()
        else:
            return tensor.cpu()
    else:
        if detach:
            return tensor.detach()
        else:
            return tensor


def compare_gpu_cpu_speed(
    operation_fn,
    input_data,
    num_iterations: int = 10,
    warmup_iterations: int = 3
) -> dict:
    """
    Compare GPU vs CPU speed for a given operation.
    
    Args:
        operation_fn: Function that takes input_data and performs the operation
                     Should accept a device parameter: operation_fn(input_data, device)
        input_data: Input data for the operation (will be moved to appropriate device)
        num_iterations: Number of iterations to run for timing (default: 10)
        warmup_iterations: Number of warmup iterations before timing (default: 3)
    
    Returns:
        dict with keys:
            - 'gpu_time': Average time per iteration on GPU (seconds), or None if GPU unavailable
            - 'cpu_time': Average time per iteration on CPU (seconds)
            - 'speedup': GPU speedup ratio (gpu_time / cpu_time), or None if GPU unavailable
            - 'faster_device': 'gpu' or 'cpu' or None
            - 'gpu_available': bool
    """

    
    results = {
        'gpu_time': None,
        'cpu_time': None,
        'speedup': None,
        'faster_device': None,
        'gpu_available': is_gpu_available()
    }
    
    # Benchmark CPU
    try:
        cpu_times = []
        for i in range(warmup_iterations + num_iterations):
            start = time.time()
            operation_fn(input_data, torch.device('cpu'))
            if i >= warmup_iterations:
                cpu_times.append(time.time() - start)
        results['cpu_time'] = sum(cpu_times) / len(cpu_times)
    except Exception as e:
        logger.error(f"CPU benchmark failed: {e}")
        return results
    
    # Benchmark GPU if available
    if results['gpu_available']:
        try:
            device = get_device()
            gpu_times = []
            for i in range(warmup_iterations + num_iterations):
                start = time.time()
                operation_fn(input_data, device)
                if device.type == 'cuda':
                    torch.cuda.synchronize()
                elif device.type == 'mps':
                    # MPS doesn't have explicit sync, but we can wait a bit
                    import time as time_module
                    time_module.sleep(0.001)  # Small delay to ensure completion
                if i >= warmup_iterations:
                    gpu_times.append(time.time() - start)
            results['gpu_time'] = sum(gpu_times) / len(gpu_times)
            
            # Calculate speedup
            if results['cpu_time'] > 0:
                results['speedup'] = results['cpu_time'] / results['gpu_time']
                results['faster_device'] = 'gpu' if results['speedup'] > 1.0 else 'cpu'
            else:
                results['faster_device'] = 'gpu'
        except Exception as e:
            logger.error(f"GPU benchmark failed: {e}")
            results['gpu_available'] = False
    
    # If GPU not available or failed, CPU is the only option
    if results['gpu_time'] is None:
        results['faster_device'] = 'cpu'
    
    return results


# Convenience aliases for backward compatibility
set_device_cpu = set_backend_cpu
set_device_gpu = set_backend_gpu
reset_device = reset_backend

# Initialize backend on import
_backend = _detect_backend()

