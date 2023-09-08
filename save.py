
import sys, os, struct, json, base64

gPage = "utf8"

def decode(rt, meta = "00000000000000000000000000000000"):
    if rt and not rt.endswith("/") and not rt.endswith("\\") : rt += "/"
    dst = rt + "save/"
    os.makedirs(dst, exist_ok = True)
    meta = json.loads(
        base64.b64decode(
            open(rt + meta, "rb").read()
        )[4:].decode("utf-16-le")
    )
    open(dst + "meta.json", "wb").write(
        json.dumps(meta, indent = 4, sort_keys = False).encode(gPage)
    )
    for k in meta.keys():
        out = dst + k + "/"
        os.makedirs(out, exist_ok = True)
        raw = base64.b64decode(open(rt + k, "rb").read())
        p0 = 4
        p1 = len(raw)
        while p0 < p1:
            sz, = struct.unpack("<I", raw[p0 : p0 + 4])
            p0 += 4
            nm = raw[p0 : p0 + sz].decode("utf-16-le")
            p0 += sz
            sz, = struct.unpack("<I", raw[p0 : p0 + 4])
            p0 += 4
            open(out + nm + ".json", "wb").write(
                raw[p0 : p0 + sz].decode("utf-16-le").encode(gPage)
            )
            p0 += sz

def encode(rt, meta = "00000000000000000000000000000000"):
    if rt and not rt.endswith("/") and not rt.endswith("\\") : rt += "/"
    dst = rt + "save/"
    m = json.loads(
        open(dst + "meta.json", "rb").read().decode(gPage)
    )
    raw = json.dumps(m, indent = 4, sort_keys = False).encode("utf-16-le")
    open(rt + meta, "wb").write(
        base64.b64encode(struct.pack("<I", len(raw)) + raw)
    )
    for k in m.keys():
        out = dst + k + "/"
        with open(k, "wb+") as f:
            fwrite = f.write
            fs = next(os.walk(out))[-1]
            fwrite(struct.pack("<I", len(fs)))
            for fn in fs:
                nm = fn[: -5].encode("utf-16-le")
                fwrite(struct.pack("<I", len(nm)) + nm)
                raw = open(out + fn, "rb").read().decode(gPage).encode("utf-16-le")
                fwrite(struct.pack("<I", len(raw)) + raw)
            f.seek(0)
            raw = f.read()
            f.seek(0)
            fwrite(base64.b64encode(raw))
   

if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)
    if argc > 2:
        rt = ""
        if argc > 3:
            rt = argv[3]
        print(argv)
        {
             "d": decode,
             "e": encode
        }[argv[1]](rt, argv[2])
    
            
            