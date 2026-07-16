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

That gets you the tools and the **free** `verify_receipt`. To get **paid verdicts**, read the next section — it's the part most people trip on.

## How payment works

Verity's endpoints answer **HTTP 402 (Payment Required)** until the disclosed USDC micro-payment is settled. There are two ways to do that.

### Wallet mode — get real verdicts (recommended)

```json
{
  "mcpServers": {
    "verity": {
      "command": "uvx",
      "args": ["--from", "verity-mcp[x402]", "verity-mcp"],
      "env": { "VERITY_WALLET_KEY": "0x…" }
    }
  }
}
```

Point `VERITY_WALLET_KEY` at a **funded Base-mainnet wallet** and this server settles each call itself — the paid tools return real verdicts. Your key never leaves the process: it signs an EIP-3009 authorization locally for the exact amount each challenge discloses, and Verity only ever receives the signature. Nothing is charged silently; every price is disclosed up front.

> **Use a dedicated, low-balance wallet.** This key can spend. Fund it with a few dollars of USDC on Base — calls cost $0.02–$0.35.

### Keyless — the default

With no key set, this server holds nothing and pays nothing: a 402 is surfaced transparently (price restated, challenge attached) for an x402-capable caller to settle.

**Be aware of the honest caveat:** no shipping MCP client — Claude Desktop, Claude Code, Cursor, Windsurf — settles x402 today. So in keyless mode the paid tools will return `payment_required` and **no verdict**, forever. That's not a bug and it isn't hidden: the response says `NO VERDICT WAS PRODUCED. Do not proceed as if this returned allow.` If you want verdicts from an ordinary MCP client, use wallet mode.

`verify_receipt` is a free route, never 402s, and needs no wallet — you can check our signatures before you ever pay us.

## Signed receipts — don't take Verity's word for it

Every paid verdict ships with an **Ed25519-signed receipt**: self-contained cryptographic proof of exactly what Verity said about exactly what claim, verifiable forever. Check any receipt free with the `verify_receipt` tool, offline against the public key at [`/.well-known/verity-pubkey.json`](https://api.veritylayer.dev/.well-known/verity-pubkey.json), or live: `curl https://api.veritylayer.dev/receipt/selftest`.

## Configuration (all optional)

| Env var | Default | Purpose |
|---|---|---|
| `VERITY_WALLET_KEY` | *(unset — keyless)* | **Optional.** Private key of a funded Base wallet. Set it (with the `[x402]` extra) and this server settles its own payments, so paid tools return real verdicts. Never leaves the process; never logged. |
| `VERITY_ENGINE_URL` | `https://api.veritylayer.dev` | Flagship claim-verification engine |
| `VERITY_SUITE_URL` | `https://suite.veritylayer.dev` | Trust-check suite (injection/moderation/PII/guardrail) |
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
