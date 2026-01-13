#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel, ConfigDict
from pydantic import validator


class ColumnType(Enum):
    SET = "set"
    SCALAR = "scalar"
    FREE_STRING = "free_string"
    LIST_OF_A_SET = "list_of_a_set"
    VECTOR = "vector"
    URL = "url"
    JSON = "json"
    TIMESTAMP = "timestamp"
    EMAIL = "email"
    DOMAIN = "domain_name"


class SimpleMLPConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())  # Allow fields starting with "model_" to avoid Pydantic warnings
    
    d_in: int
    d_out: int
    d_hidden: Optional[int] = 256
    n_hidden_layers: Optional[int] = 0
    dropout: Optional[float] = 0.3  # Increased from 0.1 for better regularization on imbalanced data
    normalize: Optional[bool] = True
    residual: Optional[bool] = True
    use_batch_norm: Optional[bool] = True
    use_attention: Optional[bool] = None  # None = use global config, True/False = override
    attention_heads: Optional[int] = 4  # Number of attention heads (only used if use_attention=True)
    attention_dropout: Optional[float] = None  # Dropout for attention (None = use same as dropout)


class SetEncoderConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())  # Allow fields starting with "model_" to avoid Pydantic warnings
    
    d_model: int
    n_members: int
    normalize_output: Optional[bool] = True  # Config-controlled normalization
    sparsity_ratio: Optional[float] = 0.0  # Ratio of null/missing values (0.0 = dense, 1.0 = all null)
    initial_mixture_logit: Optional[float] = None  # Initial value for mixture logit (None = random small value ~0.1)
                                                    # Positive → prefer learned embeddings, Negative → prefer semantic (BERT)
                                                    # 0.0 = 50/50 mixture, +1.0 ≈ 73% learned, -1.0 ≈ 27% learned
    
    # ============================================================================
    # ADVANCED SET ENCODING OPTIONS (v0.2+)
    # ============================================================================
    
    # Per-member mixture weights: Each category value gets its own mixture weight
    # instead of a global weight for the entire column. This allows "A14" (opaque code)
    # to trust learned embeddings while "unemployed" trusts BERT semantics.
    use_per_member_mixture: Optional[bool] = True  # Default: enabled
    
    # Ordinal encoding: If detected, add positional embeddings that encode order
    # e.g., ["poor", "fair", "good", "excellent"] → positions [0, 1, 2, 3]
    ordinal_info: Optional[dict] = None  # Set by ordinal detection: {"is_ordinal": bool, "ordered_values": [...]}
    ordinal_weight: Optional[float] = 0.3  # Weight for ordinal position embedding (0=ignore, 1=full)
    
    # Curriculum learning: Start with semantic (BERT) embeddings, gradually allow learned to take over
    # semantic_floor decays from semantic_floor_start to semantic_floor_end over training
    use_curriculum_learning: Optional[bool] = True  # Default: enabled
    semantic_floor_start: Optional[float] = 0.7  # Start training with 70% minimum semantic weight
    semantic_floor_end: Optional[float] = 0.1  # End training with 10% minimum semantic weight
    
    # Entropy regularization: Encourage decisive mixing (not 50/50)
    # Higher values push harder away from 50/50 toward 0 or 1
    entropy_regularization_weight: Optional[float] = 0.3  # Default: 0.3 (was 0.1)
    
    # Temperature annealing: Make mixture decisions sharper over training
    # temperature decays from temp_start to temp_end, lower = sharper decisions
    use_temperature_annealing: Optional[bool] = True  # Default: enabled
    temperature_start: Optional[float] = 1.0  # Start with soft mixture
    temperature_end: Optional[float] = 0.2  # End with sharp mixture decisions


class ScalarEncoderConfig(SimpleMLPConfig):
    d_in: int = 1


class TimestampEncoderConfig(SimpleMLPConfig):
    d_in: int = 12  # 12 temporal features from TimestampCodec


class StringEncoderConfig(SimpleMLPConfig):
    n_hidden_layers: int = 0
    d_model: Optional[int] = None  # Target dimension for stacking (if different from d_out)


class VectorEncoderConfig(SimpleMLPConfig):
    n_hidden_layers: int = 0


class ListOfASetEncoderConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())  # Allow fields starting with "model_" to avoid Pydantic warnings
    
    d_model: int
    n_members: int
    normalize: bool = False  # Control normalization to prevent double normalization with JointEncoder


ColumnEncoderConfigType = Union[
    SetEncoderConfig,
    ScalarEncoderConfig,
    TimestampEncoderConfig,
    StringEncoderConfig,
    ListOfASetEncoderConfig,
    VectorEncoderConfig,
    SimpleMLPConfig,  # Fallback for other types
]


ColumnPredictorConfigType = Union[SimpleMLPConfig]


JointEncoderInConverterConfigType = Union[SimpleMLPConfig]


class SpreadLossConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())  # Allow fields starting with "model_" to avoid Pydantic warnings
    
    joint_weight: float = 1
    marginal_weight: float = 1


class CurriculumPhaseConfig(BaseModel):
    """Configuration for a single curriculum learning phase."""
    model_config = ConfigDict(protected_namespaces=())
    
    name: str  # Human-readable phase name (e.g., "Spread Focus", "Marginal Focus")
    start_progress: float  # Start of phase (0.0 to 1.0)
    end_progress: float  # End of phase (0.0 to 1.0)
    spread_weight: float  # Weight for spread loss during this phase
    marginal_weight: float  # Weight for marginal loss during this phase
    joint_weight: float  # Weight for joint loss during this phase
    transition_width: float = 0.05  # Width of transition window (as fraction of total epochs, default 5%)


class CurriculumLearningConfig(BaseModel):
    """Configuration for curriculum learning schedule."""
    model_config = ConfigDict(protected_namespaces=())
    
    enabled: bool = True  # Whether to use curriculum learning
    phases: List[CurriculumPhaseConfig] = []  # List of phases in order
    
    @validator('phases')
    # pylint: disable=no-self-argument
    def validate_phases(cls, v):
        """Validate that phases cover 0.0 to 1.0 without gaps or overlaps."""
        if not v:
            return v
        
        # Sort by start_progress
        sorted_phases = sorted(v, key=lambda p: p.start_progress)
        
        # Check coverage
        if sorted_phases[0].start_progress != 0.0:
            raise ValueError(f"First phase must start at 0.0, got {sorted_phases[0].start_progress}")
        
        if sorted_phases[-1].end_progress != 1.0:
            raise ValueError(f"Last phase must end at 1.0, got {sorted_phases[-1].end_progress}")
        
        # Check for gaps and overlaps
        for i in range(len(sorted_phases) - 1):
            current_end = sorted_phases[i].end_progress
            next_start = sorted_phases[i + 1].start_progress
            
            if abs(current_end - next_start) > 1e-6:
                raise ValueError(
                    f"Phases {i} and {i+1} have gap/overlap: "
                    f"phase {i} ends at {current_end}, phase {i+1} starts at {next_start}"
                )
        
        return sorted_phases


class LossFunctionConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())  # Allow fields starting with "model_" to avoid Pydantic warnings
    
    joint_loss_weight: float = 1
    marginal_loss_weight: float = 1
    spread_loss_weight: float = 1
    spread_loss_config: SpreadLossConfig
    spread_lr_multiplier: Optional[float] = None  # If set, scale spread loss gradients by this factor (e.g., 0.3 = 30% of base LR)
    marginal_loss_scaling_coefficient: Optional[float] = None  # Scaling coefficient applied to marginal loss value (not weight) to match spread/joint magnitudes
    curriculum_learning: Optional[CurriculumLearningConfig] = None  # Curriculum learning schedule (None = disabled)


class RelationshipFeatureConfig(BaseModel):
    """
    Configuration for the dynamic relationship extractor.
    
    This module adds relationship tokens (A*B, A+B, A-B, B-A, A/B, B/A) to the
    transformer sequence, helping the model learn interactions between columns.
    
    The extractor uses dynamic pruning:
    - Exploration phase (first N epochs): compute all N*(N-1)/2 pairs
    - Focused phase (remaining epochs): prune to top K% of relationships per column
    """
    model_config = ConfigDict(protected_namespaces=())
    
    exploration_epochs: int = 10         # Number of epochs for full exploration before pruning
    top_k_fraction: float = 0.25         # Fraction of top relationships to keep after pruning
    
    # MLP configuration for relationship tokens (optional, will use defaults if None)
    relationship_mlp_config: Optional[SimpleMLPConfig] = None


class JointEncoderConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())  # Allow fields starting with "model_" to avoid Pydantic warnings
    
    # dimensionality of the transformer's internal representation
    d_model: int = 256
    # number of attention heads in the transformer
    n_heads: int = 8
    # Whether to use column encodings.
    # Analogous to positional encodings in language models.
    # FIXME: this parameter should be called "use_additive_positional_encoding_for_columns"
    use_col_encoding: bool = True
    # Number of columns to generate positional encodings for.
    # This is only relevant when use_col_encoding=True
    n_cols: int = None
    # number of transofmer layers to use
    n_layers: int = 1
    # how large the internal feedforward layer should be
    # this factor multiplies d_model
    dim_feedforward_factor: int = 4
    # dropout factor to use in each transformer layer
    dropout: float = 0
    normalize_output: bool = True
    # Relationship feature extraction configuration
    # If None, relationship features are disabled
    relationship_features: Optional[RelationshipFeatureConfig] = None
    # FIXME: allow a fixed, known value for the positional column embeddings
    # so that we can use embeddings from LLMs (although we'd likely only see)
    # a benefit from this if we were using a pre-trained model that used a
    # similar
    in_converter_configs: Dict[str, JointEncoderInConverterConfigType]
    out_converter_config: SimpleMLPConfig


class FeatrixTableEncoderConfig(BaseModel):
    # NOTE: something I don't like is that the values in different field are not
    # independent, e.g. the number of items in 'cols_in_order' must be equal to 'n_cols',
    # and the values in 'cols_in_order' must be the same as the keys in 'col_types'.
    # What's the best way to enforce this? Does pydantic have a way to handle this?

    # More generally, we'll need a way to enforce that e.g. d_out in the encoder is the
    # same as the input to the joint encoder. Otherwise we'll run into difficult-to-diagnose
    # issues. Also, it will be very difficult to hand-edit json configuration files.

    # One solution, would be to have a system where part of the configuration can be serialized,
    # and another part is overwriten dynamically, so that a model that composes other models could
    # override some of the serialized settings, and enforce that all the parameters match. But then
    # it would result in possibly confusing behavior where the instantiated model is different from
    # what the serialized data might imply.

    # The best of both worlds would be to have a validator tells the user EXACTLY what the problem is
    # with the serialized configuration, and what to do to make it work.

    model_config = ConfigDict(protected_namespaces=())  # Allow fields starting with "model_" to avoid Pydantic warnings
    
    d_model: int
    n_cols: int
    cols_in_order: List[str]
    col_types: Dict[str, ColumnType]
    column_encoders_config: Dict[str, ColumnEncoderConfigType]
    column_predictors_config: Dict[str, ColumnPredictorConfigType]
    # All column predictors for short embeddings share the same config because
    # they're just for UI and visualization so they don't need much fidelity.
    column_predictors_short_config: SimpleMLPConfig
    joint_encoder_config: JointEncoderConfig
    joint_predictor_config: SimpleMLPConfig
    joint_predictor_short_config: SimpleMLPConfig
    loss_config: LossFunctionConfig


# ============================================================================
# GraphEncoder Configuration
# ============================================================================

class KeyMatcherConfig(BaseModel):
    """Configuration for key matching between tables."""
    model_config = ConfigDict(protected_namespaces=())
    
    use_hash_matching: bool = True  # Use hash-based matching for efficiency
    hash_bucket_size: int = 10000  # Size of hash buckets
    exact_match_threshold: float = 1e-6  # Threshold for exact numeric matches


class RelationshipEncoderConfig(BaseModel):
    """Configuration for relationship encoding between tables."""
    model_config = ConfigDict(protected_namespaces=())
    
    d_model: int
    key_matcher_config: KeyMatcherConfig
    n_hidden_layers: int = 2
    dropout: float = 0.1
    aggregation_method: str = "mean"  # "mean", "max", "attention", "sum"


class CrossTableAttentionConfig(BaseModel):
    """Configuration for cross-table attention mechanism."""
    model_config = ConfigDict(protected_namespaces=())
    
    d_model: int
    n_heads: int = 8
    dropout: float = 0.1
    use_relationship_weights: bool = True
    max_related_tables: Optional[int] = None  # Limit number of related tables to attend to


class FusionLayerConfig(BaseModel):
    """Configuration for fusion layer that combines embeddings."""
    model_config = ConfigDict(protected_namespaces=())
    
    d_model: int
    n_hidden_layers: int = 2
    use_gating: bool = True
    dropout: float = 0.1
    fusion_weight: float = 0.5  # Weight for fused vs original embeddings


class GraphEncoderConfig(BaseModel):
    """Configuration for GraphEncoder that bridges multiple TableEncoders."""
    model_config = ConfigDict(protected_namespaces=())
    
    d_model: int
    relationship_config: RelationshipEncoderConfig
    attention_config: CrossTableAttentionConfig
    fusion_config: FusionLayerConfig
    
    # Training parameters
    freeze_table_encoders: bool = False  # Freeze individual table encoders during graph training
    relationship_weight: float = 1.0  # Weight for relationship loss
    cross_table_weight: float = 1.0  # Weight for cross-table prediction loss
