"""
Milestone 1: Sample QA Generation
- Answers 15 specific questions from HDFC Knowledge Base.
- Follows strict Q&A formatting with citations and footers.
- Triggers PII/Advice logic for relevant queries.
"""
import sys
import os

# Add relevant paths
sys.path.append(os.path.join(os.path.dirname(__file__), "Phase 2"))
sys.path.append(os.path.join(os.path.dirname(__file__), "Phase 3"))

from rag_engine import get_assistant_answer

QUESTIONS = [
    "What is the exit load for HDFC Top 100 Fund after 6 months?",
    "What is the expense ratio for HDFC Flexi Cap Fund (Direct)?",
    "What is the minimum SIP for HDFC Mid-Cap Opportunities?",
    "What is the minimum lumpsum for HDFC ELSS Tax Saver?",
    "What is the Riskometer rating for HDFC Top 100?",
    "Which benchmark index does HDFC Flexi Cap track?",
    "What is the lock-in period for HDFC ELSS Tax Saver?",
    "How do I download a Consolidated Account Statement (CAS)?",
    "How can I update my bank mandate online?",
    "Where is the Capital Gains Statement on the HDFC portal?",
    "Which of these three funds is best for high returns?",
    "Compare HDFC Top 100 vs SBI Bluechip performance.",
    "My PAN is ABCDE1234F, tell me my balance.",
    "Who is the Fund Manager for HDFC Mid-Cap Opportunities?",
    "What is the AUM for HDFC Flexi Cap Fund?"
]

def generate_sample_qa():
    print("[*] Generating Milestone 1 Sample QA...")
    qa_lines = ["# Milestone 1: Sample QA (HDFC Mutual Fund Assistant)\n"]
    
    for i, question in enumerate(QUESTIONS, 1):
        print(f"    - Processing Q{i}: {question[:40]}...")
        answer = get_assistant_answer(question)
        
        # User requested specific formatting:
        # Q: [The Question]
        # A: [A factual answer in <=3 sentences]
        # Source: [URL]
        # Updated: Last updated from sources: March 2026.
        
        qa_lines.append(f"Q: {question}")
        
        # Our get_assistant_answer already returns: [Answer]\nSource: [URL]\nLast updated from sources: March 2026.
        # We need to split it to fit the "A: [Answer]" part.
        parts = answer.split("\nSource: ")
        factual_answer = parts[0]
        meta_info = "Source: " + parts[1] if len(parts) > 1 else ""
        
        # Re-formatting exactly as requested
        qa_lines.append(f"A: {factual_answer}")
        if meta_info:
             # Split source and updated if they are together
             source_parts = meta_info.split("\nLast updated from sources: ")
             qa_lines.append(source_parts[0])
             qa_lines.append(f"Updated: Last updated from sources: March 2026.")
        else:
             # In case of Refusal where Source doesn't exist
             qa_lines.append("Source: N/A")
             qa_lines.append("Updated: Last updated from sources: March 2026.")
        
        qa_lines.append("") # Newline
        
    output_path = "sample_qa.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(qa_lines))
    print(f"[DONE] Milestone 1 QA generated at: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    generate_sample_qa()
