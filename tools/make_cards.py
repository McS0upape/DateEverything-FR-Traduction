"""Crée les fiches personnages (translation/personnages/<knot>.md) à partir du Date-A-Dex.

Usage : python make_cards.py <main.json> <dossier_po> <dossier_fiches>
N'écrase jamais une fiche existante (elles sont faites pour être éditées à la main).
"""
import collections
import os
import sys

import polib

import inklib


def dex_entries(data):
    """internalname -> dict des tags du Date-A-Dex."""
    entries = collections.defaultdict(dict)
    for path, knot, kind, text in inklib.iter_strings(data["root"]):
        if knot != "DateADex" or kind != "tag":
            continue
        stitch = path.split("/")[1]
        if ":" in text:
            k, v = text.split(":", 1)
            entries[stitch].setdefault(k.strip().lower(), v.strip())
    by_name = {}
    for stitch, tags in entries.items():
        name = tags.get("internalname")
        if name:
            by_name[name.lower()] = tags
    return by_name


TEMPLATE = """# {title}

<!-- Fiche de voix pour la traduction. Les champs « À compléter » sont remplis par l'étape « bible » puis relus par un humain. -->

## Identité (Date-A-Dex)

- **Fichier** : `{knot}.po`
- **Objet** : {obj}
- **Doublage VO** : {va}
- **Aime** : {likes}
- **N'aime pas** : {dislikes}
- **Le saviez-vous ?** : {dyk}

## Intervenants dans ce fichier

{speakers}

## Voix en français

- **Genre grammatical du personnage** : À compléter
- **Tutoie ou vouvoie le joueur ou la joueuse** : À compléter
- **Le joueur ou la joueuse lui parle avec** : tu
- **Registre** : À compléter
- **Personnalité, manière de parler** : À compléter
- **Tics verbaux, expressions récurrentes, jeux de mots à préserver** : À compléter
- **Exemples de répliques traduites (référence de ton)** : À compléter
"""


def main(src, po_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    data = inklib.load(src)
    dex = dex_entries(data)
    made = 0
    for name in sorted(os.listdir(po_dir)):
        if not name.endswith(".po") or name.startswith("_"):
            continue
        knot = name[:-3]
        out = os.path.join(out_dir, f"{knot}.md")
        if os.path.exists(out):
            continue
        po = polib.pofile(os.path.join(po_dir, name))
        speakers = collections.Counter(e.msgctxt for e in po)
        prefix = knot.split("_")[0].lower()
        tags = dex.get(prefix, {})
        title = tags.get("name") or knot
        lines = "\n".join(f"- {s} ({n} répliques)" for s, n in speakers.most_common(12))
        with open(out, "w", encoding="utf-8") as f:
            f.write(TEMPLATE.format(
                title=title, knot=knot,
                obj=tags.get("objname", "—"), va=tags.get("voactor", "—"),
                likes=tags.get("likes", "—"), dislikes=tags.get("dislikes", "—"),
                dyk=tags.get("didyouknow", "—"), speakers=lines))
        made += 1
    print(f"{made} fiches créées")


if __name__ == "__main__":
    main(*sys.argv[1:4])
