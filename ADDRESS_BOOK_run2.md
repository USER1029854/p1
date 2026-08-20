# Address Book — Run 2 (multi-condition rerun)

Per-run address book. Scope: the on-chain anchors **added in Run 2** — the convergence-scoring rerun
that introduced families K–N (perp/GMX-fork vaults, KiloEx forwarder+feed, LST/LRT mint+NAV, SYMM
intent-perp) in `CANDIDATE_QUEUE.md` (commit `9c9d296`). ⛓️ read on-chain 2026-08-20.

| Protocol | Chain | Role | Address | Created | Note |
|---|---|---|---|---|---|
| GMX V1 | ARB | `Vault` (GLP-fork fingerprint) | `0x489ee077994B6658eAfA855C308275EAd8097C4A` | 2021-08-31 | reference to bytecode-match forks (BMX/Vela/Level/EDE); July-2025 mark-price/reentrancy lineage |
| Cream Finance | ETH | CRETH2 / CreamETH2 LST | `0xcBc1065255cBc3aB41a6868c22d1f1C573AB89fd` | 2020-11-18 | abandoned Cream LST, mint authority, ~$1.58M; `owner()` null → resolve minter |

Run 2 was primarily analytic (scoring rubric + stacked leaderboard + families K–N); most family
members were handed over as entry points to resolve rather than fully addressed — see
`CANDIDATE_QUEUE.md` §K–N. The two anchors above are the addresses newly confirmed on-chain that run.
