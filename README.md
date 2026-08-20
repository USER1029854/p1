# Protocol-Tier Candidate Surfacing

This repo holds the output of a **surfacing / triage** pass over live protocol contracts on
**BNB Chain, Ethereum, Arbitrum, and Base**. The goal of the pass is to hand a downstream stage a
**candidate queue** — contracts worth reading in full — not findings. Nothing here is audited,
simulated, or proven exploitable; that is the next stage's job.

## Deliverable

- **[`CANDIDATE_QUEUE.md`](./CANDIDATE_QUEUE.md)** — the queue. Candidates are grouped into systems
  and families (by shared codebase / fork lineage), each flagged by the exact shape that caught it,
  with on-chain-confirmed anchors where reachable and honestly-named gaps where not.

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
