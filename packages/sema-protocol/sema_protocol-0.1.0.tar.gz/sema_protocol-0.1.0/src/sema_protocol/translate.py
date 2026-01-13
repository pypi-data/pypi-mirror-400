"""
SEMA Translate - Cross-Context Semantic Translation
====================================================

Translate meaning across jurisdictions, cultures, and domains.
"""

from typing import Optional, Dict, List, Tuple
from .core import (
    SemanticTerm, SemanticContext, SemanticMapping,
    RegulatoryRegion, CulturalContext, get_registry
)
from .domains import get_finance_domain, get_compliance_domain


def translate_term(
    term: str,
    source_region: RegulatoryRegion,
    target_region: RegulatoryRegion,
    domain: str = "compliance"
) -> Dict:
    """
    Translate a term from one regulatory context to another.

    Example:
        translate_term("personal data", EU, US)
        -> {"term": "personal information", "confidence": 0.95, ...}
    """
    registry = get_registry()
    source_context = SemanticContext(region=source_region, domain=domain)
    target_context = SemanticContext(region=target_region, domain=domain)

    result = registry.translate(term, source_context, target_context)

    if result:
        return {
            "status": "found",
            "source_term": term,
            "source_region": source_region.value,
            "target_term": result.term,
            "target_region": target_region.value,
            "confidence": 0.95,
            "definition": result.definition,
            "regulatory_refs": result.regulatory_refs,
            "note": "Direct mapping found in registry"
        }

    # Try domain-specific lookup
    if domain == "finance":
        finance = get_finance_domain()
        fraud_term = finance.terms.get(term.lower(), {})
        if target_region.value in fraud_term:
            target = fraud_term[target_region.value]
            return {
                "status": "found",
                "source_term": term,
                "target_term": target.term,
                "target_region": target_region.value,
                "confidence": 0.90,
                "definition": target.definition,
                "regulatory_refs": target.regulatory_refs,
                "note": "Found in domain vocabulary"
            }

    return {
        "status": "not_found",
        "source_term": term,
        "source_region": source_region.value,
        "target_region": target_region.value,
        "suggestion": "Term may not have direct equivalent. Consider context-specific interpretation.",
        "note": "No mapping found - may need manual alignment"
    }


def align_contexts(
    source_context: SemanticContext,
    target_context: SemanticContext
) -> Dict:
    """
    Analyze differences between two contexts and provide alignment guidance.

    Useful for understanding what adjustments are needed when
    communicating across jurisdictions.
    """
    differences = []
    adjustments = []

    # Region differences
    if source_context.region != target_context.region:
        differences.append({
            "aspect": "regulatory_region",
            "source": source_context.region.value,
            "target": target_context.region.value
        })

        # Get regulation mapping
        compliance = get_compliance_domain()
        mapping = compliance.get_regulation_mapping(
            source_context.region,
            target_context.region
        )
        if mapping:
            adjustments.append({
                "type": "regulation_mapping",
                "mappings": mapping
            })

    # Cultural differences
    if source_context.culture != target_context.culture:
        differences.append({
            "aspect": "cultural_style",
            "source": source_context.culture.value,
            "target": target_context.culture.value
        })

        # Provide communication guidance
        if source_context.culture == CulturalContext.DIRECT and \
           target_context.culture == CulturalContext.INDIRECT:
            adjustments.append({
                "type": "communication_style",
                "guidance": "Soften direct statements, add context and qualifiers",
                "example": "'This is wrong' -> 'Perhaps we might consider alternative approaches'"
            })
        elif source_context.culture == CulturalContext.INDIRECT and \
             target_context.culture == CulturalContext.DIRECT:
            adjustments.append({
                "type": "communication_style",
                "guidance": "Be more explicit about conclusions and requests",
                "example": "'It might be difficult' -> 'This cannot be done because...'"
            })

    # Language differences
    if source_context.language != target_context.language:
        differences.append({
            "aspect": "language",
            "source": source_context.language,
            "target": target_context.language
        })
        adjustments.append({
            "type": "translation_needed",
            "recommendation": "Use certified translation for legal documents"
        })

    return {
        "compatible": len(differences) == 0,
        "differences": differences,
        "adjustments": adjustments,
        "risk_level": "low" if len(differences) <= 1 else "medium" if len(differences) <= 2 else "high"
    }


def map_regulation(
    regulation: str,
    source_region: RegulatoryRegion,
    target_region: RegulatoryRegion
) -> Dict:
    """
    Map a regulation from one jurisdiction to equivalent in another.

    Example:
        map_regulation("GDPR", EU, US)
        -> {"equivalent": "CCPA/CPRA", "coverage": "partial", ...}
    """
    compliance = get_compliance_domain()
    mapping = compliance.get_regulation_mapping(source_region, target_region)

    if regulation.upper() in mapping:
        return {
            "status": "found",
            "source_regulation": regulation,
            "source_region": source_region.value,
            "target_equivalent": mapping[regulation.upper()],
            "target_region": target_region.value,
            "note": "Equivalence may be partial - verify specific provisions"
        }

    return {
        "status": "not_found",
        "source_regulation": regulation,
        "source_region": source_region.value,
        "target_region": target_region.value,
        "suggestion": "No direct mapping. Consider jurisdiction-specific legal advice."
    }


def semantic_distance(term1: SemanticTerm, term2: SemanticTerm) -> float:
    """
    Calculate semantic distance between two terms.

    Returns value between 0 (identical) and 1 (completely different).
    """
    # Same canonical = very close
    if term1.canonical == term2.canonical:
        return 0.1  # Not 0 because context still matters

    # Same domain = closer
    domain_match = term1.context.domain == term2.context.domain

    # Calculate basic distance
    distance = 1.0

    if domain_match:
        distance -= 0.3

    # Check for shared regulatory refs
    shared_refs = set(term1.regulatory_refs) & set(term2.regulatory_refs)
    if shared_refs:
        distance -= 0.2

    # Check for overlapping related terms
    related1 = set(t.lower() for t in term1.related_terms)
    related2 = set(t.lower() for t in term2.related_terms)
    if related1 & related2:
        distance -= 0.2

    return max(0.0, distance)
