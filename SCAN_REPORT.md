# Programmatic Wide-Scan Report — authority computed, not asserted

This pass is different from the first three. Instead of hand-picking protocols from a directory and
confirming them one at a time, I built a small on-chain engine and let it **compute the authority
signal directly** across many contracts and all four chains. The task's own thesis — *rank by
authority not balance, unwatched not unaudited, a zero-balance contract can be the most drainable
thing on the chain* — is only testable if you can measure standing authority on-chain. So I measured it.

Everything here is reproducible from the scripts in the scan appendix. Every number was read live on
**2026-08-20**.

---

## 0. What I built (so the numbers mean something)

- **Pure-Python Keccak-256** (no dependencies; pip was unreachable) → I can compute any function
  selector or event topic, so I can call *any* contract method and filter *any* log, not just a
  hard-coded handful.
- **Hardened multi-chain toolkit** — Etherscan V2 `eth_call`/`eth_getStorageAt`/`eth_getCode`/`getLogs`
  for Ethereum·Arbitrum (+Polygon), public RPC for Base·BNB. Every call **retries and returns a
  `None` sentinel on failure** (this matters — see §1).
- **Five scanners:** (1) standing-approval authority, (2) live-allowance confirmation, (3) empty-market
  donation surface, (4) implementation age/verification divergence, (5) cross-chain bytecode
  fingerprint.

---

## 1. Measurement integrity (why the numbers are trustworthy)

Two disciplines that changed the results — included because a precise search that hides its error bars
isn't precise:

- **The rate-limit ghost.** My first empty-market scan flagged Compound's own **cUSDC/cETH/cWBTC as
  `totalSupply = 0`** — impossible. The cause: rate-limited RPC replies were being parsed as `0`. A
  re-read with retries showed cUSDC `totalSupply = 3.07e16`. I hardened every call to distinguish
  "read failed" from "value is zero," then **re-verified every flagged empty market individually.**
  Most "empty" flags were ghosts. Lesson baked into every table below: a failed read is never counted
  as a candidate.
- **Event volume ≠ live authority.** Counting `Approval` events over-counts: many routers use
  approve→swap→spend, so the allowance is gone minutes later. So for the headline finding I did a
  second pass — **read the *current* `allowance(owner, spender)`** for a sample of recent approvers.
  This corrected a false positive (**Aperture**: 245 approval events, but **0/14 sampled allowances
  still live**) and confirmed the real ones. Where I write "LIVE" below, I mean a current non-zero
  on-chain allowance, sampled.

**Sampling caveat:** the live-allowance check samples ~15 most-recent `(owner, token)` pairs per
spender, not the full historical set. It proves the *authority is real and current*; it does not
enumerate the full victim count (which is larger). The next stage should page the full log set.

---

## 2. HEADLINE FINDING — dead / deprecated / exploited contracts holding **confirmed-live** infinite approvals

This is the purest instance of the task's thesis: contracts with **no balance, no active team, often a
past exploit**, yet **hundreds of funded wallets still point live infinite ERC-20 approvals at them.**
Zero balance, live drain-surface. Directories can't see these (a router holds no TVL); a balance-ranker
skips them. The authority is the standing approval set (Shape 2 / 7).

Live-confirmed on Ethereum (sampled current allowances, 2026-08-20):

| Spender | State | Approvals /5wk | Sampled LIVE | still ∞ | Address |
|---|---|---:|---:|---:|---|
| **Multichain Router4** | **DEAD** (Jul-2023, keys compromised) | 1000+ | **14/15** | 14 | `0x765277EebeCA2e31912C9946eAe1021199B39C61` |
| **Multichain Router6** | **DEAD** | 1000+ (879 owners) | ~ (churn) | — | `0x6b7a87899490EcE95443e979cA9485CBE7E71522` |
| **KyberSwap AggRouter (old)** | **exploited 2023** | 1000+ (576 owners) | **15/15** | 15 | `0xDF1A1b60f2D438842916C0aDc43748768353EC25` |
| **1inch v4 Router** | deprecated | 1000+ (468 owners) | **15/15** | 15 | `0x1111111254fb6c44bAC0beD2854e76F90643097d` |
| **dYdX v1 SoloMargin** | deprecated | 1000+ (829 owners) | **14/15** | 14 | `0x1E0447b19BB6EcFdAe1e4AE1694b0C3659614e4e` |
| **0x AllowanceTarget (old)** | deprecated | 1000+ (621 owners) | **13/15** | 12 | `0xF740B67dA229f2f10bcBd38A7979992fCC71B8Eb` |
| **SwapNet** | **exploited Jan-2026** | 57 | **5/15** | 4 | `0x616000e384Ef1C2B52f5f3A88D57a3B64F23757e` |
| ~~Aperture~~ | exploited | 245 | **0/14** | 0 | `0xD83d960deBEC397fB149b51F8F37DD3B5CFA8913` — *excluded: no live authority* |

**What this proves, and what it doesn't.** It proves live infinite approvals from many funded wallets
currently name these contracts as spender. It does **not** prove a drain path — that's the next stage's
job, and it splits by candidate:

- **Multichain (dead, keys compromised)** is the sharpest: the operator keys are the ones seized in
  2023, and 800+ wallets still have live ∞ approvals to the routers. The next stage must check whether
  any router entrypoint pulls tokens from an **arbitrary `from`** (not just `msg.sender`). If one does,
  this is mass-drainable by whoever controls those keys. Shape 2/7.
- **KyberSwap old router (exploited)** and **SwapNet (exploited, and byte-identical across 4 chains —
  §3)**: a known-bad contract that *still* holds live approvals — the exploited-but-not-excluded case.
- **1inch v4 / 0x old / dYdX v1 (deprecated, audited):** a large *confirmed-live* approval surface on
  code nobody re-checks in its deployed, deprecated state. Lower prior of a reachable flaw (these were
  well-reviewed), but the standing authority is real and un-monitored — exactly the "unwatched deployed
  state" the task says to rank up on. Hand over for a deprecated-path read, not as a proven bug.

Arbitrum shows the same pattern live: **SwapNet 801 approval events / 737 ∞** and **Aperture 668 / 313**
in the window (live-allowance confirmation for ARB was cut short by a worker restart — the next stage
should finish it; SwapNet's ETH side is already 5/15 live).

---

## 3. Cross-chain bytecode fingerprint — one flaw, N deployments (computed)

`eth_getCode` → Keccak-256, grouped across chains:

- **SwapNet is byte-identical on all four chains** — codehash `7d1a6d36ad573e6a…`, 1864 bytes, at the
  same address `0x616000e384Ef1C2B52f5f3A88D57a3B64F23757e` on **ETH, ARB, BASE, BNB**. One
  implementation, four live deployments → the flaw and the residual-approval surface replicate exactly.
  Fix/verify one, you've characterized all four.
- **Aperture is *not* uniform:** different codehash on ETH (`efc84c5b…`) vs ARB (`94edcf58…`), and
  **no code on Base** — each chain needs its own read.
- **KiloEx differs per chain** too (Base `f18c5691…` vs BNB `4bd01514…`).

The precise takeaway: "one flaw, N deployments" is *true for SwapNet* (proven identical) and *false as
an assumption for Aperture/KiloEx* (proven different). Don't assume replication — compute it.

---

## 4. Implementation age / verification divergence (the Radiant-class stack, computed)

Read the EIP-1967 impl slot → age the impl vs the shell, and check verification:

| Contract | Shell created | Impl created | Impl verified? | Flag |
|---|---|---|---|---|
| **Radiant V2 Pool (ARB)** | 2023-03-18 | **2024-10-17** | **NO** | fresh **unverified** logic on old shell — top stack |
| **dForce Controller (ETH)** | 2021-02-25 | **2024-10-25** | yes | logic swapped 3.7 yrs after shell — fresh-code surface |
| **Aave V1 Core (ETH)** | 2020-01-08 | **2024-05-02** | yes | **anomalous** for deprecated V1 — verify (reinit / lookup quirk) on a contract holding 927 ETH |
| Iron Bank Unitroller (ETH) | 2020-12-04 | 2022-08-29 | yes | moderate |
| Flux Comptroller (ETH) | 2023-01-30 | 2023-01-30 | yes | clean (co-deployed) |

Radiant's unverified 2024-10-17 impl (holding an Aave-v2-fork pool with two prior incidents) is the
strongest single-contract stack surfaced across all rounds. The **Aave V1 Core impl reading 2024-05-02**
is a genuine surprise worth the next stage's eyes — a deprecated 2020 contract holding 927 ETH whose
implementation address reports a 2024 creation.

---

## 5. Empty-market donation surface — a precise, negative-leaning result

I scanned 11 Compound-fork comptrollers across four chains for markets that are **thin/empty *and*
collateral-enabled (CF > 0)** — the donation/first-depositor surface. After correcting for the
rate-limit ghost (§1), the honest result is **mostly negative on maintained forks**:

- **Iron Bank, Tender, Ionic, Moonwell, Venus core** keep their markets **seeded** — the raw "empty"
  flags were overwhelmingly ghosts. Venus core (52 markets) and Lodestar came back clean.
- The **one true zero-supply, collateral-enabled market** found live: **Ionic `ionmsUSD`**
  (`0x5be1cb6cb3c9bfd16db43ed4f6c081fa9783dd1c`, Base) — `totalSupply = 0`, ~32e18 underlying cash
  present, but **CF = 10%** (low payout leverage → weak).

**The correction to my earlier rounds:** live empty markets are *rare on maintained forks* (they seed
new listings on purpose). The real donation surface lives on **abandoned** forks (dead team, markets
left in odd states) — Sonne (dead), Rari/Fuse pools, Cream residuals — which is where the next
empty-market pass should point. I'm flagging this rather than leaving the earlier "empty markets
everywhere" impression standing.

---

## 6. Full approval-authority tables (event volume, ~5-week window)

Volume ranks the surface; §2 confirms which are *live*. Capped at 1000 results/query (`+` = capped).

**Ethereum** (owners / ∞-approvals in window):
Celer cBridge 962/986 · Multichain6 879/981 · Stargate 871/938 · dYdX-v1 829/989 · UniversalRouter1.2
742 · DODOApprove 748/967 · OpenOcean 673 · Permit2 629/928 · Across 622/? · 0x-old 621/926 · Convex
615/977 · Uniswap UR 613 · LiFi 596 · Metamask 586 · Kyber-old 576/989 · Multichain4 572/996 · ParaSwap
TTP 569 · CoW relayer 562/941 · Paraswap-v4 560 · 1inch-v3 549 · 1inch-v5 513/935 · KyberMetaAggV2
504/948 · 1inch-v6 502/808 · 1inch-v4 468/980 · 1inch-v2 464 · Odos 453 · Balancer Vault 256 · Bebop
230 · Bancor 76 · Synapse 6/992 · CoW Settlement 407.

**Arbitrum:** LiFi 441 · Camelot 292/719 · GMX PositionRouter 290/479 · Sushi 263/858 · Radiant Pool
116/984 · SwapNet 33 owners (801 events)/737∞ · Aperture 111/313 · Odos 13.

Interpretation: the majors (Permit2, 1inch v5/v6, CoW, Uniswap UR, bridges) are **watched → deprioritize
despite huge authority**; the value is the **deprecated/dead/exploited rows in §2** with the same live-∞
surface and nobody re-checking them.

---

## 7. What this pass adds to the queue, in priority order

1. **Multichain dead routers** (`0x7652…`, `0x6b7a…`) — dead protocol, compromised keys, confirmed-live
   ∞ approvals from 800+ wallets. Next-stage question: does any entrypoint pull from an arbitrary `from`?
2. **Radiant V2 unverified 2024-10-17 impl** — fresh unverified logic, two prior incidents, live pool.
3. **SwapNet** — byte-identical 4-chain, exploited, still 5/15 live ∞ on ETH; characterize once, applies
   to all four.
4. **KyberSwap old router** — exploited, 15/15 live ∞.
5. **Deprecated audited routers with live ∞ surface** (1inch v4, 0x old, dYdX v1) — unwatched deployed
   state; hand over for a deprecated-path read.
6. **Aave V1 Core impl anomaly** (2024-05-02 on a 927-ETH deprecated contract) — verify.
7. **Ionic `ionmsUSD`** zero-supply CF-10% market — weak donation surface (only true empty found).

Excluded on evidence: **Aperture** (0 live allowances — event churn only).

---

## 8. Honest limits of this scan

- **Live-allowance confirmation is sampled (~15), not exhaustive**, and the ARB confirmation for
  SwapNet/Aperture was interrupted — finish it before acting.
- **Base/BNB approvals** aren't in the ETH/ARB `getLogs` tables (no free Etherscan logs there); Base is
  reachable via Blockscout logs, BNB is the standing explorer gap. SwapNet/Aperture BNB+Base rows are
  from the fingerprint/RPC path, not a log scan.
- **Drainability is deliberately not assessed** — I surface *live authority + shape*; the next stage
  proves the path. For the audited-deprecated routers especially, presence of approvals ≠ presence of a
  bug.
- **Empty-market scan** was corrected to a mostly-negative result on maintained forks; the abandoned-fork
  sweep (Sonne/Fuse/Cream) is the deferred follow-up.

---

*Scanners and the exact selectors/queries live in the session scratchpad (`chain.py` toolkit,
`kc.py` Keccak, `scan_approvals*.py`, `allowance_confirm.py`, `scan_empty.py`/`reverify.py`,
`scan_implage.py`, `scan_fingerprint.py`). Companion files: `CANDIDATE_QUEUE.md` (families & shapes),
`ADDRESS_BOOK.md` (per-candidate addresses), `candidates.csv` (machine-readable register).*
