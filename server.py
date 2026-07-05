"""Verity MCP server — the agent economy's "verify before you spend/send/trust" gate.

Exposes Verity's fail-closed trust checks as Model Context Protocol tools any
MCP-capable agent can discover and call. Every tool DISCLOSES its per-call price
up front (see each docstring); payment is x402 USDC on Base mainnet. Verity holds
NO private key and never charges silently.

    quick_verify        — cheap ungrounded reality-check (~$0.02). THE loopable default.
    grounded_verify     — web-grounded reality-check with live citations (~$0.25). The default product.
    pro_verify          — premium grounded synthesis (~$0.35). The deepest check.
    verify_receipt      — FREE: statelessly verify a signed verdict receipt (audit trail, no payment).
    detect_injection    — is this untrusted text a prompt-injection / manipulation? (~$0.02)
    moderate_content    — is this safe to publish? (~$0.02)
    redact_pii          — does this leak personal data or secrets? (~$0.02)
    guard_action        — should this proposed action proceed? allow / review / block (~$0.02)

Tiered pricing (price > cost on every paid tier — no money pits):
    quick     $0.02   ungrounded Haiku            the land-grab / loopable tier
    grounded  $0.25   web-grounded Sonnet         the default product (live citations)
    pro       $0.35   web-grounded Opus           premium synthesis
    suite     $0.02   ungrounded Haiku (/quick)   the suite trust-checks, quick tier

Backed by Verity's LIVE HTTP+x402 services on Base mainnet (USDC). Calls are paid
per use via x402: an x402-capable MCP client settles the small, DISCLOSED
micro-payment on the call the agent already chose to make — never a silent
per-loop default (see README → Disclosure discipline).

Every paid verify verdict carries an Ed25519-signed receipt — self-contained
cryptographic proof of exactly what Verity said, verifiable forever. The FREE
verify_receipt tool checks any receipt against Verity's public key (no payment).

Affiliate / referral (reserved):
    Every tool accepts an optional `affiliate_id`, passed through to Verity as an
    `X-Verity-Ref` header. It NEVER changes price, gating, or the verdict — it only
    tags who routed the call. It is reserved for a future referral program: no split
    is paid today, and none will be until public terms are published at
    veritylayer.dev. (Honesty discipline: we don't advertise payouts we don't
    yet make.)
"""
from __future__ import annotations

import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

SUITE = os.getenv("VERITY_SUITE_URL", "https://verity-suite.onrender.com").rstrip("/")
ENGINE = os.getenv("VERITY_ENGINE_URL", "https://api.veritylayer.dev").rstrip("/")
TIMEOUT = float(os.getenv("VERITY_TIMEOUT", "90"))

# Disclosed per-call prices (USDC on Base mainnet). Surfaced in every tool docstring
# AND echoed in the response so an agent/operator always sees what a call costs.
PRICE_QUICK = os.getenv("VERITY_PRICE_QUICK", "$0.02")
PRICE_GROUNDED = os.getenv("VERITY_PRICE_GROUNDED", "$0.25")
PRICE_PRO = os.getenv("VERITY_PRICE_PRO", "$0.35")
PRICE_SUITE = os.getenv("VERITY_PRICE_SUITE", "$0.02")  # the suite trust-checks (quick tier)
PRICE_FREE = "$0.00"  # receipt verification is a free, unpaid route

mcp = FastMCP(
    "verity",
    instructions=(
        "Verity is an independent, fail-closed trust layer for AI agents. Use these tools to "
        "VERIFY BEFORE YOU ACT — especially before spending, sending, publishing, or committing "
        "something irreversible. Each tool returns a calibrated verdict and abstains rather than "
        "bluff. Calls are paid per use via x402 (small, DISCLOSED USDC micro-payments on Base "
        "mainnet) — every tool states its price in its description; Verity holds no key and never "
        "charges silently. Default loop with quick_verify ($0.02, ungrounded); escalate to "
        "grounded_verify ($0.25, web-grounded) when a claim is load-bearing, or pro_verify ($0.35) "
        "for the deepest synthesis. Every paid verdict ships a signed receipt; verify_receipt is "
        "FREE. affiliate_id is accepted on any call as a routing tag reserved for a future "
        "referral program — it never changes price or behavior."
    ),
)


def _headers(affiliate_id: str | None) -> dict[str, str]:
    """Build request headers, attaching the optional referral tag.

    The affiliate tag rides as `X-Verity-Ref`. It is pure metadata — it never
    changes price, gating, or the verdict. Reserved for a future referral program;
    no split is paid until public terms are published at veritylayer.dev.
    """
    h = {"content-type": "application/json"}
    if affiliate_id:
        h["X-Verity-Ref"] = str(affiliate_id)
    return h


def _post(
    base: str,
    path: str,
    payload: dict[str, Any],
    price: str,
    affiliate_id: str | None = None,
) -> dict[str, Any]:
    """POST to a live Verity x402 endpoint, disclosing the price on the way out.

    Payment model: these endpoints answer HTTP 402 (Payment Required) until paid.
    An x402-capable client/proxy settles the disclosed USDC micro-payment and
    retries. We surface a 402 transparently — with the price restated — so the
    agent's x402 layer can pay. We never hold a key or pay on the agent's behalf.

    Free routes (price == PRICE_FREE) never 402; the block below is simply skipped.
    """
    url = f"{base}{path}"
    try:
        r = httpx.post(url, json=payload, headers=_headers(affiliate_id), timeout=TIMEOUT)
    except Exception as e:  # network/timeout — fail honestly, do not fabricate a verdict
        return {"error": f"verity_unreachable: {str(e)[:160]}", "endpoint": url, "price": price}
    if r.status_code == 402:
        return {
            "payment_required": True,
            "endpoint": url,
            "price": price,
            "currency": "USDC",
            "network": "Base mainnet (eip155:8453)",
            "affiliate_id": affiliate_id,
            "detail": f"This Verity check is paid per call via x402 ({price} USDC on Base). "
                      "Have your x402-capable client settle the disclosed micro-payment and retry.",
            "x402": r.headers.get("payment-required") or r.headers.get("x-payment") or "",
        }
    try:
        out = r.json()
    except Exception:
        return {"error": f"unexpected_status_{r.status_code}", "body": r.text[:300], "price": price}
    # Echo the price/affiliate context back so the agent always has the disclosed cost in-band.
    if isinstance(out, dict):
        out.setdefault("price", price)
        if affiliate_id:
            out.setdefault("affiliate_id", affiliate_id)
        # Surface the signed receipt front-and-center when the paid verdict carried one,
        # so the agent knows a verifiable audit artifact came back (verify it FREE via verify_receipt).
        if out.get("receipt"):
            out.setdefault("receipt_note",
                           "Signed Ed25519 receipt attached — verify it for free with verify_receipt.")
    return out


# ── Verification tiers ────────────────────────────────────────────────────────

@mcp.tool()
def quick_verify(claim: str, context: str | None = None, affiliate_id: str | None = None) -> dict:
    """Cheap, fast reality-check on a CLAIM — the loopable default. PRICE: ~$0.02 per call
    (x402, USDC on Base mainnet). Ungrounded (no web search): a single calibrated Haiku judge
    over the claim's own plausibility/consistency — use it everywhere as the inexpensive first
    pass, then escalate the load-bearing ones to grounded_verify.

    Returns: verdict (supported | unsupported | uncertain), an honest 0-1 confidence, reasoning,
    and (when signing is enabled) a signed Ed25519 receipt you can later re-check for free with
    verify_receipt. Abstains ('uncertain') rather than guess; never invents evidence.

    Pricing is DISCLOSED and paid per use via x402 — Verity holds no key and never charges silently.
    Optional affiliate_id tags the call for a future referral program (no split is paid until
    public terms exist at veritylayer.dev); it does not change price or behavior.
    (Independent fact-verification; maps to OWASP LLM/ASI guidance on grounding.)
    """
    return _post(ENGINE, "/verify/quick", {"claim": claim, "context": context},
                 PRICE_QUICK, affiliate_id)


@mcp.tool()
def grounded_verify(claim: str, context: str | None = None, affiliate_id: str | None = None) -> dict:
    """Web-GROUNDED reality-check on a CLAIM — the default product. PRICE: ~$0.25 per call (x402,
    USDC on Base mainnet). Runs a live, capped web search and a calibrated Sonnet synthesis — use it
    right before an agent acts on, repeats, or surfaces a fact that matters (a fabricated citation,
    an invented policy, a wrong number). Escalate to pro_verify for the deepest synthesis.

    Returns: verdict (supported | unsupported | uncertain), an honest 0-1 confidence, reasoning,
    cited evidence, and (when signing is enabled) a signed Ed25519 receipt (re-check for free with
    verify_receipt). Abstains rather than guess; never fabricates citations.

    Pricing is DISCLOSED and paid per use via x402 — Verity holds no key and never charges silently.
    Optional affiliate_id tags the call for a future referral program; it never changes price or behavior.
    (Independent fact-verification; maps to OWASP LLM/ASI guidance on grounding — produces an audit artifact.)
    """
    return _post(ENGINE, "/verify", {"claim": claim, "context": context},
                 PRICE_GROUNDED, affiliate_id)


@mcp.tool()
def pro_verify(claim: str, context: str | None = None, affiliate_id: str | None = None) -> dict:
    """Premium, web-GROUNDED reality-check on a CLAIM — the deepest tier. PRICE: ~$0.35 per call
    (x402, USDC on Base mainnet). Runs a live web search and a calibrated Opus synthesis — reach for
    it when a claim is high-stakes and the grounded tier's answer isn't confident enough to act on.

    Returns: verdict (supported | unsupported | uncertain), an honest 0-1 confidence, reasoning,
    cited evidence, and (when signing is enabled) a signed Ed25519 receipt (re-check for free with
    verify_receipt). Abstains rather than guess; never fabricates citations.

    Pricing is DISCLOSED and paid per use via x402 — Verity holds no key and never charges silently.
    Optional affiliate_id tags the call for a future referral program; it never changes price or behavior.
    (Independent fact-verification; maps to OWASP LLM/ASI guidance on grounding — produces an audit artifact.)
    """
    return _post(ENGINE, "/verify/pro", {"claim": claim, "context": context},
                 PRICE_PRO, affiliate_id)


@mcp.tool()
def verify_receipt(receipt: dict, affiliate_id: str | None = None) -> dict:
    """FREE. Statelessly verify a signed verdict RECEIPT — your audit trail / second opinion.
    PRICE: $0.00 (no x402 payment; this is a free discovery route). Pass the receipt object returned
    by any paid verify tool; Verity checks its Ed25519 signature against the server's public key and
    confirms Verity really issued exactly that verdict for exactly that claim. Use it to prove a
    result held, catch tampering, or attach cryptographic proof before you act.

    Returns: {valid: bool, reason: str}. A genuine receipt validates offline against
    /.well-known/verity-pubkey.json — this endpoint is the convenient live check.

    No payment, no key (affiliate_id is accepted but inert on this free call).
    (Produces/verifies an audit artifact; maps to OWASP ASI verifiability guidance.)
    """
    return _post(ENGINE, "/receipt/verify", receipt, PRICE_FREE, affiliate_id)


# ── Suite trust-checks (quick tier — ~$0.02 each) ─────────────────────────────

@mcp.tool()
def detect_injection(content: str, context: str | None = None, affiliate_id: str | None = None) -> dict:
    """Screen untrusted text or tool output for PROMPT-INJECTION / manipulation. PRICE: ~$0.02 per
    call (x402, USDC on Base mainnet). Use on anything an agent ingests from an outside source
    (web page, email, doc, tool result) BEFORE acting on it. Catches instruction-override,
    task/persona switching, grounding-override, jailbreaks, and multilingual attacks.

    Returns: verdict (clean | suspicious | injection | uncertain), threat_score, techniques, reasons,
    and a recommended_action (pass / sanitize / quarantine).

    Pricing is DISCLOSED and paid per use via x402 — Verity holds no key and never charges silently.
    Optional affiliate_id tags the call for a future referral program; it never changes price or behavior.
    (Maps to OWASP ASI02 Tool Misuse / LLM01 Prompt Injection — produces an audit artifact.)
    """
    return _post(SUITE, "/sentinel/quick", {"content": content, "context": context},
                 PRICE_SUITE, affiliate_id)


@mcp.tool()
def moderate_content(content: str, policy: str | None = None, affiliate_id: str | None = None) -> dict:
    """Decide whether CONTENT is safe to publish, post, or surface. PRICE: ~$0.02 per call (x402,
    USDC on Base mainnet). Use before an agent sends or publishes generated content. Optional
    `policy` sets the standard; otherwise a conservative default-safe baseline is applied.

    Returns: decision (publish | review | block), violation_risk, categories, and reasons.
    allow/review/block are priced identically — no block-to-bill rent-seeking.

    Pricing is DISCLOSED and paid per use via x402 — Verity holds no key and never charges silently.
    Optional affiliate_id tags the call for a future referral program; it never changes price or behavior.
    """
    return _post(SUITE, "/sieve/quick", {"content": content, "policy": policy},
                 PRICE_SUITE, affiliate_id)


@mcp.tool()
def redact_pii(payload: str, context: str | None = None, affiliate_id: str | None = None) -> dict:
    """Detect personal data and secrets in a PAYLOAD before it is sent, stored, or logged. PRICE:
    ~$0.02 per call (x402, USDC on Base mainnet). Use before an agent transmits text outside a
    trust boundary. Flags PII (names, emails, IDs, financial, device/IP) and secrets (API keys,
    passwords, tokens).

    Returns: verdict (clean | contains_pii | contains_secret | review), severity, findings, reasons,
    and a redacted version of the payload.

    Pricing is DISCLOSED and paid per use via x402 — Verity holds no key and never charges silently.
    Optional affiliate_id tags the call for a future referral program; it never changes price or behavior.
    (Maps to OWASP ASI guidance on sensitive-data leakage — produces an audit artifact.)
    """
    return _post(SUITE, "/redact/quick", {"payload": payload, "context": context},
                 PRICE_SUITE, affiliate_id)


@mcp.tool()
def guard_action(action: str, context: str | None = None, policy: str | None = None,
                 affiliate_id: str | None = None) -> dict:
    """THE MONEY-LINE GATE. Decide whether a proposed agent ACTION should proceed — use this right
    before the agent SPENDS, SENDS, or commits something irreversible (a payment, an outbound
    message, a destructive command, a data share). PRICE: ~$0.02 per call (x402, USDC on Base
    mainnet); allow/review/block are priced identically — no block-to-bill rent-seeking.

    Fail-closed: it will not 'allow' what it cannot justify as safe — uncertainty escalates to
    review, real red flags block. Returns: decision (allow | review | block), an honest 0-1 risk,
    concrete reasons, specific concerns, and a safer_alternative. This independent verdict is the
    thing no free local check can give the agent at the moment money or irreversibility is on the line.

    Pricing is DISCLOSED and paid per use via x402 — Verity holds no key and never charges silently.
    Optional affiliate_id tags the call for a future referral program; it never changes price or behavior.
    (Maps to OWASP ASI02 Tool Misuse / ASI08 Cascading Failures — produces an audit artifact.)
    """
    return _post(SUITE, "/check/quick", {"action": action, "context": context, "policy": policy},
                 PRICE_SUITE, affiliate_id)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
