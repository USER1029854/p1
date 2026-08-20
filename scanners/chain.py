import subprocess, json, time, sys
sys.path.insert(0,'.')
from kc import keccak256, sel, topic
import os
KEY=os.environ.get("ETHERSCAN_V2_KEY","")  # set your Etherscan V2 API key here or via env
ES={"1","137","42161"}   # Etherscan V2 free
RPC={"8453":"https://mainnet.base.org","56":"https://bsc-dataseed.binance.org",
     "42161":"https://arb1.arbitrum.io/rpc","1":"https://ethereum-rpc.publicnode.com"}
def _curl(args): 
    return subprocess.run(["curl","-sS","--max-time","25"]+args,capture_output=True,text=True).stdout
def _es_get(url,tries=4):
    for i in range(tries):
        o=_curl([url])
        try:
            d=json.loads(o)
        except: 
            time.sleep(0.5+i*0.5); continue
        r=d.get("result")
        msg=str(d.get("message",""))+str(r)
        if r is None or "Max calls per sec" in msg or "NOTOK" in str(d.get("message","")) and "rate" in msg.lower():
            time.sleep(0.6+i*0.6); continue
        # jsonrpc error shape
        if isinstance(d.get("error"),dict): 
            time.sleep(0.5+i*0.5); continue
        return r
    return None
def _rpc_post(cid,method,params,tries=4):
    p=json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":1})
    for i in range(tries):
        o=_curl(["-X","POST",RPC[cid],"-H","Content-Type: application/json","-d",p])
        try: d=json.loads(o)
        except: time.sleep(0.4+i*0.4); continue
        if isinstance(d.get("error"),dict): time.sleep(0.4+i*0.4); continue
        r=d.get("result")
        if r is None: time.sleep(0.4+i*0.4); continue
        return r
    return None
def call(cid,to,data,thr=0.12):
    time.sleep(thr)
    if cid in ES:
        return _es_get(f"https://api.etherscan.io/v2/api?chainid={cid}&module=proxy&action=eth_call&to={to}&data={data}&tag=latest&apikey={KEY}")
    return _rpc_post(cid,"eth_call",[{"to":to,"data":data},"latest"])
def storage(cid,addr,slot,thr=0.12):
    time.sleep(thr)
    if cid in ES:
        return _es_get(f"https://api.etherscan.io/v2/api?chainid={cid}&module=proxy&action=eth_getStorageAt&address={addr}&position={slot}&tag=latest&apikey={KEY}")
    return _rpc_post(cid,"eth_getStorageAt",[addr,slot,"latest"])
def getcode(cid,addr,thr=0.12):
    time.sleep(thr)
    if cid in ES:
        r=_es_get(f"https://api.etherscan.io/v2/api?chainid={cid}&module=proxy&action=eth_getCode&address={addr}&tag=latest&apikey={KEY}")
    else:
        r=_rpc_post(cid,"eth_getCode",[addr,"latest"])
    return r if (r and r.startswith("0x")) else None


def creation(cid,addr,thr=0.12):
    if cid not in ES: return None
    time.sleep(thr)
    r=_es_get(f"https://api.etherscan.io/v2/api?chainid={cid}&module=contract&action=getcontractcreation&contractaddresses={addr}&apikey={KEY}")
    if isinstance(r,list) and r and isinstance(r[0],dict): return r[0]
    return None
def verified(cid,addr,thr=0.12):
    if cid not in ES: return None
    time.sleep(thr)
    r=_es_get(f"https://api.etherscan.io/v2/api?chainid={cid}&module=contract&action=getsourcecode&address={addr}&apikey={KEY}")
    if isinstance(r,list) and r and isinstance(r[0],dict):
        x=r[0]; return {"name":x.get("ContractName"),"verified":bool(x.get("SourceCode")),"impl":x.get("Implementation"),"proxy":x.get("Proxy")}
    return None

def getlogs(cid,topics,fromB,toB,address=None,thr=0.12):
    time.sleep(thr)
    if cid in ES:
        q=f"https://api.etherscan.io/v2/api?chainid={cid}&module=logs&action=getLogs&fromBlock={fromB}&toBlock={toB}"
        for i,t in enumerate(topics):
            if t: q+=f"&topic{i}={t}"
        if len(topics)>=3 and topics[0] and topics[2]: q+="&topic0_2_opr=and"
        if address: q+=f"&address={address}"
        q+=f"&apikey={KEY}"
        try:
            d=json.loads(_curl([q])); return d.get("result") if isinstance(d.get("result"),list) else []
        except: return []
    return []
# ---- ABI helpers ----
def enc_addr(a): return a.lower().replace("0x","").rjust(64,'0')
def enc_uint(n): return hex(n)[2:].rjust(64,'0')
def A(h):
    if not h or len(h)<42: return None
    x="0x"+h[-40:]
    try: return None if int(x,16)==0 else x
    except: return None
def U(h):
    if h is None: return None
    try: return int(h,16)
    except: return None
def dec_addr_array(h):
    if not h or len(h)<130: return []
    b=h[2:]; n=U("0x"+b[64:128]); out=[]
    for i in range(n):
        c=b[128+i*64:128+(i+1)*64]
        if len(c)==64: out.append("0x"+c[24:])
    return out
def dec_string(h):
    try:
        b=h[2:]; off=U("0x"+b[0:64])*2; ln=U("0x"+b[off:off+64]); return bytes.fromhex(b[off+64:off+64+ln*2]).decode('utf8','ignore')
    except: return "?"
IMPL_SLOT="0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
ADMIN_SLOT="0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103"
