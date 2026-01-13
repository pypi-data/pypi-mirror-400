"""
SEMA Core - Semantic Meaning Primitives
========================================

Core classes for semantic meaning representation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from datetime import datetime
import json
import hashlib


class CulturalContext(Enum):
    """Communication style preferences by culture"""
    DIRECT = "direct"           # Dutch, German, Israeli
    INDIRECT = "indirect"       # Japanese, Korean, Thai
    CONTEXTUAL = "contextual"   # Chinese, Arabic
    NEUTRAL = "neutral"         # International business


class RegulatoryRegion(Enum):
    """Major regulatory regions"""
    EU = "eu"           # GDPR, AI Act
    US = "us"           # State laws, sector-specific
    JP = "jp"           # APPI
    SG = "sg"           # PDPA
    ZA = "za"           # POPIA
    AU = "au"           # Privacy Act
    BR = "br"           # LGPD
    GLOBAL = "global"   # Cross-border default


@dataclass
class SemanticContext:
    """
    Context for semantic interpretation.

    The same word means different things in different contexts.
    This class captures those differences.
    """
    region: RegulatoryRegion = RegulatoryRegion.GLOBAL
    culture: CulturalContext = CulturalContext.NEUTRAL
    domain: str = "general"  # finance, healthcare, legal, etc.
    timestamp: datetime = field(default_factory=datetime.utcnow)
    language: str = "en"
    jurisdiction: str = ""  # Specific jurisdiction code
    custom: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "region": self.region.value,
            "culture": self.culture.value,
            "domain": self.domain,
            "timestamp": self.timestamp.isoformat(),
            "language": self.language,
            "jurisdiction": self.jurisdiction,
            "custom": self.custom
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SemanticContext":
        return cls(
            region=RegulatoryRegion(data.get("region", "global")),
            culture=CulturalContext(data.get("culture", "neutral")),
            domain=data.get("domain", "general"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.utcnow(),
            language=data.get("language", "en"),
            jurisdiction=data.get("jurisdiction", ""),
            custom=data.get("custom", {})
        )

    def hash(self) -> str:
        """Generate hash for context matching"""
        content = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class SemanticTerm:
    """
    A term with semantic meaning in context.

    Example:
        "fraud" in NL banking context ≠ "fraud" in ZA legal context

        nl_fraud = SemanticTerm(
            term="fraud",
            canonical="financial_fraud",
            context=SemanticContext(region=EU, domain="finance"),
            definition="Intentional deception for financial gain under EU law",
            related_terms=["bedrog", "oplichting", "fraude"],
            regulatory_refs=["GDPR Art. 5", "PSD2"]
        )
    """
    term: str
    canonical: str  # Canonical form for matching
    context: SemanticContext
    definition: str = ""
    related_terms: List[str] = field(default_factory=list)
    regulatory_refs: List[str] = field(default_factory=list)
    synonyms: Dict[str, str] = field(default_factory=dict)  # lang -> translation
    confidence: float = 1.0  # How confident are we in this definition
    source: str = ""  # Where did this definition come from

    def to_dict(self) -> Dict:
        return {
            "term": self.term,
            "canonical": self.canonical,
            "context": self.context.to_dict(),
            "definition": self.definition,
            "related_terms": self.related_terms,
            "regulatory_refs": self.regulatory_refs,
            "synonyms": self.synonyms,
            "confidence": self.confidence,
            "source": self.source
        }

    def matches(self, other: "SemanticTerm", threshold: float = 0.8) -> bool:
        """Check if two terms are semantically equivalent"""
        if self.canonical == other.canonical:
            return True
        # TODO: More sophisticated matching with embeddings
        return False


@dataclass
class SemanticMapping:
    """
    Mapping between terms in different contexts.

    Example:
        "personal data" (GDPR) <-> "personal information" (CCPA)

    These are legally equivalent but use different terminology.
    """
    source_term: SemanticTerm
    target_term: SemanticTerm
    relationship: str = "equivalent"  # equivalent, broader, narrower, related
    confidence: float = 1.0
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""

    def to_dict(self) -> Dict:
        return {
            "source": self.source_term.to_dict(),
            "target": self.target_term.to_dict(),
            "relationship": self.relationship,
            "confidence": self.confidence,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by
        }


class SemaRegistry:
    """
    Registry of semantic terms and mappings.

    This is the central knowledge base for SEMA.
    Can be populated from files, APIs, or AI-generated.
    """

    def __init__(self):
        self.terms: Dict[str, SemanticTerm] = {}  # canonical -> term
        self.mappings: List[SemanticMapping] = []
        self.contexts: Dict[str, SemanticContext] = {}

    def register_term(self, term: SemanticTerm) -> str:
        """Register a semantic term, returns canonical key"""
        key = f"{term.canonical}_{term.context.hash()}"
        self.terms[key] = term
        return key

    def find_term(self, term: str, context: Optional[SemanticContext] = None) -> List[SemanticTerm]:
        """Find terms matching the query"""
        results = []
        term_lower = term.lower()

        for key, semantic_term in self.terms.items():
            # Match on term or canonical
            if semantic_term.term.lower() == term_lower or \
               semantic_term.canonical.lower() == term_lower:
                # Filter by context if provided
                if context is None or semantic_term.context.region == context.region:
                    results.append(semantic_term)

        return results

    def add_mapping(self, mapping: SemanticMapping):
        """Add a semantic mapping"""
        self.mappings.append(mapping)

    def find_mappings(self, term: SemanticTerm) -> List[SemanticMapping]:
        """Find all mappings for a term"""
        results = []
        for mapping in self.mappings:
            if mapping.source_term.canonical == term.canonical:
                results.append(mapping)
            elif mapping.target_term.canonical == term.canonical:
                # Reverse mapping
                results.append(SemanticMapping(
                    source_term=mapping.target_term,
                    target_term=mapping.source_term,
                    relationship=self._reverse_relationship(mapping.relationship),
                    confidence=mapping.confidence,
                    notes=mapping.notes
                ))
        return results

    def _reverse_relationship(self, rel: str) -> str:
        """Reverse a relationship"""
        reverses = {
            "equivalent": "equivalent",
            "broader": "narrower",
            "narrower": "broader",
            "related": "related"
        }
        return reverses.get(rel, rel)

    def translate(self, term: str, source_context: SemanticContext,
                  target_context: SemanticContext) -> Optional[SemanticTerm]:
        """
        Translate a term from one context to another.

        Example:
            translate("personal data", EU_context, US_context)
            -> "personal information" (CCPA terminology)
        """
        # Find source term
        source_terms = self.find_term(term, source_context)
        if not source_terms:
            return None

        source_term = source_terms[0]

        # Find mappings to target context
        mappings = self.find_mappings(source_term)
        for mapping in mappings:
            if mapping.target_term.context.region == target_context.region:
                return mapping.target_term

        return None

    def to_dict(self) -> Dict:
        return {
            "terms": {k: v.to_dict() for k, v in self.terms.items()},
            "mappings": [m.to_dict() for m in self.mappings],
            "version": "1.0"
        }

    def save(self, path: str):
        """Save registry to JSON file"""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "SemaRegistry":
        """Load registry from JSON file"""
        with open(path, 'r') as f:
            data = json.load(f)

        registry = cls()
        # TODO: Implement full deserialization
        return registry


# Pre-built registries (can be extended)
def create_compliance_registry() -> SemaRegistry:
    """Create a registry with common compliance terms"""
    registry = SemaRegistry()

    # EU Context
    eu_context = SemanticContext(
        region=RegulatoryRegion.EU,
        domain="compliance",
        language="en"
    )

    # US Context
    us_context = SemanticContext(
        region=RegulatoryRegion.US,
        domain="compliance",
        language="en"
    )

    # JP Context
    jp_context = SemanticContext(
        region=RegulatoryRegion.JP,
        domain="compliance",
        language="en"
    )

    # Register terms
    personal_data_eu = SemanticTerm(
        term="personal data",
        canonical="personal_data",
        context=eu_context,
        definition="Any information relating to an identified or identifiable natural person",
        regulatory_refs=["GDPR Art. 4(1)"],
        synonyms={"nl": "persoonsgegevens", "de": "personenbezogene Daten"}
    )
    registry.register_term(personal_data_eu)

    personal_info_us = SemanticTerm(
        term="personal information",
        canonical="personal_data",
        context=us_context,
        definition="Information that identifies, relates to, or could reasonably be linked with a consumer",
        regulatory_refs=["CCPA 1798.140(o)"]
    )
    registry.register_term(personal_info_us)

    # Add mapping
    registry.add_mapping(SemanticMapping(
        source_term=personal_data_eu,
        target_term=personal_info_us,
        relationship="equivalent",
        confidence=0.95,
        notes="Similar scope, CCPA slightly narrower in some interpretations"
    ))

    return registry


# Default global registry
_global_registry = None

def get_registry() -> SemaRegistry:
    """Get the global SEMA registry"""
    global _global_registry
    if _global_registry is None:
        _global_registry = create_compliance_registry()
    return _global_registry
