from chain import *
import chain as _c
import subprocess,json
APPROVAL=topic("Approval(address,address,uint256)")
def lb(cid):
    for i in range(6):
        time.sleep(0.5+i*0.5)
        r=_c._es_get(f"https://api.etherscan.io/v2/api?chainid={cid}&module=proxy&action=eth_blockNumber&apikey={KEY}")
        try: return int(r,16)
        except: continue
    return None
# spenders to confirm LIVE authority on (dead/deprecated/exploited)
TARGETS=[
 ("1","Multichain Router (dead)","0x6b7a87899490EcE95443e979cA9485CBE7E71522"),
 ("1","Kyber old router (exploited)","0xDF1A1b60f2D438842916C0aDc43748768353EC25"),
 ("1","1inch v4 (deprecated)","0x1111111254fb6c44bAC0beD2854e76F90643097d"),
 ("1","0x AllowanceTarget (old)","0xF740B67dA229f2f10bcBd38A7979992fCC71B8Eb"),
 ("1","dYdX v1 SoloMargin","0x1E0447b19BB6EcFdAe1e4AE1694b0C3659614e4e"),
 ("1","Aperture (exploited)","0xD83d960deBEC397fB149b51F8F37DD3B5CFA8913"),
]
L=lb("1"); frm=L-250000
print("Confirming LIVE current allowances (sampled) still pointed at each spender:\n")
for cid,label,sp in TARGETS:
    logs=getlogs(cid,[APPROVAL,None,"0x"+enc_addr(sp)],hex(frm),hex(L),thr=0.3) or []
    # dedupe last (owner,token), newest first
    seen=[]; pairs=[]
    for lg in reversed(logs):
        try:
            owner="0x"+lg["topics"][1][-40:]; tok=lg["address"].lower()
        except: continue
        if (owner,tok) in seen: continue
        seen.append((owner,tok)); pairs.append((owner,tok))
        if len(pairs)>=15: break
    live=0; maxlive=0; checked=0
    for owner,tok in pairs:
        al=U(call(cid,tok,sel("allowance(address,address)")+enc_addr(owner)+enc_addr(sp),thr=0.3))
        if al is None: continue
        checked+=1
        if al>0: live+=1
        if al>=(1<<255): maxlive+=1
    print(f"[{label}] {sp}")
    print(f"   sampled {checked} recent (owner,token) -> {live} STILL LIVE (nonzero allowance), {maxlive} still INFINITE\n")
