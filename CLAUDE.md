# Repo conventions — protocol-tier candidate surfacing

This repo is a **candidate-surfacing queue** for protocol-tier contracts on BNB Chain, Ethereum,
Arbitrum, and Base — a triage stage that hands a downstream auditor contracts worth reading (not
findings). The user takes a contract address from here and starts an audit.

## Deliverable layout (keep this shape)

- **`AUDIT_TARGETS.md`** — THE start-here file: one consolidated, prioritized, audit-ready worksheet.
  Each row = a contract address + the exact vulnerability hypothesis to check. This is what the user
  opens to begin auditing.
- **`AUDIT_SCOPE.md`** — the full source-bearing contract surface to load per target (impl, upgrade
  authority, oracle/minter/vault, deps). Scope the whole surface, not one address (the MAYAChain lesson).
- **`ADDRESS_BOOK.md`** — cumulative address reference the worksheet points into (every grounded
  candidate; latest run merged at the bottom).
- `CANDIDATE_QUEUE.md` — families/shapes reasoning · `SCAN_REPORT.md` — the on-chain scan writeup ·
  `at_risk_protocols.csv` — the 379-protocol ranked universe (run4) · `candidates.csv` — earlier
  register · `scanners/` — reproducible, dependency-free on-chain tooling.

## Run convention (IMPORTANT — carry forward)

- **Runs so far = 4 discovery runs:** run1 = initial candidate queue; run2 = multi-condition rerun
  (families K–N); run3 = programmatic wide + precise scan (approval-authority live-confirmation,
  bytecode fingerprint, impl-age); run4 = **fresh & at-risk, prevention-first** — pivoted away from
  already-hacked/deprecated contracts to live/funded/unaudited/complex-mechanic protocols; built the
  authority-concentration + source dangerous-pattern scanners; produced `at_risk_protocols.csv` (379
  ranked candidates). **The next discovery run is run5.**
- User steer (carry forward): **do not over-index on already-hacked contracts** — the prevention value
  is in live, unexploited, under-reviewed protocols. Give **volume** (conversion is ~1–3%). Think for
  yourself about what makes a protocol risky (authority concentration, fresh unaudited complex money
  math, keeper/caller-settable pricing, mint authority, upgrade risk, unverified code), not just the
  fixed shape catalog.
- A follow-up that only reorganizes or asks a meta-question is **not** a numbered discovery run.
- **On each new run: refresh `AUDIT_TARGETS.md` (re-prioritized, latest first) and merge the run's new
  addresses into `ADDRESS_BOOK.md`.** Keep it to these living files (+ `at_risk_protocols.csv` /
  `candidates.csv`) — do **not** create per-run snapshot files (`ADDRESS_BOOK_runN.md`); confusing.

## Working conventions

- Develop on branch `claude/protocol-contract-surfacing-sg0eil`; commit + push each run.
- Never commit the Etherscan/Blockscout API keys — `scanners/chain.py` reads `ETHERSCAN_V2_KEY` from env.
- On-chain data channels: Etherscan V2 free tier covers **Ethereum, Arbitrum, Polygon** only; **Base**
  via Blockscout; **BNB** via Sourcify + public RPC (the standing explorer gap). Public RPC does
  `eth_call`/storage/code/logs on all four.
- Precision discipline: a failed/rate-limited read must never be counted as `0` (see the ghost bug in
  `SCAN_REPORT.md` §1); confirm standing approvals with a **current `allowance` read**, not event volume.
