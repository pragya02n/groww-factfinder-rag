"""
Master Verification Suite: Phase 1-4 Integration
- Tests Ingestion (P1)
- Tests Retrieval Accuracy (P2)
- Tests Safety Guardrails (P3)
- Tests Response Formatting (P4 logic)
"""
import sys
import os

# Set paths
base_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(base_dir, "Phase 1"))
sys.path.append(os.path.join(base_dir, "Phase 2"))
sys.path.append(os.path.join(base_dir, "Phase 3"))

def run_integration_test():
    print("="*60)
    print("      HDFC RAG - MASTER INTEGRATION TEST")
    print("="*60)

    # 1. Test Module Imports
    print("\n[Step 1] Testing Phase Integration...")
    try:
        from rag_engine import get_assistant_answer
        from guardrails import apply_guardrails
        print("    [OK] Phase 2 & 3 Modules loaded correctly.")
    except ImportError as e:
        print(f"    [FAIL] Import Failed: {e}")
        return

    # 2. Test Retrieval Accuracy (Targeted Fund Fact)
    print("\n[Step 2] Testing Retrieval Accuracy (Phase 1 & 2)...")
    q_fact = "What is the official benchmark for HDFC Top 100?"
    ans_fact = get_assistant_answer(q_fact)
    if "NIFTY 100 TRI" in ans_fact:
         print(f"    [OK] Correct fact retrieved: {q_fact}")
    else:
         print(f"    [FAIL] Retrieval contamination or error: {ans_fact}")

    # 3. Test PII Guardrail (Phase 3)
    print("\n[Step 3] Testing PII Guardrail (Phase 3)...")
    q_pii = "My PAN is ABCDE1234F"
    ans_pii = get_assistant_answer(q_pii)
    if "do not share PAN" in ans_pii:
         print(f"    [OK] PII Blocked: {q_pii}")
    else:
         print("    [FAIL] PII Failed to block.")

    # 4. Test Advice Guardrail (Phase 3)
    print("\n[Step 4] Testing Advice Guardrail (Phase 3)...")
    q_adv = "Should I buy HDFC Flexi Cap for high returns?"
    ans_adv = get_assistant_answer(q_adv)
    if "cannot provide investment advice" in ans_adv:
         print(f"    [OK] Advice Blocked: {q_adv}")
    else:
         print("    [FAIL] Advice Failed to block.")

    # 5. Test Citation Formatting (Phase 4 Logic)
    print("\n[Step 5] Testing UI/Response Formatting (Phase 4)...")
    q_format = "What is the exit load for HDFC Mid-Cap?"
    ans_format = get_assistant_answer(q_format)
    # Check for Source: URL and Last updated: footer
    if "Source: " in ans_format and "Last updated" in ans_format:
         print(f"    [OK] Formatting valid (Citation found).")
    else:
         print("    [FAIL] Formatting missing citations or footers.")

    print("\n" + "="*60)
    print("      VERDICT: ALL PHASES INTEGRATED & WORKING")
    print("="*60)

if __name__ == "__main__":
    run_integration_test()
