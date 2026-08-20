# Protocol-Tier Candidate Queue — BNB Chain · Ethereum · Arbitrum · Base

**Stage:** surfacing / triage. This is a *candidate queue*, not findings. Nothing here is audited,
simulated, or proven reachable. The next stage reads each survivor's full source, resolves its
dependencies, and decides what is actually exploitable. My job was to locate the right contracts,
describe each by the exact shape that flagged it, and group them into systems and families.

**Target severity:** fund loss or authority takeover (HIGH/CRITICAL). Griefing, DoS, and
low-severity shapes were skipped.

**Date of pass:** 2026-08-20. All on-chain reads below were performed on that date against live
state. Creation dates are from the contract-creation transaction, pinned to the block.

---

## 0. How this queue is ranked (read before the candidates)

The two inversions that shape every entry:

1. **Rank by authority, not balance.** Most drained contracts in this population held no money of
   their own — the money sat in user wallets as standing approvals, or the contract held the right to
   mint / move / redirect it. A zero-balance contract can be the most drainable thing on the chain
   because power is pointed at it. Balance is *one* form of authority, not the axis.

2. **Watched is the disqualifier, not "unaudited."** High TVL, an active bounty, a named security
   team, a recent famous audit, general fame → many eyes already looked, so a reachable flaw is less
   likely to still be there. Those are reasons to **deprioritize**. The signal I rank *up* on is
   **unwatched**: nobody has re-checked the deployed contract and its current live state against what
   its code assumes. For every watched protocol of interest, the candidate is the **obscure fork** —
   the one that changed the money path and got a fraction of the scrutiny — or the protocol's own
   **long-tail market / instance** that no one covers individually.

**Resolution is one hop to the mover.** A protocol is a dozen addresses and the one a directory
names is usually bookkeeping (a governance proxy, a token, an empty factory). I resolved:
factory → implementation + a live instance; proxy → both shell and implementation (aging the
implementation *separately*, because it is often far younger than the shell and that is the age that
matters); oracle/registry → the contract that moves funds on its word; token → its minter/vault.

**Fingerprint the implementation, not the instance.** A broken path in one mastercopy behind many
clones is *every clone*. A flaw in one byte-identical sibling is *every sibling*. Families below are
grouped on shared code, and where a family spans clones I say "resolve all siblings."

**Two age humps, hollow middle.** Fresh hump = new code with new bugs (days–months old, funded or
granted authority at deploy). Ancient hump = built, funded, walked away from for years, un-re-examined
(deprecated-but-funded is ~a quarter of the tier). I deprioritized (did not reject) the
6-month–2-year band. Both humps appear on all four chains.

**Shape catalog (highest-yield first), used as the flag on every candidate:**

1. Signature / proof verification (largest class)
2. Caller-supplied identity or context (second largest)
3. Thin-source pricing
4. Diverged vault / market accounting
5. Free-to-manufacture eligibility
6. Live-state conditions (read storage, not just source)
7. Arbitrary external call + standing authority

---

## 1. Data channels reached, and what this pass structurally could not reach

**Honesty first, because a named gap beats a silent omission.**

| Chain | Source / ABI / creation | Logs (approvals) | eth_call / storage / balance |
|---|---|---|---|
| Ethereum (1) | Etherscan V2 ✅ full | Etherscan V2 ✅ | ✅ |
| Arbitrum (42161) | Etherscan V2 ✅ full | Etherscan V2 ✅ | ✅ |
| Base (8453) | Blockscout ✅ (no Etherscan V2 free) | Blockscout ⚠️ partial | ✅ (RPC) |
| BNB Chain (56) | **Sourcify only** (verified source), no free explorer for logs/creation-date | ❌ **GAP** | ✅ (public RPC) |

Concrete limits that bias this queue — treat every one as "candidates I could not enumerate live":

- **BNB Chain is under-covered.** Etherscan V2's free tier does **not** cover chain 56; there is no
  free Blockscout instance. I can read BSC source (Sourcify) and do `eth_call`/`balanceOf`/`getStorageAt`
  via public RPC, but I **cannot** cheaply enumerate `Approval` logs or pin creation dates. Given the
  weight of BSC in this tier (Venus, PancakeSwap forks, the SwapNet-class routers), **BSC is the single
  biggest blind spot in this pass.** BSC candidates below are named by protocol + role + resolution
  path, not fully aged/authority-summed. Flagged inline.
- **The new-deployment firehose is unreachable here.** The fresh hump — code exploited within *days*
  of deploy — requires watching the new-verified-contract stream on each chain (especially BSC/Base).
  A periodic re-scan of *known* addresses structurally misses it. This pass leans on the ancient hump
  and on known fork lineages; the freshest fresh-hump candidates are under-represented and named only
  where a 2026 incident already surfaced the pattern.
- **Directory thresholds hide the smallest protocols.** DefiLlama's fork listing endpoint (`/forks`)
  is paywalled on the free tier, and the `forkedFrom` field in the free protocol feed is populated for
  only 6 of 8,090 protocols. Fork lineage below is reconstructed from research + code fingerprints, not
  from the directory. The very smallest forks (sub-$100k TVL, or TVL-untracked) are below DefiLlama's
  listing floor and are represented only as families ("resolve all clones of this mastercopy").
- **Approval sums are named as a read, not always computed.** For the router/settlement family the
  authority *is* the aggregate standing `Approval` set; where I could not run the log scan (BSC, some
  Base) I hand over the spender address + the exact read to run, per the shape.

---

## 2. Candidate families

Grouped by protocol and clustered by shared codebase / fork lineage, so the next stage sees systems,
not loose addresses. Within each family: the lineage, the shape's **on-chain read**, the watched/
unwatched call, then candidates.

Legend for each candidate: **[chain] address** · *deploy* · *authority (how confirmed)* · *money
logic* · *shape(s)* · *role + siblings* · *shared base* · *prior-review signal* · *disclosure path*.
"⛓️ confirmed" = I read it on-chain this pass. "🔎 resolve" = handed over as an entry point for the
next stage (address named where known, gap named where not).

---

### Family A — Compound V2 fork lending: donation / empty-market + oracle authority

**Lineage:** Compound v2 (`Comptroller`/`Unitroller` + `cToken` markets + `PriceOracle`). The whole
long tail — Venus, Benqi, Moonwell, Iron Bank, Cream (RIP), Sonne (RIP), Onyx, Hundred (RIP), Midas →
Ionic, dForce/Unitus, WePiggy, and dozens of sub-$1M forks — carries the original DNA: **raw
`balanceOf()` accounting**, so a direct ERC-20 transfer ("donation") into a market bypasses supply
caps and inflates the exchange rate. On a market whose supply has returned to ~zero (a freshly listed
collateral, a wound-down market, or a low-liquidity isolated pool) on code without the empty-market
mint guard, this recreates first-depositor share-inflation. Cumulative historical losses across this
family exceed $230M; **Venus's THE market was drained this way in March 2026**, and **Onyx was hit by
the identical bug twice (Nov 2023, Sep 2024), never patched between**.

**On-chain read (the flag):** `comptroller.getAllMarkets()` → for each `cToken`: `totalSupply()`,
`getCash()`, `exchangeRateStored()`. Flag any market with near-zero `totalSupply` but a live collateral
factor, on a fork whose `mintFresh`/listing path lacks the "mint a seed amount at listing" mitigation.
Separately resolve `comptroller.oracle()` — the price oracle is the authority that moves funds on its
word (Family A shades into Shape 3).

**Shapes:** 4 (diverged accounting / first-depositor via donation) + 3 (oracle).

**Watched/unwatched:** Venus/Moonwell/Benqi cores are heavily watched now (post-2026-incident). The
candidates are **(a) isolated / newly-listed markets** on those same forks (unwatched individually),
and **(b) the obscure sub-$10M forks** below.

Candidates:

- **⛓️ confirmed — Iron Bank (Ethereum)** · Unitroller `0xAB1c342C7bf5Ec5F02ADEA1c2270670bCa144CbB`
  (proxy → impl `0xcb9ab119be270f58d40e3d57d1ecc82bd479d59f`, created **2020-12-04**) · oracle
  `PriceOracleProxyIB 0xbd6f5add9b7a6eb151933cb4efd50be4eca71451` (created 2023-03-13, verified). ·
  *Authority:* comptroller admin + the price-oracle proxy is single-source for all market valuations
  (confirmed `oracle()` returns the proxy on-chain); markets still hold residual balances (DefiLlama
  ~$0.2M). · *Money logic:* Cream/Compound-v2 money market with protocol-to-protocol credit lines
  (its distinctive divergence). · *Shape:* 4 + 3. · *Role:* comptroller + oracle are the movers;
  siblings = all `iToken` markets (resolve via `getAllMarkets()`). · *Base:* Compound v2 (Cream
  lineage). · *Prior review:* audited, and Cream/Iron Bank has an **incident history** (2021 flash-loan
  / oracle) — treat the oracle proxy as the re-check target. · *Disclosure:* Iron Bank / former Cream
  channels are largely dormant → likely direct-outreach / abandoned.

- **⛓️ confirmed — dForce Lending / Unitus (Ethereum + Arbitrum + Base)** · Controller (ETH)
  `0x8B53Ab2c0Df3230EA327017C91Eb909f815Ad113` (TransparentUpgradeableProxy → impl
  `0xbd0ed2f6e7d84ac5a74cc29d4585d5179ece7ddd`, created **2021-02-25**, verified). · *Authority:*
  upgradeable controller (proxy admin can swap the risk layer) governing multi-chain `iToken` markets;
  live TVL (DefiLlama: dForce ~$1.0M, Unitus ~$6.3M across the three chains). · *Money logic:*
  Compound-v2-derived money market; dForce had a **2023 reentrancy incident** (ERC-777/curve-LP path)
  — a modified-money-path fork. · *Shape:* 4 + 3, plus reentrancy-on-nonstandard-collateral as a
  known divergence. · *Role:* controller = risk mover; siblings = every `iToken` + the oracle; **age
  the impl per chain separately.** · *Base:* Compound v2 (dForce variant). · *Prior review:* audited +
  prior incident (re-exploitation watch). · *Disclosure:* dForce has an Immunefi program → reportable.

- **⛓️ confirmed — Ionic Protocol (Base)** · Unitroller `0x05c9C6417F246600f8f5f49fcA9Ee991bfF73D13`
  (→ impl `Comptroller 0xc63Ee58A68C22BFd7900ab5C3eB94D0f3d1442e9`, verified; Blockscout). ·
  *Authority:* Fuse-style pool comptroller controlling all Ionic markets on Base; live TVL (~$2.0M). ·
  *Money logic:* Midas Capital → Ionic (Fuse/Rari-derived Compound v2), isolated-pool factory model. ·
  *Shape:* 4 (empty isolated markets) + 3. · *Role:* comptroller = mover; siblings = pool `cToken`s +
  the pool oracle; **Ionic was exploited (Feb 2025)** — verify which markets/paths were patched vs.
  redeployed identically. · *Base:* Compound v2 (Fuse/Midas lineage). · *Prior review:* audited +
  **incident history** → prime re-exploitation / silent-patch re-check. · *Disclosure:* Ionic Immunefi
  / security contact likely live → reportable.

- **🔎 resolve — Venus Isolated Pools (Arbitrum + Ethereum; core on BNB)** · DefiLlama ~$1.06M on
  ARB/ETH; the large core is on BNB. · *Why here:* Venus's *core* is now the most-watched Compound fork
  on the chain, but its **isolated pools** are many small `Comptroller` instances each governing a
  handful of low-liquidity markets — individually unwatched, and the empty-market donation shape lives
  per-market. · *Shape:* 4 + 3. · *Role:* one PoolRegistry → N isolated `Comptroller`s → N `vToken`s;
  resolve the registry, enumerate pools, flag low-`totalSupply` markets. · **BSC gap:** the BNB-side
  pools are the biggest set and are under my BSC blind spot — hand over PoolRegistry + "enumerate on
  BscScan/RPC." · *Prior review:* Venus core audited + **THE-market incident Mar 2026**; isolated pools
  less scrutinized. · *Disclosure:* Venus Immunefi (large) → reportable.

- **🔎 resolve — WePiggy (Arbitrum + Ethereum), Sumer.money (multi), Tarot / Impermax V2 (ARB/Base/ETH)**
  · DefiLlama live: WePiggy ~$0.76M, Sumer ~$1.2M, Tarot ~$0.55M, Impermax V2 ~$0.58M. · WePiggy &
  Sumer are Compound-v2 money-market forks (same donation shape; resolve each `Comptroller` +
  `getAllMarkets()`). Tarot/Impermax are the **leveraged-LP variant**: they price collateral off a
  Uniswap-v2 pair `getReserves()` (their `TarotPriceOracle` uses a TWAP of the pair) → this is
  **Shape 3 thin-source** in a Compound-shaped shell, worst on shallow pairs. · *Role:* comptroller/
  borrowable + the pair oracle. · *Base:* Compound v2 (WePiggy/Sumer) and Impermax (Tarot). · *Prior
  review:* audited, low fame → unwatched. · *Disclosure:* mostly small teams; check for Immunefi else
  direct outreach.

- **Re-exploitation exemplar (not a live target) — Onyx Protocol (Ethereum)** · lending side is
  effectively **drained** (⛓️ confirmed: DefiLlama Ethereum lending TVL ≈ $21k) → *excluded* as a live
  money target under the drained-corpse rule. Kept here only as the pattern anchor: same Compound-v2
  donation bug, exploited twice, unpatched between. **Note the separate XCN staking contract still
  holds ~$8.5M** (⛓️ confirmed via DefiLlama staking TVL) — different contract, different shape; worth
  the next stage's glance for its own authority, not the lending path.

---

### Family B — Aave v2 / v3 fork lending: new-market rounding + oracle source

**Lineage:** Aave v2/v3 (`LendingPool`/`Pool` proxy + `aToken`/`variableDebtToken` + `AaveOracle`).
Forks: Radiant, Kinza, ZeroLend, Seamless, Granary, UwU Lend, Sumer, and others. The recurring
divergences: **first-deposit / index rounding on a freshly activated reserve** (Radiant's Jan-2024
Arbitrum incident was exactly a zero-liquidity new market), and a **swapped oracle source** (UwU Lend
was drained twice in 2024 via a manipulable curve/price feed).

**On-chain read:** `pool.getReservesList()` → per reserve `getReserveData()` (liquidity index,
aToken supply); flag reserves with ~zero liquidity but active LTV. Resolve
`PoolAddressesProvider.getPriceOracle()` → check each feed's source (Chainlink vs. a
pool-spot/`getReserves`-derived feed = Shape 3).

**Shapes:** 4 (rounding on fresh reserve) + 3 (oracle).

- **⛓️ confirmed — Radiant Capital V2 (Arbitrum; also Base, Ethereum, BNB)** · LendingPool proxy
  `0xF4B1486DD74D07706052A33d31d7c0AAFD0659E1` (InitializableImmutableAdminUpgradeabilityProxy,
  shell created **2023-03-18**) → **implementation `0x3d4c56cdb97355807157f5c7d4f54957f0e9af44`,
  created 2024-10-17, and currently UNVERIFIED** (⛓️ confirmed both dates + verify-status). ·
  *Authority:* the Pool proxy moves all supplied liquidity on the addresses-provider/oracle's word;
  RDNT is an Aave-v2 fork with cross-chain (LayerZero/Stargate) plumbing. · *Money logic:* Aave-v2
  lending + OFT-bridged deposits. · *Shape:* 4 + 3; **also a live-state angle** — the impl was
  swapped *after* the Oct-2024 compromise, so the shell age (2023) is misleading; the age that matters
  is 2024-10-17, and the fresh impl is **unverified**, so the next stage should bytecode-match it
  against a verified sibling before reading. · *Role:* proxy = mover, impl = logic, plus
  AddressesProvider + AaveOracle siblings; **age each chain's impl separately.** · *Base:* Aave v2
  (Radiant). · *Prior review:* audited + **two incidents (Jan-2024 rounding, Oct-2024 key
  compromise)** → highest re-exploitation/silent-patch priority in this family. · *Disclosure:* Radiant
  Immunefi (live, large) → reportable.

- **🔎 resolve — Kinza Finance (BNB core; Ethereum listed), Seamless V1/V2 (Base), ZeroLend (Ethereum,
  Base), Sumer, Granary, UwU Lend (Ethereum)** · Aave-v2/v3 forks, all live per DefiLlama (Seamless V2
  ~$6.2M, ZeroLend ~$3.8M, Kinza ~$3.1M, Seamless V1 ~$0.53M). Each: resolve `Pool` proxy + its impl
  (age separately) + `AaveOracle`, then check newest reserves for rounding and each feed's source. **UwU
  Lend is a re-exploitation anchor** (two 2024 oracle drains) — if any UwU market is still live, the
  oracle path is the re-check. **Kinza core is on BNB → BSC gap** (source via Sourcify, but no cheap
  log/creation pin). · *Base:* Aave v2/v3. · *Prior review:* mixed; Seamless/ZeroLend audited, the
  smaller ones thin. · *Disclosure:* Seamless/ZeroLend have programs; UwU dormant.

---

### Family C — Router / aggregator / settlement: arbitrary external call over standing approvals

**This is the #2-weight shape family and the one directories are blind to** — a router holds **no
TVL** (it routes, it doesn't custody), so it never appears in a TVL ranking, yet it is often the single
most drainable contract on the chain because **funded wallets point infinite `Approval`s at it**. The
2026 exemplar: **SwapNet + Aperture Finance (Jan 2026, ~$13–17M, Base/BSC/Arbitrum)** — the router
exposed an **arbitrary-call** capability (insufficient validation of the external-call `target`/
`calldata` during swap execution), letting an attacker make the router `transferFrom` its users'
standing approvals. "Largest approval attack ever seen" outside phishing.

**On-chain read (the flag):** (1) sum live ERC-20 `Approval` logs whose `spender` = the router, and
the value behind them (this *is* the authority score); (2) in verified source, find any
permissionless path that forwards a caller-supplied `target.call(data)` / caller-supplied swap-step
struct without an allow-list, or an `address` parameter that reaches a `transferFrom` payer slot
(Shape 2). Worst when both are present.

**Shapes:** 2 (caller-supplied payer / target) + 7 (arbitrary call + standing authority).

**Watched/unwatched:** 0x, 1inch, CoW (`GPv2VaultRelayer 0xC92E8bdf79f0507f65a392b0ab4667716BFE0110`
holds the entire CoW approval set), UniswapX, ParaSwap are the *watched* exemplars — deprioritize, but
they define the read. The candidates are the **obscure aggregator / intent / RFQ-router forks** and
the **just-patched siblings of SwapNet/Aperture on chains that were not redeployed**.

- **⛓️ confirmed — authority-read exemplar (watched → deprioritized): CoW `GPv2VaultRelayer`
  (Ethereum)** `0xC92E8bdf79f0507f65a392b0ab4667716BFE0110` (verified, created **2021-06-08**,
  **0.000 ETH native**). · This is the shape made concrete: **zero balance, yet it holds the entire
  CoW-Swap standing-approval set** — every CoW trader's ERC-20 approval names this address as spender,
  so its authority score is enormous while its balance is nil. It is heavily watched (audited + Immunefi)
  so it is *not* a candidate — it is the **template for the read**: run `getLogs(topic0=Approval,
  topic2=spender)` against a router to score the authority pointed at it, then apply that read to the
  unwatched forks below.

- **🔎 resolve — SwapNet / Aperture Finance sibling deployments (Base, BNB, Arbitrum)** · The Jan-2026
  drain hit specific router deployments; the **flaw is in the router implementation, so every
  byte-identical sibling and every chain not yet redeployed is the same bug.** SwapNet's routers were
  **closed-source (unverified)** — per the "unverified isn't unreachable" rule, the next stage should
  pull bytecode and check for a verified twin on another chain first. · *Authority:* residual standing
  approvals still pointed at the old router addresses = live drain surface even post-incident (only
  *excluded* if every approval is revoked — check, don't assume). · *Shape:* 2 + 7. · **Both SwapNet
  (BSC/Base/Arb) and Aperture sit partly under the BSC/Base explorer gap** → hand over router addresses
  (from the post-mortems) + "scan residual Approval spenders + bytecode-match." · *Disclosure:* SwapNet/
  Matcha-Meta incident response is active → reportable via their security contact.

- **🔎 resolve — obscure DEX-aggregator & intent-settlement routers on all four chains** · The category
  is invisible to TVL, so enumerate by function, not directory: any `Router`/`Settlement`/`Executor`/
  `Reactor` that (a) accumulates infinite approvals and (b) exposes a generic external-call swap step.
  Named leads to fingerprint: OpenOcean, Firebird, Slingshot, Rango, Odos, Bebop, DODO RouteProxy,
  KyberSwap MetaAggregationRouter (Kyber has prior incident history), 1sec/SODAX bridge-routers. · The
  **unwatched** ones are the small multi-chain forks of these that copied the executor pattern. ·
  *Shape:* 2 + 7. · *Disclosure:* varies; larger ones have Immunefi, forks often none → outreach.

- **Method handoff for the next stage:** for each router, run the `Approval`-log sum on ETH/ARB
  (Etherscan V2 `getLogs`, topic0 = `Approval`, topic2 = spender) to rank by live authority; on
  Base/BSC use Blockscout/RPC where possible and flag where not.

---

### Family D — Cross-chain bridges & wrapped-asset minters: report the trust shape

The on-chain half is readable; the off-chain half is not. I surface the **shape and size of the
trust** and, critically, **what authority the contract holds if that trust is misplaced** (mint over a
wrapped asset, release over pooled reserves, admin over a token). 2026 exemplars: **Kelp DAO ($292M,
Apr 2026)** — a **1-of-1 LayerZero DVN** over rsETH minting (thin trust, on-chain-readable DVN config);
**Adshares ($May 2026)** — a bridge-minter **EOA** signing `wrapTo()` with **non-existent source-chain
txids** (a mint gated on a caller-asserted foreign txid with **no proof structure**).

**On-chain reads:** LayerZero OApp/OFT — read the `EndpointV2` send/receive **DVN config** (a 1-of-1
or single-required-DVN config = catastrophic thin trust); resolve the OFT `peer`s and whether the
receive path re-verifies a source event or merely checks a signature. Wrapped-asset minters — resolve
who holds `MINTER_ROLE` / the `wrapTo`/mint path (an EOA or 1-key multisig = finding on its face) and
whether release/mint requires a proof or only a caller-asserted id. On-chain-readable sub-shapes to
flag: hash collision (`abi.encodePacked` over ≥2 dynamic fields), caller-asserted txid, discarded
`staticcall`/proof success flag, permissionless prover registration.

**Shapes:** 1 (proof/signature) + 2 (caller-asserted source) — bridge sub-shapes.

- **🔎 resolve — small / old canonical bridges with residual reserves (Ethereum, Arbitrum)** —
  from the live bridge set, the thin-trust + incident-history + still-funded candidates:
  **Orbit Bridge** (~$16.4M; **multisig-compromise drain Jan 2024**, residual under the same trust
  model), **Meter Passport** (~$0.8M; prior incident), **Allbridge Classic** (~$1.0M; 2023 incident),
  **Knit Finance** (~$0.38M; 2023 incident), **pNetwork** (~$13.1M; prior incidents), **Nomad**
  (~$0.36M residual; the 2022 replay-root bug — *drained*, kept only if any approval/reserve remains).
  · *Authority:* each holds release authority over pooled reserves or mint authority over a wrapped
  asset, gated by a small signer set. · *Shape:* 1/2 bridge sub-shapes. · *Prior review:* all have
  **incident history** → re-check whether the trust model was actually changed. · *Disclosure:* mixed;
  several are semi-abandoned → outreach.

- **🔎 resolve — abandoned-but-funded bridge (Ethereum): Multichain** (~$37.6M residual) · Dead since
  Jul 2023 (operator arrest, keys frozen). This is the "abandoned with funds, no team" archetype — the
  authority is admin/MPC keys, not a code shape per se, and the funds are frozen, so it is **borderline
  excluded** (drained-corpse-adjacent). Handed over with the caveat: value here is only if a code path
  (not the frozen keys) can move the residual — a source read decides. · *Disclosure:* no team → not
  responsibly reportable; informational only.

- **🔎 resolve — LayerZero OFTs with thin DVN over a wrapped/LST asset (all four chains)** · The Kelp
  pattern generalizes: any OFT minting a wrapped or liquid-staking asset whose `EndpointV2` DVN config
  is 1-of-1 or single-required-DVN is a mint-authority finding on its face. Enumerate OApps with a
  configured single DVN; the **unwatched** ones are small-cap LST/wrapped OFTs, not the majors. **BSC/
  Base OFTs partly under the explorer gap** but DVN config is `eth_call`-readable via the endpoint on
  any chain → resolvable by RPC. · *Shape:* 1/2 bridge. · *Disclosure:* per-project.

- **🔎 resolve — wrapped-asset minters with EOA/1-key `wrapTo` + caller-asserted txid (the Adshares
  archetype)** · Any `wADS`-style wrapper where mint is gated on a signer asserting a source-chain txid
  with no on-chain proof. Enumerate wrapped-asset tokens whose `MINTER_ROLE` resolves to an EOA. ·
  *Shape:* 2 (caller-asserted source) + 1. · **This is exactly the sub-shape the tier over-indexes on;
  the smallest wrapped assets on BSC are the blind spot.**

---

### Family E — ERC-4626 & yield vaults: diverged share/redemption accounting

**Lineage:** ERC-4626 (`deposit`/`mint`/`withdraw`/`redeem` + `totalAssets`/`convertToAssets`). The
"known base, modified money-path" shape: a `withdraw` that **omits the allowance spend when
caller ≠ owner**; `totalAssets` read live off a **donatable** balance; **first-depositor share
rounding** on a vault that already holds a balance, or a round whose supply returned to zero on old
code; a NAV computed from a component the vault does not itself price; a fixed daily share price with
no re-entrancy invariant across deposit/withdraw.

**On-chain read:** diff the deployed `withdraw`/`redeem`/`totalAssets` against canonical OZ 4626 —
missing `_spendAllowance` in the caller≠owner branch, or `totalAssets = asset.balanceOf(this)`
(donatable) are the tells; `totalSupply()==0` with non-zero `totalAssets` = live first-depositor
condition. `previewRedeem`/`convertToAssets` on a shallow underlying = Shape 3 overlap.

**Shapes:** 4 (primary) + 3 (NAV from spot).

- **🔎 resolve — Superform (Ethereum + Arbitrum + Base, ~$17M)** · A **cross-chain 4626 meta-router**:
  it takes user approvals and routes deposits/withdrawals into many underlying 4626 vaults across
  chains → it sits at the **intersection of Family C (router holding approvals) and Family E (4626
  accounting)**. · *Authority:* standing approvals to the SuperformRouter + it drives share accounting
  across heterogeneous underlying vaults it does not itself price. · *Shape:* 4 + 2/7 (router). ·
  *Role:* SuperformRouter + SuperformFactory + per-vault `Superform` wrappers — resolve the router impl
  and one funded wrapper; **age impl separately** (Superform core ~2024). · *Prior review:* audited +
  Immunefi → *more watched*, so deprioritize the core and look at **individual community-created
  Superforms** (permissionless factory → long tail of unwatched wrappers). · *Disclosure:* Immunefi →
  reportable.

- **🔎 resolve — older/again-funded vault systems with prior incidents (Ethereum, Arbitrum)** ·
  **Harvest Finance** (~$15.6M; 2020 flash-loan incident), **Badger DAO** (~$11.9M; 2021 incident),
  **Pickle** (~$4.7M; 2020 incident), **Zunami** (~$0.54M; 2023 incident), **yAxis / YFII / Idle**
  (older Yearn-era vault code). · These are **ancient-hump vault code, funded, unwatched, some with an
  unpatched-class history.** Resolve each strategy/vault: check `totalAssets` donatability and any
  strategy that marks value from a spot LP. · *Base:* Yearn-v1/v2-era vault patterns + Convex/Curve
  strategy wrappers. · *Prior review:* audited long ago + incident history → silent-patch re-check. ·
  *Disclosure:* Harvest/Badger have programs; the smaller ones dormant.

- **🔎 resolve — Rari Capital / Fuse residue (Ethereum, ~$1.37M)** · Fuse pools are Compound-forks
  *and* the yield layer is 4626-adjacent; Rari is effectively abandoned post-2022, pools with residual
  balances and no maintainer = ancient-hump + empty-market donation overlap. · *Shape:* 4. ·
  *Disclosure:* abandoned → outreach only.

---

### Family F — Signature / proof-gated fund paths (the largest single class)

**Absent from bare tokens; present wherever a fund path is gated on a signature or a Merkle/settlement
proof.** The readable break shapes: an EIP-712 struct hash covering **fewer fields than the struct it
names** (unsigned fields are attacker-free); `SignatureChecker`/`isValidSignature` called against a
signer that arrives as a **caller-supplied parameter**; an `ecrecover` result **never compared to
`address(0)`**; `keccak256(abi.encodePacked(...))` over **two consecutive dynamic-bytes fields**
(collision, SWC-133); a `staticcall` whose success flag is **discarded**; a proof/settlement field
mismatch; or an entrypoint literally shaped like a bypass (e.g. a `prooflessDeposit`).

**On-chain read:** in verified source, count the fields in the `keccak256`/`_hashTypedDataV4` struct
hash vs. the struct definition; grep the signer argument's provenance (constant/registry vs. calldata);
check for the `== address(0)` guard after `ecrecover`; check `abi.encodePacked` arg types.

**Shapes:** 1 (primary).

- **🔎 resolve — RFQ / intent settlement resolvers (all four chains)** · Systems that fill on a
  **market-maker's signed quote**: Hashflow (⛓️ probed a Hashflow-era router `0xF6a94dfD0E6ea9d…`,
  created 2022-10-10, **unverified** — bytecode-match before reading), Bebop, native/PMM RFQ settlers,
  0x Settler, 1inch Fusion resolvers, UniswapX fillers. The signature *is* the authorization to move
  funds, so a struct-hash field omission or a caller-supplied signer = direct fund path. · *Authority:*
  these hold or pull standing maker/taker approvals. · *Shape:* 1 (+ 2 if the payer/counterparty is a
  parameter). · **Watched:** 0x/1inch/Uniswap majors → deprioritize; the candidates are the **obscure
  RFQ forks** and small-MM settlers. · *Disclosure:* majors have Immunefi; forks vary.

- **🔎 resolve — Merkle-proof claim / airdrop / reward distributors (all four chains)** · Contracts
  holding a large token balance released on a Merkle proof + `(index, account, amount)` leaf. The
  breaks: a leaf hashed with `abi.encodePacked` over adjacent dynamic fields (collision), a missing
  claimed-bitmap (Shape 5 overlap), or a root settable by a non-timelocked admin. These are
  **numerous, funded, and individually unwatched.** Enumerate `MerkleDistributor`/`claim`-bearing
  contracts with a live balance. · *Shape:* 1 (+ 5). · *Disclosure:* per-project.

- **🔎 resolve — smart-account / wallet mastercopies behind EIP-1167 clones (Ethereum, Base, Arbitrum)**
  · The "one signature-check flaw behind thousands of user proxies; the exploited address is a 45-byte
  EIP-1167 shell, the flaw is in the mastercopy" archetype. **Fingerprint the mastercopy, not the
  clone.** Enumerate wallet/account factories (Argent, Ambire, Safe-module wallets, ERC-4337 account
  factories) → resolve the singleton implementation → check its `isValidSignature`/validation path for
  a caller-supplied signer or an unchecked `ecrecover`. A flaw here is *every* deployed clone. ·
  *Authority:* the mastercopy defines who can move funds for all clones. · *Shape:* 1. · *Disclosure:*
  wallet vendors have programs (Safe/Argent) → reportable; obscure 4337 factories → outreach.

---

### Family G — Ancient, deprecated-but-funded (the ancient hump; ~a quarter of the tier)

Built, funded, and **walked away from for years**, un-re-examined. Deprecation + non-trivial exposure
is *itself* a candidate. These are the strongest **balance-as-authority** entries and the easiest to
confirm on-chain.

**On-chain read:** 30-day call volume collapsed vs. lifetime peak; balance or live-approval count
still non-trivial; no code/config change in N months; original compiler (0.4.x/0.5.x) = old code
without modern guards.

- **⛓️ confirmed — Aave V1 (Ethereum), still holding reserves** · LendingPoolCore
  `0x3dfd23A6c5E8BbcFc9581d2E864a68feb6a076d3` (proxy → impl
  `0x0e26e0bf83b4ec2cb0dcbc037bb01da5bb352eae`, created **2020-01-08**) — **⛓️ holds 927.9 ETH
  (~$2.1M) natively** plus ERC-20 reserves; LendingPool entry
  `0x398eC7346DcD622eDc5ae82352F02bE94C62d119` (→ impl `0x588790f64ac1424862081a56b8329decae206249`).
  · *Authority:* the Core custodies all Aave-v1 reserves and is the mover; it is an
  `InitializableAdminUpgradeabilityProxy` (proxy-admin authority is itself a re-check target —
  resolve the admin). · *Money logic:* Aave v1 money market (deprecated since v2/v3; **Solidity
  0.5.14** code). · *Shape:* ancient-hump balance authority; check the v1 flash-loan/reentrancy
  surface and the proxy-admin. · *Role:* Core + LendingPool + LendingPoolConfigurator siblings. ·
  *Base:* Aave v1 (canonical). · *Prior review:* audited long ago, **deprecated and unwatched** — the
  deployed state has not been re-checked against modern attack shapes. · *Disclosure:* Aave Immunefi is
  large **but scoped to current versions** — v1 may be out-of-scope → confirm scope, else Aave security
  contact / outreach.

- **⛓️ confirmed — Compound V1 MoneyMarket (Ethereum)** · `0x3FDA67f7583380E67ef93072294a7fAc882FD7E7`
  (non-proxy, **Solidity 0.4.24**, created **2018-09-26**, verified) · *Authority:* the original 2018
  Compound money market, immutable, still holding balances (DefiLlama ~$3M). · *Money logic:* v1
  supply/borrow with admin-set price oracle. · *Shape:* ancient-hump balance + the v1 admin-oracle
  (Shape 3/6). · *Base:* Compound v1 (canonical, immutable). · *Prior review:* superseded by v2/v3,
  **walked away from** → unwatched deployed state. · *Disclosure:* Compound Immunefi likely scopes v2/
  v3 only → confirm scope / outreach.

- **🔎 resolve — the ancient-hump long tail (Ethereum, mostly)** · From the live-but-old set worth a
  balance/authority read: **Flux Finance** (~$44.5M, aud=0 — a Compound-v2 fork for OUSG/RWA, notably
  **unaudited at this size**), **BiFi** (~$4.5M), **88mph** (~$0.35M, fixed-rate bond code), **Beta
  Finance V1** (~$0.46M), **ParaSpace Lending V1** (~$0.22M; ParaSpace had a 2023 incident),
  **Notional V2** (~$3.1M), **Wing Finance** (~$5.1M). · Each: confirm creation age, collapsed call
  volume, residual balance, and no-recent-config-change, then read for the deprecated-code shape. ·
  **Flux Finance is the standout (⛓️ confirmed)**: Comptroller/Unitroller
  `0x95Af143a021DF745bc78e845b54591C53a8B3A51` (proxy → impl
  `0xdc7b90593cafe7a919d22b903fed21bf27da9719`, created **2023-01-30**, Solidity **0.5.17** — same
  toolchain as Compound/Iron Bank, confirming Compound-v2 lineage). $44.5M TVL, **aud=0**, RWA
  (OUSG/OMMF) collateral → **high balance authority + Family-A donation shape + unaudited at scale**.
  It straddles Family A (resolve `getAllMarkets()` and flag low-supply `fToken` markets + the price
  oracle that values RWA collateral) and Family G (deprecated-code hump does *not* apply — this is a
  fresh-ish 2023 deploy, so weight it as unaudited-new-code rather than ancient). · *Disclosure:* Flux
  (Ondo Finance) has a security contact → reportable.

---

### Family H — Free-to-manufacture eligibility (Shape 5)

A reward / claim / redeem path gated **only** on the caller's *current* balance, on a caller-supplied
array/ID set with **no de-duplication**, on a **checkpoint written after payout**, or with **no
per-address ledger** — so a fresh address, a duplicated ID, or a repeated call always qualifies.
Includes the Sybil-farmable incentive where fresh addresses (cheap under EIP-7702) each clear a
per-address threshold.

**On-chain read:** in source, check the claim path for (a) a `claimed[address]`/bitmap ledger, (b)
dedup on any caller-supplied `ids[]`, (c) checkpoint-before-payout ordering, (d) snapshot vs.
live-`balanceOf` gating.

**Shapes:** 5 (+ 1 where a proof is involved).

- **🔎 resolve — staking / restaking / points reward distributors on all four chains** · The category
  is large and mostly unwatched. Leads: LST/LRT reward and points contracts (restaking wave), farm
  reward distributors in DefiLlama's **Farm (244)** and **Launchpad (241)** categories, and any
  `claimRewards(ids[])` that trusts a caller-supplied id array. · *Authority:* these hold or mint the
  reward token; a manufacture bug drains the emission. · *Base:* MasterChef-derived and custom reward
  code. · **Fresh-hump-heavy and BSC/Base-heavy → partly under the explorer/firehose gap.** ·
  *Disclosure:* per-project.

---

### Family I — Live-state / config shapes (read storage, not just source) (Shape 6)

These are invisible to a source-only reader and carry lead time; each is one `eth_call` or one
`getStorageAt` from detection.

**On-chain reads & candidates (method-led, since these are state, not a fixed list):**

- **Uninitialized proxy / diamond facet** — read the EIP-1967 implementation slot
  (`0x360894...bbc`) and the initializer-guard storage; an impl set while the guard is still zero =
  a callable `initialize*` on a live proxy (Parity-class). Sweep **recently-deployed proxies** (fresh
  hump) on Base/Arbitrum/Ethereum for this. *Shape 6.*
- **Oracle configured pool → `address(0)`** — the "one such config sat live for three months"
  archetype: a Uniswap-v3-based oracle whose configured fee tier ∉ {100, 500, 3000, 10000}, so
  `factory.getPool()` returns zero and the consumer prices reserves at zero. Resolve any v3-TWAP
  oracle's stored fee tier and `getPool()` result. *Shape 6 + 3.*
- **Admin / owner at `address(0)` where a check needs it non-zero.** Read `owner()`/admin slots.
- **Governance proposal sitting in a public timelock queue** that upgrades a proxy or reassigns a
  role on a contract with **live approvals** — enumerate queued (not-yet-executed) timelock ops on
  major protocols; a queued upgrade to an approval-holding contract has built-in lead time. *Shape 6.*

Handed over as reads because the surviving instances are found by scanning state on the day, not from
a static directory — and the freshest ones sit in the new-deployment firehose I could not tap.

---

### Family J — Safe modules & standing spend/credit delegation

The archetype: an **enabled Safe module with spend rights over one or many Safes** (one such module
held **wildcard authority over 86+ Safes and held nothing itself**), or a non-zero **Aave
`CreditDelegation`** pointed at a contract, or a permissionless function that spends a standing
allowance. Zero-balance, total control.

**On-chain read:** enumerate `enabledModules` across Safes (via the Safe `ModuleManager` events /
`getModulesPaginated`), flag any module contract with a permissionless `execTransactionFromModule`
path; read `variableDebtToken.borrowAllowance(delegator, delegatee)` for standing credit delegation
into a contract.

**Shapes:** 7 (arbitrary spend over standing authority) + 2.

- **🔎 resolve — treasury/automation Safe modules on Ethereum & Arbitrum** · DAO treasuries,
  vesting/streaming (Sablier/Superfluid-adjacent), and DeFi automation (DCA, auto-compounders) commonly
  install modules with broad `execTransactionFromModule` rights. Enumerate module installs; flag any
  module whose call path is reachable permissionlessly or whose own admin is a single key. · *Authority:*
  the module can move the Safe's full balance. · **Requires an indexer for module events → partly under
  my log gap; handed over as the read to run.** · *Disclosure:* per-treasury; often a named team →
  reportable.

---

## 3. Cross-cutting: re-exploitation & silent-patch watchlist

The tier's two highest-signal historical patterns, pulled together so the next stage prioritizes them:

- **Re-exploitation (same unpatched path, again).** **Onyx** (Compound donation, twice — lending now
  drained, exemplar only), **Radiant** (rounding Jan-2024 then key-compromise Oct-2024 — *live*, impl
  swapped 2024-10-17 and unverified), **UwU Lend** (oracle, twice in 2024), **Ionic** (exploited
  Feb-2025 — check patch vs. redeploy). A contract exploited once through a path never fixed is a prime
  candidate for the same path again.
- **Silent patch / package lag.** Flag any deployed implementation that lags the current upstream of
  the package it came from (a flaw fixed quietly in a newer library release while the deployment still
  runs the old package is reachable until upgraded). Concretely: OZ-4626/`ECDSA`/`SignatureChecker`
  versions in Family E/F candidates, LayerZero OApp versions in Family D, and the Compound-v2
  empty-market-guard adoption in Family A. The Radiant unverified impl and the SwapNet closed-source
  routers are the first bytecode-match jobs.

---

## 4. Priority ordering rationale (for the next stage's read budget)

Ranked on **authority × unwatched × live-state-match**, not TVL or headline loss:

1. **Family C routers + Family D wrapTo/OFT minters** — highest weight shapes (2/1), authority wildly
   exceeds balance, and the obscure/forked members are genuinely unwatched. Zero-TVL, so directories
   miss them entirely.
2. **Family A/B isolated & newly-listed markets + obscure forks** — a proven, *recurring* 2024–2026
   money path; the per-market empty-supply condition is unwatched even on "watched" protocols.
3. **Family F signature/proof paths** — largest single class; the mastercopy-behind-clones and
   obscure-RFQ members are high-authority and under-reviewed.
4. **Family G ancient-funded** — easiest to confirm (Aave V1 ⛓️ 927 ETH, Compound V1 ⛓️ $3M, Flux
   $44.5M/aud=0), lowest scrutiny, real balances.
5. **Family E vaults, Family H eligibility, Family I state, Family J modules** — solid shape matches;
   several need the log/state scans I flagged as partly out of reach here.

---

## 5. What this pass structurally missed (say it plainly)

- **BNB Chain is under-enumerated** — no free explorer for logs/creation dates; Venus isolated pools,
  Kinza core, PancakeSwap-fork routers, and the SwapNet/Aperture BSC deployments are named by role but
  not fully aged or authority-summed. This is the biggest gap.
- **The fresh-hump firehose** — code exploited within days of deploy needs the new-verified-contract
  stream per chain; a known-address re-scan (what I did) misses it. Base and BSC fresh deploys are the
  most under-represented.
- **Directory floor** — DefiLlama `/forks` is paywalled and `forkedFrom` is near-empty on the free
  feed, so fork lineage is reconstructed, and sub-listing-threshold micro-forks appear only as
  "resolve all clones."
- **Approval / module / timelock log scans** — named as the exact read to run per family, but not
  fully executed on Base/BSC (and not at all where the free log API is absent). The router-approval
  ranking (Family C) and Safe-module enumeration (Family J) are the biggest deferred reads.

---

*Appendix — on-chain anchors confirmed this pass (chain · address · created · note):*

- ETH · `0x3dfd23A6c5E8BbcFc9581d2E864a68feb6a076d3` · 2020-01-08 · Aave V1 Core, proxy→`0x0e26e0bf…`, **holds 927.9 ETH**
- ETH · `0x398eC7346DcD622eDc5ae82352F02bE94C62d119` · 2020-01-08 · Aave V1 LendingPool, proxy→`0x588790f6…`
- ETH · `0x3FDA67f7583380E67ef93072294a7fAc882FD7E7` · 2018-09-26 · Compound V1 MoneyMarket (0.4.24, non-proxy)
- ETH · `0xAB1c342C7bf5Ec5F02ADEA1c2270670bCa144CbB` · 2020-12-04 · Iron Bank Unitroller, proxy→`0xcb9ab119…`
- ETH · `0xbd6f5add9b7a6eb151933cb4efd50be4eca71451` · 2023-03-13 · Iron Bank PriceOracleProxyIB (the mover)
- ETH · `0x8B53Ab2c0Df3230EA327017C91Eb909f815Ad113` · 2021-02-25 · dForce Controller, proxy→`0xbd0ed2f6…`
- ETH · `0x95Af143a021DF745bc78e845b54591C53a8B3A51` · 2023-01-30 · Flux Finance Unitroller (Compound-v2 RWA fork, aud=0, ~$44.5M), proxy→`0xdc7b9059…`
- ETH · `0xC92E8bdf79f0507f65a392b0ab4667716BFE0110` · 2021-06-08 · CoW GPv2VaultRelayer (Family C read exemplar: 0 balance, holds entire CoW approval set)
- ARB · `0xF4B1486DD74D07706052A33d31d7c0AAFD0659E1` · shell 2023-03-18 · Radiant V2 Pool; **impl `0x3d4c56cdb9…` created 2024-10-17, UNVERIFIED**
- BASE · `0x05c9C6417F246600f8f5f49fcA9Ee991bfF73D13` · Ionic Unitroller → impl Comptroller `0xc63Ee58A…` (verified)
- ETH · `0xA2cd3D43c775978A96BdBf12d733D5A1ED94fb18` · 2022-03 · XCN/"Chain" token (Onyx context; lending side ≈ drained)
