# Protocol-Tier Candidate Surfacing

This repo holds the output of a **surfacing / triage** pass over live protocol contracts on
**BNB Chain, Ethereum, Arbitrum, and Base**. The goal of the pass is to hand a downstream stage a
**candidate queue** — contracts worth reading in full — not findings. Nothing here is audited,
simulated, or proven exploitable; that is the next stage's job.

## Deliverable

- **[`CANDIDATE_QUEUE.md`](./CANDIDATE_QUEUE.md)** — the queue. Candidates are grouped into systems
  and families (by shared codebase / fork lineage), each flagged by the exact shape that caught it,
  with on-chain-confirmed anchors where reachable and honestly-named gaps where not.
- **[`ADDRESS_BOOK.md`](./ADDRESS_BOOK.md)** — cumulative per-candidate address dossier: for each
  grounded candidate, every useful address (contract, implementation, admin/owner, oracle, markets/
  pools and their underlyings, plus incident contract + attacker for the exploited entries), each
  marked ⛓️ resolved-on-chain / 📄 from-registry / 🔎 to-resolve, with the exact selector to reproduce
  it. **Each run also has its own frozen snapshot** — `ADDRESS_BOOK_run1.md` (initial anchors),
  `ADDRESS_BOOK_run2.md` (GMX Vault, CRETH2), `ADDRESS_BOOK_run3.md` (full resolved dossier),
  `ADDRESS_BOOK_run4.md` (wide computed scan) — and every future run adds `ADDRESS_BOOK_run<N>.md`
  (convention recorded in `CLAUDE.md`).
- **[`SCAN_REPORT.md`](./SCAN_REPORT.md)** — a programmatic wide-scan pass that *computes* authority
  on-chain (standing-approval authority + live-allowance confirmation, cross-chain bytecode
  fingerprinting, impl-age/verification divergence, empty-market surface). Headline: dead/deprecated/
  exploited contracts (Multichain, KyberSwap-old, 1inch-v4, dYdX-v1, SwapNet) that still hold
  **confirmed-live infinite approvals** from hundreds of wallets — zero balance, live drain surface.
- **[`candidates.csv`](./candidates.csv)** — machine-readable register (chain, address, family, shapes,
  condition score, authority status, prior incident, disclosure).
- **[`scanners/`](./scanners/)** — the reproducible, dependency-free scanner tooling (pure-Python
  Keccak, hardened multi-chain reader, and the five scanners) so the next stage can re-run and extend.

The queue is scored for **convergence** (see §0.5): the strongest candidates trip *more than one*
independent condition on the same fund path — two+ catalog shapes stacked, plus authority type(s),
age extremity, a readability gap, a prior-incident lineage, and cross-chain replication. Every recent
protocol-tier drain reconstructed here was a stack, not a single bug, so the top of the queue is a
condition-count leaderboard rather than a TVL ranking.

## How candidates were ranked

- **Authority, not balance** — a zero-balance contract can be the most drainable thing on the chain
  when standing approvals, a mint role, or a registry write is pointed at it.
- **Unwatched, not unaudited** — fame / TVL / a live bounty / a recent audit mean many eyes already
  looked; the signal is a deployed contract-and-state nobody has re-checked. For every watched
  protocol, the candidate is the obscure fork or the long-tail market.
- **One hop to the mover** — resolve proxy→impl (aging the impl separately), factory→instance,
  oracle/registry→the contract that moves funds on its word.
- **Both age humps** — fresh code with new bugs, and ancient deprecated-but-funded code left running.

## Data channels used

Etherscan V2 (Ethereum/Arbitrum), Blockscout (Base), Sourcify + public RPC (BNB Chain), DefiLlama
public API, and public post-mortems. Everything read is public on-chain data. The BNB Chain
explorer gap and the new-deployment firehose are the two biggest structural limits — both are named
explicitly in the queue.
