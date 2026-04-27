# 💹 Groww Factual Assistant (HDFC Mutual Funds RAG)
**Milestone 1 - Phase 1-4 Complete**

A robust, citation-first RAG (Retrieval-Augmented Generation) assistant for HDFC mutual fund queries. This system is designed for high-fidelity factual accuracy, strict compliance with Indian financial guardrails, and a premium "Tiny UI" delivery.

---

## 🏗️ Modular Architecture

### **Phase 1: Knowledge Ingestion**
- **Crawl & Ingest**: Targeted extraction of SID/KIM details (Top 100, Flexi Cap, ELSS, Mid-Cap).
- **Vector Base**: ChromaDB with `all-MiniLM-L6-v2` embeddings for lightweight, high-speed semantic search.
- **Chunking**: Specialized 800-character chunks with a 50-character overlap to preserve table-like fund facts.

### **Phase 2: Retrieval Logic**
- **Top-K Selection**: Set to **3** (reads the top 3 most relevant snippets).
- **Conciseness**: Answers are strictly limited to **≤3 sentences**.
- **Citation Renderer**: Every response maps back to the official HDFC product URL found in the source metadata.

### **Phase 3: Safety & Guardrails**
- **PII Block**: Regex detection for Indian **PAN** (10-char alnum) and **Aadhaar** (12-digit).
- **No-Advice Intent**: Rejects speculative or comparative queries ("Should I buy?", "Compare performance") with a direct consulting refusal.

### **Phase 4: Final Delivery (Tiny UI)**
- **Interface**: Premium "Groww-Green" themed Streamlit dashboard.
- **Transparency**: Data recency stamps and clickable source tags for users to verify directly on the HDFC portal.

---

## 🚀 Getting Started

### **1. Setup Dependency Environment**
```powershell
pip install -r Phase 1/requirements.txt
```

### **2. Re-Ingest Knowledge Base**
If you update `sources.md` or the curated fact lists:
```powershell
python "Phase 1/ingest_final.py"
```

### **3. Run the Assistant (Tiny UI)**
Launch the premium web interface:
```powershell
streamlit run "Phase 4/app.py"
```

### **4. Generate QA Milestone Report**
To regenerate the `sample_qa.md` report (15-question verification):
```powershell
python "generate_qa.py"
```

---

## 📄 Project Artifacts
- **[sources.md](./sources.md)**: Master list of HDFC official URLs.
- **[architecture.md](./architecture.md)**: Detailed technical plan.
- **[sample_qa.md](./sample_qa.md)**: Factual verification suite results.

---

## 📅 Maintenance
- **Data Recency**: Last updated March 2026.
- **Contact**: For core engine updates, refer to Phase 2/rag_engine.py.
