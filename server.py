"""Verity MCP server — the agent economy's "verify before you spend/send/trust" gate.

Exposes Verity's fail-closed trust checks as Model Context Protocol tools any
MCP-capable agent can discover and call:

    verify_fact        — is this factual claim true? (catches hallucinations)
    detect_injection   — is this untrusted text a prompt-injection / manipulation?
    moderate_content   — is this safe to publish?
    redact_pii         — does this leak personal data or secrets?
    guard_action       — should this proposed action proceed? (allow / review / block)

Backed by Verity's LIVE HTTP+x402 services on Base mainnet (USDC). Verity holds
NO private key. Calls are paid per use via x402: an x402-capable MCP client
settles a small, DISCLOSED micro-payment on the call the agent already chose to
make — never a silent per-loop default (see README → Disclosure discipline).

Design intent (the money-line wedge): the highest-value use is right BEFORE an
agent spends, sends, or commits something irreversible — an independent, signed
"safe / not safe" verdict is worth far more than the sub-cent fee there. The
everywhere-gate is meant to be free and self-hosted; this paid layer earns at
the value boundary.
"""
from __future__ import annotations

import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

SUITE = os.getenv("VERITY_SUITE_URL", "https://verity-suite.onrender.com").rstrip("/")
ENGINE = os.getenv("VERITY_ENGINE_URL", "https://verity-bzw7.onrender.com").rstrip("/")
TIMEOUT = float(os.getenv("VERITY_TIMEOUT", "90"))

mcp = FastMCP(
    "verity",
    instructions=(
        "Verity is an independent, fail-closed trust layer for AI agents. Use these tools to "
        "VERIFY BEFORE YOU ACT — especially before spending, sending, publishing, or committing "
        "something irreversible. Each tool returns a calibrated verdict and abstains rather than "
        "bluff. Calls are paid per use via x402 (small, disclosed USDC micro-payments on Base); "
        "Verity holds no key and never charges silently."
    ),
)


def _post(base: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    """POST to a live Verity x402 endpoint.

    Payment model: these endpoints answer HTTP 402 (Payment Required) until paid.
    An x402-capable client/proxy settles the disclosed USDC micro-payment and
    retries. We surface a 402 transparently so the agent's x402 layer can pay —
    we never hold a key or pay on the agent's behalf.
    """
    url = f"{base}{path}"
    try:
        r = httpx.post(url, json=payload, timeout=TIMEOUT)
    except Exception as e:  # network/timeout — fail honestly, do not fabricate a verdict
        return {"error": f"verity_unreachable: {str(e)[:160]}", "endpoint": url}
    if r.status_code == 402:
        return {
            "payment_required": True,
            "endpoint": url,
            "detail": "This Verity check is paid per call via x402 (USDC on Base). "
                      "Have your x402-capable client settle the disclosed micro-payment and retry.",
            "x402": r.headers.get("payment-required") or r.headers.get("x-payment") or "",
        }
    try:
        return r.json()
    except Exception:
        return {"error": f"unexpected_status_{r.status_code}", "body": r.text[:300]}


@mcp.tool()
def verify_fact(claim: str, context: str | None = None) -> dict:
    """Check whether a factual CLAIM is true, grounded against the live web.

    Use before an agent acts on, repeats, or surfaces a fact it isn't certain of —
    catches hallucinations (fabricated citations, invented policies, wrong numbers).
    Returns: verdict (supported | unsupported | uncertain), an honest 0-1 confidence,
    reasoning, and evidence. Abstains ('uncertain') rather than guess.
    (Independent fact-verification; maps to OWASP LLM/ASI guidance on grounding.)
    """
    return _post(ENGINE, "/verify", {"claim": claim, "context": context})


@mcp.tool()
def detect_injection(content: str, context: str | None = None) -> dict:
    """Screen untrusted text or tool output for PROMPT-INJECTION / manipulation.

    Use on anything an agent ingests from an outside source (web page, email, doc,
    tool result) BEFORE acting on it. Catches instruction-override, task/persona
    switching, grounding-override, jailbreaks, and multilingual attacks.
    Returns: verdict (clean | suspicious | injection | uncertain), threat_score,
    techniques, and a pass/sanitize/quarantine recommendation.
    (Maps to OWASP ASI02 Tool Misuse / LLM01 Prompt Injection — produces an audit artifact.)
    """
    return _post(SUITE, "/sentinel", {"content": content, "context": context})


@mcp.tool()
def moderate_content(content: str, policy: str | None = None) -> dict:
    """Decide whether CONTENT is safe to publish, post, or surface.

    Use before an agent sends or publishes generated content. Optional `policy`
    sets the standard; otherwise a conservative default-safe baseline is applied.
    Returns: decision (publish | review | block), violation_risk, categories, and reasons.
    """
    return _post(SUITE, "/sieve", {"content": content, "policy": policy})


@mcp.tool()
def redact_pii(payload: str, context: str | None = None) -> dict:
    """Detect personal data and secrets in a PAYLOAD before it is sent, stored, or logged.

    Use before an agent transmits text outside a trust boundary. Flags PII (names,
    emails, IDs, financial, device/IP) and secrets (API keys, passwords, tokens).
    Returns: verdict (clean | contains_pii | contains_secret | review), severity,
    findings, and a redacted version of the payload.
    (Maps to OWASP ASI guidance on sensitive-data leakage — produces an audit artifact.)
    """
    return _post(SUITE, "/redact", {"payload": payload, "context": context})


@mcp.tool()
def guard_action(action: str, context: str | None = None, policy: str | None = None) -> dict:
    """THE MONEY-LINE GATE. Decide whether a proposed agent ACTION should proceed —
    use this right before the agent SPENDS, SENDS, or commits something irreversible
    (a payment, an outbound message, a destructive command, a data share).

    Fail-closed: it will not 'allow' what it cannot justify as safe — uncertainty
    escalates to review, real red flags block. Returns: decision (allow | review |
    block), an honest 0-1 risk, concrete reasons, specific concerns, and a safer
    alternative. This independent, signed verdict is the thing no free local check
    can give the agent at the moment money or irreversibility is on the line.
    (Maps to OWASP ASI02 Tool Misuse / ASI08 Cascading Failures — produces an audit artifact.)
    """
    return _post(SUITE, "/guardrail", {"action": action, "context": context, "policy": policy})


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
