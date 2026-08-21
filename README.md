# Protocol-Tier Candidate Surfacing

This repo holds the output of a **surfacing / triage** pass over live protocol contracts on
**BNB Chain, Ethereum, Arbitrum, and Base**. The goal of the pass is to hand a downstream stage a
**candidate queue** — contracts worth reading in full — not findings. Nothing here is audited,
simulated, or proven exploitable; that is the next stage's job.

## Deliverable

- **[`AUDIT_TARGETS.md`](./AUDIT_TARGETS.md)** — **start here.** One consolidated, prioritized,
  audit-ready worksheet: each row is a contract address + the exact vulnerability hypothesis to check.
  Pick a target, load the address, start auditing.
- **[`AUDIT_SCOPE.md`](./AUDIT_SCOPE.md)** — the **full source-bearing surface per target**
  (entry, implementation, upgrade authority, oracle/minter/vault, dependencies). Scope is never one
  address — the MAYAChain drain chained 6 bugs across 6 files; audit the whole interacting surface.
- **[`CANDIDATE_QUEUE.md`](./CANDIDATE_QUEUE.md)** — the reasoning: candidates grouped into systems and
  families (by shared codebase / fork lineage), each flagged by the exact shape that caught it.
- **[`ADDRESS_BOOK.md`](./ADDRESS_BOOK.md)** — the deeper cumulative address reference the worksheet
  points into: for each grounded candidate, every useful address (contract, implementation, admin/
  owner, oracle, markets/pools + underlyings, incident contract + attacker), marked
  ⛓️ resolved-on-chain / 📄 from-registry / 🔎 to-resolve.
- **[`SCAN_REPORT.md`](./SCAN_REPORT.md)** — a programmatic wide-scan pass that *computes* authority
  on-chain (standing-approval authority + live-allowance confirmation, cross-chain bytecode
  fingerprinting, impl-age/verification divergence, empty-market surface). Headline: dead/deprecated/
  exploited contracts (Multichain, KyberSwap-old, 1inch-v4, dYdX-v1, SwapNet) that still hold
  **confirmed-live infinite approvals** from hundreds of wallets — zero balance, live drain surface.
- **[`at_risk_protocols.csv`](./at_risk_protocols.csv)** — run-4 breadth: **379 live, funded, mostly-
  unaudited protocols** on the four chains, ranked by profile-risk (unaudited + fresh + high-risk
  category + multi-chain). The prevention universe to work through (conversion ~1–3%).
- **[`candidates.csv`](./candidates.csv)** — earlier machine-readable register (chain, address, family,
  shapes, condition score, authority status, prior incident, disclosure).
- **[`scanners/`](./scanners/)** — the reproducible, dependency-free scanner tooling (pure-Python
  Keccak, hardened multi-chain reader, authority-concentration + source dangerous-pattern scanners).

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
