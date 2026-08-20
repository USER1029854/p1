# Repo conventions — protocol-tier candidate surfacing

This repo is a **candidate-surfacing queue** for protocol-tier contracts on BNB Chain, Ethereum,
Arbitrum, and Base (a triage stage that hands a downstream reviewer contracts worth reading — not
findings). Deliverables: `CANDIDATE_QUEUE.md`, `ADDRESS_BOOK.md` (+ per-run books), `SCAN_REPORT.md`,
`candidates.csv`, and `scanners/` (reproducible, dependency-free on-chain tooling).

## Per-run address-book convention (IMPORTANT — carry this forward)

**Every time the user asks for a new research run, produce a dedicated address book named
`ADDRESS_BOOK_run<N>.md`** capturing the addresses that run surfaced/characterized, AND merge its new
addresses into the cumulative master `ADDRESS_BOOK.md` (latest run appended at the bottom, with a
pointer in the master's per-run index near the top).

- Keep the same clean per-candidate/dossier style (contract · implementation · admin/owner · oracle ·
  markets/pools + underlyings · incident contract/attacker where relevant), and mark how each address
  was obtained (⛓️ on-chain this run / 📄 registry-postmortem / 🔎 to-resolve).
- Number runs in order. Runs so far:
  - **run1** — initial candidate queue (`ADDRESS_BOOK_run1.md`)
  - **run2** — multi-condition rerun; families K–N (`ADDRESS_BOOK_run2.md`)
  - **run3** — full resolved per-candidate dossier (`ADDRESS_BOOK_run3.md`)
  - **run4** — programmatic wide computed scan (`ADDRESS_BOOK_run4.md`)
  - **the next discovery run is run5 → create `ADDRESS_BOOK_run5.md`.**
- A run that only reorganizes/asks meta-questions (like setting up this convention) is **not** a new
  numbered discovery run — don't bump the counter for it.

## Other working conventions

- Develop on branch `claude/protocol-contract-surfacing-sg0eil`; commit + push each run.
- Never commit the Etherscan/Blockscout API keys — `scanners/chain.py` reads `ETHERSCAN_V2_KEY` from env.
- On-chain data channels: Etherscan V2 free tier covers **Ethereum, Arbitrum, Polygon** only; **Base**
  via Blockscout; **BNB** via Sourcify + public RPC (the standing explorer gap). Public RPC works for
  `eth_call`/storage/code/logs on all four.
- Precision discipline: a failed/rate-limited read must never be counted as `0` (see the ghost bug in
  `SCAN_REPORT.md` §1); confirm standing approvals with a **current `allowance` read**, not event volume.
