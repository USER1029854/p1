import json,sys,re,subprocess
sys.path.insert(0,'.')
from chain import KEY,ES
def fetch_source(cid,addr):
    """Return concatenated Solidity source (all files) or None."""
    if cid in ("1","42161","137"):
        u=f"https://api.etherscan.io/v2/api?chainid={cid}&module=contract&action=getsourcecode&address={addr}&apikey={KEY}"
        import time
        for _ in range(4):
            time.sleep(0.3)
            o=subprocess.run(["curl","-sS","--max-time","25",u],capture_output=True,text=True).stdout
            try:
                r=json.loads(o).get("result")
                if not r or not isinstance(r,list): continue
                impl=r[0].get("Implementation","")
                if r[0].get("Proxy")=="1" and impl and len(impl)==42:
                    import time as _t; _t.sleep(0.3)
                    o2=subprocess.run(["curl","-sS","--max-time","25",f"https://api.etherscan.io/v2/api?chainid={cid}&module=contract&action=getsourcecode&address={impl}&apikey={KEY}"],capture_output=True,text=True).stdout
                    try:
                        r2=json.loads(o2).get("result")
                        if r2 and r2[0].get("SourceCode"): r=r2  # scan the impl
                    except Exception: pass
                sc=r[0].get("SourceCode","")
                name=r[0].get("ContractName","")+(" (impl)" if r[0] is not None and r[0].get("Implementation","")=="" else "")
                if not sc: return ("",name)  # unverified
                # sc may be {{...}} multi-file JSON
                if sc.startswith("{"):
                    body=sc
                    try:
                        j=json.loads(sc[1:-1]) if sc.startswith("{{") else json.loads(sc)
                        srcs=j.get("sources",j)
                        body="\n".join(v.get("content","") for v in srcs.values())
                    except Exception:
                        body=sc
                    return (body,name)
                return (sc,name)
            except Exception: continue
        return None
    if cid=="8453":
        import time; time.sleep(0.2)
        o=subprocess.run(["curl","-sS","--max-time","25",f"https://base.blockscout.com/api/v2/smart-contracts/{addr}"],capture_output=True,text=True).stdout
        try:
            j=json.loads(o); body=j.get("source_code","") or ""
            for a in (j.get("additional_sources") or []): body+="\n"+(a.get("source_code","") or "")
            return (body,j.get("name","")) if body else ("",j.get("name",""))
        except Exception: return None
    return None
PATTERNS=[
 ("delegatecall","HIGH",r"\.delegatecall\s*\("),
 ("arbitrary .call(data)","MED",r"\.call\s*(\{[^}]*\})?\s*\(\s*\w*data\w*\s*\)"),
 ("low-level .call{value}","LOW",r"\.call\s*\{"),
 ("transferFrom(param_from","MED",r"transferFrom\s*\(\s*(?!msg\.sender)[a-zA-Z_]\w*\s*,"),
 ("ecrecover","INFO",r"\becrecover\s*\("),
 ("encodePacked","LOW",r"abi\.encodePacked\s*\("),
 ("selfdestruct","MED",r"\bselfdestruct\s*\("),
 ("tx.origin","MED",r"\btx\.origin\b"),
 ("block.timestamp-rng","LOW",r"block\.(timestamp|prevrandao|difficulty)"),
 ("spot getReserves","MED",r"\.getReserves\s*\("),
 ("spot slot0","MED",r"\.slot0\s*\("),
 ("balanceOf(this)-pricing","MED",r"balanceOf\s*\(\s*address\s*\(\s*this\s*\)\s*\)"),
 ("4626 previewRedeem","INFO",r"previewRedeem|convertToAssets"),
 ("assembly","INFO",r"\bassembly\s*\{"),
 ("upgradeTo","INFO",r"function\s+upgradeTo"),
 ("sweep/rescue","MED",r"function\s+(sweep|rescue|recover|skim)\w*"),
 ("arbitrary execute","HIGH",r"function\s+(execute|multicall|aggregate|batch)\w*\s*\([^)]*bytes"),
 ("mint public?","INFO",r"function\s+mint\w*\s*\("),
 ("_disableInitializers","GOOD",r"_disableInitializers"),
 ("initializer modifier","INFO",r"\binitializer\b"),
]
def scan(cid,addr,label):
    r=fetch_source(cid,addr)
    if r is None: print(f"[{label}] {addr} c{cid}: FETCH FAIL"); return
    body,name=r
    if not body: print(f"[{label}] {addr} c{cid}: UNVERIFIED ({name})"); return
    L=len(body); hits=[]
    for pn,sev,rx in PATTERNS:
        m=re.findall(rx,body)
        if m: hits.append((sev,pn,len(m)))
    order={"HIGH":0,"MED":1,"LOW":2,"INFO":3,"GOOD":4}
    hits.sort(key=lambda h:order.get(h[0],9))
    ecr = "ecrecover" in body
    ec_guarded = bool(re.search(r"ecrecover[^;]{0,200}?address\(0\)",body,re.S)) or bool(re.search(r"address\(0\)[^;]{0,200}?ecrecover",body,re.S))
    disable_init = "_disableInitializers" in body
    is_init = re.search(r"\binitializer\b",body) is not None
    print(f"[{label}] {name} c{cid} {addr}  ({L//1024}KB)")
    print("   " + " | ".join(f"{s}:{p}×{n}" for s,p,n in hits[:12]))
    warn=[]
    if ecr and not ec_guarded: warn.append("ecrecover w/o address(0) guard")
    if is_init and not disable_init: warn.append("initializer but NO _disableInitializers (impl init risk)")
    if warn: print("   ⚠ " + " ; ".join(warn))
if __name__=="__main__":
    import sys
    # test on Flux comptroller impl (verified)
    scan("1","0xdc7b90593cafe7a919d22b903fed21bf27da9719","TEST-Flux-impl")
