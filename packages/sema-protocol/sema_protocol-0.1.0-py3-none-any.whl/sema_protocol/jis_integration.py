"""
SEMA + JIS Integration
======================

Combines Semantic Meaning (SEMA) with Identity Standard (JIS)
for complete semantic identity.

JIS provides: Identity, Trust, Intent
SEMA adds:    Meaning across contexts

Together: Who you are + What you mean = Complete semantic identity
"""

from typing import Dict, Any, Optional
from .core import SemanticContext, SemanticTerm, RegulatoryRegion, CulturalContext
from .translate import translate_term, align_contexts


def semantic_identity(
    jis_identity: Dict[str, Any],
    context: Optional[SemanticContext] = None
) -> Dict[str, Any]:
    """
    Enrich a JIS identity with semantic context.

    JIS identity contains:
        - actor_id: Who is acting
        - trust_score: FIR/A score (0.0-1.0)
        - intent: Why they're acting
        - capabilities: What they can do

    SEMA adds:
        - semantic_context: Cultural/regulatory context
        - intent_interpretation: What the intent MEANS in context
        - cross_border_notes: Considerations for international use
    """
    if context is None:
        # Infer context from identity if possible
        context = SemanticContext(
            region=RegulatoryRegion.GLOBAL,
            culture=CulturalContext.NEUTRAL,
            domain="general"
        )

    enriched = {
        **jis_identity,
        "semantic_layer": {
            "context": context.to_dict(),
            "intent_clarity": analyze_intent(jis_identity.get("intent", ""), context),
            "cross_border_ready": context.region == RegulatoryRegion.GLOBAL,
            "sema_version": "0.1.0"
        }
    }

    return enriched


def analyze_intent(intent: str, context: SemanticContext) -> Dict[str, Any]:
    """
    Analyze intent for semantic clarity in context.

    Returns analysis of how the intent would be interpreted
    in the given cultural/regulatory context.
    """
    intent_lower = intent.lower()

    # Detect potential ambiguities
    ambiguities = []

    # Financial terms that vary by jurisdiction
    financial_terms = ["fraud", "transaction", "payment", "transfer", "money"]
    for term in financial_terms:
        if term in intent_lower:
            ambiguities.append({
                "term": term,
                "note": f"'{term}' has jurisdiction-specific definitions",
                "recommendation": "Specify regulatory context for precision"
            })

    # Compliance terms
    compliance_terms = ["consent", "personal data", "processing", "controller"]
    for term in compliance_terms:
        if term in intent_lower:
            ambiguities.append({
                "term": term,
                "note": f"'{term}' differs between GDPR, CCPA, APPI etc.",
                "recommendation": "Include applicable regulation reference"
            })

    # Cultural interpretation
    cultural_notes = []
    if context.culture == CulturalContext.INDIRECT:
        cultural_notes.append(
            "Intent may be understated - actual urgency could be higher than expressed"
        )
    elif context.culture == CulturalContext.DIRECT:
        cultural_notes.append(
            "Intent is likely stated directly - take at face value"
        )

    return {
        "original_intent": intent,
        "ambiguities": ambiguities,
        "cultural_notes": cultural_notes,
        "clarity_score": max(0.0, 1.0 - (len(ambiguities) * 0.2)),
        "recommendation": "Add jurisdiction context for higher clarity" if ambiguities else "Intent is clear"
    }


def enrich_intent(
    intent: str,
    actor_context: SemanticContext,
    recipient_context: SemanticContext
) -> Dict[str, Any]:
    """
    Enrich an intent statement for cross-context communication.

    When an actor from one context communicates with a recipient
    in another context, this function provides:
    - Translation guidance
    - Cultural adaptation notes
    - Regulatory alignment

    Example:
        Actor (NL, direct culture): "Stop processing my data now"
        Recipient (JP, indirect culture): Need softer phrasing

        enrich_intent(
            "Stop processing my data",
            nl_context,
            jp_context
        )
        -> Provides cultural adaptation and regulatory mapping
    """
    # Align contexts
    alignment = align_contexts(actor_context, recipient_context)

    result = {
        "original_intent": intent,
        "actor_context": actor_context.to_dict(),
        "recipient_context": recipient_context.to_dict(),
        "context_alignment": alignment
    }

    # If cultural differences exist, provide adapted version
    if actor_context.culture != recipient_context.culture:
        result["cultural_adaptation"] = adapt_for_culture(
            intent,
            actor_context.culture,
            recipient_context.culture
        )

    # If regulatory differences exist, add compliance notes
    if actor_context.region != recipient_context.region:
        result["regulatory_notes"] = get_regulatory_notes(
            intent,
            actor_context.region,
            recipient_context.region
        )

    return result


def adapt_for_culture(
    message: str,
    source_culture: CulturalContext,
    target_culture: CulturalContext
) -> Dict[str, Any]:
    """
    Suggest cultural adaptation for a message.
    """
    adaptations = {
        (CulturalContext.DIRECT, CulturalContext.INDIRECT): {
            "strategy": "soften_and_contextualize",
            "techniques": [
                "Add qualifiers ('perhaps', 'it might be')",
                "Use passive voice instead of direct commands",
                "Include context and reasoning before conclusions",
                "Allow face-saving options"
            ],
            "example_transform": {
                "before": "This is wrong. Fix it.",
                "after": "I wonder if we might consider whether there could be some adjustments that would help us achieve better results together."
            }
        },
        (CulturalContext.INDIRECT, CulturalContext.DIRECT): {
            "strategy": "make_explicit",
            "techniques": [
                "State conclusions upfront",
                "Be specific about requests",
                "Remove hedging language",
                "Give clear deadlines"
            ],
            "example_transform": {
                "before": "It might be somewhat difficult to proceed with the current approach.",
                "after": "This approach won't work. Here's what we need to change: ..."
            }
        }
    }

    key = (source_culture, target_culture)
    if key in adaptations:
        return {
            "adaptation_needed": True,
            **adaptations[key]
        }

    return {
        "adaptation_needed": False,
        "note": "Cultures are compatible or similar"
    }


def get_regulatory_notes(
    intent: str,
    source_region: RegulatoryRegion,
    target_region: RegulatoryRegion
) -> Dict[str, Any]:
    """
    Get regulatory notes for cross-border intent.
    """
    notes = {
        "cross_border": True,
        "source_region": source_region.value,
        "target_region": target_region.value,
        "considerations": []
    }

    intent_lower = intent.lower()

    # Data-related intents
    if any(term in intent_lower for term in ["data", "personal", "privacy"]):
        notes["considerations"].append({
            "topic": "Data Protection",
            "note": f"Verify data transfer mechanisms between {source_region.value} and {target_region.value}",
            "example": "EU to US requires SCCs or other transfer mechanism post-Schrems II"
        })

    # Financial intents
    if any(term in intent_lower for term in ["payment", "transfer", "transaction", "fraud"]):
        notes["considerations"].append({
            "topic": "Financial Regulation",
            "note": "Financial terms have jurisdiction-specific legal definitions",
            "example": "Fraud elements differ - intent requirements vary"
        })

    return notes
