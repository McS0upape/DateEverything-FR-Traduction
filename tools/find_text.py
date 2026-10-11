"""Cherche une chaîne dans les objets (MonoBehaviour, TextAsset...) des fichiers du jeu et affiche leur contexte.

Usage : python find_text.py <dossier Date Everything_Data> "<texte>"
"""
import os
import sys

import UnityPy

data_dir, needle = sys.argv[1], sys.argv[2]
bdir = os.path.join(data_dir, "StreamingAssets", "aa", "StandaloneWindows64")
paths = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith(".assets") or f.startswith("level")]
paths += [os.path.join(bdir, f) for f in os.listdir(bdir) if "texture" not in f and "audio" not in f and "video" not in f]
nb = needle.encode("utf-8")
for p in paths:
    raw = open(p, "rb").read() if not p.endswith(".bundle") else None
    env = UnityPy.load(p)
    for o in env.objects:
        if o.type.name not in ("MonoBehaviour", "TextAsset"):
            continue
        try:
            data = o.get_raw_data()
        except Exception:
            continue
        if nb in data:
            try:
                tree = o.read_typetree()
                name = tree.get("m_Name", "")
                script = ""
                try:
                    script = o.read().m_Script.read().m_Name
                except Exception:
                    pass
            except Exception:
                name, script = "?", "?"
            print(f"{os.path.basename(p)} | {o.type.name} | path_id={o.path_id} | name={name!r} | script={script!r}")
