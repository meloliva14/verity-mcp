mcp-name: io.github.meloliva14/verity-mcp

# Verity MCP — verify before you act

The official [Model Context Protocol](https://modelcontextprotocol.io) server for [VerityLayer](https://veritylayer.dev): independent, fail-closed trust checks any MCP-capable agent can discover and call. Fact-check a claim, screen for prompt-injection, catch PII, and gate irreversible actions — each check returns a calibrated verdict and **abstains rather than guess**. Payment is pay-per-call via [x402](https://docs.x402.org) (USDC on Base mainnet). Verity holds **no private key** and never charges silently.

> **Name note:** this is VerityLayer's official server — PyPI package `verity-mcp`, npm package [`@veritylayer/mcp`](https://www.npmjs.com/package/@veritylayer/mcp). The *npm* package named `verity-mcp` is an unrelated third-party project.

## Tools & pricing (every docstring states its price up front)

| Tool | Price | Grounded? | What it's for |
|---|---|---|---|
| `quick_verify` | **$0.02** | no (Haiku) | Cheap reality-check on a claim — **the loopable default**. Run everywhere, escalate the load-bearing ones. |
| `grounded_verify` | **$0.25** | yes (Sonnet, live web citations) | The default product — web-grounded with cited evidence, for facts that matter before you act on them. |
| `pro_verify` | **$0.35** | yes (Opus, premium synthesis) | The deepest tier — high-stakes claims where the grounded answer isn't confident enough to act on. |
| `verify_receipt` | **free** | — | Statelessly verify a signed Ed25519 verdict receipt — the audit trail / second opinion, no payment. |
| `detect_injection` | $0.02 | — | Screen untrusted text / tool output for prompt-injection before acting on it. |
| `moderate_content` | $0.02 | — | Is this safe to publish? (allow / review / block priced identically — no block-to-bill.) |
| `redact_pii` | $0.02 | — | Does this leak PII or secrets? Returns findings + a redacted version. |
| `guard_action` | $0.02 | — | **The money-line gate:** allow / review / block right before an irreversible action. |

## Quickstart

With [uv](https://docs.astral.sh/uv/) (recommended — Claude Desktop / any MCP client):

```json
{
  "mcpServers": {
    "verity": {
      "command": "uvx",
      "args": ["verity-mcp"]
    }
  }
}
```

Or with pip:

```bash
pip install verity-mcp
verity-mcp        # stdio MCP server
```

## How payment works

Verity's endpoints answer **HTTP 402 (Payment Required)** until paid. When a tool call hits a 402, this server surfaces it transparently — price restated, x402 challenge attached — so your x402-capable client or proxy can settle the small, disclosed USDC micro-payment and retry. This server never holds a key and never pays on your behalf. `verify_receipt` is a free route and never 402s.

## Signed receipts — don't take Verity's word for it

Every paid verdict ships with an **Ed25519-signed receipt**: self-contained cryptographic proof of exactly what Verity said about exactly what claim, verifiable forever. Check any receipt free with the `verify_receipt` tool, offline against the public key at [`/.well-known/verity-pubkey.json`](https://api.veritylayer.dev/.well-known/verity-pubkey.json), or live: `curl https://api.veritylayer.dev/receipt/selftest`.

## Configuration (all optional)

| Env var | Default | Purpose |
|---|---|---|
| `VERITY_ENGINE_URL` | `https://api.veritylayer.dev` | Flagship claim-verification engine |
| `VERITY_SUITE_URL` | `https://verity-suite.onrender.com` | Trust-check suite (injection/moderation/PII/guardrail) |
| `VERITY_TIMEOUT` | `90` | HTTP timeout (seconds) |
| `VERITY_PRICE_QUICK` | `$0.02` | Disclosed price echo for `quick_verify` |
| `VERITY_PRICE_GROUNDED` | `$0.25` | Disclosed price echo for `grounded_verify` |
| `VERITY_PRICE_PRO` | `$0.35` | Disclosed price echo for `pro_verify` |
| `VERITY_PRICE_SUITE` | `$0.02` | Disclosed price echo for the suite checks |

## Referral tag (reserved)

Every tool accepts an optional `affiliate_id`, forwarded as an `X-Verity-Ref` header. It never changes price, gating, or the verdict — it only tags who routed the call, and it is **reserved for a future referral program**: no split is paid today, and none will be until public terms are published at veritylayer.dev.

## Links

- Website: https://veritylayer.dev · Manifesto: https://veritylayer.dev/manifesto/
- Live API + discovery: https://api.veritylayer.dev/llms.txt · [`/.well-known/x402.json`](https://api.veritylayer.dev/.well-known/x402.json)
- npm client: [`@veritylayer/mcp`](https://www.npmjs.com/package/@veritylayer/mcp)
- Contact: veritylayer@gmail.com

*Independent · fail-closed · keyless · pay-per-call. The only trust form an autonomous agent can pick up mid-task with no human and no account.*
