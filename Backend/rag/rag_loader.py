import os
from Backend.rag.section_parser import parse_sections

# RAG is advisory only — governance enums are authoritative
# This layer must never override deterministic governance decisions

def load_rag_context(domain: str, risk_tier: str) -> str:
    """
    Loads relevant RAG sections based on domain and risk_tier.
    """
    # Null Safety
    domain = (domain or "GENERAL").upper()
    file_path = os.path.join(RAG_DOMAINS_DIR, f"{domain}.md")
    
    if not os.path.exists(file_path):
        # Fallback to GENERAL if domain-specific file doesn't exist
        file_path = os.path.join(RAG_DOMAINS_DIR, "GENERAL.md")

    sections = parse_sections(file_path)
    
    context_parts = []
    
    # 1. Always include compliance section if it exists
    if "SECTION_COMPLIANCE" in sections:
        context_parts.append(f"### Domain Compliance Guidance\n{sections['SECTION_COMPLIANCE']}")

    # 2. Enum-Strict Risk Mapping (No numeric casting, no assumptions)
    if risk_tier == "TIER_1":
        risk_mapped = "HIGH"
    elif risk_tier == "TIER_2":
        risk_mapped = "MEDIUM"
    elif risk_tier == "TIER_3":
        risk_mapped = "LOW"
    else:
        risk_mapped = "LOW" # Default fallback for safety

    risk_section_key = f"SECTION_RISK_{risk_mapped}"
    if risk_section_key in sections:
        context_parts.append(f"### Risk-Tier Advisory ({risk_tier})\n{sections[risk_section_key]}")

    # 3. Always include modeling patterns if present
    if "SECTION_MODELING_PATTERNS" in sections:
        context_parts.append(f"### Modeling Patterns\n{sections['SECTION_MODELING_PATTERNS']}")

    if not context_parts:
        return ""

    # Structured Return Format for Demo Visibility
    sections_joined = "\n\n".join(context_parts)
    return (
        f"--------------------------------------------------\n"
        f"Domain: {domain}\n"
        f"Risk Tier: {risk_tier}\n\n"
        f"{sections_joined}\n"
        f"--------------------------------------------------"
    )
