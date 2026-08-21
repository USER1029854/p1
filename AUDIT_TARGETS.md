# Audit Targets — start here

**One consolidated, audit-ready worksheet** merging the best of all research runs. Each target is a
**contract address + the exact thing to check**, ordered by priority. Pick a row, load the address,
audit the hypothesis. Everything read live on-chain **2026-08-20**.

- **✅ live** = confirmed on-chain this pass (allowance / storage / creation read).
- "Load first" = the address to open in a decompiler/explorer to begin.
- "Audit this" = the specific vulnerability hypothesis and where it lives.
- Full address detail is in `ADDRESS_BOOK.md`; the reasoning/data behind each is in `SCAN_REPORT.md`
  and `CANDIDATE_QUEUE.md`; `candidates.csv` is the sortable register; `scanners/` reproduces the reads.

---

## TIER 1 — confirmed live authority, unwatched deployed state (audit these first)

### T1 · Radiant V2 — fresh **unverified** implementation on a twice-exploited pool  ✅
- **Load first:** implementation `0x3d4c56cdb97355807157f5c7d4f54957f0e9af44` (Arbitrum) — created **2024-10-17, UNVERIFIED**
- Proxy (entry): `0xF4B1486DD74D07706052A33d31d7c0AAFD0659E1` (shell 2023-03-18)
- **Audit this:** pull the unverified impl bytecode; diff against a verified Aave-v2 `LendingPool` twin.
  Check (a) new-reserve index/rounding on a freshly-activated market, (b) the price-oracle source via
  the `LendingPoolAddressesProvider` → `getPriceOracle()`. Aave-v2 fork; **hit twice** (Jan-2024
  rounding, Oct-2024 key compromise) and the logic was swapped right after.
- **Why:** fresh + unverified + prior-incident + live pool. Disclosure: Radiant Immunefi.

### T2 · Multichain — dead bridge routers still holding live ∞ approvals  ✅
- **Load first:** `0x765277EebeCA2e31912C9946eAe1021199B39C61` (Router4, Ethereum) — and `0x6b7a87899490EcE95443e979cA9485CBE7E71522` (Router6)
- **Audit this:** does **any entrypoint pull tokens from an arbitrary `from`** (not `msg.sender`)? The
  protocol is dead (Jul-2023, operator keys seized) yet **14/15 sampled recent approvers still have a
  live infinite allowance** to Router4. If such a path exists, whoever holds the seized keys can drain
  every current approver. Shape 2/7.
- **Why:** dead protocol + compromised keys + confirmed live ∞ approvals from 800+ wallets. Disclosure:
  no team → this one is a warn-the-users / informational case, not a bounty.

### T3 · SwapNet — one router, byte-identical on 4 chains, still live ∞ approvals  ✅
- **Load first:** `0x616000e384Ef1C2B52f5f3A88D57a3B64F23757e` (same address & bytecode on **ETH·ARB·BASE·BNB**; codehash `7d1a6d36…`, closed-source → get bytecode)
- **Audit this:** the arbitrary `target.call(data)` swap step with insufficient validation that reaches
  `transferFrom` of user approvals (the Jan-2026 drain path). Confirm whether it was patched/redeployed;
  ETH still shows **5/15 sampled live ∞ approvals**. Characterize once → applies to all four chains.
- **Why:** exploited, closed-source, still holds live authority. Disclosure: SwapNet/Matcha-Meta contact.

### T4 · KyberSwap old aggregation router — live ∞ approvals on exploited code  ✅
- **Load first:** `0xDF1A1b60f2D438842916C0aDc43748768353EC25` (Ethereum)
- **Audit this:** any arbitrary-call / arbitrary-`from` `transferFrom` reachable path. **15/15 sampled
  approvers still live & infinite.** Kyber has prior incident history. Shape 2/7.
- **Why:** exploited-lineage router with confirmed live ∞ approval surface. Disclosure: KyberSwap bounty.

### T5 · Flux Finance — unaudited $44.5M RWA Compound-v2 fork  ✅
- **Load first:** Comptroller `0x95Af143a021DF745bc78e845b54591C53a8B3A51` (Ethereum); impl `0xdc7b90593cafe7a919d22b903fed21bf27da9719`
- Price oracle (the mover): `0xa42e17f72aefc6ae585a08e6058a38ec036d37ec`
- Markets: fOUSG `0x1dd7950c266fb1be96180a8fdb0591f70200e018` (RWA collateral, underlying OUSG `0x1b19c19393e2d034d8ff31ff34c81252fcbbee92`) · fUSDC `0x465a5a630482f3abd6d3b84b39b29b07214d19e5` · fDAI `0xe2ba8693ce7474900a045757fe0efca900f6530b` · fUSDT `0x81994b9607e06ab3d5cf3afff9a67374f05f27d7` · **fFRAX (thin)** `0x1c9a2d6b33b4826757273d47ebee0e2dddcd978b`
- **Audit this:** (a) Compound-v2 donation / raw-`balanceOf` accounting on the thin `fFRAX` market;
  (b) how the oracle values `fOUSG` (an RWA NAV Flux reads but does not derive — Shape 3). **aud=0.**
- **Why:** unaudited at scale + RWA oracle + Compound-fork mechanics. Disclosure: Ondo contact.

---

## TIER 2 — strong shape + funded (audit after Tier 1)

### T6 · Iron Bank (ex-CREAM) Compound-v2 fork  ✅
- Comptroller `0xAB1c342C7bf5Ec5F02ADEA1c2270670bCa144CbB`; oracle `0xbd6f5add9b7a6eb151933cb4efd50be4eca71451`; impl `0xcb9ab119be270f58d40e3d57d1ecc82bd479d59f` (Ethereum)
- **Audit this:** the protocol-to-protocol credit-line divergence from stock Compound-v2, + single-source oracle. Thin markets: iMIM `0x9e8e207083ffd5bdc3d99a1f32d1e6250869c1a9`, iEUR `0x00e5c0774a5f065c285068170b20393925c84bf3`, iGBP `0xecab2c76f1a8359a06fab5fa0ceea51280a97ecf`.

### T7 · dForce Lending — controller logic swapped 2024-10-25  ✅
- Controller `0x8B53Ab2c0Df3230EA327017C91Eb909f815Ad113`; impl `0xbd0ed2f6e7d84ac5a74cc29d4585d5179ece7ddd` (fresh 2024-10-25); owner `0x17e66b1e0260c930bfa567ff3ab5c71794279b94` (Ethereum; also ARB/Base)
- **Audit this:** the fresh 2024 controller logic + the 2023 reentrancy-on-nonstandard-collateral path (verify it's fixed on every chain — age each chain's impl separately).

### T8 · Ionic (Base) — Fuse fork, exploited Feb-2025  ✅
- Comptroller `0x05c9C6417F246600f8f5f49fcA9Ee991bfF73D13`; impl `0xc63Ee58A68C22BFd7900ab5C3eB94D0f3d1442e9`; oracle `0x1d89e5ba287e67ac0046d2218be5fe1382ce47b4`
- **Audit this:** verify the Feb-2025 patch vs. redeploy; the **restaking/exotic collateral oracle** —
  ionezETH `0x079f84161642d81aafb67966123c9949f9284bf5`, ionwstETH `0x9d62e30c6cb7964c99314dcf5f847e36fcb29ca9`, ionwsuperOETHb `0xc462eb5587062e2f2391990b8609d2428d8cf598`, ioncbBTC `0x1de166df671ae6db4c4c98903df88e8007593748`. Empty market: ionmsUSD `0x5be1cb6cb3c9bfd16db43ed4f6c081fa9783dd1c` (totalSupply 0, CF 10% — weak).

### T9 · Aave V1 — deprecated, holds 927.9 ETH, impl-date anomaly  ✅
- LendingPoolCore `0x3dfd23A6c5E8BbcFc9581d2E864a68feb6a076d3` (holds 927.9 ETH); impl `0x0e26e0bf83b4ec2cb0dcbc037bb01da5bb352eae` (**creation reads 2024-05-02 — verify why on a 2020 deprecated contract**); shared ProxyAdmin `0x24a42fd28c976a61df5d00d0599c34c4f90748c8` (Ethereum)
- **Audit this:** the impl-date anomaly (reinit / CREATE2 / lookup quirk?) and the v1 flashloan/reentrancy surface on a contract still custodying 927 ETH.

### T10 · Compound V1 — original 2018 money market  ✅
- MoneyMarket `0x3FDA67f7583380E67ef93072294a7fAc882FD7E7`; admin `0x8b8592e9570e96166336603a1b4bd1e8db20fa20` (Ethereum)
- **Audit this:** 2018 Solidity 0.4.24 code, admin-settable price oracle (Shape 3/6), ~$3M residual.

### T11 · KiloEx — caller-settable price feed behind a weak forwarder  ✅
- Base `0xd649a0876453fc7626569b28e364262192874e18` · BSC `0xcc6a5784194bd516db29aa505179857025d8bef4` (differ per chain)
- **Audit this:** the `MinimalForwarder` signature-spoof → forged trusted-role → `setPrices()` chain (Shapes 1+2+3). Relaunched → verify the forwarder access-control hole is actually closed.

### T12 · GMX-v1 GLP-fork family — mark-price + vault accounting
- Fingerprint reference (Arbitrum): GMX-v1 `Vault` `0x489ee077994B6658eAfA855C308275EAd8097C4A`
- **Audit this:** bytecode-match forks (BMX/Morphex on Base·BNB, Vela, **Level Finance** & **El Dorado/EDE** on BNB — both prior-exploited) against this Vault; check whether the **July-2025** GMX-v1 mark-price/reentrancy fix was back-ported. Shapes 3+4.

### T13 · CRETH2 — abandoned Cream liquid-staking token  ✅
- Token `0xcBc1065255cBc3aB41a6868c22d1f1C573AB89fd` (Ethereum, ~$1.58M)
- **Audit this:** the mint/redemption authority (Cream is dead; `owner()` null → resolve the minter role); is it frozen or live?

### T14 · Deprecated audited routers with confirmed live ∞ approvals  ✅
- 1inch v4 `0x1111111254fb6c44bAC0beD2854e76F90643097d` (15/15 live ∞) · dYdX v1 SoloMargin `0x1E0447b19BB6EcFdAe1e4AE1694b0C3659614e4e` (14/15) · 0x old AllowanceTarget `0xF740B67dA229f2f10bcBd38A7979992fCC71B8Eb` (12/15) — all Ethereum
- **Audit this:** any arbitrary-`from` `transferFrom` path. **Lower prior** (these were well audited) but the standing authority is real and the deprecated deployed state is unmonitored — a quick negative clears them.

---

## TIER 3 — leads to resolve before auditing (entry point + the call to run)

- **SYMM intent-perp forks** (SYMMIO/IntentX/ELFi, ARB·Base, aud=0): resolve the shared `Symmio` **diamond**, check for an uninitialized facet (Shape 6) + the Muon price trust.
- **LRT deposit pools** (Meta Pool ETH, GETH, GLIF-Base, aud=0 at 8-figure TVL): resolve `MINTER_ROLE` holder + NAV source + (if OFT) LayerZero DVN config.
- **Small/old bridges** (Orbit ~$16M prior-incident, Allbridge, Meter Passport, Knit, pNetwork): resolve the mint/release authority + signer-set/DVN.
- **Safe modules / credit delegation:** enumerate `enabledModules` with a permissionless `execTransactionFromModule`; read `borrowAllowance`.
- **Abandoned Compound forks** (Sonne-dead, Rari/Fuse pools, Cream residuals): the real empty-market donation surface (maintained forks are seeded — see `SCAN_REPORT.md` §5).

---

## Excluded on evidence
- **Aperture** `0xD83d960deBEC397fB149b51F8F37DD3B5CFA8913` — 245 approval *events* but **0/14 sampled allowances live** (churn, not standing authority).
- **Onyx** lending markets — drained (~$21k residual).
- Maintained-fork "empty markets" flagged in an early scan — rate-limit ghosts (corrected; see `SCAN_REPORT.md` §1).

---

*This is the single audit-ready handoff. If you want it as a spreadsheet, `candidates.csv` has the same
targets in sortable columns.*
