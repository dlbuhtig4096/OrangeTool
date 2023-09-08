import os, json, struct, base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import lz4.block

gAesKey = b"cbs4/+-jDAf!?s/#cbs4/+-jDAf!?s/#"
gAesIv = b"=!r19kCsGHTAcr/@"

def _req(dst, src):
    raw = unpad(
        AES.new(gAesKey, AES.MODE_CBC, gAesIv).decrypt(
            base64.b64decode(open(src, "rb").read())
        ), AES.block_size
    ).decode("utf8")
    data = json.loads(raw[: raw.rfind("}") + 1])
    open(dst, "wb").write(json.dumps(data, indent = 4, sort_keys = False).encode("utf8"))
    return data

def _ext(src):
    def _xorpad():
        s = gAesKey + gAesIv
        while True:
            for c in s: yield c
    raw = unpad(AES.new(gAesKey, AES.MODE_CBC, gAesIv).decrypt(base64.b64decode(src)), AES.block_size)
    raw = bytes([c ^ k for c, k in zip(raw, _xorpad())])
    raw = lz4.block.decompress(raw)
    return raw
    
def decode(dst, src):
    if src and not src.endswith("/") and not src.endswith("\\") : src += "/"
    if dst and not dst.endswith("/") and not dst.endswith("\\") : dst += "/"
    os.makedirs(dst, exist_ok = True)
    _req(dst + "PlayerInfo.json", src + "RetrievePlayerInfoReq")
    pRawExData = _req(dst + "Collector1.json", src + "LoginRetrieveCollector1Req")["aa"]
    pRawExData += _req(dst + "Collector2.json", src + "LoginRetrieveCollector2Req")["aa"]
    pRawExData += _req(dst + "Collector3.json", src + "LoginRetrieveCollector3Req")["aa"]
    pRawExData += _req(dst + "Collector4.json", src + "LoginRetrieveCollector4Req")["aa"]
    open(dst + "ExData.json", "wb").write(_ext(pRawExData.encode("utf8")))

decode("./out/", "./")
