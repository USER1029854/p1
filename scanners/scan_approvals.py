from chain import *
import sys
APPROVAL=topic("Approval(address,address,uint256)")
# spender universe (label, chain, address)
SPENDERS=[
 ("0x ExchangeProxy","1","0xDef1C0ded9bec7F1a1670819833240f027b25EfF"),
 ("1inch v5 Router","1","0x1111111254EEB25477B68fb85Ed929f73A960582"),
 ("1inch v6 Router","1","0x111111125421cA6dc452d289314280a0f8842A65"),
 ("Uniswap UniversalRouter","1","0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD"),
 ("Permit2","1","0x000000000022D473030F116dDEE9F6B43aC78BA3"),
 ("CoW VaultRelayer","1","0xC92E8bdf79f0507f65a392b0ab4667716BFE0110"),
 ("ParaSwap TokenTransferProxy","1","0x216B4B4Ba9F3e719726886d34a177484278Bfcae"),
 ("KyberSwap MetaAggRouterV2","1","0x6131B5fae19EA4f9D964eAc0408E4408b66337b5"),
 ("Socket Gateway","1","0x3a23F943181408EAC424116Af7b7790c94Cb97a5"),
 ("LiFi Diamond","1","0x1231DEB6f5749EF6cE6943a275A1D3E7486F4EaE"),
 ("OpenOcean Exchange","1","0x6352a56caadC4F1E25CD6c75970Fa768A3304e64"),
 ("Odos RouterV2","1","0xCf5540fFFCdC3d510B18bFcA6d2b9987b0772559"),
 ("DODOApprove","1","0xCB859eA579b28e02B87A1FDE08d087ab9dbE5149"),
 ("Metamask Swap Router","1","0x881D40237659C251811CEC9c364ef91dC08D300C"),
 ("SwapNet (exploited)","1","0x616000e384Ef1C2B52f5f3A88D57a3B64F23757e"),
 ("Aperture (exploited)","1","0xD83d960deBEC397fB149b51F8F37DD3B5CFA8913"),
 ("Bebop Settlement","1","0xbEB09beB09e95E6FEBf0d6EEb1d0D46d1013CC3C"),
]
# latest block
lb=U(call("1","0x0000000000000000000000000000000000000000",sel("x()")) or "0x0")  # dummy, use proxy blockNumber instead
import subprocess,json
lbraw=json.loads(subprocess.run(["curl","-sS",f"https://api.etherscan.io/v2/api?chainid=1&module=proxy&action=eth_blockNumber&apikey={KEY}"],capture_output=True,text=True).stdout)["result"]
lb=int(lbraw,16)
frm=lb-250000  # ~5 weeks on ETH
print(f"ETH latest={lb}  window=[{frm},{lb}] (~5 weeks)\n")
rows=[]
for label,cid,addr in SPENDERS:
    logs=getlogs("1",[APPROVAL,None,"0x"+enc_addr(addr)],hex(frm),hex(lb),thr=0.25)
    n=len(logs)
    owners=set(); tokens=set(); maxcount=0
    for lg in logs:
        try:
            owners.add(lg["topics"][1][-40:]); tokens.add(lg["address"].lower())
            if int(lg["data"],16) >= (1<<255): maxcount+=1
        except: pass
    cap="(capped)" if n>=1000 else ""
    rows.append((n,len(owners),len(tokens),maxcount,label,addr,cap))
rows.sort(reverse=True)
print(f"{'approvals':>9} {'owners':>6} {'tokens':>6} {'max∞':>5}  spender")
for n,o,t,mx,label,addr,cap in rows:
    print(f"{n:>9}{cap:9s} {o:>6} {t:>6} {mx:>5}  {label:28s} {addr}")
