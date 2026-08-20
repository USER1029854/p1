from chain import *
import datetime
# proxies to age: (label, chain, proxy)
PROXIES=[
 ("Radiant_V2_ARB","42161","0xF4B1486DD74D07706052A33d31d7c0AAFD0659E1"),
 ("Flux_Comptroller","1","0x95Af143a021DF745bc78e845b54591C53a8B3A51"),
 ("dForce_Controller","1","0x8B53Ab2c0Df3230EA327017C91Eb909f815Ad113"),
 ("AaveV1_Core","1","0x3dfd23A6c5E8BbcFc9581d2E864a68feb6a076d3"),
 ("IronBank_Unitroller","1","0xAB1c342C7bf5Ec5F02ADEA1c2270670bCa144CbB"),
]
def dt(ts):
    try: return datetime.datetime.utcfromtimestamp(int(ts)).date().isoformat()
    except: return "?"
def age_one(label,cid,proxy):
    impl=A(storage(cid,proxy,IMPL_SLOT))
    # comptroller-style impl fallback
    if not impl: impl=A(call(cid,proxy,sel("comptrollerImplementation()")))
    if not impl: impl=A(call(cid,proxy,sel("implementation()")))
    sc=creation(cid,proxy); ic=creation(cid,impl) if impl else None
    sv=verified(cid,proxy); iv=verified(cid,impl) if impl else None
    print(f"[{label}] {cid} shell={proxy}")
    print(f"   shell created={dt(sc['timestamp']) if sc else '?'} verified={sv['verified'] if sv else '?'}")
    print(f"   impl={impl} created={dt(ic['timestamp']) if ic else '?'} verified={iv['verified'] if iv else '?'}")
    flags=[]
    if sc and ic and int(ic['timestamp'])-int(sc['timestamp'])>180*86400: flags.append("IMPL≫SHELL (fresh logic on old shell)")
    if iv and not iv['verified']: flags.append("IMPL UNVERIFIED")
    if flags: print("   FLAGS:", " | ".join(flags))
for a in PROXIES: age_one(*a)
