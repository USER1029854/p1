# Audit Targets — start here  (run 4: fresh & at-risk, prevention-first)

**What changed this run.** Prior runs leaned on already-hacked / deprecated contracts. Those are low
prevention value — the money already left, and everyone's watching. This run pivots to the real
prevention target: **live, funded, freshly-deployed, under-reviewed protocols where the bug is still
in the code and nobody has drained it yet.** Conversion in this tier is 1–3%, so this is a *wide* list
(379 candidates in [`at_risk_protocols.csv`](./at_risk_protocols.csv)) with **deep hypotheses on the
top ~25**. Read a target, load the address, audit the hypothesis. For the **full set of source-bearing
contracts to load per target** (impl, upgrade authority, oracle, minter, vault — the whole surface, not
one address), see [`AUDIT_SCOPE.md`](./AUDIT_SCOPE.md).

> Honesty up front: a surfacing pass can't prove a bug. Each target below is **a specific hypothesis +
> the on-chain signal that made it worth your time**, not a confirmed finding. The 1-in-30-to-100 that
> converts is what you're hunting; my job is to make the 30–100 the *right* ones. On-chain reads:
> 2026-08-20.

---

## How I chose these — what makes a *live, unhacked* protocol risky (my rubric)

Not "was it hacked" but "what would make it hackable, and why hasn't anyone looked":

1. **Authority concentration** — a funded upgradeable contract whose upgrade admin / owner / minter is
   a single EOA (not a multisig/timelock). One key = total loss, and it's audit-independent.
2. **Fresh + unaudited + real TVL** — new code (listed < ~12 mo) holding 7–9 figures with `aud=0`.
   Untested money math is where new bugs live; nobody has re-read the *deployed* state.
3. **Novel / complex money mechanics** — leverage loops, delta-neutral basis, self-repaying debt, RWA
   NAV, cross-margin. More moving parts, more invariants to break; forks of these copy the bug.
4. **Caller/keeper-settable pricing** — perps & synths whose mark price comes from a keeper or a
   signed message (the KiloEx class). If the price setter's auth is weak, positions mint free PnL.
5. **Mint authority over an off-chain-backed token** — RWA / synthetic stablecoins where a role can
   mint the token; if the mint check or the collateral-proof is wrong, it depegs / prints unbacked.
6. **Upgradeable + weak governance / short timelock** — the code you audit today isn't the code that
   runs tomorrow.
7. **Unverified code holding real money** — you can't review what you can't read; get the bytecode.
8. **Composability blast radius** — a vault that routes into other protocols inherits their bugs.

The 379-row CSV is scored on a computable proxy of these (unaudited + fresh + high-risk-category +
multi-chain + unwatched TVL band). The deep-dives below add the mechanic-specific hypothesis a scanner
can't.

---

## TIER 1 — deep-dive targets (fresh, funded, high-risk; audit these first)

Format: **what it is · money mechanic · AUDIT THIS (hypothesis) · signal · chain · address**
("core" = the money contract; "token → resolve" = DefiLlama gives the token, resolve the minter/vault
via its `MINTER_ROLE`/`owner` or docs before auditing).

### Synthetic / basis-trading stablecoins — *does minted supply stay backed?*
The recurring bug class: mint/redeem accounting that lets supply exceed collateral, or a collateral
NAV read from a source the protocol doesn't control.
- **Aegis YUSD** — Basis-trading synthetic USD, $34M, aud=0, listed 2025-04. **Audit this:** the
  `AegisMinting` contract — the collateral-in vs YUSD-out accounting, the redeem queue, and the
  custody/oracle that asserts off-chain collateral. Token → resolve minter. [ETH]
- **Resolv USR** — delta-neutral stablecoin, $6M + RLP insurance layer, aud=0. **Audit this:** the
  RequestManager/minter: can USR be minted beyond the delta-neutral collateral? Is RLP (the junior
  tranche) correctly subordinated on loss? Token `0x259338656198ec7a76c729514d3cb45dfbf768a1` → resolve minter. [ETH]
- **Usual ETH0** — synthetic ETH, aud=0, listed 2026-02. **Signal:** the core contract shows a
  `delegatecall` + **2× arbitrary `.call(data)`** and 3 sweep paths — verify the external-call targets
  are allow-listed and the collateral manager can't be steered. Token `0xC4441c2BE5d8fA8126822B9929CA0b81Ea0DE38E`. [ETH]
- **BounceBit Prime / CeDeFi Yield** ($11M / $258M, Basis, aud=0), **BitFi Basis** ($218M), **Aegis** —
  same class at scale; the CeDeFi ones hinge on how on-chain accounting mirrors an off-chain position.

### Self-repaying loans / CDPs — *debt accounting & liquidation*
- **Alchemix V3** — self-repaying loans, $35M, listed 2026-04 (brand-new version). **Audit this:** the
  V3 debt-reduction-by-yield accounting and the transmuter; a rounding/credit bug lets debt vanish or
  over-borrow. Token `0xdBdb4d16EdA451D0503b854CF79D55697F90c8DF` → resolve `AlchemistV3`. [ETH]
- **mStable V2** — CDP, aud=0. **⚠ concrete signal:** the resolved implementation uses an `initializer`
  **without `_disableInitializers()`** — classic uninitialized-implementation risk (Shape 6). **Audit
  this:** confirm the implementation can't be initialized by an attacker to seize the proxy. `0xca1207647ff814039530d7d35df0e1dd2e91fa84`. [ETH]
- **Cooler Loans** — Olympus lending, **$216M**, listed 2026-02. **Audit this:** the Clearinghouse/Cooler
  terms & the gOHM collateral valuation in the new accounting (DefiLlama address is the OHM token;
  resolve the Clearinghouse). [ETH]
- **Templar Protocol** ($26M lending, 2025-08, aud=0), **BIMA CDP** ($8.6M), **Threshold thUSD**,
  **Inverse Frontier** — CDP/lending accounting on fresh unaudited code.

### Perps / options — *keeper- or caller-settable pricing (the KiloEx class, applied to fresh perps)*
The prevention question: is the mark/settlement price set by a keeper or a signed message, and is that
auth tight? A weak setter = free PnL.
- **Extended Perps** ($121M, 2025-03, aud=0), **AZverse Perps** ($51M, listed **2026-07-31**, aud=0),
  **Antarctic** ($9.5M, aud=0), **Evedex** ($2.9M, aud=0), **Apex Omni** ($29.7M, aud=0). **Audit this
  (each):** the price-feed contract — is `setPrice`/settlement gated by a robust signature/role, or a
  single keeper / forwarder (KiloEx pattern)? Then the LP-vault accounting on open/close. [ETH/ARB]
- **Rysk V12** ($65M Options Vault, aud=0), **Deri V4** ($7.5M Options, BSC), **IntentX/SYMMIO**
  (SYMM diamonds — check uninitialized facet). Options settlement pricing + collateral.

### Leveraged / yield vaults — *4626 accounting & strategy authority*
- **Yield Basis** — leveraged BTC farming, **$148M**, Curve ecosystem, listed 2025-09, aud=0. **Audit
  this:** the leverage-loop math and the crvUSD/LP oracle it borrows against — leveraged AMM positions
  are the densest source of oracle/rounding invariants. Token `0x01791f726b4103694969820be083196cc7c045ff` → resolve the AMM/leverage core. [ETH]
- **Avalon Superearn** ($30M Yield, aud=0). **Signal:** resolved impl `AvalonMintable` shows an
  **arbitrary `.call(data)`** path — verify it can't be steered to move vault funds. `0x5c8d0c48810fd37a0a824d074ee290e64f7a8fa2`. [ETH]
- **Spectra V2** ($35M interest-rate/yield, Base, PROXY), **RockSolid Network** ($24M), **Syntropia**
  ($5M), **Zoo Finance** ($19M), **Royco V1/V2** ($1.5M/$23M), **Nerona**, **TermFinance Vaults**
  ($12M). **Audit this (each):** 4626 `withdraw`/`totalAssets` divergence from canonical, first-depositor
  rounding, and who controls the strategy/allocation.

### RWA — *mint authority & redemption*
- **KAIO** ($41M RWA, aud=0). **Signal:** resolved impl `KaioToken` exposes **4× sweep/rescue**
  functions — verify each is tightly access-controlled (a loose one drains reserves). `0x00bac91fd8f5b4a0dc03c8021139b76f6549ee7e`. [ETH]
- **Stobox** ($14M RWA, Arbitrum). **⚠ concrete signal: the core contract is UNVERIFIED** — get the
  bytecode / demand source before this holds more. `0xa6422e3e219ee6d4c1b18895275fe43556fd50ed`. [ARB]
- **GAIB** ($20M RWA, AI-compute backed, novel, aud=0), **Theo Network thBill** ($26M), **Clearpool
  TPOOL** ($20M), **Lista RWA**, **eva Markets**. **Audit this:** who holds mint authority over the RWA
  token, and how is the off-chain collateral asserted on-chain?

### Uncollateralized / novel
- **Wildcat Protocol** ($7.3M, Uncollateralized Lending, aud=0) — risk is *by design*: lenders trust
  borrowers. **Audit this:** the market-parameter & withdrawal-cycle access control; a borrower-side
  auth bug is catastrophic here. [ETH]
- **GETH** (LST, aud=0). **Signal:** `StakeToken` shows `transferFrom(param_from)` — verify it's not an
  arbitrary-from pull. `0x3802c218221390025bceabbad5d8c59f40eb74b8`. [ETH]

---

## TIER 2 — the volume list (breadth for the 1–3% conversion)

**379 funded ($500k–$150M), risky-category protocols on BNB/ETH/ARB/Base, ranked by profile-risk —
now with the contract for each**: [`at_risk_protocols.csv`](./at_risk_protocols.csv) carries
`address · address_chain · contract_name · is_proxy · implementation · verified` (resolved on-chain
for the 192 that list a contract; the other 187 need the address pulled from the protocol's docs).
Score = unaudited + fresh + high-risk-category + multi-chain + unwatched-TVL-band. Sort by `score`,
take the address, audit. `verified=NO` rows are blind spots (get bytecode first). Top of the list is
the Tier-1 pool above; the long tail (scores 4–5) is your breadth. Note: a listed `address` is often
the protocol's main/token contract — for the full money-contract surface use `AUDIT_SCOPE.md`.

Highest-scoring beyond the deep-dives: Ledgity Yield, Metronome Synth, Native Credit Pool, Hyperbeat
USD, Rezerve Lending, Everything (ARB lending, `EV` impl 245KB), Fraxlend, Penpie, Sushi BentoBox,
Blur Lending, BTCFi CDP, SMARDEX USDN, Zircuit, Acre, Lazy, Flex, AirPuff, Rho X LP Vault.

---

## Concrete on-chain flags found this run (triage — verify the access control before trusting)

| Protocol | Chain | Flag | Address |
|---|---|---|---|
| **mStable V2** | ETH | `initializer` **without `_disableInitializers`** (impl-init / Shape 6) | `0xca1207647ff814039530d7d35df0e1dd2e91fa84` |
| **Stobox** (RWA $14M) | ARB | **core UNVERIFIED** | `0xa6422e3e219ee6d4c1b18895275fe43556fd50ed` |
| **Usual ETH0** | ETH | delegatecall + **2× arbitrary `.call(data)`** | `0xC4441c2BE5d8fA8126822B9929CA0b81Ea0DE38E` |
| **Avalon Superearn** | ETH | arbitrary `.call(data)` in `AvalonMintable` | `0x5c8d0c48810fd37a0a824d074ee290e64f7a8fa2` |
| **KAIO** (RWA $41M) | ETH | 4× sweep/rescue paths | `0x00bac91fd8f5b4a0dc03c8021139b76f6549ee7e` |
| **GETH** (LST) | ETH | `transferFrom(param_from)` | `0x3802c218221390025bceabbad5d8c59f40eb74b8` |

These are **triage flags, not findings** — the pattern scanner over-flags common idioms (a `rescue`
behind `onlyOwner` is fine; a permit `ecrecover` is guarded in the OZ lib). Confirm the access control
and the data-flow before spending real time.

---

## Methodology & honest limits

- **New tooling this run** (`scanners/`): a keccak-driven authority scanner (proxy admin / owner
  classified EOA vs Safe vs timelock) and a **source dangerous-pattern scanner** (delegatecall,
  arbitrary call, `transferFrom(from)`, ecrecover-without-`address(0)`, spot-oracle reads, missing
  `_disableInitializers`, sweep/rescue), with impl auto-resolution.
- **The address-resolution gap is the real limit:** DefiLlama exposes the governance *token*, not the
  vault/minter/pool. For token-layer scans that's shallow; the Tier-1 hypotheses name the money
  contract to resolve. The deepest audit (reading each core's source) is the step you're about to do.
- **Pattern-scan false positives:** `sweep/rescue` and permit-`ecrecover` are ubiquitous and mostly
  benign — I've de-weighted them and surfaced only the sharper flags above.
- **BNB is still the explorer gap** (Sourcify + RPC only); several BNB perps/forks are under-covered.
- Full dataset: `at_risk_protocols.csv` (379). Prior-run detail (hacked/deprecated, demoted): see below.

---

## Prior-run targets (runs 1–3) — demoted, kept for reference

Lower prevention value (already exploited or deprecated), but real live authority in a few: the dead
**Multichain** routers with live ∞ approvals, **Radiant V2**'s unverified 2024-10-17 impl, **Flux**
(unaudited RWA Compound fork), the ancient-funded **Aave V1 / Compound V1**. Full detail in
[`ADDRESS_BOOK.md`](./ADDRESS_BOOK.md) and [`SCAN_REPORT.md`](./SCAN_REPORT.md). Per your steer, this
run does not lead with them.
