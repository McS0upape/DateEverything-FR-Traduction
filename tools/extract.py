"""Extrait les textes du script Ink vers des fichiers PO (un par knot / personnage).

Usage : python extract.py <main.json> <dossier_po>
Relançable : les traductions déjà présentes dans <dossier_po> sont conservées ;
les entrées disparues du jeu passent en obsolètes (#~).
"""
import os
import sys
from collections import OrderedDict

import polib

import inklib
import rules

HEADER = {
    "Project-Id-Version": "Date Everything - Traduction FR",
    "Language": "fr",
    "MIME-Version": "1.0",
    "Content-Type": "text/plain; charset=UTF-8",
    "Content-Transfer-Encoding": "8bit",
    "Plural-Forms": "nplurals=2; plural=(n > 1);",
}


def main(src, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    data = inklib.load(src)
    frags = inklib.fragment_paths(data["root"])

    per_knot = OrderedDict()  # knot -> OrderedDict[(ctxt, body)] -> {"paths": [], "fragment": bool}
    for path, knot, kind, text in inklib.iter_strings(data["root"]):
        seg = rules.decompose(path, knot, kind, text)
        if seg is None:
            continue
        entries = per_knot.setdefault(knot, OrderedDict())
        e = entries.setdefault((seg.ctxt, seg.body), {"paths": [], "fragment": False})
        e["paths"].append(path)
        e["fragment"] |= path in frags

    total = 0
    for knot, entries in per_knot.items():
        po_path = os.path.join(out_dir, f"{knot}.po")
        old = {}
        if os.path.exists(po_path):
            for oe in polib.pofile(po_path):
                old[(oe.msgctxt, oe.msgid)] = oe
        po = polib.POFile(wrapwidth=0)
        po.metadata = dict(HEADER)
        for (ctxt, body), info in entries.items():
            entry = polib.POEntry(
                msgctxt=ctxt,
                msgid=body,
                msgstr="",
                occurrences=[(p, "") for p in info["paths"]],
            )
            if info["fragment"]:
                entry.comment = "Morceau de phrase coupé par une variable (nom du joueur, nombre...)."
            prev = old.pop((ctxt, body), None)
            if prev is not None:
                entry.msgstr = prev.msgstr
                entry.flags = list(prev.flags)
                entry.tcomment = prev.tcomment
            po.append(entry)
        for oe in old.values():  # disparues du jeu
            if oe.msgstr and not oe.obsolete:
                oe.obsolete = True
                po.append(oe)
        po.save(po_path)
        total += len(entries)
    print(f"{len(per_knot)} fichiers, {total} entrées")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
