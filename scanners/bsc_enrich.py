import json,subprocess,csv,time,sys
sys.path.insert(0,'.')
from kc import sel
import os
RPC=os.environ.get("BSC_RPC","https://bsc-dataseed.binance.org")  # set BSC_RPC to your provider
IMPL="0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
ADMIN="0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103"
def rpc(method,params):
    p=json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":1})
    for _ in range(2):
        try:
            o=subprocess.run(["curl","-sS","--max-time","9","-X","POST",RPC,"-H","Content-Type: application/json","-d",p],capture_output=True,text=True).stdout
            d=json.loads(o)
            if "result" in d: return d["result"]
        except Exception: pass
        time.sleep(0.25)
    return None
def call(to,data): return rpc("eth_call",[{"to":to,"data":data},"latest"])
def code(a): return rpc("eth_getCode",[a,"latest"])
def store(a,s): return rpc("eth_getStorageAt",[a,s,"latest"])
def A(h):
    if not h or len(h)<42: return None
    x="0x"+h[-40:]
    try: return None if int(x,16)==0 else x
    except: return None
def is_contract(a):
    c=code(a); return c is not None and len(c)>2
def classify(a):
    if not a: return None
    c=code(a)
    if c is None: return "?"
    if len(c)<=2: return "EOA"
    if A(call(a,sel("getThreshold()"))): return "Safe"
    md=call(a,sel("getMinDelay()"))
    if md not in (None,"","0x"): return "Timelock"
    return "contract"
def sourcify(a):
    try:
        o=subprocess.run(["curl","-sS","--max-time","9",f"https://sourcify.dev/server/v2/contract/56/{a}"],capture_output=True,text=True).stdout
        d=json.loads(o); return "yes" if d.get("match") in ("match","exact_match","perfect","partial_match") or d.get("matchId") else "no"
    except Exception: return "?"
def tname(a):
    r=call(a,sel("name()"))
    try:
        if r and len(r)>130:
            ln=int(r[2+64:2+128],16); return bytes.fromhex(r[2+128:2+128+ln*2]).decode("utf8","ignore")[:24]
    except Exception: pass
    return ""
def parse(addr,chains):
    if not addr: return None
    if ":" in addr:
        c,_,x=addr.partition(":")
        return x if (c.lower() in ("bsc","binance") and x.startswith("0x")) else None
    if addr.startswith("0x") and "Binance" in chains: return addr
    return None
rows=json.load(open("bsc_universe.json"))
out=[["score","tvl","audits","category","name","address","contract_name","is_proxy","implementation","owner","owner_type","admin_type","verified","listedAt","slug"]]
done=0
for s,tvl,aud,cat,name,ch,addr,la,slug in rows:
    a=parse(addr,ch)
    cn=ip=impl=ow=ot=at=ver=""
    if a and is_contract(a):
        im=A(store(a,IMPL)); ad=A(store(a,ADMIN)); ow=A(call(a,sel("owner()")))
        ip="yes" if im else "no"; impl=im or ""
        ot=classify(ow) if ow else ""
        at=classify(ad) if ad else ""
        cn=tname(a); ver=sourcify(a); done+=1
    import datetime
    dt=datetime.datetime.utcfromtimestamp(la).date().isoformat() if la else ""
    out.append([s,int(tvl),aud,cat,name,a or "",cn,ip,impl,ow or "",ot,at,ver,dt,slug])
    if done and done%20==0: print(f"...{done}",flush=True)
csv.writer(open("bsc_candidates.csv","w",newline="")).writerows(out)
print(f"DONE enriched {done} BSC contracts -> bsc_candidates.csv",flush=True)
