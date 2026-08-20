# On-chain scanners (reproducible)

Pure-Python, no external deps (Keccak-256 is implemented in `kc.py`). Reads go through Etherscan V2
(Ethereum/Arbitrum/Polygon) and public RPC (Base/BNB). Set the Etherscan V2 key in `chain.py` (`KEY`).

- `kc.py` — Keccak-256 + `sel()`/`topic()` helpers.
- `chain.py` — hardened multi-chain toolkit (call/storage/getcode/getlogs/creation/verified) with
  retry + `None` sentinel on failure (never fabricates a 0), plus ABI encode/decode helpers.
- `scan_approvals.py`, `scan_appr_wide.py`, `scan_arb_appr.py` — standing-approval authority by spender.
- `allowance_confirm.py` — reads CURRENT `allowance(owner,spender)` for recent approvers (event
  volume != live authority).
- `scan_empty.py` + `reverify.py` — Compound-fork thin/empty collateral-enabled market scan (+ ghost
  re-verification).
- `scan_implage.py` — EIP-1967 impl age vs shell + verification divergence.
- `scan_fingerprint.py` — `eth_getCode` -> Keccak, group identical bytecode across chains.

Run: `python3 scan_fingerprint.py` etc. See `../SCAN_REPORT.md` for what each produced on 2026-08-20.
