import subprocess,json,sys,time
sys.path.insert(0,'.')
from kc import sel
import os
KEY=os.environ.get("ETHERSCAN_V2_KEY","")
IMPL="0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
ADMIN="0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103"
def g(url):
    for _ in range(2):
        try:
            o=subprocess.run(["curl","-sS","--max-time","8",url],capture_output=True,text=True).stdout
            d=json.loads(o); r=d.get("result")
            if r is not None and "Max calls" not in str(r): return r
        except Exception: pass
        time.sleep(0.35)
    return None
def call(cid,to,data): return g(f"https://api.etherscan.io/v2/api?chainid={cid}&module=proxy&action=eth_call&to={to}&data={data}&tag=latest&apikey={KEY}")
def store(cid,a,s): return g(f"https://api.etherscan.io/v2/api?chainid={cid}&module=proxy&action=eth_getStorageAt&address={a}&position={s}&tag=latest&apikey={KEY}")
def A(h):
    if not h or len(h)<42: return None
    x="0x"+h[-40:]
    try: return None if int(x,16)==0 else x
    except: return None
def name(cid,a):
    r=g(f"https://api.etherscan.io/v2/api?chainid={cid}&module=contract&action=getsourcecode&address={a}&apikey={KEY}")
    if isinstance(r,list) and r:
        return (r[0].get("ContractName") or "?", "verified" if r[0].get("SourceCode") else "UNVERIFIED")
    return ("?","?")
GET=["oracle","priceOracle","priceFeed","asset","underlying","collateral","vault","pool","controller",
 "comptroller","manager","strategy","treasury","minter","addressesProvider","gov","authority","factory"]
def resolve(cid,e,label):
    print(f"\n### {label} [{cid}] {e}",flush=True)
    d={}
    im=A(store(cid,e,IMPL)) or A(call(cid,e,sel("comptrollerImplementation()")))
    ad=A(store(cid,e,ADMIN)); ow=A(call(cid,e,sel("owner()")))
    if im: d[im.lower()]="implementation"
    if ad: d[ad.lower()]="admin(1967)"
    if ow: d[ow.lower()]="owner"
    for x in GET:
        r=A(call(cid,e,sel(x+"()")))
        if r and r.lower()!=e.lower(): d.setdefault(r.lower(),x)
    for a,how in d.items():
        n,v=name(cid,a); print(f"   [{how:12s}] {a}  {n} ({v})",flush=True)
    if not d: print("   (leaf/token — scope = entry + impl)",flush=True)
for t in [
 ("1","0x5c8d0c48810fd37a0a824d074ee290e64f7a8fa2","Avalon Superearn (Yield $30M)"),
 ("1","0x00bac91fd8f5b4a0dc03c8021139b76f6549ee7e","KAIO (RWA $41M)"),
 ("1","0xC4441c2BE5d8fA8126822B9929CA0b81Ea0DE38E","Usual ETH0 (Synth)"),
 ("1","0x259338656198ec7a76c729514d3cb45dfbf768a1","Resolv USR (Basis)"),
 ("1","0xca1207647ff814039530d7d35df0e1dd2e91fa84","mStable V2 (CDP)"),
 ("1","0x64aa3364F17a4D01c6f1751Fd97C2BD3D7e7f1D5","Cooler/OHM (Lending $216M)"),
 ("1","0x01791f726b4103694969820be083196cc7c045ff","Yield Basis (Lev $148M)"),
 ("42161","0xe7e7e741c23a4767831a56a8c99f522c5ac1e7e7","Everything (ARB Lending)"),
 ("42161","0xa6422e3e219ee6d4c1b18895275fe43556fd50ed","Stobox (ARB RWA)"),
]:
    try: resolve(*t)
    except Exception as ex: print(f"### {t[2]} ERR {ex}",flush=True)
print("\nDONE",flush=True)
