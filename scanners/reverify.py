from chain import *
# flagged empties to re-verify (chain, comptroller, market, label)
CANDS=[
 ("1","IronBank","0xAB1c342C7bf5Ec5F02ADEA1c2270670bCa144CbB","0x7736ffb07104c0c400bb0cc9a7c228452a732992","iDPI",55),
 ("1","IronBank","0xAB1c342C7bf5Ec5F02ADEA1c2270670bCa144CbB","0xbc6b6c837560d1fe317ebb54e105c89f303d5afd","iWSTETH",70),
 ("42161","Tender","0xeeD247bA513a8D6f78Be9318399f5eD1a4808F8e","0x20a6768f6aabf66b787985ec6ce0ebea6d7ad497","t?1",70),
 ("42161","Tender","0xeeD247bA513a8D6f78Be9318399f5eD1a4808F8e","0xb287180147ef1a97cbfb07e2f1788b75df2f6299","t?2",75),
 ("42161","Tender","0xeeD247bA513a8D6f78Be9318399f5eD1a4808F8e","0xc6121d58e01b3f5c88eb8a661770db0046523539","t?3",80),
 ("42161","Tender","0xeeD247bA513a8D6f78Be9318399f5eD1a4808F8e","0x242f91207184fcc220bea3c9e5f22b6d80f3fac5","tWETH",80),
 ("8453","Ionic","0x05c9C6417F246600f8f5f49fcA9Ee991bfF73D13","0xd333681242f376f9005d1208ff946c3ee73ed659","ion?",50),
 ("8453","Ionic","0x05c9C6417F246600f8f5f49fcA9Ee991bfF73D13","0x5be1cb6cb3c9bfd16db43ed4f6c081fa9783dd1c","ionmsUSD",10),
 ("8453","Moonwell","0xfBb21d0380beE3312B33c4353c8936a0F13EF26C","0x628ff693426583d9a7fb391e54366292f509d457","mw?1",84),
 ("8453","Moonwell","0xfBb21d0380beE3312B33c4353c8936a0F13EF26C","0x73b06d8d18de422e269645eace15400de7462417","mDAI",50),
 ("8453","Moonwell","0xfBb21d0380beE3312B33c4353c8936a0F13EF26C","0x3bf93770f2d4a794c3d9ebefbaebae2a8f09a5e5","mcbETH",81),
]
print(f"{'chain':>6} {'proto':10} {'sym':10} {'CF%':>4} {'totalSupply':>18} {'getCash':>18}  VERDICT")
for cid,proto,comp,m,s,cf in CANDS:
    ts=U(call(cid,m,sel("totalSupply()"),thr=0.35))
    cash=U(call(cid,m,sel("getCash()"),thr=0.35))
    if ts is None or cash is None:
        v="READ-FAIL (inconclusive)"
    elif ts==0 and cash==0:
        v="*** TRUE EMPTY (donation surface) ***"
    elif ts<10**12:
        v=f"thin (ts={ts})"
    else:
        v="NOT empty (ghost)"
    print(f"{cid:>6} {proto:10} {s:10} {cf:>4} {str(ts):>18} {str(cash):>18}  {v}")
