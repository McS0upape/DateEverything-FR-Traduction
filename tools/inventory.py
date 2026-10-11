"""Inventorie les TextAssets du jeu (scripts Ink, tables de texte...)."""
import sys, os, collections
import UnityPy

data_dir = sys.argv[1]
files = [os.path.join(data_dir, "resources.assets"), os.path.join(data_dir, "sharedassets0.assets")]
bdir = os.path.join(data_dir, "StreamingAssets", "aa", "StandaloneWindows64")
for f in os.listdir(bdir):
    if "audio" in f or "texture" in f or "video" in f:
        continue
    files.append(os.path.join(bdir, f))

for path in files:
    env = UnityPy.load(path)
    counts = collections.Counter(o.type.name for o in env.objects)
    texts = []
    for o in env.objects:
        if o.type.name == "TextAsset":
            d = o.read()
            raw = d.m_Script
            size = len(raw.encode("utf-8", "surrogateescape")) if isinstance(raw, str) else len(raw)
            texts.append((d.m_Name, size))
    print(f"== {os.path.basename(path)}  TextAssets={len(texts)} MonoBehaviour={counts.get('MonoBehaviour',0)}")
    for name, size in sorted(texts, key=lambda t: -t[1])[:15]:
        print(f"     {size:>10}  {name}")
