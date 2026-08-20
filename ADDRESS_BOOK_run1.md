# Address Book — Run 1 (initial candidate queue)

Per-run address book. Scope: the on-chain anchors confirmed while building the initial
`CANDIDATE_QUEUE.md` (commit `62e4503`). All ⛓️ read on-chain 2026-08-20. The full resolved detail
(admins, all markets, underlyings) was added in Run 3 — see `ADDRESS_BOOK_run3.md` / `ADDRESS_BOOK.md`.

| Protocol | Chain | Role | Address | Created | Note |
|---|---|---|---|---|---|
| Aave V1 | ETH | LendingPoolCore (proxy) | `0x3dfd23A6c5E8BbcFc9581d2E864a68feb6a076d3` | 2020-01-08 | **holds 927.9 ETH**; impl `0x0e26e0bf83b4ec2cb0dcbc037bb01da5bb352eae` |
| Aave V1 | ETH | LendingPool (proxy) | `0x398eC7346DcD622eDc5ae82352F02bE94C62d119` | 2020-01-08 | impl `0x588790f64ac1424862081a56b8329decae206249` |
| Compound V1 | ETH | MoneyMarket | `0x3FDA67f7583380E67ef93072294a7fAc882FD7E7` | 2018-09-26 | immutable, Solidity 0.4.24, ~$3M |
| Iron Bank | ETH | Unitroller | `0xAB1c342C7bf5Ec5F02ADEA1c2270670bCa144CbB` | 2020-12-04 | impl `0xcb9ab119be270f58d40e3d57d1ecc82bd479d59f` |
| Iron Bank | ETH | Price oracle (mover) | `0xbd6f5add9b7a6eb151933cb4efd50be4eca71451` | 2023-03-13 | `PriceOracleProxyIB` |
| dForce | ETH | Controller (proxy) | `0x8B53Ab2c0Df3230EA327017C91Eb909f815Ad113` | 2021-02-25 | impl `0xbd0ed2f6e7d84ac5a74cc29d4585d5179ece7ddd` |
| Radiant V2 | ARB | LendingPool (proxy) | `0xF4B1486DD74D07706052A33d31d7c0AAFD0659E1` | shell 2023-03-18 | impl `0x3d4c56cdb97355807157f5c7d4f54957f0e9af44` (2024-10-17, UNVERIFIED) |
| Ionic | BASE | Comptroller (Unitroller) | `0x05c9C6417F246600f8f5f49fcA9Ee991bfF73D13` | — | impl `0xc63Ee58A68C22BFd7900ab5C3eB94D0f3d1442e9` |
| Flux Finance | ETH | Comptroller (Unitroller) | `0x95Af143a021DF745bc78e845b54591C53a8B3A51` | 2023-01-30 | impl `0xdc7b90593cafe7a919d22b903fed21bf27da9719`; unaudited $44.5M RWA |
| CoW Protocol | ETH | GPv2VaultRelayer (read exemplar) | `0xC92E8bdf79f0507f65a392b0ab4667716BFE0110` | 2021-06-08 | 0 balance, holds entire CoW approval set |
| Onyx (context) | ETH | XCN token | `0xA2cd3D43c775978A96BdBf12d733D5A1ED94fb18` | 2022-03 | lending side ≈ drained; exemplar only |
