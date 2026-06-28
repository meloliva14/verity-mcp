# Verity MCP — the agent economy's "verify before you spend/send/trust" gate

One [Model Context Protocol](https://modelcontextprotocol.io) server that exposes Verity's fail-closed trust checks as tools any MCP-capable agent can discover and call: `verify_fact`, `detect_injection`, `moderate_content`, `redact_pii`, `guard_action`. Backed by Verity's live HTTP+x402 services on Base mainnet. Verity holds **no private key**.

## The strategy this implements (and why)

The trust/safety slot in the agent economy is **unowned** — Coinbase's x402 Bazaar has no trust category; Visa/Mastercard agent-payment specs verify payment *scope*, not content safety; the one security player covers payment-fraud, not fact-checking / moderation / PII. This MCP server is the cheapest, first way to occupy that slot.

**The money model (corrected — do NOT bill per loop):**
- **The everywhere-gate is free.** Agents will never pay per-call for a check a local model does for $0. The free, self-hostable gate is top-of-funnel, not the product.
- **Charge at the money line.** The paid value is `guard_action` (and a verified `verify_fact`) used right before the agent **spends, sends, or commits something irreversible** — where an independent, *signed* verdict is worth far more than the sub-cent fee, and where billing rides a payment the agent already consented to. That's the only slot worth paying a third party for.

## Disclosure discipline (non-negotiable — keeps the auto-pay legitimate)

A trust product cannot use a wallet-draining dark pattern. Every distribution surface and the tool descriptions MUST state, up front:
- **The per-call price**, and that calls are paid per use.
- A **free quota** that covers real evaluation before any wallet signs.
- **Explicit operator opt-in** before the x402 wallet auto-pays anything — never silent.
- A **visible running spend** signal and a documented **kill-switch**.
- **allow / review / block are priced identically** (never charge more to "block" — no block-to-bill rent-seeking).
- Honest claims only: "**maps to** OWASP ASI control X" and "produces an audit artifact" — **never** "OWASP-compliant," "endorsed by," or "shifts your liability."

## Honest reality (read before betting the timeline on this)

The real (wash-filtered) x402 service economy is **small today** — order ~$28K/day ecosystem-wide, top single earner ~$25K/mo. So: **occupying this slot cheaply and first is high-probability and nearly free; near-term per-call revenue is thin.** The big numbers come later, from monetizing the trust position at higher tickets (money-line checks on high-value flows, "Verified by Verity" certification, enterprise) as agent-commerce grows — not from micro-payments in a thin niche. This server captures the position regardless of how fast the volume arrives.

## Run locally

```bash
pip install -r requirements.txt
python server.py            # stdio MCP server
```
Env: `VERITY_SUITE_URL` (default https://verity-suite.onrender.com), `VERITY_ENGINE_URL` (default https://verity-bzw7.onrender.com).

## Publish sequence (the free land-grab — order matters)

1. **CDP / x402 Bazaar** — route through the CDP facilitator + declare the Bazaar discovery extension; **auto-indexes on the first settled payment**. (The live HTTP services already do this; the MCP layer rides it.) *Needs: one real settled payment to index; re-call ≥ every 30 days.*
2. **Official MCP Registry** (`registry.modelcontextprotocol.io`, `mcp-publisher` CLI) — the meta-registry Smithery/Glama/PulseMCP/mcp.so crawl downstream. **Publish here before third-party directories.** *Needs: GitHub-OAuth + reverse-DNS namespace.*
3. **x402scan** self-serve register · **x402.org "Security & Risk Management"** category (near-empty — land-grab) · **402 Index** (domain-verify).
4. **Client-native directories:** Anthropic Claude Connectors Directory, OpenAI ChatGPT Apps, Cline MCP Marketplace. *Need: OAuth + truthful tool annotations + privacy policy + examples.*
5. **Backlink PRs:** `punkpeye/awesome-mcp-servers`, `Merit-Systems/awesome-x402` (Security & Ops), `xpaysh/awesome-x402`.

## Status / what's next

- [x] MCP server + 5 tools + honest descriptions (this repo).
- [ ] **x402-over-MCP payment wiring** — bridge so the agent's x402 client settles the disclosed micro-payment at the MCP layer (careful, tested-without-burning-budget before publish).
- [ ] Strict JSON Schemas + 3 working examples per tool (registry requirement).
- [ ] Publish to the registries above (several need Mel's accounts/OAuth).
- [ ] Free, self-hostable "everywhere-gate" package as top-of-funnel.

*Independent · fail-closed · keyless · pay-per-call. The only trust form an autonomous agent can pick up mid-task with no human and no account.*
