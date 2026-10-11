"""Ajoute dans translation/fr/_ui.po les textes d'interface collectés en jeu (ui_untranslated.txt).

Usage : python ui_dump_to_po.py <ui_untranslated.txt>
Les textes qui proviennent des dialogues (déjà gérés par les autres PO) sont ignorés.
"""
import os
import re
import sys

import polib

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PO_DIR = os.path.join(ROOT, "translation", "fr")
UI_PO = os.path.join(PO_DIR, "_ui.po")


def known_dialogue():
    known = set()
    for name in os.listdir(PO_DIR):
        if name.endswith(".po") and not name.startswith("_"):
            for e in polib.pofile(os.path.join(PO_DIR, name)):
                known.add(e.msgid)
                if e.msgstr:
                    known.add(e.msgstr)
    return known


def main(dump):
    po = polib.pofile(UI_PO, wrapwidth=0) if os.path.exists(UI_PO) else polib.POFile(wrapwidth=0)
    if not po.metadata:
        po.metadata = {"Language": "fr", "Content-Type": "text/plain; charset=UTF-8"}
    have = {e.msgid for e in po}
    known = known_dialogue()
    regex_src = os.path.join(PO_DIR, "_ui_regex.tsv")
    patterns = []
    if os.path.exists(regex_src):
        for line in open(regex_src, encoding="utf-8"):
            if "\t" in line and not line.startswith("#"):
                patterns.append(re.compile(line.split("\t", 1)[0]))
    added = 0
    for line in open(dump, encoding="utf-8"):
        s = line.rstrip("\n").replace("\\n", "\n").replace("\\\\", "\\")
        plain = re.sub(r"<[^>]+>", "", s).strip()
        if not plain or not re.search(r"[A-Za-z]{2}", plain) or s in have or plain in known:
            continue
        core = s.strip(" \t\n\r​﻿")
        if any(p.fullmatch(core) for p in patterns):
            continue
        po.append(polib.POEntry(msgid=s, msgstr=""))
        have.add(s)
        added += 1
    po.save(UI_PO)
    print(f"{added} textes d'interface ajoutés à _ui.po")


if __name__ == "__main__":
    main(sys.argv[1])
