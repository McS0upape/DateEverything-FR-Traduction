"""Compile les fichiers PO traduits en données pour le plugin, avec validation.

Usage : python build.py <main.json> <dossier_po> <dossier_sortie>

Sortie :
  dialogues.tsv : une ligne par chaîne Ink traduite
                  chemin \t knot \t sûr(1/0) \t original \t traduction
  ui.tsv        : traductions de l'interface (depuis _ui.po) : original \t traduction
Les entrées invalides sont ignorées (le jeu garde l'anglais) et listées dans le rapport.
"""
import collections
import hashlib
import os
import re
import sys

import polib

import inklib
import rules

MARKUP_RE = re.compile(r"</?[a-zA-Z]+/?>")
GENDER_RE = re.compile(r"\{\{(.*?)\}\}")


def esc(s):
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


def validate(entry, fr):
    """Renvoie (erreurs, avertissements)."""
    errors, warnings = [], []
    en = entry.msgid
    if fr != fr.strip():
        warnings.append("espaces en début/fin (retirés)")
    if ("\t" in fr and "\t" not in en) or ("\n" in fr and "\n" not in en):
        errors.append("tabulation ou retour à la ligne interdit")
    if "::" in fr:
        errors.append("'::' interdit (sépare le nom du personnage)")
    if collections.Counter(MARKUP_RE.findall(en)) != collections.Counter(MARKUP_RE.findall(fr)):
        warnings.append(f"balises différentes de l'original {MARKUP_RE.findall(en)} -> {MARKUP_RE.findall(fr)}")
    for m in GENDER_RE.finditer(fr):
        if len(m.group(1).split("|")) not in (2, 3):
            errors.append(f"syntaxe de genre invalide : {m.group(0)} (attendu {{{{masc|fém}}}} ou {{{{masc|fém|neutre}}}})")
    if fr.count("{{") != fr.count("}}"):
        errors.append("accolades {{ }} non équilibrées")
    ctxt = entry.msgctxt or ""
    if en.count(">>>") != fr.count(">>>"):
        errors.append("le nombre de séparateurs '>>>' doit être identique")
    if ctxt == "Tag SPECS" and en.count(",") != fr.count(",") and ">>>" not in en and len(en.split(",")) >= 5:
        errors.append("la liste des niveaux doit garder le même nombre de virgules")
    if ctxt == "Tag SPECS" and ":" in fr:
        errors.append("':' interdit dans les textes SPECS (le jeu découpe sur ': ')")
    if ctxt.startswith("Tag Nom d'objet") and ":" in fr:
        errors.append("':' interdit dans un nom d'objet")
    return errors, warnings


def main(src, po_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    raw = open(src, "rb").read()
    data = inklib.load(src)

    # index des chaînes du jeu
    by_path = {}
    logic_by_knot = collections.defaultdict(set)
    for path, knot, kind, text in inklib.iter_strings(data["root"]):
        if kind == "logic":
            logic_by_knot[knot].add(text)
            continue
        seg = rules.decompose(path, knot, kind, text)
        if seg is not None:
            by_path[path] = (knot, text, seg)

    report = []
    stats = collections.Counter()
    lines = []
    for name in sorted(os.listdir(po_dir)):
        if not name.endswith(".po") or name.startswith("_"):
            continue
        po = polib.pofile(os.path.join(po_dir, name))
        for entry in po:
            stats["entrees"] += 1
            if entry.obsolete or not entry.msgstr.strip() or "fuzzy" in entry.flags:
                continue
            errors, warnings = validate(entry, entry.msgstr)
            where = f"{name} [{entry.msgctxt}] {entry.msgid[:60]!r}"
            for w in warnings:
                report.append(f"AVERTISSEMENT {where} : {w}")
            if errors:
                stats["rejetees"] += 1
                for e in errors:
                    report.append(f"ERREUR {where} : {e}")
                continue
            fr = entry.msgstr.strip()
            stats["traduites"] += 1
            for path, _ in entry.occurrences:
                info = by_path.get(path)
                if info is None:
                    stats["chemins_introuvables"] += 1
                    continue
                knot, original, seg = info
                if seg.body != entry.msgid or seg.ctxt != entry.msgctxt:
                    stats["chemins_modifies"] += 1
                    report.append(f"DECALAGE {where} : le texte du jeu à {path} a changé, relancez extract.py")
                    continue
                safe = "0" if original in logic_by_knot[knot] else "1"
                lines.append("\t".join([path, knot, safe, esc(original), esc(seg.compose(fr))]))

    with open(os.path.join(out_dir, "dialogues.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"#DEFR1\t{hashlib.md5(raw).hexdigest()}\n")
        f.write("\n".join(lines))
        f.write("\n")

    # interface
    ui_po = os.path.join(po_dir, "_ui.po")
    ui_lines = []
    if os.path.exists(ui_po):
        for entry in polib.pofile(ui_po):
            if entry.obsolete or not entry.msgstr.strip() or "fuzzy" in entry.flags:
                continue
            ui_lines.append(esc(entry.msgid) + "\t" + esc(entry.msgstr))
    with open(os.path.join(out_dir, "ui.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(ui_lines) + ("\n" if ui_lines else ""))

    with open(os.path.join(out_dir, "..", "build_report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print(dict(stats), f"| chaînes écrites : {len(lines)} | UI : {len(ui_lines)} | problèmes : {len(report)}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
