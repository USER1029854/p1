# Address Book — Run 4 (programmatic wide computed scan)

Per-run address book. Scope: the addresses **surfaced or newly characterized in Run 4** — the
`SCAN_REPORT.md` pass that computed authority on-chain (standing-approval authority + live-allowance
confirmation, cross-chain bytecode fingerprint, impl-age/verification). All read live **2026-08-20**.
Companion: `SCAN_REPORT.md` (analysis), `candidates.csv` (register), cumulative `ADDRESS_BOOK.md`.

Legend: ⛓️ read on-chain this run · LIVE = current non-zero `allowance` sampled (not just an event).

---

## A. Dead / deprecated / exploited spenders holding CONFIRMED-LIVE infinite approvals (Shape 2/7)

The headline. Zero balance, live drain-surface. "LIVE n/15" = of ~15 most-recent distinct
`(owner,token)` approvers sampled, how many still have a non-zero current allowance to this spender.

| Spender | Chain | Address | State | LIVE sample | ∞ |
|---|---|---|---|---|---|
| **Multichain Router4** | ETH | `0x765277EebeCA2e31912C9946eAe1021199B39C61` | DEAD 2023-07, keys seized | **14/15** | 14 |
| **Multichain Router6** | ETH | `0x6b7a87899490EcE95443e979cA9485CBE7E71522` | DEAD 2023-07 | 879 owners/5wk (churn) | — |
| **KyberSwap AggRouter (old)** | ETH | `0xDF1A1b60f2D438842916C0aDc43748768353EC25` | exploited 2023 | **15/15** | 15 |
| **1inch v4 Router** | ETH | `0x1111111254fb6c44bAC0beD2854e76F90643097d` | deprecated | **15/15** | 15 |
| **dYdX v1 SoloMargin** | ETH | `0x1E0447b19BB6EcFdAe1e4AE1694b0C3659614e4e` | deprecated | **14/15** | 14 |
| **0x AllowanceTarget (old)** | ETH | `0xF740B67dA229f2f10bcBd38A7979992fCC71B8Eb` | deprecated | **13/15** | 12 |
| **SwapNet** | ETH·ARB·BASE·BNB | `0x616000e384Ef1C2B52f5f3A88D57a3B64F23757e` | exploited 2026-01 | **5/15** (ETH) | 4 |
| ~~Aperture~~ | ETH·ARB | `0xD83d960deBEC397fB149b51F8F37DD3B5CFA8913` | exploited 2026-01 | **0/14 → EXCLUDED** | 0 |

Next-stage note: presence of live approvals ≠ a drain path. Sharpest = **Multichain** (dead + seized
keys + 800+ live ∞ approvers → check for an arbitrary-`from` `transferFrom` entrypoint). Audited
deprecated routers (1inch v4, 0x, dYdX v1) are a large *surface*, low prior of a reachable flaw.

## B. Cross-chain bytecode fingerprint (⛓️ `eth_getCode` → Keccak-256)

| Contract | Chains | codehash | Verdict |
|---|---|---|---|
| **SwapNet** | ETH·ARB·BASE·BNB | `7d1a6d36ad573e6a…` (1864 B) | **byte-identical on all 4** — one flaw, N deployments |
| Aperture | ETH `efc84c5b…` / ARB `94edcf58…` / Base = no code | — | **differs per chain** (don't assume replication) |
| KiloEx | Base `f18c5691…` / BSC `4bd01514…` | — | **differs per chain** |

## C. Implementation age / verification divergence (⛓️ EIP-1967 impl slot)

| Proxy (chain) | Shell created | Impl address | Impl created | Verified |
|---|---|---|---|---|
| **Radiant V2 Pool (ARB)** `0xF4B1486DD74D07706052A33d31d7c0AAFD0659E1` | 2023-03-18 | `0x3d4c56cdb97355807157f5c7d4f54957f0e9af44` | **2024-10-17** | **NO** |
| **dForce Controller (ETH)** `0x8B53Ab2c0Df3230EA327017C91Eb909f815Ad113` | 2021-02-25 | `0xbd0ed2f6e7d84ac5a74cc29d4585d5179ece7ddd` | **2024-10-25** | yes |
| **Aave V1 Core (ETH)** `0x3dfd23A6c5E8BbcFc9581d2E864a68feb6a076d3` | 2020-01-08 | `0x0e26e0bf83b4ec2cb0dcbc037bb01da5bb352eae` | **reads 2024-05-02** ⚠ anomaly | yes |

Radiant's fresh **unverified** impl on a 2-incident pool is the strongest single-contract stack;
bytecode-match it against a verified twin before reading.

## D. Empty-market donation surface (⛓️ re-verified after the rate-limit ghost correction)

Only one TRUE zero-supply, collateral-enabled market found live (maintained forks are seeded):

| Market | Chain | Address | totalSupply | cash | CF | underlying |
|---|---|---|---|---|---|---|
| Ionic `ionmsUSD` | BASE | `0x5be1cb6cb3c9bfd16db43ed4f6c081fa9783dd1c` | **0** | ~32e18 | 10% (weak) | msUSD `0x526728dbc96689597f85ae4cd716d4f7fccbae9d` |

---

*Attacker/context addresses (for flow-of-funds, not candidates): SwapNet/Aperture attacker (ETH)
`0x5c92884dFE0795db5ee095E68414d6aaBf398130`; KiloEx attacker `0x00fac92881556a90fdb19eae9f23640b95b4bcbd`.*
