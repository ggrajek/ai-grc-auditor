# AI GRC Auditor (`ai-grc-auditor`)

An open-source, air-gapped, zero-cost AI Governance, Risk, and Compliance (GRC) audit engine. It evaluates non-human identities (NHI), autonomous agents, and AI service principals against authoritative frameworks (such as the **NIST AI RMF 1.0** and **Zero Trust NHI Standards**) using pure local Retrieval-Augmented Generation (RAG).

## Architecture & Data Flow

The engine cleanly separates identity state, regulatory baselines, and inference:

```
[ identity_inventory.json ]          [ framework_controls.json ]
  (Directory / NHI Objects)            (NIST AI RMF / Zero Trust Controls)
             │                                    │
             │                                    ▼
             │                         [ nomic-embed-text ]
             │                       (Local Vector Embeddings)
             │                                    │
             ▼                                    ▼
      [ rag_auditor.py ] ◄────────────── [ Cosine Similarity Match ]
      (Ingestion & Dossier)              (Retrieves Top-K Relevant Controls)
             │
             ▼
      [ LLaMA 3.2:3b ] (Local Ollama Engine)
             │
             ▼
      [ Grounded Audit Report: PASS / FAIL with Exact Citations ]
```

### Key Components

1. **Identity State Tier (`identity_inventory.json`):** Holds directory objects, assigned scopes, credential persistence, operational agency boundaries, and session-attribution flags.
2. **Governance Knowledge Base (`framework_controls.json`):** Contains official control language, titles, and unique control IDs (e.g., `NIST-AI-RMF-GOVERN-1.2`, `ZT-NHI-AUTH-03`).
3. **Local Vector Search (`nomic-embed-text`):** Generates 768-dimensional embeddings to match identity findings semantically to relevant controls without cloud APIs or token costs.
4. **Deterministic Local Inference (`llama3.2:3b`):** Delivers grounded audit reports containing explicit PASS/FAIL verdicts and remediation requirements.

---

## Prerequisites

- [Ollama](https://ollama.com/) installed and running.
- Python 3.10+ (tested on Windows ARM64 / x64).

Pull the local models:
```powershell
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

---

## Installation & Setup

1. Clone the repository:
```powershell
git clone [https://github.com/ggrajek/ai-grc-auditor.git](https://github.com/ggrajek/ai-grc-auditor.git)
cd ai-grc-auditor
```

2. Create and activate a Python virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install dependencies:
```powershell
pip install -r requirements.txt
```

---

## Running the Auditor

Execute the RAG engine against the configured directory inventory:

```powershell
python rag_auditor.py
```

### Sample Output

The engine evaluates both non-compliant and compliant identities:
- **`Tier-2 Support AI Remediation Agent`**: Produces a **`[FAIL]`** verdict citing excessive permissions (`Directory.ReadWrite.All`), missing secret rotation, and lack of human-in-the-loop authorization.
- **`SecOps Incident Triage Copilot`**: Produces a **`[PASS]`** verdict validating ephemeral short-lived tokens, least-privilege read scopes, and session-bound attribution.
