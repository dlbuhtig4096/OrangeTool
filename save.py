
import sys, os, struct, json, base64

gPage = "utf8"
gLdr = {
    
    "Stage": (
        ("$ka", "StageID"),
        ("$kb", "Star"),
        ("$kc", "ClearCount"),
        ("$kd", "IsNew"),
        ("$ke", "Score"),
        ("$kf", "ExtraResetCount"),
        ("$kg", "LastCharacterID"),
        ("$kh", "LastMainWeaponID"),
        ("$ki", "LastSubWeaponID")
    )
}

def bfDecode(data, hwd):
    data.update(
        json.loads(
            base64.b64decode(
                hwd.read()
            )[4:].decode("utf-16-le")
        )
    )
    return data

def bfEncode(data, hwd):
    raw = json.dumps(data, indent = 4, sort_keys = False).encode("utf-16-le")
    raw = base64.b64encode(struct.pack("<I", len(raw)) + raw)
    hwd.write(raw)
    return raw

def sdDecode(data, hwd):
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

def sdEncode(data, hwd):
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

def procDecode(brief = "BRIEF", rt = ""):
    if rt and not rt.endswith("/") and not rt.endswith("\\") : rt += "/"
    dst = rt + "save/"
    os.makedirs(dst, exist_ok = True)
    m = bfDecode({}, open(rt + brief, "rb"))
    open(dst + "brief.json", "wb").write(
        json.dumps(m, indent = 4, sort_keys = False).encode(gPage)
    )
    for k in m.keys():
        out = dst + k + "/"
        os.makedirs(out, exist_ok = True)
        for nm, dt in sdDecode({}, open(rt + k, "rb")).items():
            open(out + nm + ".json", "wb").write(dt.encode(gPage))

def procEncode(brief = "BRIEF", rt = ""):
    if rt and not rt.endswith("/") and not rt.endswith("\\") : rt += "/"
    dst = rt + "save/"
    m = json.loads(
        open(dst + "brief.json", "rb").read().decode(gPage)
    )
    bfEncode(m, open(rt + brief, "wb"))
    for k in m:
        out = dst + k + "/"
        data = {}
        for fn in next(os.walk(out))[-1]:
            data[fn[: -5]] = open(out + fn, "rb").read().decode(gPage)
        sdEncode(data, open(rt + k, "wb+"))

if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)
    if argc > 1 and argc < 4:
        {
             "d": procDecode,
             "e": procEncode
        }[argv[1]](*argv[2:])
            