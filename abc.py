
import os, sys, json, hashlib, base64, zlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

gAesKey = b"cbs4/+-jDAf!?s/#cbs4/+-jDAf!?s/#"
gAesIv = b"=!r19kCsGHTAcr/@"

def _iter(key):
    while True:
        for c in key: yield c

_id = lambda s : s
crcCrypto = lambda s, k : bytes([c ^ x for c, x in zip(s, _iter(k))])
capCrypto = lambda s : crcCrypto(s, gAesKey + gAesIv)
binDecode = lambda s : capCrypto(unpad(
    AES.new(gAesKey, AES.MODE_CBC, gAesIv).decrypt(s), AES.block_size
))
binEncode = lambda s : AES.new(gAesKey, AES.MODE_CBC, gAesIv).encrypt(
    pad(capCrypto(s), AES.block_size)
)
netDecode = lambda s : unpad(
    AES.new(gAesKey, AES.MODE_CBC, gAesIv).decrypt(
        base64.b64decode(s)
    ), AES.block_size
)
netEncode = lambda s : base64.b64encode(
    AES.new(gAesKey, AES.MODE_CBC, gAesIv).encrypt(
        pad(s, AES.block_size)
    )
)

gOrangeDecoder = {
    "abconfig": netDecode,
    "audiofileinfo": netDecode,
    "RelayParam": netDecode,
    "GameData.bin": binDecode,
    "TextData.bin": binDecode,
    "ORANGE_SOUND.acf": _id
}
gOrangeEncoder = {
    "abconfig": netEncode,
    "audiofileinfo": netEncode,
    "RelayParam": netEncode,
    "GameData.bin": binEncode,
    "TextData.bin": binEncode,
    "ORANGE_SOUND.acf": _id
}

def procEncode(dst, src):
    if src and not src.endswith("/") and not src.endswith("\\") : src += "/"
    if dst and not dst.endswith("/") and not dst.endswith("\\") : dst += "/"
    os.makedirs(src, exist_ok = True)
    data = {}
    for fn in gOrangeEncoder:
        data[fn] = open(dst + fn, "rb").read()
    abc = json.loads(data["abconfig"])
    afi = json.loads(data["audiofileinfo"])
    for d in abc["ListAssetbundleId"]:
        fn = d["name"]
        raw = open(dst + fn, "rb").read()
        d["hash"] = fn = hashlib.md5(fn.encode("utf8")).hexdigest()
        d["crc"] = crc = zlib.crc32(raw)
        open(src + fn, "wb").write(
            crcCrypto(
                raw,
                [min(1 << int(i), 0x80) for i in str(crc)]
            )
        )
    rt = dst + "audio/" 
    for d in afi:
        fn = d["name"]
        if not fn.endswith(".awb"): fn += ".acb"
        open(src + hashlib.md5(fn.encode("utf8")).hexdigest(), "wb").write(
            open(rt + fn, "rb").read()
        )
        
    data["abconfig"] = json.dumps(abc, sort_keys = False).encode("utf8")
    for fn, raw in data.items():
        open(dst + fn, "wb").write(raw)
        open(src + hashlib.md5(fn.encode("utf8")).hexdigest(), "wb").write(
            gOrangeEncoder[fn](raw)
        )

def procDecode(dst, src):
    if src and not src.endswith("/") and not src.endswith("\\") : src += "/"
    if dst and not dst.endswith("/") and not dst.endswith("\\") : dst += "/"
    os.makedirs(dst, exist_ok = True)
    data = {}
    for fn, cb in gOrangeDecoder.items():
        data[fn] = raw = cb(open(src + hashlib.md5(fn.encode("utf8")).hexdigest(), "rb").read())
        open(dst + fn, "wb").write(raw)
    for d in json.loads(data["abconfig"].decode("utf8"))["ListAssetbundleId"]:
        fn = d["name"]
        rt = fn[: fn.rfind("/") + 1]
        if rt : os.makedirs(dst + rt, exist_ok = True)
        open(dst + fn, "wb").write(
            crcCrypto(
                open(src + d["hash"], "rb").read(),
                [min(1 << int(i), 0x80) for i in str(d["crc"])]
            )
        )
    rt = dst + "audio/" 
    os.makedirs(dst + rt, exist_ok = True)
    for d in json.loads(data["audiofileinfo"]):
        fn = d["name"]
        if not fn.endswith(".awb"): fn += ".acb"
        open(rt + fn, "wb").write(
            open(src + hashlib.md5(fn.encode("utf8")).hexdigest(), "rb").read()
        )

if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)
    if argc == 3:
        {
             "d": procDecode,
             "e": procEncode
        }[argv[1]](*argv[2:])
            