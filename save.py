
import sys, os, struct, json, base64

gPage = "utf8"

def metaDecode(data, hwd):
    data.update(
        json.loads(
            base64.b64decode(
                hwd.read()
            )[4:].decode("utf-16-le")
        )
    )
    return data

def metaEncode(data, hwd):
    raw = json.dumps(data, indent = 4, sort_keys = False).encode("utf-16-le")
    raw = base64.b64encode(struct.pack("<I", len(raw)) + raw)
    hwd.write(raw)
    return raw

def slotDecode(data, hwd):
    raw = base64.b64decode(hwd.read())
    p0 = 4
    p1 = len(raw)
    while p0 < p1:
        sz, = struct.unpack("<I", raw[p0 : p0 + 4])
        p0 += 4
        nm = raw[p0 : p0 + sz].decode("utf-16-le")
        p0 += sz
        sz, = struct.unpack("<I", raw[p0 : p0 + 4])
        p0 += 4
        data[nm] = raw[p0 : p0 + sz].decode("utf-16-le")
        p0 += sz
    return data

def slotEncode(data, hwd):
    fwrite = hwd.write
    fwrite(struct.pack("<I", len(data)))
    for nm, dt in data.items():
        nm = nm.encode("utf-16-le")
        fwrite(struct.pack("<I", len(nm)) + nm)
        dt = dt.encode("utf-16-le")
        fwrite(struct.pack("<I", len(dt)) + dt)
    hwd.seek(0)
    raw = hwd.read()
    hwd.seek(0)
    raw = base64.b64encode(raw)
    fwrite(raw)
    return raw

def procDecode(rt, meta = "00000000000000000000000000000000"):
    if rt and not rt.endswith("/") and not rt.endswith("\\") : rt += "/"
    dst = rt + "save/"
    os.makedirs(dst, exist_ok = True)
    m = metaDecode({}, open(rt + meta, "rb"))
    open(dst + "meta.json", "wb").write(
        json.dumps(m, indent = 4, sort_keys = False).encode(gPage)
    )
    for k in m.keys():
        out = dst + k + "/"
        os.makedirs(out, exist_ok = True)
        for nm, dt in slotDecode({}, open(rt + k, "rb")).items():
            open(out + nm + ".json", "wb").write(dt.encode(gPage))

def procEncode(rt, meta = "00000000000000000000000000000000"):
    if rt and not rt.endswith("/") and not rt.endswith("\\") : rt += "/"
    dst = rt + "save/"
    m = json.loads(
        open(dst + "meta.json", "rb").read().decode(gPage)
    )
    metaEncode(m, open(rt + meta, "wb"))
    for k in m:
        out = dst + k + "/"
        data = {}
        for fn in next(os.walk(out))[-1]:
            data[fn[: -5]] = open(out + fn, "rb").read().decode(gPage)
        slotEncode(data, open(rt + k, "wb+"))

if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)
    if argc > 2:
        rt = ""
        if argc > 3:
            rt = argv[3]
        print(argv)
        {
             "d": procDecode,
             "e": procEncode
        }[argv[1]](rt, argv[2])
            