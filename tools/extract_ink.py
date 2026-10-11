"""Extrait le script Ink 'main' depuis resources.assets et le bundle leftovers."""
import sys, os, hashlib
import UnityPy

data_dir, out_dir = sys.argv[1], sys.argv[2]
os.makedirs(out_dir, exist_ok=True)
sources = {
    "resources": os.path.join(data_dir, "resources.assets"),
    "bundle": os.path.join(data_dir, "StreamingAssets", "aa", "StandaloneWindows64",
                           "base_leftovers_assets_all.bundle"),
}
for tag, path in sources.items():
    env = UnityPy.load(path)
    for o in env.objects:
        if o.type.name == "TextAsset":
            d = o.read()
            if d.m_Name == "main":
                raw = d.m_Script
                if isinstance(raw, str):
                    raw = raw.encode("utf-8", "surrogateescape")
                out = os.path.join(out_dir, f"main_{tag}.json")
                with open(out, "wb") as f:
                    f.write(raw)
                print(tag, len(raw), hashlib.md5(raw).hexdigest())
