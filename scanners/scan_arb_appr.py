from chain import *
import chain as _c
APPROVAL=topic("Approval(address,address,uint256)")
def lb(cid):
    for i in range(6):
        time.sleep(0.5+i*0.4)
        r=_c._es_get(f"https://api.etherscan.io/v2/api?chainid={cid}&module=proxy&action=eth_blockNumber&apikey={KEY}")
        try: return int(r,16)
        except: continue
def live_check(cid,sp,frm,L,n=12):
    logs=getlogs(cid,[APPROVAL,None,"0x"+enc_addr(sp)],hex(frm),hex(L),thr=0.3) or []
    seen=[];pairs=[]
    for lg in reversed(logs):
        try: owner="0x"+lg["topics"][1][-40:]; tok=lg["address"].lower()
        except: continue
        if (owner,tok) in seen: continue
        seen.append((owner,tok)); pairs.append((owner,tok))
        if len(pairs)>=n: break
    live=mx=chk=0
    for owner,tok in pairs:
        al=U(call(cid,tok,sel("allowance(address,address)")+enc_addr(owner)+enc_addr(sp),thr=0.3))
        if al is None: continue
        chk+=1; live+=al>0; mx+= al>=(1<<255)
    return len(logs),chk,live,mx
# Re-confirm Multichain (ETH) robustly
L1=lb("1"); 
print("=== Multichain (dead) ETH live-allowance re-check ===")
for label,sp in [("Multichain Router6","0x6b7a87899490EcE95443e979cA9485CBE7E71522"),
                 ("Multichain Router4","0x765277EebeCA2e31912C9946eAe1021199B39C61")]:
    n,chk,live,mx=live_check("1",sp,L1-250000,L1,15)
    print(f"  {label} {sp}: events={n} sampled={chk} LIVE={live} INFINITE={mx}")
# ARB wide approval scan
print("\n=== ARBITRUM approval-authority (event volume, ~5wk) ===")
L=lb("42161"); frm=L-3000000  # arb blocks are fast; ~ weeks
ARB=[
 ("GMX Router","0xaBBc5F99639c9B6bCb58544ddf04EFA6802F4064"),
 ("GMX PositionRouter","0xb87a436B93fFE9D75c5cFA7bAcFff96430b09868"),
 ("Radiant LendingPool","0xF4B1486DD74D07706052A33d31d7c0AAFD0659E1"),
 ("1inch v5","0x1111111254EEB25477B68fb85Ed929f73A960582"),
 ("Odos ARB","0xa669e7A0d4b3e4Fa48af2dE86BD4CD7126Be4e13"),
 ("Camelot Router","0xc873fEcbd354f5A56E00E710B90EF4201db2448d"),
 ("SushiSwap Router","0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"),
 ("Stargate Router ARB","0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614"),
 ("SwapNet(exploited)","0x616000e384Ef1C2B52f5f3A88D57a3B64F23757e"),
 ("Aperture(exploited)","0xD83d960deBEC397fB149b51F8F37DD3B5CFA8913"),
 ("LiFi Diamond","0x1231DEB6f5749EF6cE6943a275A1D3E7486F4EaE"),
 ("Socket Gateway","0x3a23F943181408EAC424116Af7b7790c94Cb97a5"),
]
rows=[]
for label,sp in ARB:
    logs=getlogs("42161",[APPROVAL,None,"0x"+enc_addr(sp)],hex(frm),hex(L),thr=0.3) or []
    ow=set();mx=0
    for lg in logs:
        try:
            ow.add(lg["topics"][1][-40:])
            if int(lg["data"],16)>=(1<<255):mx+=1
        except:pass
    rows.append((len(logs),len(ow),mx,label,sp))
rows.sort(reverse=True)
print(f"{'appr':>6} {'ownrs':>5} {'max∞':>5}  spender")
for n,o,mx,label,sp in rows:
    print(f"{n:>6}{'+' if n>=1000 else ' '} {o:>5} {mx:>5}  {label:22s} {sp}")
