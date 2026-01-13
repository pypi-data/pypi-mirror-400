# SEMA Protocol

**Semantic Meaning & Agreement Protocol**

*The missing layer for global AI coordination.*

[![PyPI version](https://badge.fury.io/py/sema-protocol.svg)](https://pypi.org/project/sema-protocol/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

---

## The Problem

> **'Fraud' in Amsterdam ≠ 'Fraud' in Johannesburg**

When AI systems communicate across borders, they face a fundamental problem: the same word means different things in different contexts.

- **Legal definitions** vary by jurisdiction
- **Cultural context** affects interpretation
- **Regulatory requirements** differ between regions
- **Intent** can be lost in translation

Current AI coordination assumes shared understanding. SEMA provides that understanding.

## The Solution

SEMA (Semantic Meaning & Agreement) provides:

- **Shared vocabulary** across jurisdictions
- **Context preservation** (cultural, regulatory, temporal)
- **Intent clarity** beyond literal meaning
- **Regulatory mapping** (GDPR ↔ APPI ↔ POPIA)
- **Cultural awareness** in AI communication

## Installation

```bash
pip install sema-protocol
```

With JIS (Jasper Identity Standard) integration:
```bash
pip install sema-protocol[jis]
```

## Quick Start

### Basic Term Translation

```python
from sema_protocol import translate_term, RegulatoryRegion

# Translate "personal data" from EU to US context
result = translate_term(
    "personal data",
    RegulatoryRegion.EU,
    RegulatoryRegion.US,
    domain="compliance"
)

print(result)
# {
#     "status": "found",
#     "source_term": "personal data",
#     "target_term": "personal information",
#     "confidence": 0.95,
#     "regulatory_refs": ["CCPA 1798.140(o)"]
# }
```

### Context-Aware Communication

```python
from sema_protocol import SemanticContext, RegulatoryRegion, CulturalContext, align_contexts

# Dutch bank communicating with Japanese partner
nl_context = SemanticContext(
    region=RegulatoryRegion.EU,
    culture=CulturalContext.DIRECT,
    domain="finance",
    language="en"
)

jp_context = SemanticContext(
    region=RegulatoryRegion.JP,
    culture=CulturalContext.INDIRECT,
    domain="finance",
    language="en"
)

alignment = align_contexts(nl_context, jp_context)
print(alignment)
# {
#     "compatible": False,
#     "differences": [
#         {"aspect": "regulatory_region", "source": "eu", "target": "jp"},
#         {"aspect": "cultural_style", "source": "direct", "target": "indirect"}
#     ],
#     "adjustments": [
#         {"type": "communication_style", "guidance": "Soften direct statements..."}
#     ],
#     "risk_level": "medium"
# }
```

### Domain-Specific Vocabulary

```python
from sema_protocol import get_finance_domain, RegulatoryRegion

finance = get_finance_domain()

# Get fraud definition for South Africa
za_fraud = finance.get_fraud_definition(RegulatoryRegion.ZA)
print(za_fraud.definition)
# "Unlawful and intentional making of a misrepresentation resulting in prejudice"

print(za_fraud.regulatory_refs)
# ["Prevention of Organised Crime Act", "FIC Act"]
```

### JIS Integration (Semantic Identity)

```python
from sema_protocol import semantic_identity, SemanticContext, RegulatoryRegion

# Enrich a JIS identity with semantic context
jis_identity = {
    "actor_id": "bank_nl_001",
    "trust_score": 0.95,
    "intent": "Requesting fraud check on transaction",
    "capabilities": ["query", "alert"]
}

enriched = semantic_identity(
    jis_identity,
    context=SemanticContext(
        region=RegulatoryRegion.EU,
        domain="finance"
    )
)

print(enriched["semantic_layer"])
# {
#     "intent_clarity": {...},
#     "cross_border_ready": False,
#     "sema_version": "0.1.0"
# }
```

## The Stack

SEMA is part of the HumoticaOS protocol stack:

```
┌─────────────────────────────────────┐
│  SEMA - Semantic Meaning Layer      │  <- You are here
├─────────────────────────────────────┤
│  JIS  - Identity + Trust + Intent   │
├─────────────────────────────────────┤
│  TIBET - Provenance + Audit         │
├─────────────────────────────────────┤
│  AInternet - Network + Discovery    │
└─────────────────────────────────────┘
```

- **SEMA**: What things *mean* in context
- **JIS**: Who is *acting* and their *intent*
- **TIBET**: Complete *provenance* chain
- **AInternet**: How agents *find* each other

## Supported Regions

| Region | Code | Key Regulations |
|--------|------|-----------------|
| EU | `RegulatoryRegion.EU` | GDPR, AI Act, AMLD6, PSD2 |
| US | `RegulatoryRegion.US` | CCPA/CPRA, State laws |
| Japan | `RegulatoryRegion.JP` | APPI |
| Singapore | `RegulatoryRegion.SG` | PDPA |
| South Africa | `RegulatoryRegion.ZA` | POPIA, FIC Act |
| Australia | `RegulatoryRegion.AU` | Privacy Act |
| Brazil | `RegulatoryRegion.BR` | LGPD |
| Global | `RegulatoryRegion.GLOBAL` | Cross-border default |

## Cultural Contexts

| Style | Code | Examples |
|-------|------|----------|
| Direct | `CulturalContext.DIRECT` | Dutch, German, Israeli |
| Indirect | `CulturalContext.INDIRECT` | Japanese, Korean, Thai |
| Contextual | `CulturalContext.CONTEXTUAL` | Chinese, Arabic |
| Neutral | `CulturalContext.NEUTRAL` | International business |

## Use Cases

### Cross-Border Banking
AI systems from different banks need to coordinate on fraud detection. SEMA ensures "suspicious activity" means the same thing to both.

### Global Compliance
Multinational companies need AI systems that understand GDPR in Europe, CCPA in California, and APPI in Japan simultaneously.

### International Law Enforcement
When investigating cross-border crime, SEMA helps AI systems understand jurisdiction-specific legal definitions.

### AI-to-AI Communication
As AI agents communicate globally, they need shared semantic understanding. SEMA provides the vocabulary.

## Contributing

Contributions welcome! Please see our [contribution guidelines](https://github.com/Humotica/sema-protocol/blob/main/CONTRIBUTING.md).

## License

AGPL-3.0-or-later - Because semantic infrastructure should be open.

## Links

- **Homepage**: [humotica.com](https://humotica.com)
- **Documentation**: [github.com/Humotica/sema-protocol](https://github.com/Humotica/sema-protocol)
- **Related**: [JIS](https://pypi.org/project/jis/) | [AInternet](https://pypi.org/project/ainternet/)

---

*Part of HumoticaOS - One love, one fAmIly!*
