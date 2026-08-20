from chain import *
COMPTROLLERS=[
 ("Flux","1","0x95Af143a021DF745bc78e845b54591C53a8B3A51"),
 ("IronBank","1","0xAB1c342C7bf5Ec5F02ADEA1c2270670bCa144CbB"),
 ("Compound_v2","1","0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B"),
 ("Strike","1","0xe2e17b2CBbf48211FA7eB8A875360e5e39bA2602"),
 ("dForce","1","0x8B53Ab2c0Df3230EA327017C91Eb909f815Ad113"),
 ("Lodestar_ARB","42161","0xa86DD95c210dd186Fa7639F93E4177E97d057576"),
 ("Tender_ARB","42161","0xeeD247bA513a8D6f78Be9318399f5eD1a4808F8e"),
 ("Ionic_BASE","8453","0x05c9C6417F246600f8f5f49fcA9Ee991bfF73D13"),
 ("Moonwell_BASE","8453","0xfBb21d0380beE3312B33c4353c8936a0F13EF26C"),
 ("Sonne_BASE","8453","0x1DB2466d9F5e10D7090E7152B68d62703a2245F0"),
 ("Venus_BSC","56","0xfD36E2c2a6789Db23113685031d7F16329158384"),
]
def sym(cid,m):
    r=call(cid,m,sel("symbol()"),thr=0.1)
    try:
        b=r[2:]; off=U("0x"+b[0:64])*2; ln=U("0x"+b[off:off+64]); return bytes.fromhex(b[off+64:off+64+ln*2]).decode('utf8','ignore')
    except: return "?"
print("Scanning Compound-fork comptrollers for THIN markets usable as collateral (CF>0)\n")
for label,cid,comp in COMPTROLLERS:
    mkts=dec_addr_array(call(cid,comp,sel("getAllMarkets()"),thr=0.15))
    if not mkts:
        print(f"[{label}] {comp} -> no markets (bad addr / dead / RPC) — skip"); continue
    thin=[]
    for m in mkts[:30]:
        ts=U(call(cid,m,sel("totalSupply()"),thr=0.1))
        mk=call(cid,comp,sel("markets(address)")+enc_addr(m),thr=0.1)
        cf=U("0x"+mk[2+64:2+128]) if mk and len(mk)>=130 else 0
        if cf>0 and ts < 10**15:  # collateral-enabled AND thin
            s=sym(cid,m); u=A(call(cid,m,sel("underlying()"),thr=0.1))
            thin.append((ts,s,m,cf,u))
    print(f"[{label}] {comp}  markets={len(mkts)}  THIN-collateral={len(thin)}")
    for ts,s,m,cf,u in sorted(thin):
        print(f"    THIN {m} {s:12s} totalSupply={ts:<20d} CF={cf/1e16:.0f}% underlying={u}")
