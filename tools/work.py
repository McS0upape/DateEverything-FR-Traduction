"""Outil de traduction « à la main » (par une personne ou par Claude en session), lot par lot.

  python work.py status                     # avancement par fichier
  python work.py next <knot> [N]            # affiche les N prochaines entrées vides (défaut 80) : id|locuteur|anglais
  python work.py apply <knot> <fichier.json> [--ai]
        fichier.json = {"<id>": "traduction", ...} ; chaque traduction est validée (règles de build.py)
        --ai ajoute le commentaire « Traduction IA – à relire »
"""
import json
import os
import sys

import polib

import build

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PO_DIR = os.path.join(ROOT, "translation", "fr")
AI_COMMENT = "Traduction IA – à relire"


def load(knot):
    return polib.pofile(os.path.join(PO_DIR, f"{knot}.po"), wrapwidth=0)


def status():
    tot_w = done_w = 0
    rows = []
    for name in sorted(os.listdir(PO_DIR)):
        if not name.endswith(".po") or name.startswith("_"):
            continue
        po = polib.pofile(os.path.join(PO_DIR, name))
        live = [e for e in po if not e.obsolete]
        w = sum(len(e.msgid.split()) for e in live)
        d = sum(len(e.msgid.split()) for e in live if e.msgstr.strip())
        tot_w += w
        done_w += d
        if d:
            rows.append(f"{name[:-3]:28} {d:>7}/{w:<7} mots ({100 * d / w:.0f} %)")
    print("\n".join(rows) or "(rien de traduit)")
    print(f"TOTAL : {done_w}/{tot_w} mots ({100 * done_w / tot_w:.2f} %)")


def next_entries(knot, n):
    po = load(knot)
    shown = 0
    for i, e in enumerate(po):
        if e.obsolete or e.msgstr.strip():
            continue
        frag = " [fragment]" if e.comment and "Morceau" in e.comment else ""
        print(f"{i}|{e.msgctxt}|{e.msgid}{frag}")
        shown += 1
        if shown >= n:
            break
    left = sum(1 for e in po if not e.obsolete and not e.msgstr.strip())
    print(f"# {left} entrées restantes dans {knot}")


def apply(knot, path, ai):
    po = load(knot)
    data = json.load(open(path, encoding="utf-8"))
    ok, bad = 0, []
    for k, fr in data.items():
        i = int(k)
        fr = fr.strip()
        errors, warnings = build.validate(po[i], fr)
        if errors:
            bad.append((i, po[i].msgid[:50], errors))
            continue
        for w in warnings:
            print(f"avertissement {i}: {w}")
        po[i].msgstr = fr
        if ai:
            po[i].tcomment = AI_COMMENT
        ok += 1
    po.save()
    print(f"{ok} traductions enregistrées dans {knot}.po")
    for i, en, errs in bad:
        print(f"REJET {i} ({en!r}) : {'; '.join(errs)}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "status":
        status()
    elif cmd == "next":
        next_entries(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 80)
    elif cmd == "apply":
        apply(sys.argv[2], sys.argv[3], "--ai" in sys.argv)
