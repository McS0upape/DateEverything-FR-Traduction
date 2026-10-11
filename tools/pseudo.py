"""Génère une pseudo-traduction ("[FR] " + anglais) de tous les PO, pour tester la couverture du plugin."""
import os, sys, polib
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
for name in os.listdir(src):
    if not name.endswith(".po"): continue
    po = polib.pofile(os.path.join(src, name))
    for e in po:
        e.msgstr = "[FR] " + e.msgid
    po.save(os.path.join(dst, name))
