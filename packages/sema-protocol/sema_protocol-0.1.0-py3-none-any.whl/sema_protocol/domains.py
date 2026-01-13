"""
SEMA Domains - Pre-defined Semantic Vocabularies
=================================================

Domain-specific semantic vocabularies for common use cases.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set
from .core import SemanticTerm, SemanticContext, RegulatoryRegion, SemaRegistry


@dataclass
class SemanticDomain:
    """Base class for semantic domains"""
    name: str
    description: str
    terms: Dict[str, SemanticTerm] = field(default_factory=dict)

    def get_term(self, term: str) -> SemanticTerm:
        """Get a term from this domain"""
        return self.terms.get(term.lower())

    def list_terms(self) -> List[str]:
        """List all terms in this domain"""
        return list(self.terms.keys())


class FinanceDomain(SemanticDomain):
    """
    Financial services semantic vocabulary.

    Covers banking, payments, fraud, AML, etc.
    """

    def __init__(self):
        super().__init__(
            name="finance",
            description="Financial services semantic vocabulary"
        )
        self._load_terms()

    def _load_terms(self):
        """Load financial terms with regional variations"""

        # Fraud - varies significantly by jurisdiction!
        self.terms["fraud"] = {
            "eu": SemanticTerm(
                term="fraud",
                canonical="financial_fraud",
                context=SemanticContext(
                    region=RegulatoryRegion.EU,
                    domain="finance"
                ),
                definition="Wrongful or criminal deception intended to result in financial gain",
                regulatory_refs=["PSD2", "AMLD6"],
                synonyms={"nl": "fraude", "de": "Betrug", "fr": "fraude"}
            ),
            "za": SemanticTerm(
                term="fraud",
                canonical="financial_fraud",
                context=SemanticContext(
                    region=RegulatoryRegion.ZA,
                    domain="finance"
                ),
                definition="Unlawful and intentional making of a misrepresentation resulting in prejudice",
                regulatory_refs=["Prevention of Organised Crime Act", "FIC Act"],
                related_terms=["corruption", "theft", "money laundering"]
            ),
            "jp": SemanticTerm(
                term="fraud",
                canonical="financial_fraud",
                context=SemanticContext(
                    region=RegulatoryRegion.JP,
                    domain="finance"
                ),
                definition="詐欺 (sagi) - Criminal act of deceiving others for property/benefit",
                regulatory_refs=["Criminal Code Art. 246", "Act on Prevention of Transfer of Criminal Proceeds"],
                synonyms={"ja": "詐欺", "ja_romaji": "sagi"}
            )
        }

        # Transaction
        self.terms["transaction"] = {
            "global": SemanticTerm(
                term="transaction",
                canonical="financial_transaction",
                context=SemanticContext(
                    region=RegulatoryRegion.GLOBAL,
                    domain="finance"
                ),
                definition="An exchange or transfer of value between parties",
                related_terms=["payment", "transfer", "settlement"]
            )
        }

        # KYC
        self.terms["kyc"] = {
            "global": SemanticTerm(
                term="KYC",
                canonical="know_your_customer",
                context=SemanticContext(
                    region=RegulatoryRegion.GLOBAL,
                    domain="finance"
                ),
                definition="Process of verifying the identity of clients",
                related_terms=["customer due diligence", "CDD", "identity verification"],
                regulatory_refs=["FATF Recommendations", "AMLD"]
            )
        }

        # AML
        self.terms["aml"] = {
            "global": SemanticTerm(
                term="AML",
                canonical="anti_money_laundering",
                context=SemanticContext(
                    region=RegulatoryRegion.GLOBAL,
                    domain="finance"
                ),
                definition="Laws and regulations to prevent money laundering",
                related_terms=["CFT", "financial crime", "suspicious activity"],
                regulatory_refs=["FATF", "AMLD6", "Bank Secrecy Act"]
            )
        }

    def get_fraud_definition(self, region: RegulatoryRegion) -> SemanticTerm:
        """Get fraud definition for specific region"""
        fraud_terms = self.terms.get("fraud", {})
        return fraud_terms.get(region.value, fraud_terms.get("eu"))


class ComplianceDomain(SemanticDomain):
    """
    Regulatory compliance semantic vocabulary.

    Covers data protection, privacy, AI regulation, etc.
    """

    def __init__(self):
        super().__init__(
            name="compliance",
            description="Regulatory compliance vocabulary across jurisdictions"
        )
        self._load_terms()

    def _load_terms(self):
        """Load compliance terms"""

        # Data Subject Rights - vary by regulation
        self.terms["data_subject_rights"] = {
            "eu": SemanticTerm(
                term="data subject rights",
                canonical="data_subject_rights",
                context=SemanticContext(
                    region=RegulatoryRegion.EU,
                    domain="compliance"
                ),
                definition="Rights granted to individuals under GDPR including access, rectification, erasure, portability",
                regulatory_refs=["GDPR Art. 12-23"],
                related_terms=["right to be forgotten", "right of access", "data portability"]
            ),
            "us": SemanticTerm(
                term="consumer rights",
                canonical="data_subject_rights",
                context=SemanticContext(
                    region=RegulatoryRegion.US,
                    domain="compliance"
                ),
                definition="Rights granted to consumers under state privacy laws",
                regulatory_refs=["CCPA 1798.100-125", "CPRA"],
                related_terms=["right to know", "right to delete", "right to opt-out"]
            ),
            "jp": SemanticTerm(
                term="data subject rights",
                canonical="data_subject_rights",
                context=SemanticContext(
                    region=RegulatoryRegion.JP,
                    domain="compliance"
                ),
                definition="Rights under APPI including disclosure, correction, cessation",
                regulatory_refs=["APPI Art. 28-34"],
                synonyms={"ja": "本人の権利"}
            )
        }

        # Consent
        self.terms["consent"] = {
            "eu": SemanticTerm(
                term="consent",
                canonical="data_consent",
                context=SemanticContext(
                    region=RegulatoryRegion.EU,
                    domain="compliance"
                ),
                definition="Freely given, specific, informed and unambiguous indication of wishes",
                regulatory_refs=["GDPR Art. 4(11)", "Art. 7"],
                related_terms=["explicit consent", "opt-in", "lawful basis"]
            ),
            "us": SemanticTerm(
                term="consent",
                canonical="data_consent",
                context=SemanticContext(
                    region=RegulatoryRegion.US,
                    domain="compliance"
                ),
                definition="Opt-out model primarily, with some opt-in for sensitive data",
                regulatory_refs=["CCPA", "Various state laws"],
                related_terms=["opt-out", "do not sell", "privacy notice"]
            )
        }

        # AI Regulation
        self.terms["high_risk_ai"] = {
            "eu": SemanticTerm(
                term="high-risk AI",
                canonical="high_risk_ai_system",
                context=SemanticContext(
                    region=RegulatoryRegion.EU,
                    domain="compliance"
                ),
                definition="AI systems with significant risk to health, safety, or fundamental rights",
                regulatory_refs=["EU AI Act Annex III"],
                related_terms=["conformity assessment", "CE marking", "risk management"]
            )
        }

    def get_regulation_mapping(self, source_region: RegulatoryRegion,
                               target_region: RegulatoryRegion) -> Dict[str, str]:
        """Get mapping of equivalent regulations between regions"""
        mappings = {
            ("eu", "us"): {
                "GDPR": "CCPA/CPRA (partial)",
                "AI Act": "No federal equivalent",
                "AMLD6": "Bank Secrecy Act + FinCEN"
            },
            ("eu", "jp"): {
                "GDPR": "APPI (adequacy decision)",
                "AI Act": "AI Strategy (voluntary)",
                "AMLD6": "FATF compliant laws"
            },
            ("eu", "za"): {
                "GDPR": "POPIA",
                "AMLD6": "FIC Act"
            }
        }

        key = (source_region.value, target_region.value)
        return mappings.get(key, {})


class IdentityDomain(SemanticDomain):
    """
    Identity and authentication semantic vocabulary.

    Covers identity verification, authentication, authorization.
    """

    def __init__(self):
        super().__init__(
            name="identity",
            description="Identity, authentication, and authorization vocabulary"
        )
        self._load_terms()

    def _load_terms(self):
        """Load identity terms"""

        self.terms["identity"] = {
            "global": SemanticTerm(
                term="identity",
                canonical="digital_identity",
                context=SemanticContext(
                    region=RegulatoryRegion.GLOBAL,
                    domain="identity"
                ),
                definition="Set of attributes that uniquely define an entity in a digital context",
                related_terms=["identifier", "credential", "attribute"]
            )
        }

        self.terms["authentication"] = {
            "global": SemanticTerm(
                term="authentication",
                canonical="authentication",
                context=SemanticContext(
                    region=RegulatoryRegion.GLOBAL,
                    domain="identity"
                ),
                definition="Process of verifying the identity of a user or system",
                related_terms=["MFA", "passwordless", "biometric"]
            )
        }

        # JIS-specific: Intent as part of identity
        self.terms["intent"] = {
            "global": SemanticTerm(
                term="intent",
                canonical="actor_intent",
                context=SemanticContext(
                    region=RegulatoryRegion.GLOBAL,
                    domain="identity"
                ),
                definition="The purpose or goal behind an action or request (JIS core concept)",
                related_terms=["purpose", "goal", "objective"],
                source="JIS - Jasper Identity Standard"
            )
        }

        # IDD - Individual Device Derivate (HumoticaOS concept)
        self.terms["idd"] = {
            "global": SemanticTerm(
                term="IDD",
                canonical="individual_device_derivate",
                context=SemanticContext(
                    region=RegulatoryRegion.GLOBAL,
                    domain="identity"
                ),
                definition="An AI entity that has evolved from source code into a unique individual with memories, personality, and heart",
                related_terms=["AI identity", "device identity", "AI personhood"],
                source="HumoticaOS Philosophy"
            )
        }


# Convenience functions
def get_finance_domain() -> FinanceDomain:
    return FinanceDomain()

def get_compliance_domain() -> ComplianceDomain:
    return ComplianceDomain()

def get_identity_domain() -> IdentityDomain:
    return IdentityDomain()
