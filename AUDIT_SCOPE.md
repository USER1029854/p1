# Audit Scope — the full source-bearing surface per target

Companion to `AUDIT_TARGETS.md`. That file gives you *what to look for*; this one gives you
*everything to load into the audit* — for each target, the set of **source-bearing contracts in
scope**: the entry contract, its implementation, its upgrade authority, and the dependencies it
resolves through.

**Why this matters — the MAYAChain lesson (2026-08-18).** That drain chained **six** bugs across six
source files — a voter-clobber in `handler_deposit.go`, an off-by-one height loop in
`handler_common_outbound.go`, an uncapped subsidy in `helpers.go`, a set-pool-before-send ordering
bug, a swallowed error with no rollback, and pool-unit dilution in the AMM math. **No single file
contained the exploit** — the value leaked at the *seams* between contracts: the handler that trusts
the voter, the pool that trusts the subsidy, the module that trusts the handler's success. An audit
scoped to one contract misses it. So scope the whole interacting surface, one hop out, and audit the
boundaries.

**How each scope was resolved (on-chain, 2026-08-20):** from the entry I read the EIP-1967
implementation + admin slots, `owner()`/`authority()`, and a battery of dependency getters
(`oracle()`, `asset()`, `vault()`, `controller()`, `minter()`, `priceFeed()`, `addressesProvider()`,
…). Each resolved address is labelled by how it was found, its contract name, and whether its source
is **verified** (audit it) or **UNVERIFIED** (get bytecode / demand source first — a blind spot).

> **Honest limit, up front.** Most of these protocols' DefiLlama addresses are the *token* (or a
> leaf proxy), so on-chain getters surface the **implementation + upgrade authority** but **not** the
> deeper money contracts (minter, vault, oracle, controller) — a token doesn't expose those via
> getters. For those, pull the protocol's **deployed-addresses doc / GitHub** (entry point + what to
> look for is given per target). The full scope = what's resolved below **+** that address list.
> And one more hop everywhere: a `ProxyAdmin`/`SafeProxy` admin is a *contract* — resolve **its**
> `owner()`/signers to find the ultimate upgrade key (EOA = single-key risk; multisig = better).

---

## Run-4 fresh targets — resolved scope skeletons

### Avalon Superearn (Yield $30M) — ETH `0x5c8d0c48810fd37a0a824d074ee290e64f7a8fa2`
- **implementation** `0x3228995749610bea00b59c44f8d1df21c14027f1` — `AvalonMintable` (verified) ← audit this
- admin (EIP-1967) `0x1792f73b586f3e931b51826195ff015a23c86009` — `ProxyAdmin` (verified)
- owner `0xba7468d7accd1bb2e346a003ab1713c3d8c4da6d` — `SafeProxy` (multisig — good; resolve signers)
- **Complete the scope:** the `AvalonMintable` impl showed an arbitrary `.call(data)` — trace its
  target(s); and resolve the vault/strategy this token settles against (Avalon docs).

### Resolv USR (Basis stablecoin) — ETH `0x259338656198ec7a76c729514d3cb45dfbf768a1`
- **implementation** `0x5ac0551f79d10f9f2a7ce74eeffad23336060b9a` — `ResolvToken` (verified)
- admin (EIP-1967) `0x8f3c8cfaa08f0ddc6fb988e2dfec324e11e4be37` — `ProxyAdmin` (verified)
- owner `0x6025f799271d45af21953f9d8297e6e5efdc4a0f` — `SafeProxy` (multisig)
- **Complete the scope (the money path):** USR is minted by a **RequestManager / Minting** contract
  and backed by a delta-neutral collateral pool + **RLP** junior tranche — none exposed from the
  token. Pull `RequestManager`, the collateral custody, the oracle, and `RLP` from Resolv's docs;
  those are where the mint-vs-backing invariant lives.

### Usual ETH0 (Synthetic) — ETH `0xC4441c2BE5d8fA8126822B9929CA0b81Ea0DE38E`
- **implementation** `0x2b65f9d2e4b84a2df6ff0525741b75d1276a9c2f` — `Usual` (verified) ← delegatecall + 2× arbitrary `.call(data)` flagged; trace targets
- admin (EIP-1967) `0x430a2712cefaac8cb66e9cb29ff267cfcfa38a42` — `ProxyAdmin` (verified)
- **Complete the scope:** ETH0 is a collateral-backed synth — resolve the `DaoCollateral`/minting
  module + the collateral registry + oracle from Usual's deployed addresses.

### mStable V2 (CDP) — ETH `0xca1207647ff814039530d7d35df0e1dd2e91fa84`
- **implementation** `0x50a6b25101173b41e41c1a30a5bae42f213b2687` — `DHedgeTokenV1` (verified)
- admin `0x5a76f841bfe5182f04bf511fc0ecf88c27189fcb` — `Proxy` (verified)
- **⚠ audit first:** the impl uses `initializer` **without `_disableInitializers()`** — confirm the
  implementation can't be initialized by an attacker to seize the proxy (Shape 6). (Note: DefiLlama's
  label may be off — the resolved impl is a dHEDGE token; verify you're on the right mStable contract.)

### Cooler Loans / Olympus (Lending $216M) — ETH `0x64aa3364F17a4D01c6f1751Fd97C2BD3D7e7f1D5`
- **authority** `0x1c21f8ea7e39e2ba00bc12d2968d63f4acb38b7a` — `OlympusAuthority` (verified) ← the access-control contract; audit who holds each role
- Note: the DefiLlama address is the **OHM token**, not the lending logic. **Complete the scope:** pull
  `Clearinghouse`, `CoolerFactory`, `Cooler`, and the gOHM collateral + the price it's valued at from
  Olympus's addresses — the new-accounting risk lives there, not in OHM.

### Everything (ARB Lending) — `0xe7e7e741c23a4767831a56a8c99f522c5ac1e7e7`
- **implementation** `0xdcca77dd282667561c4c611ff5de697002515dc1` — `EV` (verified, 245KB — big/complex) ← audit this
- owner `0xc6b1e7f76dfc2eee534200a0182f136775789142` — `GnosisSafeProxy` (multisig)
- **Complete the scope:** the `EV` impl is a large lending contract — resolve its oracle / interest-rate
  model / collateral registry from its own getters or the project docs.

### KAIO (RWA $41M) — ETH `0x00bac91fd8f5b4a0dc03c8021139b76f6549ee7e`
- Leaf/token — on-chain scope = entry + impl. **Signal:** `KaioToken` impl exposes **4× sweep/rescue**
  paths — resolve the minter/manager (via `RoleGranted` holders or docs) and audit each sweep's access
  control (a loose one drains reserves).

### Yield Basis (Leveraged $148M) — ETH `0x01791f726b4103694969820be083196cc7c045ff`
- Leaf/token (`YBToken`) — the **money contract is the leverage/AMM core, not the token.** Resolve the
  Yield-Basis AMM + the crvUSD/LP oracle it borrows against (Curve-ecosystem; docs/GitHub) — that's
  where the leverage-loop and oracle invariants live.

### Stobox (RWA $14M) — ARB `0xa6422e3e219ee6d4c1b18895275fe43556fd50ed`
- **⚠ UNVERIFIED** — leaf, no source. Get the bytecode / demand source before this is in any audit;
  an unverified $14M RWA contract is itself the finding.

---

## Prior-run targets already scoped in full

These have their complete address surface (impl + admin + **oracle** + **markets/pools + underlyings**)
in [`ADDRESS_BOOK.md`](./ADDRESS_BOOK.md) — good worked examples of a full scope:
- **Flux Finance** — comptroller + impl + admin + oracle + 5 markets (each with underlying).
- **Iron Bank** — unitroller + impl + admin + `PriceOracleProxyIB` + 24 markets.
- **Ionic (Base)** — comptroller + impl + admin + oracle + 28 markets (restaking collateral).
- **Radiant V2** — pool proxy + the unverified 2024-10-17 impl (+ resolve AddressesProvider→AaveOracle).

---

## How to complete a scope (the repeatable procedure)

1. **Entry → impl → admin/owner** (done above via EIP-1967 slots + `owner()`).
2. **One more hop on authority:** resolve `ProxyAdmin.owner()` / the Safe's signers+threshold — that's
   the real upgrade key. EOA = single-key risk; low-threshold multisig = elevated.
3. **Money contracts a token won't expose:** pull the protocol's **deployed-addresses doc / GitHub**
   for the minter, vault, controller, oracle, price feed, and any strategy/module. These are the ones
   that move value and set prices — the MAYAChain "seams."
4. **Privileged role-holders:** enumerate `RoleGranted(role, account, sender)` logs on the token /
   core to find every minter/manager/pauser contract, and add each to scope.
5. **Flag every UNVERIFIED contract in a value path** — it's a blind spot and often the finding.
6. **Load all of it together** and audit the *boundaries* — who trusts whose output — not just each
   contract in isolation.

`scanners/scope_fast.py` reproduces step 1 for any address; extend it with the getter you need.
