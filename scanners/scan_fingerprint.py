from chain import *
# (label, chain, addr) — group identical bytecode across chains = fork siblings / same-flaw clones
TARGETS=[
 ("SwapNet_ETH","1","0x616000e384Ef1C2B52f5f3A88D57a3B64F23757e"),
 ("SwapNet_ARB","42161","0x616000e384Ef1C2B52f5f3A88D57a3B64F23757e"),
 ("SwapNet_BASE","8453","0x616000e384Ef1C2B52f5f3A88D57a3B64F23757e"),
 ("SwapNet_BSC","56","0x616000e384Ef1C2B52f5f3A88D57a3B64F23757e"),
 ("Aperture_ETH","1","0xD83d960deBEC397fB149b51F8F37DD3B5CFA8913"),
 ("Aperture_ARB","42161","0xD83d960deBEC397fB149b51F8F37DD3B5CFA8913"),
 ("Aperture_BASE","8453","0xD83d960deBEC397fB149b51F8F37DD3B5CFA8913"),
 ("KiloEx_BASE","8453","0xd649a0876453fc7626569b28e364262192874e18"),
 ("KiloEx_BSC","56","0xcc6a5784194bd516db29aa505179857025d8bef4"),
]
from collections import defaultdict
groups=defaultdict(list)
for label,cid,addr in TARGETS:
    code=getcode(cid,addr,thr=0.15)
    if not code or code=="0x": 
        print(f"{label}: NO CODE at {addr} on {cid}"); continue
    h=keccak256(bytes.fromhex(code[2:])).hex()
    groups[h].append((label,cid,addr,len(code)//2))
    print(f"{label:16s} {cid:>6} {addr} codelen={len(code)//2:>6} codehash={h[:16]}..")
print("\n=== identical-bytecode groups (same flaw, N deployments) ===")
for h,members in groups.items():
    if len(members)>1:
        print(f" hash {h[:20]}.. -> {len(members)} deployments: {[m[0] for m in members]}")
