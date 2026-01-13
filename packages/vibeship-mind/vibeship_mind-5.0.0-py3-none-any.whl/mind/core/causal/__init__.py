"""Causal inference module for Mind v5.

This module provides causal reasoning capabilities:
- Causal graph management (nodes, edges, paths)
- Counterfactual analysis
- Attribution of outcomes to memories
- Predictive recommendations based on causal patterns
- Formal causal inference with DoWhy integration
- Robustness testing with refutation methods
"""

from mind.core.causal.models import (
    CausalAttribution,
    CausalGraph,
    CausalNode,
    CausalRelationship,
    CounterfactualQuery,
    CounterfactualResult,
)
from mind.core.causal.service import CausalInferenceService

# DoWhy integration (optional - requires ml extras)
try:
    from mind.core.causal.dowhy_integration import (
        CausalEffect,
        DoWhyAnalyzer,
        RefutationResult,
        SensitivityResult,
        get_dowhy_analyzer,
    )

    DOWHY_AVAILABLE = True
except ImportError:
    DOWHY_AVAILABLE = False
    DoWhyAnalyzer = None
    CausalEffect = None
    RefutationResult = None
    SensitivityResult = None
    get_dowhy_analyzer = None

# Shapley value computation (always available)
from mind.core.causal.shapley import (
    ShapleyCalculator,
    ShapleyConfig,
    ShapleyResult,
    compute_shapley_attribution,
    get_shapley_calculator,
)

__all__ = [
    # Core models
    "CausalNode",
    "CausalRelationship",
    "CausalGraph",
    "CausalAttribution",
    "CounterfactualQuery",
    "CounterfactualResult",
    # Service
    "CausalInferenceService",
    # DoWhy integration
    "DOWHY_AVAILABLE",
    "DoWhyAnalyzer",
    "CausalEffect",
    "RefutationResult",
    "SensitivityResult",
    "get_dowhy_analyzer",
    # Shapley values
    "ShapleyCalculator",
    "ShapleyConfig",
    "ShapleyResult",
    "compute_shapley_attribution",
    "get_shapley_calculator",
]
