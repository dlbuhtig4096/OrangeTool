
import os, sys, json
import yaml
gYamlLdr = yaml.CLoader if hasattr(yaml, "CLoader") else yaml.Loader
gYamlDpr = yaml.CDumper if hasattr(yaml, "CDumper") else yaml.Dumper

def cvtTbl(dst, src):
    fn = src[max(src.rfind("/"), src.rfind("\\")) + 1:]
    try:
        tbl = yaml.load(open(src, "rb").read().decode("utf8"), gYamlLdr)
    except:
        return
    open(dst, "wb").write(
        json.dumps({fn: tbl[1:]}, indent = 4, sort_keys = False).encode("utf8")
    )
    
def cvtInf(dst, src):
    a = yaml.load(open(src, "rb").read().decode("utf8"), gYamlLdr)
    t = set(a)
    t.remove("")
    t.remove("$CreateTime")
    open(dst, "wb").write(
        json.dumps({k: a[k] for k in t}, indent = 4, sort_keys = False).encode("utf8")
    )

def cvtAll(dst, src):
    if src and not src.endswith("/") and not src.endswith("\\") : src += "/"
    if dst and not dst.endswith("/") and not dst.endswith("\\") : dst += "/"
    os.makedirs(dst, exist_ok = True)
    
    a = yaml.load(open(src + ".yaml", "rb").read().decode("utf8"), gYamlLdr)
    for fn in a[""]:
        if not isinstance(fn, str): continue
        try:
            tbl = yaml.load(open(src + fn + ".yaml", "rb").read().decode("utf8"), gYamlLdr)
        except:
            continue
        open(dst + fn + ".json", "wb").write(
            json.dumps({fn: tbl[1:]}, indent = 4, sort_keys = False).encode("utf8")
        )
    t = set(a)
    t.remove("")
    t.remove("$CreateTime")
    open(dst + "Parameters.json", "wb").write(
        json.dumps({k: a[k] for k in t}, indent = 4, sort_keys = False).encode("utf8")
    )

if __name__ == "__main__":
    argv = sys.argv
    if len(argv) == 3:
        dst, src = argv
        (
            cvtAll if not src.endswith(".yaml") else 
                cvtInf if src.endswith("/.yaml") or src.endswith("\\.yaml")
                    else cvtTbl 
        )(dst, src)

