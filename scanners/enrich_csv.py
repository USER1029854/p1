import subprocess,json,csv,time,sys
sys.path.insert(0,'.')
import os
KEY=os.environ.get("ETHERSCAN_V2_KEY","")
CID={'Ethereum':'1','Arbitrum':'42161'}  # Etherscan V2 free
def g(url):
    for _ in range(2):
        try:
            o=subprocess.run(["curl","-sS","--max-time","8",url],capture_output=True,text=True).stdout
            d=json.loads(o); r=d.get("result")
            if r is not None and "Max calls" not in str(r): return r
        except Exception: pass
        time.sleep(0.3)
    return None
def meta(cid,a):
    r=g(f"https://api.etherscan.io/v2/api?chainid={cid}&module=contract&action=getsourcecode&address={a}&apikey={KEY}")
    if isinstance(r,list) and r:
        x=r[0]
        return (x.get("ContractName") or "?", "yes" if x.get("Proxy")=="1" else "no",
                x.get("Implementation") or "", "yes" if x.get("SourceCode") else "NO")
    return ("?","?","","?")
rows=list(csv.reader(open('at_risk_enriched.csv')))
hdr=rows[0]; body=rows[1:]
out=[['score','tvl','audits','category','name','chains','address','address_chain','contract_name','is_proxy','implementation','verified','listedAt','slug']]
done=0
for r in body:
    score,tvl,aud,cat,name,dt,chains,addr,achain,slug=r
    cn=iproxy=impl=ver=''
    ac=achain.replace('?','')
    if addr and ac in CID:
        cn,iproxy,impl,ver=meta(CID[ac],addr); done+=1
        time.sleep(0.18)
    elif addr:
        ver='base/bsc: check Blockscout/Sourcify'
    out.append([score,tvl,aud,cat,name,chains,addr,achain,cn,iproxy,impl,ver,dt,slug])
    if done%25==0 and done: print(f"...{done} resolved",flush=True)
with open('at_risk_protocols_final.csv','w',newline='') as f:
    csv.writer(f).writerows(out)
print(f"DONE resolved {done} ETH/ARB rows -> at_risk_protocols_final.csv",flush=True)
