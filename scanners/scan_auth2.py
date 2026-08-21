import json,sys
sys.path.insert(0,'.')
from chain import *
EVM={'Ethereum':'1','Arbitrum':'42161','Base':'8453','BSC':'56'}
d=json.load(open('protocols2.json'))
RISKY={'Lending','CDP','Yield','Yield Aggregator','Derivatives','Farm','RWA','Algo-Stables',
 'Liquid Staking','Restaking','Options','Options Vault','Leveraged Farming','Liquidity manager',
 'Basis Trading','Synthetics','Reserve Currency','Interest Rate','NFT Lending','Uncollateralized Lending'}
def oc(p): return set(p.get('chains',[]))&set(EVM)
def parse_addr(a,chains):
    if not a: return None
    if ':' in a:
        c,_,x=a.partition(':'); cm={'ethereum':'1','arbitrum':'42161','base':'8453','bsc':'56'}
        return (cm[c.lower()],x) if c.lower() in cm and x.startswith('0x') else None
    if a.startswith('0x'):
        ev=[EVM[c] for c in chains if c in EVM]
        return ('1' if '1' in ev else ev[0],a) if ev else None
    return None
cands=[]
for p in d:
    if not oc(p): continue
    tvl=p.get('tvl') or 0
    if not (1_000_000<=tvl<=150_000_000): continue
    if p.get('category','') not in RISKY: continue
    if str(p.get('audits','0')) not in ('0','1'): continue
    pa=parse_addr(p.get('address'),oc(p))
    if pa: cands.append((tvl,p.get('category'),p.get('name'),pa[0],pa[1],str(p.get('audits','0'))))
cands.sort(reverse=True)
print(f"AUTH+4626 scan: {len(cands)} low-audit funded candidates\n",flush=True)
def classify(cid,addr):
    if not addr: return None
    c=getcode(cid,addr,thr=0.08)
    if c is None: return "?"
    if len(c)<=2: return "EOA"
    if U(call(cid,addr,sel("getThreshold()"),thr=0.08)): return "Safe"
    md=call(cid,addr,sel("getMinDelay()"),thr=0.08)
    if md not in (None,"","0x"): return "Timelock"
    return "contract"
for tvl,cat,name,cid,addr,aud in cands:
    impl=A(storage(cid,addr,IMPL_SLOT,thr=0.08))
    admin=A(storage(cid,addr,ADMIN_SLOT,thr=0.08))
    owner=A(call(cid,addr,sel("owner()"),thr=0.08))
    asset=A(call(cid,addr,sel("asset()"),thr=0.08))  # ERC-4626 => money vault
    flags=[]
    if asset: flags.append("4626-VAULT")
    if impl:
        flags.append("PROXY")
        if admin:
            ac=classify(cid,admin); flags.append("EOA-ADMIN!!" if ac=="EOA" else f"admin={ac}")
        elif owner:
            oc2=classify(cid,owner); flags.append("EOA-OWNER(UUPS)!!" if oc2=="EOA" else f"upgAuth={oc2}")
    if owner and not impl:
        oc2=classify(cid,owner); flags.append("EOA-OWNER!!" if oc2=="EOA" else f"owner={oc2}")
    print(f"${tvl:>11,.0f} {aud} {cat[:13]:13s} c{cid:>5} {name[:22]:22s} {addr} {'|'.join(flags)}",flush=True)
print("\nDONE",flush=True)
