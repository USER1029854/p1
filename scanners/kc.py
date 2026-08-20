# Pure-Python Keccak-256 (Ethereum). No deps.
_RC=[0x0000000000000001,0x0000000000008082,0x800000000000808A,0x8000000080008000,
0x000000000000808B,0x0000000080000001,0x8000000080008081,0x8000000000008009,
0x000000000000008A,0x0000000000000088,0x0000000080008009,0x000000008000000A,
0x000000008000808B,0x800000000000008B,0x8000000000008089,0x8000000000008003,
0x8000000000008002,0x8000000000000080,0x000000000000800A,0x800000008000000A,
0x8000000080008081,0x8000000000008080,0x0000000080000001,0x8000000080008008]
_R=[[0,36,3,41,18],[1,44,10,45,2],[62,6,43,15,61],[28,55,25,21,56],[27,20,39,8,14]]
M=(1<<64)-1
def _rol(x,n): return ((x<<n)|(x>>(64-n)))&M
def _keccak_f(S):
    for rc in _RC:
        C=[S[x][0]^S[x][1]^S[x][2]^S[x][3]^S[x][4] for x in range(5)]
        D=[C[(x-1)%5]^_rol(C[(x+1)%5],1) for x in range(5)]
        for x in range(5):
            for y in range(5): S[x][y]^=D[x]
        B=[[0]*5 for _ in range(5)]
        for x in range(5):
            for y in range(5): B[y][(2*x+3*y)%5]=_rol(S[x][y],_R[x][y])
        for x in range(5):
            for y in range(5): S[x][y]=B[x][y]^((~B[(x+1)%5][y])&B[(x+2)%5][y])
        S[0][0]^=rc
    return S
def keccak256(msg):
    rate=136
    S=[[0]*5 for _ in range(5)]
    m=bytearray(msg)
    m.append(0x01)
    while len(m)%rate: m.append(0x00)
    m[-1]^=0x80
    for off in range(0,len(m),rate):
        blk=m[off:off+rate]
        for i in range(rate//8):
            w=int.from_bytes(blk[i*8:i*8+8],'little')
            S[i%5][i//5]^=w
        _keccak_f(S)
    out=bytearray()
    for i in range(4):
        out+=int(S[i%5][i//5]).to_bytes(8,'little')
    return bytes(out[:32])
def sel(sig): return '0x'+keccak256(sig.encode()).hex()[:8]
def topic(sig): return '0x'+keccak256(sig.encode()).hex()
if __name__=="__main__":
    assert sel("transfer(address,uint256)")=="0xa9059cbb", sel("transfer(address,uint256)")
    assert topic("Approval(address,address,uint256)")=="0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"
    assert sel("getAllMarkets()")=="0xb0772d0b"
    assert sel("oracle()")=="0x7dc0d1d0"
    assert sel("getReserves()")=="0x0902f1ac"
    print("Keccak-256 OK. Sample selectors:")
    for s in ["getAllPools()","markets(address)","slot0()","getReservesList()","exchangeRateStored()","comptrollerImplementation()","borrowAllowance(address,address)","MINTER_ROLE()","hasRole(bytes32,address)"]:
        print(f"  {s:34s} {sel(s)}")
