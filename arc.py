
import io, os, sys, struct, json, hashlib, base64, zlib, threading
import yaml
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import lz4.block
import requests

gAesKey = b"cbs4/+-jDAf!?s/#cbs4/+-jDAf!?s/#"
gAesIv = b"=!r19kCsGHTAcr/@"
gYamlLdr = yaml.CLoader if hasattr(yaml, "CLoader") else yaml.Loader
gYamlDpr = yaml.CDumper if hasattr(yaml, "CDumper") else yaml.Dumper

_id = lambda s : s

# XOR crypto
def _iter(key):
    while True:
        for c in key: yield c
ccCrypto = lambda s, k : bytes([c ^ x for c, x in zip(s, _iter(k))])

# Capcom Data Diagram
_cdd_i32 = lambda cb: struct.unpack("<i", cb(4))[0]
_cdd_i64 = lambda cb: struct.unpack("<q", cb(8))[0]
_cdd_f64 = lambda cb: struct.unpack("<d", cb(8))[0]
_cdd_a8 = lambda cb: cb(struct.unpack("<I", cb(4))[0]).decode("utf-16-le")
_cdd_a16 = _cdd_a8
_cdd_u8 = lambda cb: cb(1)[0]
_cdd_u32 = lambda cb: struct.unpack("<I", cb(4))[0]
_cdd_jpt = [_cdd_i32, _cdd_i64, _cdd_f64, _cdd_a8, _cdd_a16, _cdd_u8, _cdd_a16]
_cdd_lbl = ["i32", "i64", "f64", "a8", "a16", "u8", "cmt"]
_cde_i32 = lambda cb, v: cb(struct.pack("<i", v))
_cde_i64 = lambda cb, v: cb(struct.pack("<q", v))
_cde_f64 = lambda cb, v: cb(struct.pack("<d", v))
def _cde_a8(cb, v):
    s = v.encode("utf-16-le")
    cb(struct.pack("<I", len(s)))
    cb(s)
_cde_a16 = _cde_a8
_cde_u8 = lambda cb, v: cb(chr(v))
_cde_u32 = lambda cb, v: cb(struct.pack("<I", v))
_cde_jpt = [_cde_i32, _cde_i64, _cde_f64, _cde_a8, _cde_a16, _cde_u8, _cde_a16]
_cde_lbl = {v: k for k, v in enumerate(_cdd_lbl)}

# 
class NullLdr:
    hf = hashlib.md5
    
    def __init__(self, name, url = None):
        self.mName = name
        self.mHash = self.hf(name.encode("utf8")).hexdigest()
        self.mPath = name
        self.mUrl = url
    
    load = staticmethod(_id)
    dump = staticmethod(_id)
    decode = staticmethod(_id)
    encode = staticmethod(_id)
    
    def unpackImpl(self, dst, src, dt, ls):
        return dt
    
    def unpack(self, dst, src, ls):
        s = self.dump(
            self.unpackImpl(
                dst, src,
                self.decode(
                    open(src + self.mHash, "rb").read()
                ), ls
            )
        )
        open(dst + self.mPath, "wb").write(s)
        
    def repackImpl(self, dst, src, dt, ls):
        return dt
        
    def repack(self, dst, src, ls):
        s = self.encode(
            self.repackImpl(
                dst, src,
                self.load(
                    open(dst + self.mPath, "rb").read()
                ), ls
            )
        )
        open(src + self.mHash, "wb").write(s)
        
    def crawlImpl(self, dst, src, dt, url, hdr):
        return dt
        
    def crawl(self, dst, src, url, hdr):
        r = requests.get(self.mUrl or url + requests.utils.quote(self.mName), hdr)
        if r.status_code != 200:
            print("[Error] Skipping %s" % self.mName)
            return
        
        raw = r.content
        open(src + self.mHash, "wb").write(raw)
        s = self.dump(
            self.crawlImpl(
                dst, src, self.decode(raw), url, hdr
            )
        )
        open(dst + self.mPath, "wb").write(s)
    
# Json
class JsonLdr(NullLdr):
        
    load = staticmethod(
        lambda dt: json.loads(dt.decode("utf8"))
    )
        
    dump = staticmethod(
        lambda dt: json.dumps(
            dt, indent = 4, sort_keys = False
        ).encode("utf8")
    )

    decode = staticmethod(
        lambda dt : json.loads(
            unpad(
                AES.new(gAesKey, AES.MODE_CBC, gAesIv).decrypt(
                    base64.b64decode(dt)
                ), AES.block_size
            ).decode("utf8")
        )
    )
    
    encode = staticmethod(
        lambda dt : base64.b64encode(
            AES.new(gAesKey, AES.MODE_CBC, gAesIv).encrypt(
                pad(
                    json.dumps(dt, indent = None, sort_keys = False).encode("utf8"),
                    AES.block_size
                )
            )
        )
    )

# abconfig
class AbcLdr(JsonLdr):
    
    # Unpack asset bundle
    def unpackImpl(self, dst, src, dt, ls):
        tbl = dt["ListAssetbundleId"]
        tbl = [d for d in tbl if d["name"] in ls or d["hash"] in ls] if ls else tbl
        for d in tbl:
            fn = d["name"]
            rt = fn[: fn.rfind("/") + 1]
            if rt : os.makedirs(dst + rt, exist_ok = True)
            open(dst + fn, "wb").write(
                ccCrypto(
                    open(src + d["hash"], "rb").read(),
                    [min(1 << int(i), 0x80) for i in str(d["crc"])]
                )
            )
        return dt
        
    # Repack asset bundle
    def repackImpl(self, dst, src, dt, ls):
        hf = self.hf
        tbl = dt["ListAssetbundleId"]
        tbl = [d for d in tbl if d["name"] in ls or d["hash"] in ls] if ls else tbl
        for d in tbl:
            fn = d["name"]
            if ls and not fn in ls: continue
            raw = open(dst + fn, "rb").read()
            d["hash"] = fn = hf(fn.encode("utf8")).hexdigest()
            crc = d["crc"] # d["crc"] = crc = zlib.crc32(raw)
            open(src + fn, "wb").write(
                ccCrypto(
                    raw,
                    [min(1 << int(i), 0x80) for i in str(crc)]
                )
            )
        return dt
    
    # Crawl asset bundle
    def crawlImpl(self, dst, src, dt, url, hdr):
        for d in dt["ListAssetbundleId"]:
            fn = d["name"]
            rt = fn[: fn.rfind("/") + 1]
            if rt : os.makedirs(dst + rt, exist_ok = True)
            
            if os.path.exists(dst + fn): continue
            r = requests.get(url + requests.utils.quote(fn), hdr)
            if r.status_code != 200:
                print("[Error] Skipping %s" % fn)
                continue
            
            raw = r.content
            open(src + d["hash"], "wb").write(raw)
            open(dst + fn, "wb").write(
                ccCrypto(
                    raw,
                    [min(1 << int(i), 0x80) for i in str(d["crc"])]
                )
            )
        return dt
       
# audiofileinfo
class AfiLdr(JsonLdr):
    
    # Unpack audio
    def unpackImpl(self, dst, src, dt, ls):
        rt = dst + "audio/" 
        hf = self.hf
        os.makedirs(rt, exist_ok = True)
        tbl = []
        for d in dt:
            fn = d["Name"]
            tbl.append([fn + ".acb" if not fn.endswith(".awb") else fn, d])
        if ls: tbl = [d for d in tbl if d[0] in ls or hf(d[0]) in ls]
        for fn, d in tbl:
            open(rt + fn, "wb").write(
                open(src + hf(fn.encode("utf8")).hexdigest(), "rb").read()
            )
        return dt
            
    # Repack audio
    def repackImpl(self, dst, src, dt, ls):
        rt = dst + "audio/" 
        hf = self.hf
        tbl = []
        for d in dt:
            fn = d["Name"]
            tbl.append([fn + ".acb" if not fn.endswith(".awb") else fn, d])
        if ls: tbl = [d for d in tbl if d[0] in ls or hf(d[0]) in ls]
        for fn, d in tbl:
            raw = open(rt + fn, "rb").read()
            d["Crc"] = hashlib.sha1(raw).hexdigest()
            d["Size"] = len(raw)
            open(src + hf(fn.encode("utf8")).hexdigest(), "wb").write(raw)
        return dt
    
    # Crawl audio
    def crawlImpl(self, dst, src, dt, url, hdr):
        rt = dst + "audio/" 
        hf = self.hf
        os.makedirs(rt, exist_ok = True)
        for d in dt:
            fn = d["Name"]
            if not fn.endswith(".awb"): fn += ".acb"
            
            if os.path.exists(rt + fn): continue
            r = requests.get(url + requests.utils.quote(fn), hdr)
            if r.status_code != 200:
                print("[Error] Skipping %s" % fn)
                continue
            
            raw = r.content
            open(src + hf(fn.encode("utf8")).hexdigest(), "wb").write(raw)
            open(rt + fn, "wb").write(raw)
            
        return dt
       
# Extra raw data
class ExtLdr(NullLdr):
    decode = staticmethod(
        lambda dt: lz4.block.decompress(
            ccCrypto(
                unpad(
                    AES.new(gAesKey, AES.MODE_CBC, gAesIv).decrypt(dt),
                    AES.block_size
                ),
                gAesKey + gAesIv
            )
        )
    )
    
    encode = staticmethod(
        lambda dt: AES.new(gAesKey, AES.MODE_CBC, gAesIv).encrypt(
            pad(
                ccCrypto(
                    lz4.block.compress(dt),
                    gAesKey + gAesIv
                ),
                AES.block_size
            )
        )
    )
    
    
# Capcom data diagram
class CddLdr(ExtLdr):
    
    def __init__(self, name, url = None):
        super(CddLdr, self).__init__(name, url)
        self.mPath = name[: name.rfind(".") + 1][: -1] + "/.yaml"
    
    load = staticmethod(
        lambda dt: yaml.load(dt.decode("utf8"), Loader = gYamlLdr)
    )
    dump = staticmethod(
        lambda dt: yaml.dump(dt, Dumper = gYamlDpr, indent = 4, allow_unicode = True, sort_keys = False).encode("utf8")
    )
    
    @staticmethod
    def decode(dt):
        ls = []
        dv = {"": ls}
        dp = {"": dv}
        dt = ExtLdr.decode(dt)
        with io.BytesIO(dt) as f:
            fread = f.read
            
            numTbl = _cdd_u32(fread)
            for i in range(numTbl):
                h = _cdd_u32(fread)
                if h != 0x2:
                    ls.append(h)
                    continue
                dCol = {}
                pCol = []
                name = _cdd_a16(fread)
                ls.append(name)
                dp[name] = df = [dCol]
                numCol = _cdd_u32(fread)
                for j in range(numCol):
                    lCol = _cdd_a16(fread)
                    tCol = _cdd_u32(fread)
                    dCol[lCol] = _cdd_lbl[tCol]
                    pCol.append([lCol, _cdd_jpt[tCol]])
                numRow = _cdd_u32(fread)
                for j in range(numRow):
                    dr = {}
                    df.append(dr)
                    for k, p in pCol: dr[k] = p(fread)
                
            numVar = _cdd_u32(fread)
            for i in range(numVar):
                k = _cdd_a16(fread)
                dv[k] = _cdd_a16(fread)
            dv["$CreateTime"] = _cdd_a16(fread)
                
        return dp
    
    @staticmethod
    def encode(dt):
        dv = dt.get("", {})
        ls = dv.get("", [])
        with io.BytesIO() as f:
            fwrite = f.write
            
            fwrite(struct.pack("<I", len(ls)))
            for i in ls:
                if not isinstance(i, str):
                    _cde_u32(fwrite, i)
                    continue
                _cde_u32(fwrite, 0x2)
                dCol, *df = dt[i]
                pCol = []
                _cde_a16(fwrite, i)
                _cde_u32(fwrite, len(dCol))
                for lCol, tCol in dCol.items():
                    tCol = _cde_lbl[tCol]
                    _cde_a16(fwrite, lCol)
                    _cde_u32(fwrite, tCol)
                    pCol.append([lCol, _cde_jpt[tCol]])
                _cde_u32(fwrite, len(df))
                for dr in df:
                    for k, p in pCol: p(fwrite, dr[k])
                    
            sv = set(dv)
            sv.remove("")
            sv.remove("$CreateTime")
            _cde_u32(fwrite, len(sv))
            for i in sv:
                _cde_a16(fwrite, i)
                _cde_a16(fwrite, dv[i])
            _cde_a16(fwrite, dv.get("$CreateTime", ""))
                
            return ExtLdr.encode(f.getvalue())
        
    # Unpack data diagram
    def unpackImpl(self, dst, src, dt, ls):
        rt = dst + self.mPath[: -5]
        os.makedirs(rt, exist_ok = True)
        d = dt.pop("", {})
        for k, df in dt.items():
            if not isinstance(k, str): continue
            open(rt + k + ".yaml", "wb").write(self.dump(df))
        return d
    
    # Repack data diagram
    def repackImpl(self, dst, src, dt, ls):
        rt = dst + self.mPath[: -5]
        dv = dt
        dt = {"": dt}
        for k in dv.get("", []):
            if not isinstance(k, str): continue
            dt[k] = self.load(open(rt + k + ".yaml", "rb").read())
        return dt
    
    # Crawl data diagram
    def crawlImpl(self, dst, src, dt, url, hdr):
        rt = dst + self.mPath[: -5]
        os.makedirs(rt, exist_ok = True)
        d = dt.pop("", {})
        for k, df in dt.items():
            if not isinstance(k, str): continue
            open(rt + k + ".yaml", "wb").write(self.dump(df))
        return d
    
# =============================================================================
PROTOCOL = "http"
ORIGIN = "rxdres.capcom.com.tw"
DOMAIN = "%s://%s/" % (PROTOCOL, ORIGIN)

gHdr = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=1.0",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "DNT": "1",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0"
}

def _proc(ldr, ls):
    if not ls: return ldr
    tbl = []
    for L in ldr:
        try:
            ls.remove(L.mName)
        except KeyError:
            try:
                ls.remove(L.mHash)
            except KeyError:
                continue
        tbl.append(L)
    return tbl

def _run(f, *a):
    t = threading.Thread(target = f, args = a)
    t.start()
    return t

def procUnpack(dst, src, ldr, ls):
    if src and not src.endswith("/") and not src.endswith("\\") : src += "/"
    if dst and not dst.endswith("/") and not dst.endswith("\\") : dst += "/"
    ls = set(ls)
    os.makedirs(dst, exist_ok = True)
    for L in ldr: L.unpack(dst, src, ls)
    
def procRepack(dst, src, ldr, ls):
    if src and not src.endswith("/") and not src.endswith("\\") : src += "/"
    if dst and not dst.endswith("/") and not dst.endswith("\\") : dst += "/"
    ls = set(ls)
    os.makedirs(src, exist_ok = True)
    for L in ldr: L.repack(dst, src, ls)

def procCrawl(dst, src, ldr = None, ls = None):
    if src and not src.endswith("/") and not src.endswith("\\") : src += "/"
    if dst and not dst.endswith("/") and not dst.endswith("\\") : dst += "/"
    os.makedirs(src, exist_ok = True)
    os.makedirs(dst, exist_ok = True)
    for t in [
        _run(AbcLdr("abconfig").crawl, dst, src, DOMAIN + "325/AssetBundlesEncrypt/StandaloneWindows/", gHdr),
        _run(AfiLdr("audiofileinfo").crawl, dst, src, DOMAIN + "325/CriWare/Android/Assets/StreamingAssets/", gHdr),
        _run(JsonLdr("localizationfileinfo").crawl, dst, src, DOMAIN + "325/Localization/", gHdr),
        _run(JsonLdr("RelayParam").crawl, dst, src, DOMAIN + "325/CriWare/Android/Assets/StreamingAssets/", gHdr),
        _run(CddLdr("GameData.bin", DOMAIN + "325/Designs/OrangeData.bin").crawl, dst, src, DOMAIN + "325/Designs/", gHdr),
        _run(CddLdr("TextData.bin", DOMAIN + "325/Designs/OrangeTextData.bin").crawl, dst, src, DOMAIN + "325/Designs/", gHdr),
        _run(CddLdr("ExGameData.bin", DOMAIN + "ExOrangeData.bin").crawl, dst, src, DOMAIN, gHdr),
        _run(CddLdr("ExTextData.bin", DOMAIN + "ExOrangeTextData.bin").crawl, dst, src, DOMAIN, gHdr),
        _run(JsonLdr("5.1.1.bin").crawl, dst, src, DOMAIN, gHdr),
        _run(NullLdr("forbiddenInfo.json").crawl, dst, src, DOMAIN + "325/Designs/", gHdr),
        _run(NullLdr("ORANGE_SOUND.acf").crawl, dst, src, DOMAIN + "325/CriWare/Android/Assets/StreamingAssets/", gHdr),
        _run(NullLdr("StandaloneWindows.manifest").crawl, dst, src, DOMAIN + "325/AssetBundlesEncrypt/StandaloneWindows/", gHdr)
    ]: t.join()

if __name__ == "__main__":
    argv = sys.argv
    if len(argv) > 3:
        ls = set(argv[4:])
        {
            "c": procCrawl,
            "d": procUnpack,
            "e": procRepack
        }[argv[1]](
            argv[2],
            argv[3],
            _proc([
                    AbcLdr("abconfig"),
                    AfiLdr("audiofileinfo"),
                    JsonLdr("RelayParam"),
                    CddLdr("GameData.bin"),
                    CddLdr("TextData.bin"),
                    NullLdr("ORANGE_SOUND.acf")
                ], ls
            ),
            ls
        )
            