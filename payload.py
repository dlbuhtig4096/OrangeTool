
import os, sys, json, base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import lz4.block

gAesKey = b"cbs4/+-jDAf!?s/#cbs4/+-jDAf!?s/#"
gAesIv = b"=!r19kCsGHTAcr/@"

gLdr1 = {
    "a": "Item",
    "b": "Character",
    "c": "CharacterSkill",
    "d": "CharacterSkin",
    "e": "Pet",
    "f": "Card",
    "g": "CharacterCardSlot",
    "h": "CardDeploy",
    "i": "CardDeployName",
    "j": "CharacterDNA",
    "k": "CharacterDNALink"
}
gLdr2 = {
    "a": "Weapon",
    "b": "WeaponExpert",
    "c": "WeaponSkill",
    "d": "Equipment",
    "e": "PlayerEquip",
    "f": "FinalStrike",
    "g": "Chip",
    "h": "Charge",
    "i": "Tutorial",
    "j": "PlayerService",
    "k": "BenchWeapon",
    "l": "WeaponDiVESkill"
}
gLdr3 = {
    "a": "Stage",
    "b": "Gallery",
    "c": "GalleryExp",
    "d": "MailCount",
    "e": "Mail",
    "f": "ExtraSystemContext",
    "g": "Mission",
    "h": "Research",
    "i": "ResearchRecord",
    "j": "FreeResearch",
    "k": "StageSecret",
    "l": "TowerBoss",
    "m": "GalleryMainId"
}
gLdr4 = {
    "a": "GachaRecord",
    "b": "GachaGuaranteeRecord",
    "c": "MultiPlayerGacha",
    "d": "ShopRecord",
    "e": "BoxGachaRecord",
    "f": "EventRanking",
    "u": "Banner",
    "v": "ItemEx",
    "w": "GachaEx",
    "x": "GachaEventEx",
    "y": "ShopEx",
    "z": "EventEx"
}

def _req(src):
    return json.loads(
        unpad(
            AES.new(gAesKey, AES.MODE_CBC, gAesIv).decrypt(
                base64.b64decode(open(src, "rb").read())
            ), AES.block_size
        ).decode("utf8")
    )

def _ext(src):
    def _xorpad():
        s = gAesKey + gAesIv
        while True:
            for c in s: yield c
    raw = unpad(AES.new(gAesKey, AES.MODE_CBC, gAesIv).decrypt(base64.b64decode(src)), AES.block_size)
    raw = bytes([c ^ k for c, k in zip(raw, _xorpad())])
    raw = lz4.block.decompress(raw)
    
    # Todo: parse the bson
    return raw
    
def procDecode(dst, src):
    if src and not src.endswith("/") and not src.endswith("\\") : src += "/"
    if dst and not dst.endswith("/") and not dst.endswith("\\") : dst += "/"
    os.makedirs(dst, exist_ok = True)
    _req(src + "RetrievePlayerInfoReq")
    C1 = _req(src + "LoginRetrieveCollector1Req")
    C2 = _req(src + "LoginRetrieveCollector2Req")
    C3 = _req(src + "LoginRetrieveCollector3Req")
    C4 = _req(src + "LoginRetrieveCollector4Req")
    for k, v in gLdr1.items(): open(dst + v + ".json", "wb").write(json.dumps(C1[k], indent = 4, sort_keys = False).encode("utf8"))
    for k, v in gLdr2.items(): open(dst + v + ".json", "wb").write(json.dumps(C2[k], indent = 4, sort_keys = False).encode("utf8"))
    for k, v in gLdr3.items(): open(dst + v + ".json", "wb").write(json.dumps(C3[k], indent = 4, sort_keys = False).encode("utf8"))
    for k, v in gLdr4.items(): open(dst + v + ".json", "wb").write(json.dumps(C4[k], indent = 4, sort_keys = False).encode("utf8"))
    open(dst + "ExData.json", "wb").write(_ext((C1["aa"] + C2["aa"] + C3["aa"] + C4["aa"]).encode("utf8")))

if __name__ == "__main__":
    argv = sys.argv
    if len(argv) == 3: procDecode(*argv[1 :])
