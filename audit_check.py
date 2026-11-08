from openai import OpenAI

# 1. Point the standard OpenAI SDK to your local Ollama instance
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Required parameter by the SDK, but ignored by Ollama
)

# 2. A realistic Non-Human Identity (NHI) & Agent audit finding
sample_iam_finding = """
Finding ID: AUD-2026-084
System Boundary: Autonomous Customer Support & Tier-2 Remediation Agent
Description: The AI agent was provisioned an administrative service principal with 
unrestricted 'Directory.ReadWrite.All' and database write permissions to automatically 
resolve account locks and update user attributes. The agent uses autonomous multi-step 
tool calling, prompts are not sanitized against indirect prompt injection, credentials 
are persistent without rotation, and all actions taken by the agent inherit the service 
principal's identity rather than attributing actions to the requesting user session.
"""

print("[*] Contacting local Llama 3.2 model at http://localhost:11434/v1...")

response = client.chat.completions.create(
    model="llama3.2:3b",
    messages=[
        {
            "role": "system",
            "content": (
                "You are an expert AI GRC Auditor and Identity Security Architect. "
                "Evaluate the provided audit finding against the NIST AI Risk Management Framework (NIST AI RMF) "
                "and zero-trust non-human identity (NHI) principles. "
                "Provide a structured assessment covering:\n"
                "1. Non-Human Identity (NHI) & Excessive Agency Risks\n"
                "2. NIST AI RMF Function Gaps (GOVERN & MANAGE)\n"
                "3. Concrete Engineering Remediation Steps (Least Privilege, Tool Boundaries, Guardrails)"
            )
        },
        {
            "role": "user",
            "content": f"Please evaluate this finding:\n{sample_iam_finding}"
        }
    ],
    temperature=0.2
)

print("\n" + "=" * 65)
print("             LOCAL AI GRC AUDIT REPORT")
print("=" * 65 + "\n")
print(response.choices[0].message.content)
print("\n" + "=" * 65)
print("[+] Complete. Local inference cost: $0.00")