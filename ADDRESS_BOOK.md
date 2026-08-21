# Candidate Address Book — cumulative master

Companion to **[`CANDIDATE_QUEUE.md`](./CANDIDATE_QUEUE.md)** — one block per candidate with **every
address the next stage needs to start reading**: the named contract, its implementation, its admin/
owner, its oracle/price authority, its markets/pools and their underlyings, and (for incident-anchored
entries) the exploited contract + attacker. This is a *starting map*, not a proof of exploitability.

> **Start here for auditing:** [`AUDIT_TARGETS.md`](./AUDIT_TARGETS.md) is the single prioritized,
> audit-ready worksheet (pick a target → load the address → audit the hypothesis). This file
> (`ADDRESS_BOOK.md`) is the deeper **cumulative address reference** it points into — every grounded
> candidate across all runs, latest merged at the bottom.

**How the addresses were obtained (2026-08-20):**
- ⛓️ **resolved on-chain this pass** — via Etherscan V2 `eth_call`/`eth_getStorageAt` (Ethereum,
  Arbitrum), Base RPC (`mainnet.base.org`), or reading the exploit tx directly. Reproduced below.
- 📄 **from a source registry / post-mortem** — labelled inline.
- 🔎 **not yet resolved** — handed over as an entry point + the exact call to run.

**Selectors used** (so the next stage can reproduce): `getAllMarkets()` `0xb0772d0b` ·
`comptrollerImplementation()` `0xbb82aa5e` · `admin()` `0xf851a440` · `oracle()` `0x7dc0d1d0` ·
`underlying()` `0x6f307dc3` · `owner()` `0x8da5cb5b` · `symbol()` `0x95d89b41` ·
EIP-1967 impl slot `0x360894…382bbc` · EIP-1967 admin slot `0xb53127…5d6103`.

**Caveat on incident-anchored rows (SwapNet, Aperture, KiloEx, bridges):** these are the *exploited*
contracts. Under the queue's exclusion rule they only stay candidates if live authority still points
at them (residual approvals not revoked, or the code was relaunched byte-identical). Each row says
which to check first. Do not treat them as "still drainable" without that check.

---

## ETHEREUM (chain 1)

### Flux Finance — Compound-v2 RWA fork (⛓️ fully resolved) · leaderboard score 4
Unaudited ($44.5M), Ondo's RWA money market. Shapes 4 (donation on raw-`balanceOf`) + 3 (RWA NAV).

| Role | Address | Notes |
|---|---|---|
| Comptroller (Unitroller) | `0x95Af143a021DF745bc78e845b54591C53a8B3A51` | entry; created 2023-01-30 |
| Comptroller implementation | `0xdc7b90593cafe7a919d22b903fed21bf27da9719` | logic (age this, not the shell) |
| Admin (`admin()`) | `0x2c5898da4df1d45eab2b7b192a361c3b9eb18d9c` | proxy/market admin (likely Ondo guardian — verify) |
| **Price oracle** (`oracle()`) | `0xa42e17f72aefc6ae585a08e6058a38ec036d37ec` | **the mover** — values RWA collateral (Shape 3) |
| Market fOUSG | `0x1dd7950c266fb1be96180a8fdb0591f70200e018` | underlying OUSG `0x1b19c19393e2d034d8ff31ff34c81252fcbbee92` (RWA) |
| Market fUSDC | `0x465a5a630482f3abd6d3b84b39b29b07214d19e5` | underlying USDC `0xa0b8…eb48` |
| Market fDAI | `0xe2ba8693ce7474900a045757fe0efca900f6530b` | underlying DAI `0x6b17…1d0f` |
| Market fUSDT | `0x81994b9607e06ab3d5cf3afff9a67374f05f27d7` | underlying USDT `0xdac1…1ec7` |
| **Market fFRAX (thin)** | `0x1c9a2d6b33b4826757273d47ebee0e2dddcd978b` | underlying FRAX `0x853d955acef822db058eb8505911ed77f175b99e`; ⛓️ ~1000× thinner than siblings (donation concentration point) |

Disclosure: Ondo Finance security contact → reportable.

### Iron Bank (ex-CREAM) — Compound-v2 fork (⛓️ fully resolved) · score 4
Shapes 4 + 3; P2P credit-line divergence; Cream lineage incident history; semi-abandoned.

| Role | Address | Notes |
|---|---|---|
| Comptroller (Unitroller) | `0xAB1c342C7bf5Ec5F02ADEA1c2270670bCa144CbB` | created 2020-12-04 |
| Comptroller implementation | `0xcb9ab119be270f58d40e3d57d1ecc82bd479d59f` | |
| Admin (`admin()`) | `0x5b12f04e22384b01f42ed14da23eacd21f14ac17` | |
| **Price oracle** (`oracle()`) | `0xbd6f5add9b7a6eb151933cb4efd50be4eca71451` | `PriceOracleProxyIB`, 2023-03-13 — single-source valuation (the mover) |
| 24 markets (12 shown) | iWETH `0x41c84c0e2ee0b740cf0d31f63f3b6f627dc6b393` · iDAI `0x8e595470ed749b85c6f7669de83eae304c2ec68f` · **iMIM** `0x9e8e207083ffd5bdc3d99a1f32d1e6250869c1a9` · iLINK `0xe7bff2da8a2f619c2586fb83938fa56ce803aa16` · iYFI `0xfa3472f7319477c9bfecdd66e4b948569e7621b9` · iSNX `0x12a9cc33a980daa74e00cc2d1a0e74c57a93d12c` · iWBTC `0x8fc8bfd80d6a9f17fb98a373023d72531792b431` · iUSDT `0x48759f220ed983db51fa7a8c0d2aab8f3ce4166a` · iUSDC `0x76eb2fe28b36b3ee97f3adae0c69606eedb2a37c` · iSUSHI `0x226f3738238932ba0db2319a8117d9555446102f` · **iGBP** `0xecab2c76f1a8359a06fab5fa0ceea51280a97ecf` · **iEUR** `0x00e5c0774a5f065c285068170b20393925c84bf3` | resolve remaining 12 via `getAllMarkets()`. iMIM/iGBP/iEUR are the thin/exotic markets to weight |

Disclosure: Iron Bank/Cream channels dormant → likely outreach.

### dForce Lending / Unitus — Compound-v2 fork (⛓️ resolved) · Family A
Multi-chain (ETH/ARB/Base); 2023 reentrancy incident (re-exploitation watch).

| Role | Address | Notes |
|---|---|---|
| Controller (proxy) | `0x8B53Ab2c0Df3230EA327017C91Eb909f815Ad113` | TransparentUpgradeableProxy, 2021-02-25 |
| Controller implementation | `0xbd0ed2f6e7d84ac5a74cc29d4585d5179ece7ddd` | |
| Proxy admin (EIP-1967) | `0x4ff0455bcfbb5886607c078e0f43efb5de34def4` | |
| Owner (`owner()`) | `0x17e66b1e0260c930bfa567ff3ab5c71794279b94` | governance/timelock |
| Oracle + iTokens | 🔎 resolve via `controller.priceOracle` + `getAlliTokens`/`getAllMarkets`; **age each chain's impl separately** | |

Disclosure: dForce Immunefi → reportable.

### Aave V1 — deprecated, still funded (⛓️ resolved) · ancient hump
⛓️ LendingPoolCore holds **927.9 ETH** (~$2.1M) + ERC-20 reserves. Solidity 0.5.x, walked away from.

| Role | Address | Notes |
|---|---|---|
| LendingPoolCore (proxy) | `0x3dfd23A6c5E8BbcFc9581d2E864a68feb6a076d3` | **custodies V1 reserves** (the mover), 2020-01-08 |
| LendingPoolCore impl | `0x0e26e0bf83b4ec2cb0dcbc037bb01da5bb352eae` | |
| LendingPool (proxy) | `0x398eC7346DcD622eDc5ae82352F02bE94C62d119` | entry |
| LendingPool impl | `0x588790f64ac1424862081a56b8329decae206249` | |
| Proxy admin (both) | `0x24a42fd28c976a61df5d00d0599c34c4f90748c8` | shared V1 ProxyAdmin — a re-check target |
| AddressesProvider / oracle | 🔎 resolve `LendingPoolAddressesProvider` → `getPriceOracle()` | |

Disclosure: Aave Immunefi likely scopes current versions only → confirm V1 scope, else outreach.

### Compound V1 — original 2018 money market (⛓️ resolved) · ancient hump
Immutable, Solidity 0.4.24, still holding ~$3M.

| Role | Address | Notes |
|---|---|---|
| MoneyMarket | `0x3FDA67f7583380E67ef93072294a7fAc882FD7E7` | non-proxy, 2018-09-26 |
| Admin (`admin()`) | `0x8b8592e9570e96166336603a1b4bd1e8db20fa20` | can set the v1 price oracle (Shape 3/6) |

Disclosure: Compound Immunefi likely v2/v3 only → confirm scope.

### CRETH2 / CreamETH2 — abandoned Cream LST (⛓️ resolved) · Family M
Cream dead; mint authority + ancient + funded (~$1.58M).

| Role | Address | Notes |
|---|---|---|
| CRETH2 token | `0xcBc1065255cBc3aB41a6868c22d1f1C573AB89fd` | `CreamETH2`, 2020-11-18; `owner()` returns 0 → 🔎 resolve minter via the Cream ETH2 staking controller / role holders |

Disclosure: no team → outreach / informational.

### CoW Protocol — Family-C read exemplar (⛓️ / 📄; watched → deprioritized)
Zero balance, holds the entire CoW standing-approval set. Use as the template for the approval-sum read.

| Role | Address | Notes |
|---|---|---|
| GPv2VaultRelayer | `0xC92E8bdf79f0507f65a392b0ab4667716BFE0110` | ⛓️ verified, 2021-06-08; **every CoW trader's approval names this spender** |
| GPv2Settlement | `0x9008D19f58AAbD9eD0D60971565AA8510560ab41` | 📄 settlement (EIP-712 orders) |

Read to run on unwatched forks: `getLogs(topic0=Approval, topic2=<spender>)`, sum live approvals.

---

## ARBITRUM (chain 42161)

### Radiant Capital V2 — Aave-v2 fork (⛓️ partial) · leaderboard score 6
Two incidents (Jan-2024 rounding, Oct-2024 key compromise); impl swapped post-hack + unverified.

| Role | Address | Notes |
|---|---|---|
| LendingPool (proxy shell) | `0xF4B1486DD74D07706052A33d31d7c0AAFD0659E1` | `InitializableImmutableAdminUpgradeabilityProxy`, shell 2023-03-18 |
| **LendingPool implementation** | `0x3d4c56cdb97355807157f5c7d4f54957f0e9af44` | ⛓️ **created 2024-10-17, UNVERIFIED** — bytecode-match a verified twin before reading (the age/readability stack) |
| Proxy admin / AddressesProvider / AaveOracle | 🔎 immutable-admin proxy hides the standard slots; resolve `LendingPoolAddressesProvider` → `getLendingPoolConfigurator`/`getPriceOracle`, and read the admin via Radiant's provider (from Radiant docs) | |

Disclosure: Radiant Immunefi (live) → reportable. **Age the Base/ETH/BNB impls separately.**

### GMX V1 `Vault` — GLP-fork fingerprint (⛓️ anchor) · Family K
The reference to bytecode-match forks against (BMX/Vela/Morphex/Level/EDE). July-2025 mark-price/
reentrancy lineage. GMX itself is watched — this is the fingerprint, not the prime candidate.

| Role | Address | Notes |
|---|---|---|
| Vault | `0x489ee077994B6658eAfA855C308275EAd8097C4A` | ⛓️ `Vault`, Solidity 0.6.12, 2021-08-31 |
| VaultPriceFeed / GlpManager / GLP / Router / PositionRouter | 🔎 resolve from GMX v1 docs or via the Vault's `priceFeed()`/`glpManager()` getters | mark-price source + GLP mint/redeem = the Shape-3+4 path |

---

## BASE (chain 8453)

### Ionic Protocol — Fuse/Compound fork (⛓️ fully resolved) · Family A
Exploited Feb-2025 (re-exploitation / silent-patch check). Isolated-collateral markets, several are
restaking/exotic (Shape 3 oracle risk).

| Role | Address | Notes |
|---|---|---|
| Comptroller (Unitroller) | `0x05c9C6417F246600f8f5f49fcA9Ee991bfF73D13` | entry |
| Comptroller implementation | `0xc63ee58a68c22bfd7900ab5c3eb94d0f3d1442e9` | |
| Admin (`admin()`) | `0x1155b614971f16758c92c4890ed338c9e3ede6b7` | |
| **Price oracle** (`oracle()`) | `0x1d89e5ba287e67ac0046d2218be5fe1382ce47b4` | the mover — prices restaking collateral |
| 28 markets (key/exotic shown) | **ionezETH** `0x079f84161642d81aafb67966123c9949f9284bf5` (ezETH `0x2416…cceea5`) · **ionwstETH** `0x9d62e30c6cb7964c99314dcf5f847e36fcb29ca9` · **ionwsuperOETHb** `0xc462eb5587062e2f2391990b8609d2428d8cf598` · **ioncbBTC** `0x1de166df671ae6db4c4c98903df88e8007593748` · ionWETH `0x49420311b518f3d0c94e897592014de53831cfa3` · ionUSDC `0xa900a17a49bc4d442ba7f72c39fa2108865671f0` · ioncbETH `0x9c201024a62466f9157b2daadda9326207addd29` · ioneUSD `0x9c2a4f9c5471fd36be3bbd8437a33935107215a1` · ionbsdETH `0x3d9669de9e3e98db41a1cbf6dc23446109945e3c` · ionRSR `0xfc6b82668e10aff62f208c492fc95ef1fa9c0426` · ionhyUSD `0x751911bda88efcf412326abe649b7a3b28c4dede` · ionwUSDM `0xe30965acd0ee1ce2e0cd0acbfb3596bd6fc78a51` | resolve remaining via `getAllMarkets()`; the LRT/exotic-collateral markets are the Shape-3 weights |

Disclosure: Ionic security contact / Immunefi → reportable.

---

## MULTI-CHAIN, INCIDENT-ANCHORED (📄 from post-mortems; check residual/redeploy first)

### SwapNet + Aperture — router arbitrary-call over approvals · Family C, score 5
The flaw is in the router implementation, and **both contracts share one address across all four
chains** (deterministic deploy) → one flaw, N deployments. Closed-source (bytecode-only).

| Role | Address (same on ETH / ARB / Base / BNB) | Notes |
|---|---|---|
| SwapNet victim router | `0x616000e384Ef1C2B52f5f3A88D57a3B64F23757e` | arbitrary `target.call` → `transferFrom` of standing approvals; **check residual approvals still pointed here per chain** |
| Aperture Finance contract | `0xD83d960deBEC397fB149b51F8F37DD3B5CFA8913` | closed-source; same shared flaw |
| Attacker (ETH) | `0x5c92884dFE0795db5ee095E68414d6aaBf398130` | for flow-of-funds context |

Disclosure: SwapNet / Matcha-Meta incident response active → reportable.

### KiloEx — caller-settable price feed behind a weak forwarder · Family L, score 5
⛓️ contract addresses pulled from the exploit txs. Signature-spoof → forged role → `setPrices`
(Shapes 1+2+3). Relaunched → verify the redeploy actually fixed the forwarder access control.

| Role | Address | Notes |
|---|---|---|
| KiloEx contract (Base) | `0xd649a0876453fc7626569b28e364262192874e18` | ⛓️ `to` of Base exploit tx; entry selector `0x7493b4a4` |
| KiloEx contract (BSC) | `0xcc6a5784194bd516db29aa505179857025d8bef4` | ⛓️ `to` of BSC exploit tx |
| Attacker | `0x00fac92881556a90fdb19eae9f23640b95b4bcbd` | Tornado-funded |
| KiloPriceFeed / MinimalForwarder / PositionKeeper | 🔎 resolve from the above contracts' storage/source (named by role in the post-mortems) | the forwarder+setter is the stack |

Disclosure: KiloEx bounty (offered 10% during incident) → reportable.

---

## FAMILIES HANDED OVER AS ENTRY POINTS (🔎 addresses to resolve)

Not fully resolved this pass — named with the entry point + the exact resolution, per the queue. The
biggest deferred set, and the BSC/Base ones sit under the explorer gap.

- **GMX-fork perps (Family K):** BMX/Morphex (Base/BNB), Vela (ARB/Base, aud=0), Mummy, **Level
  Finance** (BNB, 2023 incident), **El Dorado/EDE** (BNB, 2023 incident). *Resolve:* each `Vault` +
  `GlpManager` + price-feed; **bytecode-match against GMX-v1 Vault `0x489ee0…`** (above) pre/post the
  July-2025 fix.
- **Bridges / wrapped-asset minters (Family D):** Orbit Bridge (~$16.4M, Jan-2024 incident), Meter
  Passport, Allbridge Classic, Knit Finance, pNetwork, Multichain (~$37.6M, frozen). *Resolve:* the
  vault/minter + signer-set/DVN config + `MINTER_ROLE` holder over the wrapped asset.
- **LRT deposit pools + receipt-OFTs (Family M):** Meta Pool ETH, GETH, GLIF (Base), Accumulated
  Finance, Hord (all aud=0 at size). *Resolve:* deposit pool `MINTER_ROLE` + NAV/exchange-rate source
  + (if OFT) LayerZero DVN config.
- **SYMM intent-perp forks (Family N):** SYMMIO, IntentX, ELFi (ARB/Base, aud=0). *Resolve:* the
  shared `Symmio` **diamond** (check for an uninitialized facet, Shape 6) + Muon oracle trust.
- **Superform (Family E/C):** cross-chain 4626 meta-router. *Resolve:* SuperformRouter + SuperformFactory
  + one funded per-vault `Superform` wrapper (permissionless factory long-tail); age the router impl.
- **Safe modules / credit delegation (Family J):** enumerate `enabledModules` with a permissionless
  `execTransactionFromModule`; read `variableDebtToken.borrowAllowance(delegator, delegatee)`.

---

*This address book covers the on-chain-grounded candidates from `CANDIDATE_QUEUE.md`. Every ⛓️ row was
read live on 2026-08-20; every 🔎 row names the call to resolve it. Market lists truncated to the
resolved subset are marked "resolve remaining via `getAllMarkets()`."*

---

## Wide computed scan (latest run) — approval-authority, fingerprint, impl-age

Read live 2026-08-20. "LIVE n/15" = current non-zero `allowance` sampled among recent approvers.

**Dead/deprecated/exploited spenders with confirmed-live infinite approvals (Shape 2/7):**

| Spender | Chain | Address | State | LIVE |
|---|---|---|---|---|
| Multichain Router4 | ETH | `0x765277EebeCA2e31912C9946eAe1021199B39C61` | DEAD 2023, keys seized | 14/15 ∞ |
| Multichain Router6 | ETH | `0x6b7a87899490EcE95443e979cA9485CBE7E71522` | DEAD 2023 | 879 owners/5wk |
| KyberSwap AggRouter (old) | ETH | `0xDF1A1b60f2D438842916C0aDc43748768353EC25` | exploited 2023 | 15/15 ∞ |
| 1inch v4 Router | ETH | `0x1111111254fb6c44bAC0beD2854e76F90643097d` | deprecated | 15/15 ∞ |
| dYdX v1 SoloMargin | ETH | `0x1E0447b19BB6EcFdAe1e4AE1694b0C3659614e4e` | deprecated | 14/15 ∞ |
| 0x AllowanceTarget (old) | ETH | `0xF740B67dA229f2f10bcBd38A7979992fCC71B8Eb` | deprecated | 12/15 ∞ |
| SwapNet | ETH·ARB·BASE·BNB | `0x616000e384Ef1C2B52f5f3A88D57a3B64F23757e` | exploited 2026-01 | 5/15 ∞ (ETH) |
| ~~Aperture~~ | ETH·ARB | `0xD83d960deBEC397fB149b51F8F37DD3B5CFA8913` | exploited | 0/14 → EXCLUDED |

**Bytecode fingerprint:** SwapNet identical (`7d1a6d36…`) on ETH·ARB·BASE·BNB; Aperture differs per
chain (ETH `efc84c5b…` / ARB `94edcf58…` / no code on Base); KiloEx differs (Base `f18c5691…` / BSC
`4bd01514…`).

**Impl-age / verification:** Radiant V2 pool impl `0x3d4c56cdb97355807157f5c7d4f54957f0e9af44`
(2024-10-17, **unverified**); dForce controller impl `0xbd0ed2f6e7d84ac5a74cc29d4585d5179ece7ddd`
(2024-10-25); Aave V1 Core impl `0x0e26e0bf83b4ec2cb0dcbc037bb01da5bb352eae` (reads 2024-05-02 ⚠).

**Empty-market (only true empty found):** Ionic `ionmsUSD`
`0x5be1cb6cb3c9bfd16db43ed4f6c081fa9783dd1c` (Base) — totalSupply 0, cash ~32e18, CF 10%; underlying
msUSD `0x526728dbc96689597f85ae4cd716d4f7fccbae9d`.

---

## Run 4 (fresh & at-risk) — new candidates & on-chain flags

Prevention-focused: live/funded/unaudited money contracts (not hacked). Full worksheet in
`AUDIT_TARGETS.md`; the 379-protocol universe in `at_risk_protocols.csv`. Addresses read 2026-08-20.

**Concrete flags (triage — verify access control):**

| Protocol | Chain | Address | Flag |
|---|---|---|---|
| mStable V2 (CDP) | ETH | `0xca1207647ff814039530d7d35df0e1dd2e91fa84` | `initializer` w/o `_disableInitializers` (impl-init / Shape 6) |
| Stobox (RWA $14M) | ARB | `0xa6422e3e219ee6d4c1b18895275fe43556fd50ed` | core **UNVERIFIED** |
| Usual ETH0 (Synth) | ETH | `0xC4441c2BE5d8fA8126822B9929CA0b81Ea0DE38E` | delegatecall + 2× arbitrary `.call(data)` |
| Avalon Superearn (Yield $30M) | ETH | `0x5c8d0c48810fd37a0a824d074ee290e64f7a8fa2` | arbitrary `.call(data)` in `AvalonMintable` impl |
| KAIO (RWA $41M) | ETH | `0x00bac91fd8f5b4a0dc03c8021139b76f6549ee7e` | 4× sweep/rescue |
| GETH (LST) | ETH | `0x3802c218221390025bceabbad5d8c59f40eb74b8` | `transferFrom(param_from)` |

**Deep-dive entry addresses (token → resolve minter/vault before auditing; see AUDIT_TARGETS.md):**
Resolv USR `0x259338656198ec7a76c729514d3cb45dfbf768a1` · Alchemix V3 `0xdBdb4d16EdA451D0503b854CF79D55697F90c8DF` · Cooler Loans (OHM) `0x64aa3364F17a4D01c6f1751Fd97C2BD3D7e7f1D5` · Metronome Synth `0x2Ebd53d035150f328bd754D6DC66B99B0eDB89aa` · Ledgity Yield `0x482dF7483a52496F4C65AB499966dfcdf4DDFDbc` · Yield Basis `0x01791f726b4103694969820be083196cc7c045ff` · Everything (ARB lending) `0xe7e7e741c23a4767831a56a8c99f522c5ac1e7e7` · Spectra V2 (Base) `0x64fcc3a02eeeba05ef701b7eed066c6ebd5d4e51`.
