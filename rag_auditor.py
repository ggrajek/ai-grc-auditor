import json
import math
import ollama

EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.2:3b"

def cosine_similarity(vec_a, vec_b):
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

def build_vector_index(controls_file="framework_controls.json"):
    print("[*] Generating local vector embeddings for framework controls...")
    with open(controls_file, "r") as f:
        controls = json.load(f)
    
    indexed_controls = []
    for ctrl in controls:
        # Embed each control with local nomic-embed-text
        response = ollama.embeddings(
            model=EMBEDDING_MODEL,
            prompt=f"{ctrl['title']}: {ctrl['text']}"
        )
        ctrl["embedding"] = response["embedding"]
        indexed_controls.append(ctrl)
    
    print(f"[+] Successfully indexed {len(indexed_controls)} framework controls locally.")
    return indexed_controls

def retrieve_top_k(query_text, indexed_controls, top_k=2):
    print("[*] Embedding audit query and executing vector search...")
    query_resp = ollama.embeddings(
        model=EMBEDDING_MODEL,
        prompt=query_text
    )
    query_vec = query_resp["embedding"]

    scored = []
    for ctrl in indexed_controls:
        score = cosine_similarity(query_vec, ctrl["embedding"])
        scored.append((score, ctrl))

    # Sort descending by similarity score
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]

def run_rag_audit(finding_text):
    # 1. Index local controls
    knowledge_base = build_vector_index()

    # 2. Retrieve top matching controls
    top_matches = retrieve_top_k(finding_text, knowledge_base, top_k=2)

    print("\n" + "=" * 65)
    print("           RETRIEVED FRAMEWORK CONTROLS (VECTOR MATCH)")
    print("=" * 65)
    context_blocks = []
    for score, ctrl in top_matches:
        print(f"-> Matched: [{ctrl['control_id']}] (Similarity Score: {score:.4f})")
        print(f"   Framework: {ctrl['framework']} | {ctrl['title']}")
        context_blocks.append(
            f"Control ID: {ctrl['control_id']}\n"
            f"Framework: {ctrl['framework']}\n"
            f"Title: {ctrl['title']}\n"
            f"Requirement: {ctrl['text']}"
        )
    print("=" * 65 + "\n")

    combined_context = "\n\n".join(context_blocks)

    # 3. Augment generation with strict grounding instructions
    system_prompt = (
        "You are an expert AI GRC Auditor and Identity Architect. "
        "Evaluate the directory entity attributes strictly against the provided authoritative controls. "
        "You must determine compliance based on whether the entity follows least-privilege, ephemeral secrets, "
        "human-in-the-loop boundaries, and session attribution.\n\n"
        "Structure your response exactly as follows:\n"
        "1. Overall Finding Verdict: [PASS] or [FAIL]\n"
        "2. Executive Summary & Posture Analysis\n"
        "3. Framework Mapping & Control Citations (cite specific Control IDs and explain compliance or violation)\n"
        "4. Required Technical Remediation (or 'None Required' if PASS)"
    )


    user_prompt = (
        f"AUTHORITATIVE GRC CONTROLS:\n"
        f"{combined_context}\n\n"
        f"AUDIT FINDING TO EVALUATE:\n"
        f"{finding_text}"
    )

    print("[*] Dispatching grounded RAG prompt to local Llama 3.2...")
    llm_resp = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        options={"temperature": 0.2}
    )

    print("\n" + "=" * 65)
    print("                 GROUNDED AI GRC AUDIT REPORT")
    print("=" * 65 + "\n")
    print(llm_resp["message"]["content"])
    print("\n" + "=" * 65)
    print("[+] Complete. 100% Air-Gapped Local Inference.")

def audit_directory_inventory(inventory_file="identity_inventory.json"):
    with open(inventory_file, "r") as f:
        entities = json.load(f)

    for item in entities:
        print(f"\n[!] INGESTING DIRECTORY OBJECT: {item['app_display_name']} ({item['object_type']})")
        print(f"    Provider: {item['directory_provider']}")
        print(f"    Permissions: {', '.join(item['assigned_roles_and_scopes'])}")
        print(f"    Persistent Credential: {item['is_credential_persistent']}")
        print(f"    Session Bound: {item['audit_logging']['session_bound']}")
        print("-" * 65)

        # Convert structured directory attributes into an audit problem statement
        finding = (

            f"Directory Entity: {item['app_display_name']}\n"
            f"Type: {item['object_type']} via {item['directory_provider']}\n"
            f"Assigned Scopes: {', '.join(item['assigned_roles_and_scopes'])}\n"
            f"Persistent Credential: {item['is_credential_persistent']} (Rotation Days: {item['credential_rotation_days']})\n"
            f"Autonomous Agency: {item['execution_boundary']['autonomous_tool_calling']} (HITL Approval: {item['execution_boundary']['human_in_the_loop_approval']})\n"
            f"Sanitization Guardrails: {item['execution_boundary']['input_sanitization_enabled']}\n"
            f"Audit Attribution: {item['audit_logging']['attributing_identity']} (Session-Bound: {item['audit_logging']['session_bound']})"
        )

        run_rag_audit(finding)
if __name__ == "__main__":
    audit_directory_inventory()