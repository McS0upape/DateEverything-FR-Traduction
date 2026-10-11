"""Vérifie la présence des caractères français dans les polices TextMeshPro du jeu."""
import sys, os
import UnityPy

FR = "éèêëàâäîïôöùûüçœæÉÈÊÀÂÎÔÙÛÇŒ«»’…  —–"
data_dir = sys.argv[1]
bdir = os.path.join(data_dir, "StreamingAssets", "aa", "StandaloneWindows64")
paths = [os.path.join(data_dir, f) for f in ("resources.assets", "sharedassets0.assets")]
paths += [os.path.join(bdir, f) for f in os.listdir(bdir)
          if "textmeshpro" in f or "leftovers_asset" in f or "leftovers_assets" in f]
for p in paths:
    env = UnityPy.load(p)
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            t = o.read_typetree()
        except Exception:
            continue
        if "m_CharacterTable" not in t:
            continue
        codes = {c["m_Unicode"] for c in t["m_CharacterTable"]}
        dyn = t.get("m_AtlasPopulationMode")
        missing = "".join(ch for ch in FR if ord(ch) not in codes)
        fallbacks = len(t.get("m_FallbackFontAssetTable", []))
        print(f"{os.path.basename(p)[:40]:40} {t['m_Name'][:40]:40} glyphs={len(codes):5} dynamic={dyn} fallbacks={fallbacks} manquants='{missing}'")
