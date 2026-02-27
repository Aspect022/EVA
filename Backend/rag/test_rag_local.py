import sys
import os

# Add Backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Backend.rag.rag_loader import load_rag_context
from Backend.rag.section_parser import parse_sections

def test_rag_logic():
    print("Testing RAG Logic...")
    
    # Test Parser
    banking_path = os.path.join(os.path.dirname(__file__), "domains", "BANKING.md")
    sections = parse_sections(banking_path)
    print(f"Parsed Banking Sections: {list(sections.keys())}")
    assert "SECTION_COMPLIANCE" in sections
    assert "SECTION_RISK_HIGH" in sections
    
    # Test Loader - Healthcare Tier 1 (High Risk)
    context = load_rag_context("HEALTHCARE", "TIER_1")
    print(f"\nHealthcare Tier 1 Context:\n{context}")
    assert "HIPAA" in context
    assert "diagnostic assistance" in context
    
    # Test Loader - Banking Tier 3 (Low Risk)
    context = load_rag_context("BANKING", "TIER_3")
    print(f"\nBanking Tier 3 Context:\n{context}")
    assert "Basel III" in context
    assert "internal document classification" in context
    assert "rigorous stress testing" in context  # Check modeling patterns included
    
    # Test Loader - Unknown Domain (Fallback to General, TIER_1 -> HIGH)
    context = load_rag_context("UNKNOWN", "TIER_1")
    print(f"\nUnknown Domain Context:\n{context}")
    assert "general ethical guidelines" in context
    assert "human-in-the-loop" in context

    print("\nAll RAG logic tests passed!")

if __name__ == "__main__":
    test_rag_logic()
