from chain import *
import subprocess,json
APPROVAL=topic("Approval(address,address,uint256)")
CID="1"
SPENDERS=[
 ("1inch v2 (old)","0x111111125434b319222CdBf8C261674aDB56F3ae"),
 ("1inch v3 (old)","0x11111112542D85B3EF69AE05771c2dCCff4fAa26"),
 ("1inch v4 (old)","0x1111111254fb6c44bAC0beD2854e76F90643097d"),
 ("0x AllowanceTarget(old)","0xF740B67dA229f2f10bcBd38A7979992fCC71B8Eb"),
 ("Paraswap v4 (old)","0xb70Bc06D2c9Bf03b3373799606dc7d39346c06B3"),
 ("Tokenlon AllowanceTarget","0x8A42d311D282e0BccB95131cB57d43d6d50647a6"),
 ("Kyber AggRouter(old,exploited)","0xDF1A1b60f2D438842916C0aDc43748768353EC25"),
 ("Bancor Network","0xeEF417e1D5CC832e619ae18D2F140De2999dD4fB"),
 ("Furucombo Proxy","0x59DAa74F675Ce137c53848F274b0Eb3d9C3f8D9D"),
 ("dYdX SoloMargin","0x1E0447b19BB6EcFdAe1e4AE1694b0C3659614e4e"),
 ("Convex Booster","0xF403C135812408BFbE8713b5A23a04b3D48AAE31"),
 ("Across SpokePool","0x5c7BCd6E7De5423a257D81B442095A1a6ced35C5"),
 ("Stargate Router","0x8731d54E9D02c286767d56ac03e8037C07e01e98"),
 ("Synapse Bridge","0x2796317b0fF8538F253012862c06787Adfb8cEb6"),
 ("Celer cBridge","0x5427FEFA711Eff984124bFBB1AB6fbf5E3DA1820"),
 ("Multichain Router(dead)","0x6b7a87899490EcE95443e979cA9485CBE7E71522"),
 ("Multichain Router4(dead)","0x765277EebeCA2e31912C9946eAe1021199B39C61"),
 ("KyberSwap MetaAggV2","0x6131B5fae19EA4f9D964eAc0408E4408b66337b5"),
 ("Set TokenSets DEXAdapter","0x2DcF7C0bA9E33b1e75f9312Fb5 E23F7a9F7B7f7f"[:42]),
 ("InstaDapp DSA?","0x2971AdFa57b20E5a416aE5a708A8655A9c74f723"),
 ("CoW GPv2Settlement","0x9008D19f58AAbD9eD0D60971565AA8510560ab41"),
 ("Zerion Router","0x9E9Fb02Cfb642FB2b91C3aAcb53e6f5a3e6BF7fF"[:42]),
 ("UniversalRouter v1.2","0x66a9893cC07D91D95644AEDD05D03f95e1dBA8Af"),
 ("Balancer Vault","0xBA12222222228d8Ba445958a75a0704d566BF2C8"),
]
lb=int(json.loads(subprocess.run(["curl","-sS",f"https://api.etherscan.io/v2/api?chainid=1&module=proxy&action=eth_blockNumber&apikey={KEY}"],capture_output=True,text=True).stdout)["result"],16)
frm=lb-250000
print(f"ETH window ~5 weeks [{frm},{lb}]\n{'appr':>6} {'ownrs':>5} {'tok':>4} {'max∞':>5}  spender")
rows=[]
for label,addr in SPENDERS:
    if len(addr)!=42: 
        rows.append((-1,0,0,0,label,addr)); continue
    logs=getlogs("1",[APPROVAL,None,"0x"+enc_addr(addr)],hex(frm),hex(lb),thr=0.3) or []
    owners=set();tok=set();mx=0
    for lg in logs:
        try:
            owners.add(lg["topics"][1][-40:]);tok.add(lg["address"].lower())
            if int(lg["data"],16)>=(1<<255):mx+=1
        except:pass
    rows.append((len(logs),len(owners),len(tok),mx,label,addr))
rows.sort(reverse=True)
for n,o,t,mx,label,addr in rows:
    cap="+" if n>=1000 else " "
    print(f"{n:>6}{cap} {o:>5} {t:>4} {mx:>5}  {label:32s} {addr}")
