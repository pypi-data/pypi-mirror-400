#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
import base64
import hashlib
import io
import logging
import math
import traceback

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# Import logging configuration FIRST to ensure timestamps
from featrix.neural.logging_config import configure_logging
configure_logging()

from featrix.neural.gpu_utils import get_device
from featrix.neural.gpu_utils import (
    is_gpu_available, 
    get_gpu_memory_allocated,
    get_gpu_memory_reserved, 
    get_max_gpu_memory_allocated,
    empty_gpu_cache
)
from featrix.neural.featrix_token import set_not_present
from featrix.neural.featrix_token import Token
from featrix.neural.featrix_token import TokenStatus
from featrix.neural.model_config import ColumnType
from featrix.neural.model_config import SimpleMLPConfig
from featrix.neural.model_config import StringEncoderConfig
from featrix.neural.simple_mlp import SimpleMLP
from featrix.neural.simple_string_cache import SimpleStringCache
from featrix.neural.sphere_config import get_config
from featrix.neural.platform_utils import os_is_featrix_firmware

from featrix_string_server_client import StringServerClient
import socket
import platform


logger = logging.getLogger(__name__)

torch.set_printoptions(threshold=10_000)
torch.set_printoptions(profile="full")
torch.set_printoptions(linewidth=240)

# from .exceptions import NaNModelCollapseException


import os
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        
string_server_client = None

# Removed sentence transformer device caching - no longer needed

# Main process PID - set once at module import time, never updated across spawn/fork
# This allows us to detect if we're in a spawned/forked worker process
_main_pid = os.getpid()

# CRITICAL: Workers must use CPU to avoid VRAM waste
# Each worker would allocate ~600MB VRAM for sentence model
# With 8 workers, that's 4.8GB wasted!

def _init_string_server_client():
    """
    Initialize the string server client with automatic fallback.
    
    The client handles its own URL resolution and fallback:
    - Primary: http://taco.local:9000 (direct to string server)
    - Intermediate: http://sphere-compute.featrix.com:8000 (taco string server via public DNS)
    - Final Fallback: https://sphere-api.featrix.com/strings/* (proxy endpoints)
    
    Job tracking information is read from environment variables:
    - FEATRIX_JOB_TYPE: Job type for diagnostics (e.g., "training")
    - FEATRIX_JOB_ID: Job ID for diagnostics (e.g., "model-v2-epoch-5")
    - FEATRIX_JOB_COMPUTE_NODE: Compute node identifier
    """
    global string_server_client
    
    if string_server_client is not None:
        return string_server_client
    
    # CRITICAL: Print what URL we WOULD use BEFORE trying to import
    # Check environment variables and config that might affect URL
    import os
    potential_urls = []
    
    # Read job tracking info from environment variables
    job_type = os.getenv('FEATRIX_JOB_TYPE')
    job_id = os.getenv('FEATRIX_JOB_ID')
    job_compute_node = os.getenv('FEATRIX_JOB_COMPUTE_NODE')
    
    # Check common environment variables
    env_vars_to_check = ['STRING_SERVER_URL', 'FEATRIX_STRING_SERVER_URL', 'STRING_SERVER_HOST', 'FEATRIX_STRING_SERVER_HOST']
    for env_var in env_vars_to_check:
        val = os.getenv(env_var)
        if val:
            potential_urls.append(f"{env_var}={val}")
    
    # CRITICAL: Check if taco.local resolves - if it does, we should prioritize it and NOT fall back to other domains
    taco_local_resolves = False
    try:
        socket.gethostbyname("taco.local")
        taco_local_resolves = True
        logger.info("✅ taco.local resolves - will prioritize it and keep retrying (no fallback to other domains)")
    except socket.gaierror:
        logger.info("⚠️  taco.local does not resolve - will use fallback URLs")
    
    # Check if we're on firmware box
    is_firmware = os_is_featrix_firmware()
    
    # URLs to try in order
    if taco_local_resolves:
        # If taco.local resolves, ONLY use it - don't fall back to other domains
        fallback_urls = [
            "http://taco.local:9000"
        ]
        logger.info("🌐🌐🌐 ATTEMPTING TO INITIALIZE STRING SERVER CLIENT 🌐🌐🌐")
        if is_firmware:
            logger.info(f"   🔧 FIRMWARE BOX: taco.local resolves - using ONLY taco.local:9000")
            logger.info(f"   🔧 Will fail hard after 30 minutes if taco.local is unreachable")
            logger.info(f"   🔧 Will send Slack alert after 2 minutes of downtime")
        else:
            logger.info(f"   taco.local resolves - using ONLY taco.local:9000 (no fallbacks)")
    else:
        # If taco.local doesn't resolve, use full fallback chain (only on non-firmware)
        if is_firmware:
            # On firmware, we MUST have taco.local - fail if it doesn't resolve
            logger.error("❌❌❌ FIRMWARE BOX: taco.local does not resolve - this is a critical error! ❌❌❌")
            raise RuntimeError(
                "On Featrix firmware box, taco.local MUST resolve. "
                "This indicates a DNS or network configuration problem. "
                "Check /etc/hosts or DNS configuration."
            )
        fallback_urls = [
            "http://taco.local:9000",
            "http://sphere-compute.featrix.com:9000", # 9000 is the strings server.
            "https://sphere-api.featrix.com/strings/encode"
        ]
        logger.info("🌐🌐🌐 ATTEMPTING TO INITIALIZE STRING SERVER CLIENT 🌐🌐🌐")
        logger.info(f"   Fallback chain ({len(fallback_urls)} URLs):")
        for i, url in enumerate(fallback_urls, 1):
            logger.info(f"      {i}. {url}")
    
    if potential_urls:
        logger.info(f"   Environment variables: {', '.join(potential_urls)}")
    else:
        logger.info("   No relevant environment variables found")
    
    # CRITICAL: Suppress noisy WARNING/INFO logs from string server client BEFORE importing it
    # Set the logger level to ERROR to avoid spam from failed taco.local connection attempts
    client_logger = logging.getLogger('featrix_string_server_client.client')
    client_logger.setLevel(logging.ERROR)
    client_logger.propagate = False  # Don't propagate to root logger
    
    try:
        # Build user agent components to identify caller
        try:
            # Try to get firmware version
            firmware_version = "unknown"
            try:
                from version import get_version
                v = get_version()
                firmware_version = str(v)
            except:
                try:
                    with open('/sphere/VERSION', 'r') as f:
                        firmware_version = f.read().strip()
                except:
                    pass
            
            # Get hostname (taco, burrito, churro, etc.)
            hostname = socket.gethostname()
            
            # Detect if running on server (Linux) or desktop (macOS)
            system = platform.system()
            if system == "Darwin":
                # macOS - Desktop
                macos_version = platform.mac_ver()[0]
                user_agent = f"Featrix-Desktop/{firmware_version} macOS/{macos_version} ({hostname})"
            else:
                # Linux - Firmware
                user_agent = f"Featrix-Firmware/{firmware_version} ({hostname})"
        except Exception as e:
            logger.debug(f"Could not build user agent: {e}")
            user_agent = "Featrix-Client/unknown"
            hostname = socket.gethostname() if 'socket' in dir() else "unknown"
            firmware_version = "unknown"
        
        # Use client defaults - it handles taco.local -> sphere-api fallback automatically
        # Pass user_agent, hostname, firmware_version, job_type, job_id, and job_compute_node if the client supports them
        client_kwargs = {}
        if user_agent:
            client_kwargs['user_agent'] = user_agent
        if hostname:
            client_kwargs['hostname'] = hostname
        if firmware_version:
            client_kwargs['firmware_version'] = firmware_version
        if job_type:
            client_kwargs['job_type'] = job_type
        if job_id:
            client_kwargs['job_id'] = job_id
        if job_compute_node:
            client_kwargs['job_compute_node'] = job_compute_node
        
        try:
            string_server_client = StringServerClient(**client_kwargs)  # pylint: disable=unexpected-keyword-arg
        except TypeError as e:
            # Old client version might not support all parameters
            # Try with just user_agent first
            if 'user_agent' in client_kwargs:
                try:
                    string_server_client = StringServerClient(user_agent=user_agent)  # pylint: disable=unexpected-keyword-arg
                    logger.debug(f"String server client doesn't support job_type/job_id parameters (old version)")
                except TypeError:
                    # Fall back to no parameters
                    string_server_client = StringServerClient()
                    logger.debug(f"String server client doesn't support user_agent parameter (old version)")
            else:
                string_server_client = StringServerClient()
                logger.debug(f"String server client doesn't support parameters: {e}")
        
        # CRITICAL: Print the FULL URL including protocol immediately - try ALL possible attribute names
        full_url = None
        url_attrs = ['base_url', 'url', 'server_url', 'endpoint', '_base_url', '_url', '_server_url', '_endpoint', 'primary_url', 'fallback_url']
        for attr in url_attrs:
            try:
                if hasattr(string_server_client, attr):
                    full_url = getattr(string_server_client, attr)
                    logger.info(f"🌐🌐🌐 String server client FULL URL (from {attr}): {full_url} 🌐🌐🌐")
                    break
            except Exception as e:
                logger.debug(f"Could not get {attr}: {e}")
        
        # If we still don't have a URL, print ALL attributes for debugging
        if full_url is None:
            logger.error("❌❌❌ COULD NOT FIND URL IN CLIENT - PRINTING ALL ATTRIBUTES:")
            try:
                all_attrs = dir(string_server_client)
                logger.error(f"   Client type: {type(string_server_client)}")
                logger.error(f"   All attributes: {all_attrs}")
                # Try to get any string-like attributes
                for attr in all_attrs:
                    if not attr.startswith('__'):
                        try:
                            val = getattr(string_server_client, attr)
                            if isinstance(val, str) and ('http' in val.lower() or 'url' in attr.lower() or 'server' in attr.lower()):
                                logger.error(f"   {attr} = {val}")
                        except Exception:
                            pass
            except Exception as e:
                logger.error(f"   Could not inspect client: {e}")
        else:
            logger.info(f"🌐🌐🌐 CONFIRMED FULL URL: {full_url} 🌐🌐🌐")
        
        logger.info(f"✅ Initialized string server client with {len(fallback_urls)}-URL fallback chain")
        
        # Store firmware status in client for retry logic
        if hasattr(string_server_client, '_is_firmware'):
            string_server_client._is_firmware = is_firmware
        if hasattr(string_server_client, '_taco_local_resolves'):
            string_server_client._taco_local_resolves = taco_local_resolves
        
        return string_server_client
    except ImportError as import_err:
        raise ImportError(
            f"Failed to import required dependency 'featrix_string_server_client': {import_err}\n\n"
            f"Install with:\n"
            f"  python3 -m pip install --upgrade --extra-index-url https://bits.featrix.com/pypi/simple "
            f"--trusted-host bits.featrix.com featrix-string-server-client"
        ) from import_err
    except Exception as e:
        logger.error(f"❌❌❌ INITIALIZATION FAILED ❌❌❌")
        logger.error(f"   Fallback chain ({len(fallback_urls)} URLs):")
        for i, url in enumerate(fallback_urls, 1):
            logger.error(f"      {i}. {url}")
        logger.error(f"   Error: {e}")
        logger.error(f"❌ Failed to initialize string server client: {e}")
        raise RuntimeError(f"String server client initialization failed: {e}. No fallback available.")

def _is_worker_process():
    """
    Detect if we're in a PyTorch DataLoader worker process.
    
    CRITICAL: This must ONLY detect PyTorch DataLoader workers, NOT Celery workers.
    DataLoader workers read from Redis cache only - they never call the string server.
    
    ONLY checks the PYTORCH_DATALOADER_WORKER environment variable.
    This is set by worker_init_fn in dataloader_utils.py when PyTorch DataLoader workers are spawned.
    """
    # ONLY check environment variable - this is the ONLY reliable way
    # Celery workers do NOT have this set, so they will return False
    return os.environ.get('PYTORCH_DATALOADER_WORKER') == '1'

def _log_gpu_memory_string_codec(context: str = ""):
    """Quick GPU memory logging for tracing memory usage in string_codec."""
    try:
        if not is_gpu_available():
            return
        allocated = get_gpu_memory_allocated()  # GB (supports CUDA/MPS/CPU)
        reserved = get_gpu_memory_reserved()  # GB
        max_allocated = get_max_gpu_memory_allocated()  # GB
        logger.info(f"📊 GPU MEMORY [string_codec: {context}]: Alloc={allocated:.2f}GB Reserved={reserved:.2f}GB Peak={max_allocated:.2f}GB")
    except Exception as e:
        logger.debug(f"Could not log GPU memory: {e}")


STRING_DIM = 384


# ============================================================================
# ATTENTION-BASED STRING ENCODERS
# These provide structure-aware encoding for delimited and fixed-width strings
# ============================================================================

class DelimiterAttentionEncoder(nn.Module):
    """
    Attention-based encoder for delimited strings like "red,green,blue".
    
    Instead of naive averaging, uses learned attention pooling to select
    what matters from each delimited part. The model learns to weight
    different parts based on their semantic relevance.
    
    Architecture:
        1. Split string by delimiter → ["red", "green", "blue"]
        2. Get BERT embedding for each part → [n_parts, 384]
        3. Add position embeddings → captures order information
        4. Self-attention across parts → parts can attend to each other
        5. Attention pooling with learned query → [d_model] fixed output
    
    This enables the model to learn patterns like:
        - "The LAST item in the list is most predictive"
        - "Items appearing together (co-occurring) matter"
        - "Rare items in the list should be weighted higher"
    """
    
    def __init__(self, d_in: int = STRING_DIM, d_model: int = 128, 
                 max_parts: int = 32, n_heads: int = 4, dropout: float = 0.1):
        super().__init__()
        
        self.d_in = d_in
        self.d_model = d_model
        self.max_parts = max_parts
        self.n_heads = n_heads
        
        # Project input embeddings to d_model
        self.input_projection = nn.Linear(d_in, d_model)
        
        # Position embeddings for order information
        # Position 0 = first item, position 1 = second item, etc.
        self.position_embed = nn.Embedding(max_parts, d_model)
        
        # Self-attention: parts attend to each other
        # "red" in position 0 can see "green" in position 1
        self.self_attention = nn.MultiheadAttention(
            embed_dim=d_model,
            num_heads=n_heads,
            dropout=dropout,
            batch_first=True
        )
        
        # Layer norm for stability
        self.layer_norm = nn.LayerNorm(d_model)
        
        # Learned pooling query - like a [CLS] token
        # This query asks: "what's the aggregate meaning of this set?"
        self.pool_query = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)
        
        # Pooling attention: aggregate all parts into one vector
        self.pool_attention = nn.MultiheadAttention(
            embed_dim=d_model,
            num_heads=n_heads,
            dropout=dropout,
            batch_first=True
        )
        
        # Final layer norm
        self.output_norm = nn.LayerNorm(d_model)
        
        logger.info(f"🔧 DelimiterAttentionEncoder: d_in={d_in}, d_model={d_model}, "
                   f"max_parts={max_parts}, n_heads={n_heads}")
    
    def forward(self, part_embeddings: torch.Tensor, 
                attention_mask: torch.Tensor = None) -> torch.Tensor:
        """
        Encode pre-embedded parts with attention pooling.
        
        Args:
            part_embeddings: [batch, max_parts, d_in] - BERT embeddings of each part
                            (padded to max_parts, padding indicated by attention_mask)
            attention_mask: [batch, max_parts] - 1 for real parts, 0 for padding
        
        Returns:
            pooled: [batch, d_model] - single vector representing the entire set
        """
        batch_size = part_embeddings.shape[0]
        n_parts = part_embeddings.shape[1]
        device = part_embeddings.device
        
        # Project to d_model
        x = self.input_projection(part_embeddings)  # [batch, n_parts, d_model]
        
        # Add position embeddings
        positions = torch.arange(n_parts, device=device).unsqueeze(0).expand(batch_size, -1)
        positions = positions.clamp(max=self.max_parts - 1)  # Clamp to max position
        pos_emb = self.position_embed(positions)  # [batch, n_parts, d_model]
        x = x + pos_emb
        
        # Self-attention across parts
        # Key padding mask: True means IGNORE this position (opposite of attention_mask)
        key_padding_mask = None
        if attention_mask is not None:
            key_padding_mask = (attention_mask == 0)  # [batch, n_parts]
        
        x_attended, _ = self.self_attention(x, x, x, key_padding_mask=key_padding_mask)
        x = self.layer_norm(x + x_attended)  # Residual connection + norm
        
        # Pooling attention: use learned query to aggregate
        query = self.pool_query.expand(batch_size, -1, -1)  # [batch, 1, d_model]
        pooled, attn_weights = self.pool_attention(
            query, x, x, 
            key_padding_mask=key_padding_mask
        )
        
        pooled = self.output_norm(pooled.squeeze(1))  # [batch, d_model]
        
        return pooled


class RadixAttentionEncoder(nn.Module):
    """
    Attention-based encoder for fixed-width structured strings.
    
    Treats strings like numbers in a learned radix system where each position
    (or chunk) carries positional meaning. Learns which positions matter and
    how they interact.
    
    Examples:
        "550e8400-e29b-41d4" → UUID segments, dashes at fixed positions
        "2024-01-15"         → Date: year|month|day with positional meaning
        "ABC-12345-XYZ"      → Product code: category|number|variant
        "+1-555-123-4567"    → Phone: country|area|exchange|line
    
    Architecture:
        1. Chunk string into positions → "ABC-123" → ['A','B','C','-','1','2','3']
        2. Embed each character (or chunk) → [n_positions, d_char]
        3. Add strong positional embeddings → position carries semantic meaning
        4. Self-attention across positions → learns position interactions
        5. Attention pooling → [d_model] fixed output
    
    Key insight: In radix-structured strings, position is MORE important than
    the character itself. "1" in position 5 means something different than
    "1" in position 0. The attention mechanism learns these relationships.
    """
    
    def __init__(self, d_model: int = 128, max_length: int = 64, 
                 chunk_size: int = 1, n_heads: int = 4, dropout: float = 0.1,
                 vocab_size: int = 256):
        super().__init__()
        
        self.d_model = d_model
        self.max_length = max_length
        self.chunk_size = chunk_size
        self.n_positions = max_length // chunk_size
        self.vocab_size = vocab_size
        self.n_heads = n_heads
        
        # Character embedding - learns representation for each ASCII character
        # Includes special tokens: PAD=0, UNK=1
        self.char_embed = nn.Embedding(vocab_size + 2, d_model, padding_idx=0)
        
        # Position embedding - THIS IS KEY for radix encoding
        # Each position has a learned representation because position carries meaning
        self.position_embed = nn.Embedding(self.n_positions, d_model)
        
        # Self-attention across positions
        # Learns: "character at position 3 is related to character at position 7"
        self.self_attention = nn.MultiheadAttention(
            embed_dim=d_model,
            num_heads=n_heads,
            dropout=dropout,
            batch_first=True
        )
        
        # Second attention layer for deeper position interactions
        self.self_attention_2 = nn.MultiheadAttention(
            embed_dim=d_model,
            num_heads=n_heads,
            dropout=dropout,
            batch_first=True
        )
        
        # Layer norms
        self.layer_norm_1 = nn.LayerNorm(d_model)
        self.layer_norm_2 = nn.LayerNorm(d_model)
        
        # Learned pooling query
        self.pool_query = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)
        
        # Pooling attention
        self.pool_attention = nn.MultiheadAttention(
            embed_dim=d_model,
            num_heads=n_heads,
            dropout=dropout,
            batch_first=True
        )
        
        # Output projection and norm
        self.output_norm = nn.LayerNorm(d_model)
        
        logger.info(f"🔧 RadixAttentionEncoder: d_model={d_model}, max_length={max_length}, "
                   f"chunk_size={chunk_size}, n_positions={self.n_positions}, n_heads={n_heads}")
    
    def encode_strings(self, strings: list) -> tuple:
        """
        Convert list of strings to character indices tensor.
        
        Args:
            strings: List of strings to encode
        
        Returns:
            char_indices: [batch, n_positions] - character indices (0=PAD, 1=UNK, 2+=chars)
            attention_mask: [batch, n_positions] - 1 for real chars, 0 for padding
        """
        batch_size = len(strings)
        char_indices = torch.zeros(batch_size, self.n_positions, dtype=torch.long)
        attention_mask = torch.zeros(batch_size, self.n_positions, dtype=torch.float32)
        
        for i, s in enumerate(strings):
            # Handle None/empty strings
            if s is None or not isinstance(s, str):
                s = ""
            
            # Chunk the string
            for j in range(min(len(s), self.n_positions)):
                char = s[j] if self.chunk_size == 1 else s[j*self.chunk_size:(j+1)*self.chunk_size]
                
                # Convert to index (offset by 2 for PAD=0, UNK=1)
                if self.chunk_size == 1:
                    char_idx = ord(char) if len(char) == 1 else 1  # UNK for multi-byte
                    char_idx = min(char_idx + 2, self.vocab_size + 1)  # Clamp to vocab
                else:
                    # For multi-char chunks, hash to vocab
                    char_idx = hash(char) % self.vocab_size + 2
                
                char_indices[i, j] = char_idx
                attention_mask[i, j] = 1.0
        
        return char_indices, attention_mask
    
    def forward(self, char_indices: torch.Tensor, 
                attention_mask: torch.Tensor = None) -> torch.Tensor:
        """
        Encode character indices with positional attention.
        
        Args:
            char_indices: [batch, n_positions] - character indices from encode_strings()
            attention_mask: [batch, n_positions] - 1 for real chars, 0 for padding
        
        Returns:
            pooled: [batch, d_model] - single vector representing the string
        """
        batch_size = char_indices.shape[0]
        n_positions = char_indices.shape[1]
        device = char_indices.device
        
        # Embed characters
        x = self.char_embed(char_indices)  # [batch, n_positions, d_model]
        
        # Add position embeddings - STRONG positional signal
        positions = torch.arange(n_positions, device=device).unsqueeze(0).expand(batch_size, -1)
        positions = positions.clamp(max=self.n_positions - 1)
        pos_emb = self.position_embed(positions)  # [batch, n_positions, d_model]
        x = x + pos_emb
        
        # Key padding mask for attention (True = IGNORE)
        key_padding_mask = None
        if attention_mask is not None:
            key_padding_mask = (attention_mask == 0)
        
        # First self-attention layer
        x_attended, _ = self.self_attention(x, x, x, key_padding_mask=key_padding_mask)
        x = self.layer_norm_1(x + x_attended)  # Residual + norm
        
        # Second self-attention layer (deeper interactions)
        x_attended_2, _ = self.self_attention_2(x, x, x, key_padding_mask=key_padding_mask)
        x = self.layer_norm_2(x + x_attended_2)  # Residual + norm
        
        # Pooling attention
        query = self.pool_query.expand(batch_size, -1, -1)  # [batch, 1, d_model]
        pooled, attn_weights = self.pool_attention(
            query, x, x,
            key_padding_mask=key_padding_mask
        )
        
        pooled = self.output_norm(pooled.squeeze(1))  # [batch, d_model]
        
        return pooled
    
    def forward_from_strings(self, strings: list) -> torch.Tensor:
        """
        Convenience method: encode strings directly to embeddings.
        
        Args:
            strings: List of strings to encode
        
        Returns:
            pooled: [batch, d_model] - embeddings for each string
        """
        char_indices, attention_mask = self.encode_strings(strings)
        
        # Move to same device as model
        device = next(self.parameters()).device
        char_indices = char_indices.to(device)
        attention_mask = attention_mask.to(device)
        
        return self.forward(char_indices, attention_mask)


# ============================================================================
# STRING ENCODER (main adaptive encoder with multiple strategies)
# ============================================================================

class StringEncoder(nn.Module):
    def __init__(self, config: StringEncoderConfig, column_name=None):
        super().__init__()

        self.config = config
        self.column_name = column_name  # Store column name for logging

        # ADAPTIVE MIXTURE: Create multiple MLP paths with different compression levels
        # Similar to AdaptiveScalarEncoder's mixture of transformations
        # We'll create 7 compression strategies including:
        # - ZERO: for random/uninformative strings
        # - DELIMITER: simple averaging for delimited text (legacy)
        # - DELIMITER_ATTN: attention-based pooling for delimited text (new)
        # - RADIX: positional attention for fixed-width structured strings (new)
        # - AGGRESSIVE/MODERATE/STANDARD: MLP compression at different levels
        d_model = config.d_model if config.d_model is not None else config.d_out
        
        # Define the compression strategies
        # Strategy codes: 0=ZERO, -1=DELIMITER (legacy avg), -2=DELIMITER_ATTN, -3=RADIX
        # Positive values = MLP output dimension
        # TEMPORARY: Disabled DELIMITER/RADIX strategies to debug memory issue
        self.compression_levels = [
            ("ZERO", 0),                     # Zero contribution - for random/uninformative strings
            # ("DELIMITER", -1),             # DISABLED: Legacy: BERT-aware averaging for 'A,B,C' patterns
            # ("DELIM_ATTN", -2),            # DISABLED: Attention pooling for delimited text
            # ("RADIX", -3),                 # DISABLED: Positional attention for fixed-width strings
            ("AGGRESSIVE", d_model // 4),    # Heavy compression (1/4 capacity)
            ("MODERATE", d_model // 2),      # Medium compression (1/2 capacity)
            ("STANDARD", d_model),           # Match d_model exactly (full capacity)
        ]
        
        # Create separate MLP encoders for each compression level
        self.mlp_encoders = nn.ModuleList()
        
        # NEW: Create attention-based encoders for DELIM_ATTN and RADIX strategies
        self.delimiter_attention_encoder = None
        self.radix_attention_encoder = None
        
        for strategy_name, d_out_strategy in self.compression_levels:
            if d_out_strategy == 0:
                # ZERO strategy: no MLP needed, will output zeros
                self.mlp_encoders.append(None)
            elif d_out_strategy == -1:
                # DELIMITER strategy (legacy): special handling in forward(), no MLP needed here
                # We'll split the input embedding and average (happens in forward pass)
                self.mlp_encoders.append(None)
            elif d_out_strategy == -2:
                # DELIM_ATTN strategy: create attention encoder for delimited text
                if self.delimiter_attention_encoder is None:
                    self.delimiter_attention_encoder = DelimiterAttentionEncoder(
                        d_in=STRING_DIM,
                        d_model=d_model,
                        max_parts=32,
                        n_heads=4,
                        dropout=0.1
                    )
                self.mlp_encoders.append(None)  # Encoder is separate module
            elif d_out_strategy == -3:
                # RADIX strategy: create attention encoder for fixed-width strings
                if self.radix_attention_encoder is None:
                    self.radix_attention_encoder = RadixAttentionEncoder(
                        d_model=d_model,
                        max_length=64,
                        chunk_size=1,
                        n_heads=4,
                        dropout=0.1
                    )
                self.mlp_encoders.append(None)  # Encoder is separate module
            else:
                # Create a config for this specific compression level
                strategy_config = StringEncoderConfig(
                    d_in=config.d_in,
                    d_out=d_out_strategy,
                    d_model=None,  # Don't project yet - we'll do it after mixing
                    normalize=False,  # Don't normalize yet - we'll do it after mixing
                    n_hidden_layers=config.n_hidden_layers,
                    d_hidden=config.d_hidden,
                )
                mlp = SimpleMLP(strategy_config)
                
                # WARM START: Initialize MLP to better preserve BERT embedding structure
                self._warm_start_mlp_from_bert(mlp, config.d_in)
                
                self.mlp_encoders.append(mlp)
        
        # Learnable weights to select among compression strategies
        # Initialize with small random values (not zeros) to break symmetry
        self.strategy_logits = nn.Parameter(torch.randn(len(self.compression_levels)) * 0.1)
        
        # CRITICAL FIX: Replacement embedding needs to match d_model (output size after mixing)
        self._replacement_embedding = nn.Parameter(torch.zeros(d_model))
        nn.init.normal_(self._replacement_embedding, mean=0.0, std=0.01)
        
        # Final projection: all strategies project to d_model for mixing
        self.strategy_projections = nn.ModuleList()
        for strategy_name, d_out_strategy in self.compression_levels:
            if d_out_strategy == 0:
                # ZERO strategy: no projection needed (outputs zeros directly)
                proj = None
            elif d_out_strategy == -1:
                # DELIMITER strategy: operates on BERT embeddings, project from STRING_DIM to d_model
                proj = nn.Linear(STRING_DIM, d_model, bias=False)
                nn.init.xavier_uniform_(proj.weight, gain=1.0)
            elif d_out_strategy == -2:
                # DELIM_ATTN strategy: outputs d_model directly, no projection needed
                proj = None
            elif d_out_strategy == -3:
                # RADIX strategy: outputs d_model directly, no projection needed
                proj = None
            elif d_out_strategy != d_model:
                proj = nn.Linear(d_out_strategy, d_model, bias=False)
                nn.init.xavier_uniform_(proj.weight, gain=1.0)
            else:
                proj = None  # No projection needed
            self.strategy_projections.append(proj)
        
        logger.info(f"🎯 AdaptiveStringEncoder: {len(self.compression_levels)} compression strategies")
        for i, (name, d_out) in enumerate(self.compression_levels):
            if d_out == 0:
                logger.info(f"   Strategy {i}: {name:12s} ZERO (learns to ignore random/uninformative text)")
            elif d_out == -1:
                logger.info(f"   Strategy {i}: {name:12s} DELIMITER (splits & averages for 'A,B,C' or 'X-Y' patterns)")
            elif d_out == -2:
                logger.info(f"   Strategy {i}: {name:12s} DELIM_ATTN (attention pooling for delimited text)")
            elif d_out == -3:
                logger.info(f"   Strategy {i}: {name:12s} RADIX (positional attention for fixed-width strings)")
            else:
                logger.info(f"   Strategy {i}: {name:12s} d_out={d_out:4d} → d_model={d_model}")
        
        self.needs_projection = False  # We handle projection internally now
        self.final_projection = None
        
        # STRATEGY PRUNING: Track training progress for top-K selection
        self.register_buffer('_epoch_counter', torch.tensor(0, dtype=torch.long))
        self.register_buffer('_total_epochs', torch.tensor(100, dtype=torch.long))  # Will be updated
        self.register_buffer('_pruned_mask', torch.ones(len(self.compression_levels), dtype=torch.float32))
        self.register_buffer('_last_logged_epoch', torch.tensor(-1, dtype=torch.long))  # Track last logged epoch to avoid batch spam
        self._pruning_enabled = False
        self._top_k = 2  # Keep top 2 strategies after warmup
    
    def _warm_start_mlp_from_bert(self, mlp, d_in):
        """
        Warm start MLP layers to better preserve BERT embedding structure.
        
        Strategy:
        - First layer: Initialize to approximate identity mapping (preserve BERT structure)
        - Subsequent layers: Use standard initialization
        - This helps the network start closer to the BERT embedding space
        """
        layers = list(mlp.modules())
        first_linear = None
        
        # Find the first Linear layer
        for module in mlp.modules():
            if isinstance(module, nn.Linear):
                first_linear = module
                break
        
        if first_linear is not None:
            # Initialize first layer to preserve more of the input structure
            # Use smaller weights to start closer to identity-like behavior
            with torch.no_grad():
                # Initialize weights with smaller variance (more conservative)
                # This helps preserve BERT embedding structure initially
                nn.init.normal_(first_linear.weight, mean=0.0, std=0.02)  # Smaller std than xavier
                
                # Initialize bias to zero (already done, but be explicit)
                if first_linear.bias is not None:
                    nn.init.zeros_(first_linear.bias)
            
            # Initialize remaining layers with standard xavier
            found_first = False
            for name, param in mlp.named_parameters():
                if 'weight' in name and param.ndim >= 2:
                    if not found_first:
                        found_first = True  # Skip first layer (already initialized)
                        continue
                    nn.init.xavier_uniform_(param, gain=0.5)
                elif 'bias' in name:
                    if not found_first:
                        found_first = True
                        continue
                    nn.init.zeros_(param)
        else:
            # Fallback: standard initialization if no Linear layer found
            for name, param in mlp.named_parameters():
                if 'weight' in name and param.ndim >= 2:
                    nn.init.xavier_uniform_(param, gain=0.5)
                elif 'bias' in name:
                    nn.init.zeros_(param)

    @property
    def unknown_embedding(self):
        # Replacement embedding is already at d_model size
        emb = nn.functional.normalize(self._replacement_embedding, dim=-1)
        return emb

    @property
    def marginal_embedding(self):
        # We return the same vector as NOT_PRESENT token because they are treated the
        # same from a probabilistic point of view by the network, and should be treated
        # the same when the model is queried.
        # However, they must remain distinct tokens because the masking strategy for the loss
        # function is affected by whether a field is NOT_PRESENT, or MARGINAL.
        emb = nn.functional.normalize(self._replacement_embedding, dim=-1)
        return emb

    @property
    def not_present_embedding(self):
        emb = nn.functional.normalize(self._replacement_embedding, dim=-1)
        return emb

    def forward(self, token):
        # token.value can be:
        # - [STRING_DIM] for single token (will be batched by DataLoader)
        # - [batch_size, STRING_DIM] for already-batched tokens
        # After learned projection: BERT [384] + features [32] → [384]
        # Both are valid! Just pass through.
        
        # FORCE conversion to float32 if we get int64
        value = token.value
        if value.dtype == torch.int64:
            value = value.to(dtype=torch.float32)
        
        # CRITICAL: Ensure value is on the same device as module parameters
        # This fixes device mismatch errors where token.value is on CPU but module is on CUDA
        # Respect FEATRIX_FORCE_CPU_SINGLE_PREDICTOR env var - force CPU if set
        force_cpu = os.environ.get('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR') == '1'
        
        # Get device from first available parameter (projection, mlp, or strategy_logits)
        module_device = None
        if not force_cpu:
            # Only detect module device if not forcing CPU
            # Try to get device from a projection layer
            for proj in self.strategy_projections:
                if proj is not None:
                    try:
                        module_device = next(proj.parameters()).device
                        break
                    except (StopIteration, AttributeError):
                        continue
            # If no projection found, try MLP encoders
            if module_device is None:
                for mlp in self.mlp_encoders:
                    if mlp is not None:
                        try:
                            module_device = next(mlp.parameters()).device
                            break
                        except (StopIteration, AttributeError):
                            continue
            # Fallback to strategy_logits
            if module_device is None and self.strategy_logits is not None:
                module_device = self.strategy_logits.device
        
        # Force CPU mode if env var is set
        if force_cpu:
            module_device = torch.device('cpu')
            # Also ensure module is on CPU (defensive - in case it wasn't moved earlier)
            if list(self.parameters()):
                first_param_device = next(self.parameters()).device
                if first_param_device.type != 'cpu':
                    self.cpu()
        # If not forcing CPU and no device detected, try to use CUDA if available
        elif module_device is None and is_gpu_available():
            # Try to detect device from any parameter in the module
            if list(self.parameters()):
                module_device = next(self.parameters()).device
        
        # Move value to module device if there's a mismatch
        if module_device is not None and value.device != module_device:
            original_device = value.device
            value = value.to(device=module_device)
            # Log once per encoder instance to avoid spam
            if not hasattr(self, '_device_move_logged'):
                logger.debug(f"StringEncoder '{self.column_name or 'unknown'}': Moved token.value from {original_device} to {module_device} (force_cpu={force_cpu})")
                self._device_move_logged = True
        
        # Validate it's a tensor with correct dtype
        assert hasattr(value, 'dtype'), f"StringEncoder received non-tensor token.value: {type(value)}"
        assert value.dtype == torch.float32, f"StringEncoder received {value.dtype} token.value, expected float32. Shape: {value.shape}"
        
        # CRITICAL FIX: Validate and clamp input values to prevent NaN propagation
        # Check for NaN/Inf in inputs and replace with zeros
        if torch.isnan(value).any() or torch.isinf(value).any():
            nan_mask = torch.isnan(value) | torch.isinf(value)
            nan_count = nan_mask.sum().item()
            value = torch.where(nan_mask, torch.zeros_like(value), value)
            # Log warning (but not too verbose)
            if not hasattr(self, '_nan_warning_logged'):
                logger.warning(f"⚠️  StringEncoder: Detected and replaced {nan_count} NaN/Inf values in input")
                logger.warning(f"   Input shape: {value.shape}, token status: {token.status[:5] if hasattr(token.status, '__getitem__') else token.status}")
                self._nan_warning_logged = True
        
        # Clamp extreme values to reasonable range to prevent gradient explosion
        value = torch.clamp(value, min=-100.0, max=100.0)
        
        # Create new token with modified value (Token.value is read-only)
        # Always create new token to ensure device consistency
        token = Token(
            value=value,
            status=token.status,
            attention_mask=token.attention_mask if hasattr(token, 'attention_mask') else None
        )
        
        # ADAPTIVE MIXTURE: Encode with all compression strategies and mix
        # Compute softmax weights over compression strategies
        # Use subset softmax to properly handle pruning (pruned strategies get exactly 0 weight)
        
        active_mask = self._pruned_mask > 0.5 if hasattr(self, '_pruned_mask') else torch.ones(len(self.compression_levels), dtype=torch.bool, device=self.strategy_logits.device)
        active_indices = torch.where(active_mask)[0]
        
        if active_indices.numel() > 0:
            # Softmax only over active strategies
            active_logits = self.strategy_logits[active_indices]
            active_weights = F.softmax(active_logits, dim=0)
            
            # Full weight vector (zeros for pruned)
            weights = torch.zeros(len(self.compression_levels), device=self.strategy_logits.device, dtype=self.strategy_logits.dtype)
            weights[active_indices] = active_weights
        else:
            # Fallback if somehow all pruned
            weights = torch.ones(len(self.compression_levels), device=self.strategy_logits.device, dtype=self.strategy_logits.dtype) / len(self.compression_levels)
        
        # LOG ALL STRATEGY WEIGHTS: Show what's being tried
        if self.training and not hasattr(self, '_strategy_weights_logged'):
            # Log GPU memory before strategy evaluation
            _log_gpu_memory_string_codec(f"StringEncoder '{self.column_name}' BEFORE strategies")
            logger.info(f"🔍 AdaptiveStringEncoder: Evaluating {len(self.compression_levels)} compression strategies")
            for i, (strategy_name, _) in enumerate(self.compression_levels):
                if weights[i].item() > 0:
                    weight_pct = weights[i].item() * 100
                    logit_val = self.strategy_logits[i].item()
                    logger.info(f"   Strategy {i:2d}: {strategy_name:12s} weight={weight_pct:5.1f}% logit={logit_val:6.3f}")
            self._strategy_weights_logged = True
        
        # STRATEGY PRUNING: After warmup (epoch > total_epochs/5), keep only top-2 strategies
        if self.training:
            warmup_epochs = max(1, self._total_epochs.item() // 5)
            current_epoch = self._epoch_counter.item()
            
            if current_epoch >= warmup_epochs and not self._pruning_enabled:
                # Activate pruning: find top-K strategies
                top_k_values, top_k_indices = torch.topk(weights.detach(), k=min(self._top_k, active_indices.numel()), dim=0)
                new_mask = torch.zeros_like(self._pruned_mask)
                new_mask[top_k_indices] = 1.0
                self._pruned_mask.copy_(new_mask)
                self._pruning_enabled = True
                
                # Log which strategies survived
                surviving_strategies = [self.compression_levels[i][0] for i in top_k_indices.cpu().tolist()]
                pruned_strategies = [self.compression_levels[i][0] for i in range(len(self.compression_levels)) 
                                    if i not in top_k_indices.cpu().tolist()]
                logger.info(f"🔪 StringEncoder PRUNING activated at epoch {current_epoch}/{self._total_epochs.item()}")
                logger.info(f"   ✅ Keeping top-{self._top_k} strategies: {', '.join(surviving_strategies)}")
                logger.info(f"   ❌ Pruning {len(pruned_strategies)} strategies: {', '.join(pruned_strategies)}")
                logger.info(f"   📊 Final weights: {[f'{weights[i].item():.1%}' for i in top_k_indices.cpu().tolist()]}")
            
            # Recompute weights after pruning using subset softmax
            if self._pruning_enabled:
                active_mask = self._pruned_mask > 0.5
                active_indices = torch.where(active_mask)[0]
                
                if active_indices.numel() > 0:
                    active_logits = self.strategy_logits[active_indices]
                    active_weights = F.softmax(active_logits, dim=0)
                    
                    weights = torch.zeros(len(self.compression_levels), device=self.strategy_logits.device, dtype=self.strategy_logits.dtype)
                    weights[active_indices] = active_weights
                else:
                    weights = torch.ones(len(self.compression_levels), device=self.strategy_logits.device, dtype=self.strategy_logits.dtype) / len(self.compression_levels)
                
                # Log current active strategy weights periodically during training
                # Only log once per epoch (not on every batch) to avoid spam
                if current_epoch % 10 == 0 and current_epoch != self._last_logged_epoch.item():
                    active_indices = (self._pruned_mask > 0.5).nonzero(as_tuple=True)[0]
                    if len(active_indices) > 0:
                        active_strategies = [self.compression_levels[i][0] for i in active_indices.cpu().tolist()]
                        # Don't log individual columns - embedded_space.py already logs
                        # a consolidated table of all string columns together
                        # That table is much cleaner and shows all columns at once
                        
                        # Mark this epoch as logged
                        self._last_logged_epoch.fill_(current_epoch)
        
        # Encode with each strategy and project to d_model
        strategy_outputs = []
        for i, (mlp, projection) in enumerate(zip(self.mlp_encoders, self.strategy_projections)):
            strategy_name = self.compression_levels[i][0]
            
            # SKIP PRUNED STRATEGIES: Don't compute forward pass if weight is ~0
            if self.training and self._pruning_enabled and self._pruned_mask[i].item() < 0.5:
                # Strategy is pruned - use zeros (won't contribute anyway due to zero weight)
                out = torch.zeros(token.value.shape[0], self.config.d_model or self.config.d_out, 
                                 dtype=torch.float32, device=token.value.device)
                strategy_outputs.append(out)
                continue
            
            if mlp is None and strategy_name == "ZERO":
                # ZERO strategy: output zeros (for random/uninformative columns)
                out = torch.zeros(token.value.shape[0], self.config.d_model or self.config.d_out, 
                                 dtype=torch.float32, device=token.value.device)
            
            elif mlp is None and strategy_name == "DELIM_ATTN":
                # DELIM_ATTN strategy: Use attention-based encoder for delimited text
                # This provides learned pooling instead of simple averaging
                # NOTE: Requires part_embeddings tensor to be passed via token.attention_data
                # If not available, fall back to simple projection of token.value
                d_model = self.config.d_model or self.config.d_out
                batch_size = token.value.shape[0]
                
                # Check if we have pre-computed part embeddings
                # token.part_embeddings: [batch, max_parts, STRING_DIM]
                # token.part_mask: [batch, max_parts]
                part_embeddings = getattr(token, 'part_embeddings', None)
                if part_embeddings is not None:
                    # Use attention encoder on the parts
                    if self.delimiter_attention_encoder is not None:
                        # Move encoder to correct device if needed
                        enc_device = next(self.delimiter_attention_encoder.parameters()).device
                        if enc_device != token.value.device:
                            self.delimiter_attention_encoder = self.delimiter_attention_encoder.to(token.value.device)
                        
                        part_mask = getattr(token, 'part_mask', None)
                        out = self.delimiter_attention_encoder(
                            part_embeddings,
                            attention_mask=part_mask
                        )  # [batch, d_model]
                    else:
                        # Fallback: no encoder, use zeros
                        logger.warning(f"StringEncoder DELIM_ATTN: No delimiter_attention_encoder, using zeros")
                        out = torch.zeros(batch_size, d_model, dtype=torch.float32, device=token.value.device)
                else:
                    # No part embeddings available - fall back to simple projection
                    # This happens during initial tokenization or if delimiter wasn't detected
                    if token.value.ndim == 2 and token.value.shape[-1] == STRING_DIM:
                        # Project BERT embedding to d_model
                        if self.delimiter_attention_encoder is not None:
                            # Use the input projection from the attention encoder
                            enc_device = next(self.delimiter_attention_encoder.parameters()).device
                            if enc_device != token.value.device:
                                self.delimiter_attention_encoder = self.delimiter_attention_encoder.to(token.value.device)
                            out = self.delimiter_attention_encoder.input_projection(token.value)
                            out = self.delimiter_attention_encoder.output_norm(out)
                        else:
                            # Last resort: zeros
                            out = torch.zeros(batch_size, d_model, dtype=torch.float32, device=token.value.device)
                    else:
                        # Wrong shape - use zeros
                        out = torch.zeros(batch_size, d_model, dtype=torch.float32, device=token.value.device)
            
            elif mlp is None and strategy_name == "RADIX":
                # RADIX strategy: Use positional attention encoder for fixed-width strings
                # This learns position-dependent representations
                # NOTE: Requires raw strings to be passed via token.raw_strings
                # If not available, falls back to character-level encoding of token value
                d_model = self.config.d_model or self.config.d_out
                batch_size = token.value.shape[0]
                
                # Check if we have raw strings for RADIX encoding
                raw_strings = getattr(token, 'raw_strings', None)
                if raw_strings is not None:
                    # Use radix encoder on raw strings
                    if self.radix_attention_encoder is not None:
                        # Move encoder to correct device if needed
                        enc_device = next(self.radix_attention_encoder.parameters()).device
                        if enc_device != token.value.device:
                            self.radix_attention_encoder = self.radix_attention_encoder.to(token.value.device)
                        
                        out = self.radix_attention_encoder.forward_from_strings(raw_strings)
                    else:
                        logger.warning(f"StringEncoder RADIX: No radix_attention_encoder, using zeros")
                        out = torch.zeros(batch_size, d_model, dtype=torch.float32, device=token.value.device)
                else:
                    # No raw strings available
                    # This means we're working with already-encoded BERT embeddings
                    # For RADIX, this is suboptimal but we can still contribute
                    # by projecting the BERT embedding through a simple layer
                    if token.value.ndim == 2 and token.value.shape[-1] == STRING_DIM:
                        # Use a simple projection as fallback
                        # RADIX really wants raw strings, so this is suboptimal
                        if self.radix_attention_encoder is not None:
                            # Create a simple linear projection if not exists
                            if not hasattr(self, '_radix_fallback_proj'):
                                self._radix_fallback_proj = nn.Linear(STRING_DIM, d_model, bias=False)
                                self._radix_fallback_proj = self._radix_fallback_proj.to(token.value.device)
                                nn.init.xavier_uniform_(self._radix_fallback_proj.weight, gain=0.5)
                            elif self._radix_fallback_proj.weight.device != token.value.device:
                                self._radix_fallback_proj = self._radix_fallback_proj.to(token.value.device)
                            out = self._radix_fallback_proj(token.value)
                        else:
                            out = torch.zeros(batch_size, d_model, dtype=torch.float32, device=token.value.device)
                    else:
                        out = torch.zeros(batch_size, d_model, dtype=torch.float32, device=token.value.device)
            
            elif mlp is None and strategy_name == "DELIMITER":
                # DELIMITER strategy: The input is already projected [384] from learned projection
                # Just project to d_model
                # 
                # BACKWARD COMPATIBILITY: Handle old StringCodec instances that output enc_dim instead of STRING_DIM
                # Old codecs might output [batch, 128] while new ones output [batch, 384]
                
                # CRITICAL FIX: Check dimensionality first to avoid confusion between batch_size and feature_dim
                if token.value.ndim == 1:
                    # 1D tensor [batch_size] - this shouldn't happen for DELIMITER strategy
                    # The DELIMITER strategy expects string embeddings which should be 2D [batch_size, feature_dim]
                    # Fall back to zeros to avoid dimension mismatch
                    logger.error(f"StringEncoder DELIMITER strategy: token.value is 1D with shape {token.value.shape}, expected 2D [batch_size, feature_dim]. Using zeros.")
                    batch_size = token.value.shape[0]
                    d_model = self.config.d_model or self.config.d_out
                    out = torch.zeros(batch_size, d_model, dtype=torch.float32, device=token.value.device)
                elif token.value.ndim == 2:
                    # 2D tensor [batch_size, feature_dim] - correct format
                    token_dim = token.value.shape[-1]
                    expected_dim = STRING_DIM  # 384
                    d_model = self.config.d_model or self.config.d_out
                    
                    if token_dim == d_model:
                        # Token is already the right dimension (old codec with enc_dim == d_model)
                        # No projection needed
                        out = token.value
                    elif token_dim == expected_dim and projection is not None:
                        # Token is STRING_DIM (384), project to d_model
                        # CRITICAL: Ensure projection is on the same device as input
                        proj_device = next(projection.parameters()).device
                        if proj_device != token.value.device:
                            # Move projection to match input device
                            projection = projection.to(token.value.device)
                            # Update the ModuleList entry so future calls use the moved projection
                            self.strategy_projections[i] = projection
                        out = projection(token.value)  # [batch_size, d_model]
                    elif token_dim == expected_dim and projection is None:
                        # Token is STRING_DIM but no projection - shouldn't happen but handle gracefully
                        # Create a simple linear projection on the fly
                        logger.warning(f"StringEncoder DELIMITER strategy: token is {expected_dim}D but projection is None, creating projection")
                        new_projection = nn.Linear(expected_dim, d_model, bias=False)
                        new_projection = new_projection.to(token.value.device)
                        nn.init.xavier_uniform_(new_projection.weight, gain=1.0)
                        self.strategy_projections[i] = new_projection
                        out = new_projection(token.value)  # pylint: disable=not-callable
                    else:
                        # Unexpected dimension - create appropriate projection
                        logger.warning(f"StringEncoder DELIMITER strategy: unexpected token dimension {token_dim}, expected {expected_dim} or {d_model}")
                        # Create a projection from token_dim to d_model
                        new_projection = nn.Linear(token_dim, d_model, bias=False)
                        new_projection = new_projection.to(token.value.device)
                        nn.init.xavier_uniform_(new_projection.weight, gain=1.0)
                        self.strategy_projections[i] = new_projection
                        out = new_projection(token.value)  # pylint: disable=not-callable
                else:
                    # 3D or higher - unexpected
                    logger.error(f"StringEncoder DELIMITER strategy: token.value has unexpected shape {token.value.shape} (ndim={token.value.ndim}). Using zeros.")
                    batch_size = token.value.shape[0]
                    d_model = self.config.d_model or self.config.d_out
                    out = torch.zeros(batch_size, d_model, dtype=torch.float32, device=token.value.device)
            else:
                # Regular MLP strategy: encode with this strategy's MLP
                # CRITICAL: Ensure MLP is on the same device as input
                if mlp is None:
                    # This shouldn't happen in the else branch, but handle gracefully
                    logger.error(f"StringEncoder: MLP is None for strategy {i} ({strategy_name}) in else branch")
                    out = torch.zeros(token.value.shape[0], self.config.d_model or self.config.d_out, 
                                     dtype=torch.float32, device=token.value.device)
                else:
                    mlp_device = next(mlp.parameters()).device
                    if mlp_device != token.value.device:
                        # Move MLP to match input device
                        mlp = mlp.to(token.value.device)
                        # Update the ModuleList entry so future calls use the moved MLP
                        self.mlp_encoders[i] = mlp
                    out = mlp(token.value)  # [batch_size, d_out_strategy]
                
                # Check for NaN in strategy output
                if torch.isnan(out).any() or torch.isinf(out).any():
                    logger.error(f"💥 StringEncoder strategy {i} output contains NaN/Inf!")
                    logger.error(f"   Strategy: {strategy_name}")
                    logger.error(f"   Output shape: {out.shape}, NaN count: {torch.isnan(out).sum().item()}")
                    # Replace with zeros to avoid corruption
                    out = torch.zeros_like(out)
                
                # Project to d_model if needed
                if projection is not None:
                    # CRITICAL: Ensure projection is on the same device as input
                    proj_device = next(projection.parameters()).device
                    if proj_device != out.device:
                        # Move projection to match input device
                        projection = projection.to(out.device)
                        # Update the ModuleList entry so future calls use the moved projection
                        self.strategy_projections[i] = projection
                    out = projection(out)  # [batch_size, d_model]
            
            strategy_outputs.append(out)
        
        # Stack all strategy outputs: [n_strategies, batch_size, d_model]
        strategy_stack = torch.stack(strategy_outputs, dim=0)
        
        # Mix strategies using learned weights: [batch_size, d_model]
        # weights: [n_strategies] → [n_strategies, 1, 1] for broadcasting
        weights_expanded = weights.view(-1, 1, 1)
        out = (strategy_stack * weights_expanded).sum(dim=0)  # [batch_size, d_model]
        
        # ENTROPY REGULARIZATION: Encourage sharp strategy selection
        # (Similar to AdaptiveScalarEncoder)
        if self.training:
            entropy = -(weights * torch.log(weights + 1e-10)).sum()
            # Scale entropy loss - higher penalty = sharper strategies
            # Use 0.1 * entropy as penalty (encouraging sharper distributions)
            entropy_loss = 0.1 * entropy
            # Store for logging/debugging (detach to avoid keeping gradient graph in logging vars)
            if not hasattr(self, '_last_entropy'):
                self._last_entropy = entropy.detach().item()
                self._last_entropy_loss = entropy_loss.detach().item()
            else:
                self._last_entropy = 0.9 * self._last_entropy + 0.1 * entropy.detach().item()  # EMA
                self._last_entropy_loss = 0.9 * self._last_entropy_loss + 0.1 * entropy_loss.detach().item()
            # Store entropy loss so it can be collected and added to total loss
            # NOTE: We intentionally keep the gradient here so it can be backpropagated
            self._current_entropy_loss = entropy_loss
        else:
            # Not training - clear entropy loss
            self._current_entropy_loss = None

        # Override embeddings for unknown and not present tokens
        out[token.status == TokenStatus.NOT_PRESENT] = self._replacement_embedding
        out[token.status == TokenStatus.UNKNOWN] = self._replacement_embedding
        out[token.status == TokenStatus.MARGINAL] = self._replacement_embedding

        # CONDITIONAL NORMALIZATION based on config
        if self.config.normalize:
            # Add epsilon for numerical stability during normalization
            short_vec = nn.functional.normalize(out[:, 0:3], dim=1, eps=1e-8)
            full_vec = nn.functional.normalize(out, dim=1, eps=1e-8)
        else:
            # No normalization at column level - only joint encoder will normalize
            short_vec = out[:, 0:3]
            full_vec = out

        return short_vec, full_vec

    @staticmethod
    def get_default_config(d_in: int, d_out: int, d_model: int = None):
        # Import here to avoid circular import
        from .sphere_config import get_config
        
        # Get normalization setting from global config
        normalize_column_encoders = get_config().get_normalize_column_encoders()
        
        return StringEncoderConfig(
            d_in=d_in,
            d_out=d_out,
            d_model=d_model,  # Target dimension for stacking
            normalize=normalize_column_encoders,  # Config-controlled normalization
        )

# Global cache manager to share StringCache instances across all StringCodec objects
_global_string_caches = {}  # filename -> StringCache instance

# Track logged cache misses to avoid spam (only log each unique value once)
_logged_cache_misses = set()  # Set of values we've already logged

def get_global_string_cache(cache_filename=None, initial_values=None, debug_name="global_cache", string_columns=None):
    """
    Get or create a global SimpleStringCache instance.
    
    TIERED CACHE: @lru_cache → Redis → String Server (taco)
    
    Args:
        cache_filename: IGNORED (legacy compatibility)
        initial_values: Optional list of strings to pre-warm into Redis
        debug_name: Debug name for logging
        string_columns: IGNORED (legacy compatibility)
    """
    cache_key = "simple_memory_cache"
    debug_name = debug_name.strip() if debug_name else "global_cache"

    # Return existing cache if available
    if cache_key in _global_string_caches:
        cache = _global_string_caches[cache_key]
        
        # Pre-warm new values into Redis (for multi-column datasets)
        if initial_values and len(initial_values) > 0:
            logger.info(f"📦 Pre-warming {len(initial_values)} values from '{debug_name}' into Redis")
            cache._pre_warm_cache(initial_values, string_columns=None)
        
        return cache
    
    # Workers only read from Redis - no string server calls
    is_worker = _is_worker_process()
    if is_worker:
        logger.debug(f"Worker: creating Redis-only cache for '{debug_name}'")
        cache = SimpleStringCache(
            initial_values=[],
            debugName=f"worker_{debug_name}",
            string_columns=None
        )
        cache._is_worker_cache = True
        _global_string_caches[cache_key] = cache
        return cache
    
    # Main process: create cache that uses Redis + string server
    logger.debug(f"Creating SimpleStringCache: {debug_name}")
    cache = SimpleStringCache(
        initial_values=initial_values or [],
        debugName=f"global_{debug_name}",
        string_columns=None
    )
    _global_string_caches[cache_key] = cache
    return cache

def clear_global_string_caches():
    """Clear all global string caches (useful for testing or memory cleanup)."""
    global _global_string_caches, _logged_cache_misses
    count = len(_global_string_caches)
    _global_string_caches.clear()
    _logged_cache_misses.clear()
    logger.info(f"🧹 Clearing {count} global string caches")

def get_global_string_cache_stats():
    """Get statistics about all global string caches."""
    stats = {
        'total_caches': len(_global_string_caches),
        'cache_keys': list(_global_string_caches.keys()),
        'cache_details': {}
    }
    
    for cache_key, cache in _global_string_caches.items():
        try:
            # SimpleStringCache just has @lru_cache stats
            cache_info = cache.get_embedding_from_cache.cache_info()
            stats['cache_details'][cache_key] = {
                'hit_rate': cache_info.hits / max(cache_info.hits + cache_info.misses, 1),
                'cache_hits': cache_info.hits,
                'cache_misses': cache_info.misses,
                'cache_size': cache_info.currsize,
                'max_size': cache_info.maxsize
            }
        except Exception as e:
            stats['cache_details'][cache_key] = {'error': str(e)}
    
    return stats

def log_final_string_cache_stats_all():
    """
    Log final string cache statistics for all global caches.
    Should be called when dataloader shuts down or training completes.
    """
    if not _global_string_caches:
        logger.debug("No global string caches to log stats for")
        return
    
    for cache_key, cache in _global_string_caches.items():
        try:
            if hasattr(cache, 'log_final_string_cache_stats'):
                cache.log_final_string_cache_stats()
        except Exception as e:
            logger.warning(f"Failed to log final stats for cache {cache_key}: {e}")


class StringCodec(nn.Module):
    def __init__(self, enc_dim: int, debugName=None, initial_values=None, string_cache: str=None,
                 delimiter: str=None, is_random_column: bool=False):
        super().__init__()
        # String server client is initialized on first use - no local model loading needed
        assert enc_dim > 0
        assert debugName is not None, "We need debugName for the string cache -- pass in the col name"

        self._numEncodeCalls = 0
        self.colName = debugName  # HACK
        self._is_decodable = False  # String decoding not yet implemented (needs final embedding index)
        # Store without padding - padding is only for display, not for lookups
        # The cache key is based on cache_filename, not debug_name
        self.debug_name = str(debugName).strip()
        self.enc_dim = enc_dim
        # NOTE: change this based on the model used
        # After learned projection, output is still [384] (same as before)
        self.d_string_model = STRING_DIM

        # Store only the cache filename for global cache lookup
        # CRITICAL: Resolve to absolute path so workers can find it regardless of working directory
        if string_cache:
            if not os.path.isabs(string_cache):
                # Relative path - resolve to absolute based on current working directory
                self._string_cache_filename = os.path.abspath(string_cache)
            else:
                # Already absolute
                self._string_cache_filename = string_cache
        else:
            self._string_cache_filename = None
        
        # NEW: Adaptive string encoding features
        self.delimiter = delimiter  # If set, preprocess strings before encoding
        self.is_random_column = is_random_column  # If True, return zero embeddings
        
        if delimiter:
            logger.info(f"🔧 StringCodec '{debugName}' will preprocess with delimiter: '{delimiter}'")
        if is_random_column:
            logger.warning(f"🚫 StringCodec '{debugName}' marked as RANDOM - will return zero embeddings")

        # Use global string cache instead of creating individual cache per codec
        # Don't store the cache object - use lazy lookup to avoid pickling issues with DataLoader workers
        logger.info(f"🔗 StringCodec using global string cache: {string_cache or 'default'}")
        logger.info(f"🔍 STRINGCODEC DEBUG: string_cache parameter = {string_cache}")
        logger.info(f"🔍 STRINGCODEC DEBUG: debugName = {debugName}")
        logger.info(f"🔍 STRINGCODEC DEBUG: initial_values count = {len(initial_values) if initial_values else 0}")

        # Initialize the global cache with initial values, but don't store the reference
        # The cache will be accessed via lazy lookup in tokenize()
        get_global_string_cache(
            cache_filename=string_cache,
            initial_values=initial_values,
            debug_name=debugName
        )
        
        # Compute frequency statistics for frequency encoding
        from collections import Counter
        if initial_values:
            value_counts = Counter(str(v) for v in initial_values if v is not None and str(v) != 'nan')
            total_count = len([v for v in initial_values if v is not None and str(v) != 'nan'])
            self.column_freq_stats = {
                'value_counts': value_counts,
                'total_count': total_count
            }
        else:
            self.column_freq_stats = None
        
        # Separate paths for BERT and features - both contribute equally, features can matter more
        # BERT path: [384] → [384] (preserve semantic info)
        self.bert_projection = nn.Sequential(
            nn.Linear(STRING_DIM, STRING_DIM),  # [384] → [384]
            nn.ReLU(),
            nn.Dropout(0.1),
        )
        
        # Features path: [27] → [384] (give features full capacity to contribute)
        # Features might matter more than BERT for structured data
        self.feature_embedding_mlp = nn.Sequential(
            nn.Linear(27, 256),  # 27 features → 256 hidden (larger capacity)
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, STRING_DIM),  # 256 → [384] (same size as BERT)
        )
        
        # Learned merge: combine BERT [384] + features [384] → [384]
        # Learns how much to weight each (features might be more important)
        self.merge_mlp = nn.Sequential(
            nn.Linear(STRING_DIM * 2, STRING_DIM * 2),  # [768] → [768]
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(STRING_DIM * 2, STRING_DIM),  # [768] → [384]
        )
        
        # Initialize weights
        for name, param in self.bert_projection.named_parameters():
            if 'weight' in name and param.ndim >= 2:
                nn.init.xavier_uniform_(param, gain=0.5)
            elif 'bias' in name:
                nn.init.zeros_(param)
        
        for name, param in self.feature_embedding_mlp.named_parameters():
            if 'weight' in name and param.ndim >= 2:
                nn.init.xavier_uniform_(param, gain=0.5)
            elif 'bias' in name:
                nn.init.zeros_(param)
        
        for name, param in self.merge_mlp.named_parameters():
            if 'weight' in name and param.ndim >= 2:
                nn.init.xavier_uniform_(param, gain=0.5)
            elif 'bias' in name:
                nn.init.zeros_(param)
        
        logger.info(f"🔧 StringCodec '{debugName}': Separate BERT + features paths (both [384]), learned merge (features can matter more)")

    def _safe_get_bert_projection(self):
        """Safely get bert_projection if it exists and is valid, otherwise return None."""
        bert_proj = getattr(self, 'bert_projection', None)
        if bert_proj is not None:
            try:
                # Verify it's a valid module with parameters
                _ = next(bert_proj.parameters())
                return bert_proj
            except (AttributeError, StopIteration, TypeError):
                return None
        return None
    
    def _safe_get_feature_embedding_mlp(self):
        """Safely get feature_embedding_mlp if it exists and is valid, otherwise return None."""
        feature_mlp = getattr(self, 'feature_embedding_mlp', None)
        if feature_mlp is not None:
            try:
                # Verify it's a valid module with parameters
                _ = next(feature_mlp.parameters())
                return feature_mlp
            except (AttributeError, StopIteration, TypeError):
                return None
        return None
    
    def _safe_get_merge_mlp(self):
        """Safely get merge_mlp if it exists and is valid, otherwise return None."""
        merge_mlp = getattr(self, 'merge_mlp', None)
        if merge_mlp is not None:
            try:
                # Verify it's a valid module with parameters
                _ = next(merge_mlp.parameters())
                return merge_mlp
            except (AttributeError, StopIteration, TypeError):
                return None
        return None
    
    def has_mlp_layers(self):
        """Check if all MLP layers exist and are valid."""
        return (self._safe_get_bert_projection() is not None and
                self._safe_get_feature_embedding_mlp() is not None and
                self._safe_get_merge_mlp() is not None)

    def __getstate__(self):
        # Simply exclude the cache object - global cache will handle the rest
        state = self.__dict__.copy()
        state.pop("string_cache", None)
        return state

    def __setstate__(self, state):
        # Get debug_name from state dict (it hasn't been set on self yet)
        debug_name = state.get('debug_name', state.get('colName', 'unknown'))
        
        # CRITICAL: Clear GPU cache at the VERY START of __setstate__ to prevent GPU allocation during unpickling
        # This must happen before self.__dict__.update(state) which triggers unpickling of nested objects
        try:
            if is_gpu_available():
                empty_gpu_cache()
        except Exception as e:
            logger.debug(f"Could not clear GPU cache in __setstate__: {e}")
        
        # Log GPU memory at the very start of __setstate__
        allocated_start = 0.0
        reserved_start = 0.0
        if is_gpu_available():
            allocated_start = get_gpu_memory_allocated()
            reserved_start = get_gpu_memory_reserved()
        
        # CRITICAL: Check force_cpu flag BEFORE unpickling to prevent GPU allocation
        force_cpu = os.environ.get('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR') == '1'
        
        # If force_cpu is set, move any GPU tensors in state to CPU BEFORE self.__dict__.update
        if force_cpu:
            logger.info(f"StringCodec.__setstate__ '{debug_name}': force_cpu=True, moving state tensors to CPU before update")
            for key, value in list(state.items()):
                # Check if it's an nn.Module and move to CPU
                if hasattr(value, 'cpu') and hasattr(value, 'parameters'):
                    try:
                        state[key] = value.cpu()
                        logger.debug(f"  Moved {key} to CPU before update")
                    except Exception as e:
                        logger.debug(f"  Could not move {key} to CPU: {e}")
        
        # Restore state and reconnect to global cache
        self.__dict__.update(state)
        

        # Backward compatibility: set defaults for new attributes not in old pickles
        if 'is_random_column' not in state:
            self.is_random_column = False
        if 'delimiter' not in state:
            self.delimiter = None
        if 'column_freq_stats' not in state:
            # Older models don't have column_freq_stats - set to None (will use fallback in tokenize)
            self.column_freq_stats = None
        
        # MLPs should already be on CPU from above, but double-check
        if force_cpu:
            try:
                # Move all MLPs to CPU if they exist and are on GPU
                if hasattr(self, 'bert_projection') and self.bert_projection is not None:
                    if list(self.bert_projection.parameters()):
                            bert_device = next(self.bert_projection.parameters()).device
                            if bert_device.type in ['cuda', 'mps']:
                                self.bert_projection = self.bert_projection.cpu()
                                if is_gpu_available():
                                    empty_gpu_cache()
                
                if hasattr(self, 'feature_embedding_mlp') and self.feature_embedding_mlp is not None:
                    if list(self.feature_embedding_mlp.parameters()):
                        feature_device = next(self.feature_embedding_mlp.parameters()).device
                        if feature_device.type in ['cuda', 'mps']:
                            self.feature_embedding_mlp = self.feature_embedding_mlp.cpu()
                            if is_gpu_available():
                                empty_gpu_cache()
                
                if hasattr(self, 'merge_mlp') and self.merge_mlp is not None:
                    if list(self.merge_mlp.parameters()):
                        merge_device = next(self.merge_mlp.parameters()).device
                        if merge_device.type in ['cuda', 'mps']:
                            self.merge_mlp = self.merge_mlp.cpu()
                            if is_gpu_available():
                                empty_gpu_cache()
                
            except Exception as e:
                logger.error(f"❌ StringCodec.__setstate__ '{debug_name}': Could not check/move MLPs: {e}")
                logger.error(traceback.format_exc())
        
        # CRITICAL: Workers must NEVER load sentence model on GPU
        # Check multiple indicators - be VERY defensive during unpickling
        is_worker = _is_worker_process()
        
        # Additional check: spawned processes that aren't MainProcess are likely workers
        is_likely_worker = False
        try:
            import multiprocessing
            mp_name = multiprocessing.current_process().name
            if mp_name != 'MainProcess' and os.environ.get('PYTORCH_DATALOADER_WORKER') is None:
                is_likely_worker = True
        except Exception:
            pass
        
        # Only load if we're CERTAIN we're in main process
        if not is_worker and not is_likely_worker:
            allocated_before = 0.0
            reserved_before = 0.0
            if is_gpu_available():
                allocated_before = get_gpu_memory_allocated()
                reserved_before = get_gpu_memory_reserved()
            # String server client is initialized on first use - no local model loading needed
        
        # Don't reconnect here - use lazy lookup via _get_string_cache() when needed
        # This prevents storing StringCache object (which has sqlite connections) in the codec
        # This is critical for multiprocessing DataLoader workers which need to pickle the codec

    def _get_string_cache(self):
        """Get StringCache from global registry using filename. Don't store the object."""
        if not hasattr(self, '_string_cache_filename') or not self._string_cache_filename:
            # Don't spam logs - this is normal when string cache isn't configured
            return None
        try:
            # In workers, the global cache registry is empty (not shared across processes)
            # So we need to create a new cache instance that reads from the SQLite file
            # The cache will be opened in read-only mode automatically if we're in a worker
            is_worker = _is_worker_process()
            if is_worker:
                # Worker process - create cache instance that reads from existing SQLite file
                # Don't pass initial_values - workers should only read, not populate
                cache = get_global_string_cache(
                    cache_filename=self._string_cache_filename,
                    initial_values=[],  # Workers don't populate - only read
                    debug_name=getattr(self, 'debug_name', getattr(self, 'colName', 'fallback_codec'))
                )
                # Ensure it's marked as readonly
                if cache:
                    cache.is_readonly = True
                return cache
            else:
                # Main process - use global cache registry
                return get_global_string_cache(
                    cache_filename=self._string_cache_filename,
                    initial_values=[],  # Global cache already has the data
                    debug_name=getattr(self, 'debug_name', getattr(self, 'colName', 'fallback_codec'))
                )
        except Exception as e:
            # Log actual errors with more detail
            logger.error(f"❌ Failed to get string cache for '{getattr(self, 'debug_name', getattr(self, 'colName', 'unknown'))}': {e}")
            logger.error(f"   Cache filename: {self._string_cache_filename}")
            logger.error(f"   Absolute path: {os.path.abspath(self._string_cache_filename) if self._string_cache_filename else 'None'}")
            logger.error(f"   File exists: {os.path.exists(self._string_cache_filename) if self._string_cache_filename else 'N/A'}")
            logger.debug(traceback.format_exc())
            return None
    def get_codec_name(self):
        return ColumnType.FREE_STRING

    def get_not_present_token(self):
        tok = self.tokenize("")
        return set_not_present(tok)

    def get_marginal_token(self):
        """Return a token representing a masked/marginal value for reconstruction testing."""
        tok = self.tokenize("")
        return Token(
            value=tok.value,
            status=TokenStatus.MARGINAL,
            attention_mask=tok.attention_mask,
        )

    # def detokenize(self, token: Token, top_k: int = 1, debug: bool = False):
    #     """
    #     Detokenize a string token back to an actual value using nearest neighbor search.
    #     
    #     COMMENTED OUT: String decoding requires indexing final embeddings (d_model dims) in LanceDB,
    #     not BERT embeddings (384 dims). The encoder outputs d_model dimensions, but the cache stores
    #     BERT embeddings. Need to build a separate index of final embeddings for proper decoding.
    #     
    #     Args:
    #         token: Token with embedding as value (from encoder output)
    #         top_k: Number of nearest neighbors to return (default 1, use 3 for debugging)
    #         debug: If True, return top 3 neighbors for debugging
    #         
    #     Returns:
    #         If debug=False: Best matching string value
    #         If debug=True: Tuple of (best_match, top_3_list) where top_3_list is [(string, distance), ...]
    #     """
    #     raise NotImplementedError("String decoding not yet implemented - needs final embedding index")
    
    @property
    def token_dtype(self):
        return float

    def tokenize(self, value):
        """Here we actually do both the tokenize & encode."""
        # String server client is initialized on first use - no local model loading needed
        # Workers should only read from cache
        
        # Handle random columns - return zero embedding (zero contribution)
        # Backward compatibility: old pickled codecs don't have is_random_column
        is_random = getattr(self, 'is_random_column', False)
        if is_random:
            return Token(
                value=torch.zeros(STRING_DIM, dtype=torch.float32),  # [384] after projection
                status=TokenStatus.NOT_PRESENT,
            )
        
        try:
            try:
                isNan = False
                if value is None:
                    isNan = True
                if (
                    type(value) == float
                    or type(value) == int
                    or type(value) == np.float64
                    or type(value) == np.float32
                ):
                    if math.isnan(value):
                        isNan = True

                if isNan:
                    result = Token(
                        value=torch.zeros(STRING_DIM, dtype=torch.float32),  # [384]
                        status=TokenStatus.NOT_PRESENT,
                    )
                    # DEBUG: Check NOT_PRESENT token type
                    assert result.value.dtype == torch.float32, f"NOT_PRESENT token (1) is {result.value.dtype}, expected float32"
                    return result

                if str(value) == "nan":
                    assert False, "what the heck"

            except:
                traceback.print_exc()

            value = str(value)
            if value == "nan":
                result = Token(
                    value=torch.zeros(STRING_DIM, dtype=torch.float32),  # [384]
                    status=TokenStatus.NOT_PRESENT,
                )
                # DEBUG: Check NOT_PRESENT token type
                assert result.value.dtype == torch.float32, f"NOT_PRESENT token (2) is {result.value.dtype}, expected float32"
                return result

            # Check for natural language null strings ("N/A", "none", "-", "nada", etc.)
            # Uses semantic similarity to catch typos and variants
            # Note: is_null_natural_language has fallback when sentence_model is None
            from featrix.neural.string_analysis import is_null_natural_language
            if is_null_natural_language(value, sentence_model=None):
                result = Token(
                    value=torch.zeros(STRING_DIM, dtype=torch.float32),  # [384]
                    status=TokenStatus.NOT_PRESENT,
                )
                return result

            # Save original value for feature computation (before preprocessing)
            original_value = str(value)
            
            # Preprocess delimited strings BEFORE string cache lookup
            # Convert "a,b,c" → "a\nb\nc" for better BERT encoding
            if self.delimiter and isinstance(value, str):
                from featrix.neural.string_analysis import preprocess_delimited_string
                value = preprocess_delimited_string(value, self.delimiter)

            # SimpleStringCache: just call get_embedding_from_cache
            # It handles @lru_cache (32k entries) and calls string server client
            # String server client has automatic retry across fallback URLs
            # Use lazy lookup to avoid storing StringCache in codec (critical for multiprocessing)
            cache = get_global_string_cache(
                cache_filename=self._string_cache_filename if hasattr(self, '_string_cache_filename') else None,
                initial_values=None,
                debug_name=self.debug_name
            )
            val = cache.get_embedding_from_cache(value) if cache else None
            
            # Check if we got an embedding
            if val is not None:
                cache_status = "cache_hit"
                assert hasattr(val, 'dtype'), f"String cache returned non-tensor: {type(val)}"
                assert val.dtype == torch.float32, f"String cache returned {val.dtype}, expected float32"
                
                # Ensure shape is [384] not [1, 384]
                if len(val.shape) == 2:
                    val = val.squeeze(0)
                
                # Check for NaN in cached value
                if torch.isnan(val).any():
                    logger.error(f"🚨 STRING CACHE RETURNED NaN: value='{value}' -> {val}")
                    cache_status = "cache_hit_but_nan"
            else:
                cache_status = "cache_miss"

            if val is None:
                # Check if we're in a worker - workers should NEVER compute embeddings
                is_worker = _is_worker_process()
                if is_worker:
                    # Worker cache miss - CRITICAL: Don't return zero embeddings, crash instead
                    # Zero embeddings will corrupt the embedding space and produce bad models
                    error_msg = (
                        f"❌ CRITICAL: Worker cache miss for '{value[:50]}...' - value not in cache. "
                        f"Cannot return zero embedding as it would corrupt the embedding space. "
                        f"Total unique cache misses: {len(_logged_cache_misses) + 1}. "
                        f"Consider adding all unique training values to initial_values when creating StringCodec."
                    )
                    logger.error(error_msg)
                    raise RuntimeError(
                        f"StringCodec worker cache miss: '{value[:50]}...' not found in cache. "
                        f"This indicates the cache was not properly populated before workers started. "
                        f"Refusing to return zero embedding to prevent corrupting the embedding space."
                    )
                else:
                    # Main process - can compute embeddings and add to cache
                    cache_status = f"{cache_status}_fallback_to_direct"
                    try:
                        # Use string server client (required - no local model fallback)
                        client = _init_string_server_client()
                        if client is None:
                            raise RuntimeError(
                                "String server client not available. "
                                "Set 'string_server_host' in config.json to 'taco', 'taco.local', or 'localhost'. "
                                "Local sentence transformer model is no longer supported."
                            )
                        
                        # Use string server with retry logic - wait up to 10 minutes for recovery
                        import time
                        max_retry_time = 600.0  # 10 minutes
                        base_delay = 1.0  # Start with 1 second
                        max_delay = 30.0  # Cap at 30 seconds
                        last_error = None
                        val = None
                        attempt = 0
                        retry_start = time.time()
                        outage_notified = False
                        
                        while (time.time() - retry_start) < max_retry_time:
                            try:
                                embedding_list = client.encode(value)
                                val = torch.tensor(embedding_list, dtype=torch.float32)
                                cache_status = f"{cache_status}_string_server"
                                
                                # If we had an outage and recovered, log it
                                if outage_notified:
                                    elapsed = time.time() - retry_start
                                    logger.info(f"✅ String server recovered after {elapsed:.1f}s")
                                
                                break  # Success!
                            except Exception as encode_error:
                                last_error = encode_error
                                # Check if it's a retriable error (503, connection errors, timeouts)
                                error_str = str(encode_error).lower()
                                is_retriable = any(x in error_str for x in [
                                    'connection refused',
                                    'connection error',
                                    'timeout',
                                    'timed out',
                                    '503',
                                    'service unavailable',
                                    'max retries exceeded',
                                    'failed to establish'
                                ])
                                
                                if not is_retriable:
                                    # Not retriable - fail immediately
                                    raise
                                
                                elapsed = time.time() - retry_start
                                
                                # Send notification on first outage detection
                                if not outage_notified and attempt == 0:
                                    logger.error(f"🚨 String server outage detected: {error_str[:200]}")
                                    logger.error(f"   Will retry for up to 10 minutes...")
                                    outage_notified = True
                                
                                # Check if we've exceeded max retry time
                                if elapsed >= max_retry_time:
                                    logger.error(f"❌ String server failed after {elapsed:.1f}s (10 minute timeout): {error_str[:200]}")
                                    raise RuntimeError(
                                        f"String server unavailable for {elapsed:.1f}s. "
                                        f"Giving up after 10 minutes. Last error: {error_str}"
                                    ) from last_error
                                
                                # Calculate exponential backoff delay (capped at max_delay)
                                delay = min(base_delay * (1.5 ** attempt), max_delay)
                                remaining = max_retry_time - elapsed
                                
                                # Log retry attempts periodically (every 5th attempt or every 60s)
                                if attempt % 5 == 0 or attempt == 1 or elapsed % 60 < delay:
                                    logger.warning(
                                        f"⚠️  String server retry attempt {attempt + 1} "
                                        f"(elapsed: {elapsed:.1f}s, remaining: {remaining:.1f}s, "
                                        f"next retry in {delay:.1f}s): {error_str[:100]}"
                                    )
                                
                                time.sleep(delay)
                                attempt += 1
                        
                        # Should never reach here if all retries failed (would have raised)
                        if val is None:
                            elapsed = time.time() - retry_start
                            raise RuntimeError(f"String encoding failed after {elapsed:.1f}s: {last_error}")
                        
                        assert val.dtype == torch.float32, f"encode returned {val.dtype}, expected float32"
                        
                        # Check for NaN in encoding
                        if torch.isnan(val).any():
                            logger.error(f"🚨 ENCODING RETURNED NaN: value='{value}' -> {val}")
                            cache_status = f"{cache_status}_nan"
                        
                        # Try to add to cache for future use (use lazy lookup)
                        cache = get_global_string_cache(
                            cache_filename=self._string_cache_filename if hasattr(self, '_string_cache_filename') else None,
                            initial_values=None,
                            debug_name=self.debug_name
                        )
                        if cache:
                            try:
                                cache.get_embedding_from_cache(value, add_if_missing=True)
                            except Exception as cache_error:
                                logger.debug(f"Could not add to cache: {cache_error}")
                        
                    except Exception as e:
                        cache_status = f"{cache_status}_direct_failed"
                        error_msg = (
                            f"❌ CRITICAL: Failed to encode string '{value[:50]}...': {e}. "
                            f"Cannot return zero embedding as it would corrupt the embedding space."
                        )
                        logger.error(error_msg)
                        raise RuntimeError(
                            f"StringCodec encoding failure: '{value[:50]}...' could not be encoded. "
                            f"Refusing to return zero embedding to prevent corrupting the embedding space. "
                            f"Original error: {e}"
                        )
                    
            # Log cache status for debugging (first few times)
            # debug_count = getattr(self, '_debug_tokenize_count', 0)
            # if debug_count < 10:
            #     logger.info(f"🔍 STRING TOKENIZE DEBUG #{debug_count}: value='{value[:50]}' status={cache_status} result_shape={val.shape if val is not None else 'None'}")
            #     self._debug_tokenize_count = debug_count + 1
            
            # FINAL SHAPE CHECK: Ensure val is [384] not [1, 384] before creating Token
            if len(val.shape) == 2:
                val = val.squeeze(0)
            assert len(val.shape) == 1 and val.shape[0] == STRING_DIM, f"Token value must be [{STRING_DIM}], got {val.shape}"
            
            # Compute structured features and embed them (use original value before preprocessing)
            from featrix.neural.string_analysis import compute_string_features
            # Handle backward compatibility: older models might not have column_freq_stats
            column_freq_stats = getattr(self, 'column_freq_stats', None)
            raw_features = compute_string_features(original_value, column_freq_stats)
            
            # Backward compatibility: Check if this is an older model without MLP layers
            # Use safe accessors to get MLP layers
            bert_proj = self._safe_get_bert_projection()
            feature_mlp = self._safe_get_feature_embedding_mlp()
            merge_mlp = self._safe_get_merge_mlp()
            
            has_mlp_layers = self.has_mlp_layers()
            
            if has_mlp_layers:
                # New model with MLP layers: Separate paths for BERT and features
                # Double-check that we actually have valid modules (safety check)
                if bert_proj is None or feature_mlp is None or merge_mlp is None:
                    # Fallback to older model behavior if modules are missing
                    logger.warning("MLP layers detected but modules are None - using backward compatibility path")
                    result = Token(value=val, status=TokenStatus.OK)
                    assert hasattr(result.value, 'dtype'), f"Token value is non-tensor: {type(result.value)}"
                    assert result.value.dtype == torch.float32, f"Token value is {result.value.dtype}, expected float32"
                    return result
                
                # Ensure MLPs are on same device as input tensors
                device = val.device
                # Move MLPs to device if needed (they might be on CPU initially)
                # Safe access - we know they exist from has_mlp_layers() check, but add try-except for extra safety
                try:
                    if bert_proj is not None:
                        bert_device = next(bert_proj.parameters()).device
                        if bert_device != device:
                            self.bert_projection = bert_proj.to(get_device())
                            bert_proj = self.bert_projection  # Update local variable
                except (AttributeError, StopIteration, TypeError) as e:
                    logger.warning(f"Failed to check/move bert_projection device: {e}, falling back to older model path")
                    result = Token(value=val, status=TokenStatus.OK)
                    assert hasattr(result.value, 'dtype'), f"Token value is non-tensor: {type(result.value)}"
                    assert result.value.dtype == torch.float32, f"Token value is {result.value.dtype}, expected float32"
                    return result
                
                try:
                    if feature_mlp is not None:
                        feature_device = next(feature_mlp.parameters()).device
                        if feature_device != device:
                            self.feature_embedding_mlp = feature_mlp.to(get_device())
                            feature_mlp = self.feature_embedding_mlp  # Update local variable
                except (AttributeError, StopIteration, TypeError) as e:
                    logger.warning(f"Failed to check/move feature_embedding_mlp device: {e}, falling back to older model path")
                    result = Token(value=val, status=TokenStatus.OK)
                    assert hasattr(result.value, 'dtype'), f"Token value is non-tensor: {type(result.value)}"
                    assert result.value.dtype == torch.float32, f"Token value is {result.value.dtype}, expected float32"
                    return result
                
                try:
                    if merge_mlp is not None:
                        merge_device = next(merge_mlp.parameters()).device
                        if merge_device != device:
                            self.merge_mlp = merge_mlp.to(get_device())
                            merge_mlp = self.merge_mlp  # Update local variable
                except (AttributeError, StopIteration, TypeError) as e:
                    logger.warning(f"Failed to check/move merge_mlp device: {e}, falling back to older model path")
                    result = Token(value=val, status=TokenStatus.OK)
                    assert hasattr(result.value, 'dtype'), f"Token value is non-tensor: {type(result.value)}"
                    assert result.value.dtype == torch.float32, f"Token value is {result.value.dtype}, expected float32"
                    return result
                
                # Final safety check before using MLP layers
                if bert_proj is None or feature_mlp is None or merge_mlp is None:
                    logger.warning("MLP layers became None during device check - using backward compatibility path")
                    result = Token(value=val, status=TokenStatus.OK)
                    assert hasattr(result.value, 'dtype'), f"Token value is non-tensor: {type(result.value)}"
                    assert result.value.dtype == torch.float32, f"Token value is {result.value.dtype}, expected float32"
                    return result
                
                # Use MLP layers - safe because we've verified they exist
                # CRITICAL: Clone val if it was created in inference mode to avoid autograd error
                # val comes from string server client encoding
                # Always clone to ensure we have a fresh tensor that can participate in autograd
                val_clone = val.detach().clone().requires_grad_(True)
                
                # Move inputs to model devices to avoid device mismatch
                bert_device = next(bert_proj.parameters()).device
                bert_projected = bert_proj(val_clone.unsqueeze(0).to(bert_device)).squeeze(0)  # [384] → [384]
                
                mlp_device = next(feature_mlp.parameters()).device
                feature_embedding = feature_mlp(raw_features.to(mlp_device))  # [27] → [384]
                
                # Concatenate both [384] embeddings = [768]
                combined_input = torch.cat([bert_projected, feature_embedding], dim=0)
                
                # Learned merge: [768] → [384] (learns optimal combination, features can dominate)
                merge_device = next(merge_mlp.parameters()).device
                combined_embedding = merge_mlp(combined_input.unsqueeze(0).to(merge_device)).squeeze(0)
                assert combined_embedding.shape[0] == STRING_DIM, f"Merged embedding must be [{STRING_DIM}], got {combined_embedding.shape}"
                
                result = Token(value=combined_embedding, status=TokenStatus.OK)
            else:
                # Older model: Just use the BERT embedding directly (backward compatibility)
                result = Token(value=val, status=TokenStatus.OK)
            assert hasattr(result.value, 'dtype'), f"Token value is non-tensor: {type(result.value)}"
            assert result.value.dtype == torch.float32, f"Token value is {result.value.dtype}, expected float32"
            return result

        except Exception as e:
            # Log the error but re-raise - we don't want to silently return zero embeddings
            # Worker cache misses should crash the training to prevent corrupting the embedding space
            traceback.print_exc()
            logger.error(f"🚨 STRING TOKENIZATION FAILED for value: {repr(value)}")
            raise  # Re-raise the exception - don't return zero embeddings

    def save(self):
        # we create a json dict.
        buffer = io.BytesIO()
        torch.save(self.state_dict(), buffer)

        buffer_b64 = "base64:" + str(
            base64.standard_b64encode(buffer.getvalue()).decode("utf8")
        )
        checksum = hashlib.md5(buffer.getvalue()).hexdigest()

        d = {
            "type": "StringCodec",
            "embedding": buffer_b64,
            "embedding_checksum": checksum,
            "enc_dim": self.enc_dim,
        }
        return d

    def load(self, j):
        d_type = j.get("type")
        assert d_type == "StringCodec", "wrong load method called for __%s__" % d_type
        self.enc_dim = j.get("enc_dim")
        embed = j.get("embedding")
        embed_checksum = j.get("embedding_checksum")

        if embed.startswith("base64:"):
            embed = embed[6:]

        r64 = base64.standard_b64decode(embed)
        r_checksum64 = hashlib.md5(r64).hexdigest()

        if r_checksum64 != embed_checksum:
            logger.error(f"CHECKSUMS {r_checksum64} and {embed_checksum} DO NOT MATCH - !")
            return

        self.__init__(self.enc_dim)

        buffer = io.BytesIO(r64)
        theDict = torch.load(buffer, weights_only=False)
        self.load_state_dict(theDict)
        return

    def get_gpu_efficiency_report(self):
        """Get a report on GPU efficiency for string processing."""
        cache = self._get_string_cache()
        if cache is None:
            return {"status": "No string cache available"}
        
        stats = cache.get_gpu_efficiency_stats()
        
        # Get string server info
        client = _init_string_server_client()
        server_url = client.base_url if client else None
        
        report = {
            "string_server_url": server_url,
            "string_server_available": client is not None,
            "gpu_available": is_gpu_available(),
            "cache_statistics": stats,
            "recommendations": []
        }
        
        # Add recommendations based on performance
        if stats['cache_hit_rate'] < 0.5:
            report["recommendations"].append("Consider providing more comprehensive initial_values to StringCodec to reduce cache misses")
        
        if stats['individual_gpu_encodings'] > 100:
            report["recommendations"].append(f"High number of individual GPU encodings ({stats['individual_gpu_encodings']}) - consider batch processing")
            
        # Removed sentence transformer device check - string server handles encoding
            
        return report


# def runStringSaveLoadTest():
#
#     data = [
#         "hello world",
#         "foo",
#         "bar",
#     ]
#     print(data)
#
#     codec = StringCodec(50)
#     jj = codec.save()
#
#     tokenBatch = create_token_batch([codec.tokenize(x) for x in data])
#     print("tokenBatch:", tokenBatch)
#
#     preSave_encodedTokens = codec.encode(tokenBatch)
#     print("preSave_encodedTokens = ", preSave_encodedTokens)
#
#     # print(jj)
#
#     jj_enc_dim = jj.get("enc_dim")
#
#     codec = None  # remove from scope
#     tokenBatch = None
#
#     newCodec = StringCodec(jj_enc_dim)
#     newCodec.load(jj)
#     print(newCodec)
#
#     loadTokenBatch = create_token_batch([newCodec.tokenize(x) for x in data])
#     print("loadTokenBatch:", loadTokenBatch)
#
#     postLoad_encodedTokens = newCodec.encode(loadTokenBatch)
#
#     assert torch.equal(postLoad_encodedTokens, preSave_encodedTokens)
#
#     return


if __name__ == "__main__":
    from featrix.neural.featrix_token import create_token_batch, set_not_present, set_unknown

    d_embed = 50  # FIXME: somewhere this is defined.

    sc = StringCodec(enc_dim=d_embed)
    # print(sc.mlp_encoder)

    token = sc.tokenize(
        "hello world asdfas asdf a dfa df asd fas df adf asd fa sdf asdf a df adf "
    )
    # print("the real token:", token)
    token_not_present = set_not_present(token)
    token_unknown = set_unknown(token)

    tokens = create_token_batch([token, token_not_present, token_unknown])
    # print("tokens = ", tokens)
    # print("---")
    out = sc.encode(tokens)
    print("out = ", out)
    assert out.shape[0] == 3
    assert out.shape[1] == d_embed
    print(out.shape)

    # runStringSaveLoadTest()
