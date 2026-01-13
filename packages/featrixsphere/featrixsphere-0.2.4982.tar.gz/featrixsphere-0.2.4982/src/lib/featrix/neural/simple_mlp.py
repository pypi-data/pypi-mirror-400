#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
from dataclasses import dataclass
import logging
import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from featrix.neural.model_config import SimpleMLPConfig
from featrix.neural.sphere_config import SphereConfig

logger = logging.getLogger(__name__)

# class SimpleMLP(nn.Module):
#     def __init__(
#         self, d_in, d_out, d_hidden, hidden_layers=0, dropout=0.1, normalize=True
#     ):
#         super().__init__()

#         if hidden_layers == 0:
#             self.model = nn.Linear(d_in, d_out)
#         else:
#             layers_prefix = [
#                 nn.Linear(d_in, d_hidden),
#             ]

#             layers_middle = []
#             for _ in range(hidden_layers - 1):
#                 layers_middle.append(nn.LeakyReLU())
#                 layers_middle.append(nn.Linear(d_hidden, d_hidden))

#             layers_suffix = [
#                 nn.BatchNorm1d(d_hidden, affine=False),
#                 nn.LeakyReLU(),
#                 nn.Dropout(p=dropout),
#                 nn.Linear(d_hidden, d_out),
#             ]

#             layers = layers_prefix + layers_middle + layers_suffix

#             self.model = nn.Sequential(*layers)

#         self.normalize = normalize

#     def forward(self, input):
#         out = self.model(input)
#         if self.normalize:
#             out = nn.functional.normalize(out, dim=1)
#         return out


class SelfAttentionBlock(nn.Module):
    """
    Self-attention block for single embedding vectors.
    
    Learns to attend to different dimensions of the embedding vector by:
    1. Creating multiple query/key/value projections (multi-head)
    2. Computing attention weights over the embedding dimensions
    3. Re-weighting the embedding based on learned importance
    
    This allows the model to learn which embedding dimensions are most
    relevant for the prediction task.
    """
    def __init__(self, d_model: int, n_heads: int = 4, dropout: float = 0.1):
        super().__init__()
        assert d_model % n_heads == 0, f"d_model ({d_model}) must be divisible by n_heads ({n_heads})"
        
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        
        # Projections for Q, K, V - each projects to d_model
        self.w_q = nn.Linear(d_model, d_model, bias=False)
        self.w_k = nn.Linear(d_model, d_model, bias=False)
        self.w_v = nn.Linear(d_model, d_model, bias=False)
        self.w_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(d_model)
        
    def forward(self, x):
        """
        Args:
            x: [batch, d_model] - single embedding vector
            
        Returns:
            [batch, d_model] - attended representation
        """
        residual = x
        batch_size = x.size(0)
        
        # Project to Q, K, V: [batch, d_model]
        Q = self.w_q(x)  # [batch, d_model]
        K = self.w_k(x)  # [batch, d_model]
        V = self.w_v(x)  # [batch, d_model]
        
        # Reshape for multi-head: [batch, n_heads, d_k]
        Q = Q.view(batch_size, self.n_heads, self.d_k)  # [batch, n_heads, d_k]
        K = K.view(batch_size, self.n_heads, self.d_k)  # [batch, n_heads, d_k]
        V = V.view(batch_size, self.n_heads, self.d_k)  # [batch, n_heads, d_k]
        
        # Compute attention scores: Q @ K^T gives [batch, n_heads, d_k, d_k]
        # This learns relationships between different parts of the embedding
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)  # [batch, n_heads, d_k, d_k]
        
        # Apply softmax to get attention weights
        attn_weights = F.softmax(scores, dim=-1)  # [batch, n_heads, d_k, d_k]
        attn_weights = self.dropout(attn_weights)
        
        # Apply attention to values
        attn_output = torch.matmul(attn_weights, V)  # [batch, n_heads, d_k]
        
        # Concatenate heads: [batch, d_model]
        attn_output = attn_output.view(batch_size, self.d_model)
        
        # Output projection
        output = self.w_o(attn_output)  # [batch, d_model]
        output = self.dropout(output)
        
        # Add residual and layer norm
        output = self.layer_norm(output + residual)
        
        return output


class SimpleMLP(nn.Module):
    def __init__(
        # self, d_in, d_out, d_hidden, hidden_layers=0, dropout=0.1, normalize=True, residual=True, use_batch_norm=True,
        self,
        config: SimpleMLPConfig,
    ):
        super().__init__()

        self.config = config
        
        # Determine if attention should be enabled
        # If use_attention is None, check global config
        # Use getattr() for backward compatibility with old configs that don't have these fields
        use_attention = getattr(config, 'use_attention', None)
        if use_attention is None:
            sphere_config = SphereConfig.get_instance()
            self.use_attention = sphere_config.get_enable_predictor_attention()
            self.attention_heads = sphere_config.get_predictor_attention_heads()
        else:
            self.use_attention = use_attention
            self.attention_heads = getattr(config, 'attention_heads', None) or 4
        
        # Attention dropout defaults to main dropout if not specified
        attention_dropout = getattr(config, 'attention_dropout', None)
        self.attention_dropout = attention_dropout if attention_dropout is not None else config.dropout
        
        # Log attention configuration
        if self.use_attention and config.n_hidden_layers > 0:
            logger.info(f"🔍 Predictor attention ENABLED: {self.attention_heads} heads, dropout={self.attention_dropout:.3f}")
        elif self.use_attention and config.n_hidden_layers == 0:
            logger.warning(f"⚠️  Predictor attention requested but n_hidden_layers=0 - attention disabled (requires hidden layers)")

        # If there's 0 requested hidden layers, we just use a single linear layer.
        if config.n_hidden_layers == 0:
            self.single_layer = nn.Linear(config.d_in, config.d_out)
            self.use_attention = False  # Can't use attention with 0 hidden layers

        self.linear_in = nn.Linear(config.d_in, config.d_hidden, bias=True)
        self.linear_out = nn.Linear(config.d_hidden, config.d_out, bias=True)

        module_list = []
        attention_list = []
        
        for _ in range(config.n_hidden_layers):
            # Feedforward block
            if config.use_batch_norm:
                modules = [
                    nn.Linear(config.d_hidden, config.d_hidden),
                    nn.BatchNorm1d(config.d_hidden),
                    # nn.LayerNorm(d_hidden),
                    nn.GELU(),
                    nn.Dropout(config.dropout),
                ]
            else:
                modules = [
                    nn.Linear(config.d_hidden, config.d_hidden),
                    nn.GELU(),
                    nn.Dropout(config.dropout),
                ]

            module_list.append(nn.Sequential(*modules))
            
            # Attention block (if enabled)
            if self.use_attention:
                attention_list.append(
                    SelfAttentionBlock(
                        d_model=config.d_hidden,
                        n_heads=self.attention_heads,
                        dropout=self.attention_dropout
                    )
                )
            else:
                attention_list.append(None)

        self.layers = nn.ModuleList(module_list)
        self.attention_layers = nn.ModuleList(attention_list) if self.use_attention else None
        
        # Debug flag for logging batch norm statistics
        # Only enable for debugging - logs every forward pass (very verbose!)
        self.debug_batchnorm = True

    def log_batchnorm_stats(self):
        """Log statistics about all BatchNorm layers in the model."""
        if not self.config.use_batch_norm:
            logger.info("🔍 BatchNorm: Not using batch normalization")
            return
            
        logger.info(f"🔍 BatchNorm Debug - Model training mode: {self.training}")
        
        for layer_idx, layer in enumerate(self.layers):
            for module_idx, module in enumerate(layer):
                if isinstance(module, nn.BatchNorm1d):
                    bn = module
                    logger.info(f"🔍 BatchNorm Layer {layer_idx}.{module_idx}:")
                    logger.info(f"   Training mode: {bn.training}")
                    logger.info(f"   Num batches tracked: {bn.num_batches_tracked.item() if bn.num_batches_tracked is not None else 'N/A'}")
                    if bn.running_mean is not None:
                        logger.info(f"   Running mean: min={bn.running_mean.min().item():.4f}, max={bn.running_mean.max().item():.4f}, std={bn.running_mean.std().item():.4f}")
                    if bn.running_var is not None:
                        logger.info(f"   Running var: min={bn.running_var.min().item():.4f}, max={bn.running_var.max().item():.4f}, mean={bn.running_var.mean().item():.4f}")
                    if bn.weight is not None:
                        logger.info(f"   Gamma (weight): min={bn.weight.min().item():.4f}, max={bn.weight.max().item():.4f}")
                    if bn.bias is not None:
                        logger.info(f"   Beta (bias): min={bn.bias.min().item():.4f}, max={bn.bias.max().item():.4f}")

    def forward(self, x):
        if self.config.n_hidden_layers == 0:
            return self.single_layer(x)

        # CRITICAL: Ensure input is on the same device as module parameters
        # This fixes device mismatch errors where input is on CPU but module is on CUDA
        module_device = None
        try:
            module_device = next(self.parameters()).device
        except (StopIteration, AttributeError):
            pass
        
        # Move input to module device if there's a mismatch
        if module_device is not None and x.device != module_device:
            x = x.to(device=module_device)
        
        # x = self.batch_norm_in(x)
        x_input = x
        x = self.linear_in(x)

        for layer_idx, layer in enumerate(self.layers):
            x_before = x
            
            # Feedforward block
            if self.config.residual:
                x = x + layer(x)
            else:
                x = layer(x)
            
            # Attention block (if enabled)
            if self.use_attention and self.attention_layers[layer_idx] is not None:
                x = self.attention_layers[layer_idx](x)
            
            # Debug: Check if output changed (backwards compatible - check if attribute exists)
            # Only log during training mode to reduce eval noise
            # COMMENTED OUT: Too verbose, clutters logs
            # if getattr(self, 'debug_batchnorm', False) and self.config.use_batch_norm and self.training:
            #     x_diff = (x - x_before).abs().mean().item() if not self.config.residual else (x - x_before - layer(x_before)).abs().mean().item()
            #     logger.debug(f"🔍 Layer {layer_idx} output change: {x_diff:.6f}")


        x = self.linear_out(x)

        if self.config.normalize:
            x_before_norm = x
            x = F.normalize(x, p=2, dim=-1)
            # Backwards compatible - check if attribute exists
            # Only log during training mode to reduce eval noise
            if getattr(self, 'debug_batchnorm', False) and self.training:
                norm_change = (x - x_before_norm).abs().mean().item()
                logger.debug(f"🔍 Output normalization change: {norm_change:.6f}")

        return x

    # def __init__(
    #     self, d_in, d_out, d_hidden, hidden_layers=0, dropout=0.1, normalize=True
    # ):
    #     super().__init__()

    #     if hidden_layers == 0:
    #         self.model = nn.Linear(d_in, d_out)
    #     else:
    #         layers_prefix = [
    #             nn.Linear(d_in, d_hidden),
    #         ]

    #         layers_middle = []
    #         # for _ in range(hidden_layers - 1):
    #         #     layers_middle.append(nn.LeakyReLU())
    #         #     layers_middle.append(nn.Linear(d_hidden, d_hidden))

    #         layers_suffix = [
    #             # nn.BatchNorm1d(d_hidden, affine=False),
    #             # nn.LeakyReLU(),
    #             # nn.Dropout(p=dropout),
    #             nn.Linear(d_hidden, d_out),
    #         ]

    #         layers = layers_prefix + layers_middle + layers_suffix

    #         self.model = nn.Sequential(*layers)

    #     self.linear = nn.Linear(d_in, d_out)
    #     # self.linear_in = nn.Linear(d_in, d_hidden, bias=True)
    #     # self.linear_out = nn.Linear(d_hidden, d_hidden, bias=True)

    #     self.linear_in = nn.Linear(d_in, d_hidden)
    #     self.linear_out = nn.Linear(d_hidden, d_out)

    #     self.normalize = normalize

    # def forward(self, input):
    #     # out = self.model(input)
    #     # if self.normalize:
    #     #     out = nn.functional.normalize(out, dim=1)

    #     # x = self.batch_norm_in(x)
    #     x = self.linear_in(input)

    #     # layers = self.layers

    #     # for layer in layers:
    #     #     if self.residual:
    #     #         x = x + layer(x)
    #     #     else:
    #     #         x = layer(x)

    #     x = self.linear_out(x)

    #     # x = self.linear(input)

    #     if self.normalize:
    #         x = F.normalize(x, p=2, dim=1)

    #     return x
    #     # return out
