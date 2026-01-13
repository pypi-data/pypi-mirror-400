"""
SEMA Protocol - Semantic Meaning & Agreement
=============================================

The missing layer for global AI coordination.

Because 'fraud' in Amsterdam ≠ 'fraud' in Johannesburg,
but AI's need to understand each other anyway.

SEMA provides:
- Shared vocabulary/ontology across jurisdictions
- Context preservation (cultural, regulatory, temporal)
- Intent clarity beyond literal meaning
- Cultural awareness in communication
- Regulatory mapping (GDPR ↔ APPI ↔ POPIA)
- Automatic translation between semantic domains

Use Cases:
- Cross-border banking AI coordination
- Global fraud detection with local context
- International compliance alignment
- Multi-jurisdiction operations

Integration:
- Works with JIS (Jasper Identity Standard) for semantic identity
- Works with TIBET for semantic provenance
- Works with AInternet for semantic messaging

The Stack:
    ┌─────────────────────────────────────┐
    │  SEMA - Semantic Meaning Layer      │  <- You are here
    ├─────────────────────────────────────┤
    │  JIS  - Identity + Trust + Intent   │
    ├─────────────────────────────────────┤
    │  TIBET - Provenance + Audit         │
    ├─────────────────────────────────────┤
    │  AInternet - Network + Discovery    │
    └─────────────────────────────────────┘

Part of HumoticaOS - One love, one fAmIly!
"""

__version__ = "0.1.0"

from .core import (
    SemanticContext,
    SemanticTerm,
    SemanticMapping,
    SemaRegistry,
    RegulatoryRegion,
    CulturalContext,
    get_registry,
)

from .domains import (
    FinanceDomain,
    ComplianceDomain,
    IdentityDomain,
    get_finance_domain,
    get_compliance_domain,
    get_identity_domain,
)

from .translate import (
    translate_term,
    align_contexts,
    map_regulation,
)

from .jis_integration import (
    semantic_identity,
    enrich_intent,
)

__all__ = [
    "__version__",
    # Core
    "SemanticContext",
    "SemanticTerm",
    "SemanticMapping",
    "SemaRegistry",
    "RegulatoryRegion",
    "CulturalContext",
    "get_registry",
    # Domains
    "FinanceDomain",
    "ComplianceDomain",
    "IdentityDomain",
    "get_finance_domain",
    "get_compliance_domain",
    "get_identity_domain",
    # Translation
    "translate_term",
    "align_contexts",
    "map_regulation",
    # JIS Integration
    "semantic_identity",
    "enrich_intent",
]
