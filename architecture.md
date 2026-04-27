# Technical Architecture: Groww MF FAQ Assistant

---

## Phase 1: Knowledge Ingestion & Vectorization

> The goal is to turn your static URLs into a searchable, "cite-able" knowledge base.

| Component | Description |
|-----------|-------------|
| **Source Loader** | A specialized node to crawl the 8 URLs in your `sources.md`. |
| **Text Splitter** | Use a **Recursive Character Splitter**. |
| **Settings** | Chunk Size = `500`, Overlap = `50`. |
| **Vector Store** | Store these chunks in a vector database with **Source Metadata Enabled**. This ensures that every chunk of text remembers the URL it came from. |

---

## Phase 2: The Logic & Retrieval Engine (RAG)

> This phase defines how the AI "thinks" before it answers.

| Component | Description |
|-----------|-------------|
| **Semantic Search** | When a user asks a question, the bot retrieves the **Top 3** most relevant chunks. |
| **Temperature Control** | Set to `0.0` (Deterministic). This prevents the AI from being "creative" with financial numbers. |
| **The Context Window** | The prompt must inject the retrieved chunks as the **"Only Source of Truth."** |

---

## Phase 3: Guardrail & Safety Layer

> This is where you implement the "No Advice" and "No PII" rules.

| Component | Description |
|-----------|-------------|
| **Intent Classifier** | A layer that checks: *Is the user asking for a fact or an opinion?* |
| **PII Masking** | A Regex-based filter to detect and block PAN cards or Aadhaar numbers. |
| **Refusal Logic** | A hardcoded response for out-of-scope questions (e.g., "Which fund is best?"). |

---

## Phase 4: Frontend (Tiny UI) & Delivery

> The final user interface and the deliverables for your milestone.

| Component | Description |
|-----------|-------------|
| **Greeting Component** | Includes the "Facts-only" disclaimer and 3 example buttons. |
| **Citation Renderer** | A specific formatting rule to append the `source_url` at the end of every response. |
| **Deliverables Pipeline** | Automated generation of the Sample Q&A file and `README.md`. |

---

## Systematic Workflow Table

| Phase | Milestone Task | Strategy |
|-------|---------------|----------|
| **Phase 1** | Corpus Scoping | Map 8 official URLs with metadata. |
| **Phase 2** | Prompting (W2) | Strict instruction: *"Answer only from context."* |
| **Phase 3** | Compliance | Block PII and refuse "Should I buy?" queries. |
| **Phase 4** | Prototyping | Deploy a Tiny UI with persistent disclaimers. |
