"""Parcours du JSON Ink compilé (inkVersion 21) de Date Everything.

Chaque chaîne "^..." est classée selon son contexte :
  - "content" : texte affiché (dialogue, narration, choix)
  - "tag"     : texte entre "#" et "/#"
  - "logic"   : valeur de chaîne évaluée (affectation, comparaison...) -> jamais traduite

Les chemins utilisent "/" comme séparateur : index dans la liste d'un conteneur,
ou nom de clé pour le contenu nommé (dictionnaire final d'un conteneur).
Le plugin C# reproduit exactement la même convention sur les objets du runtime Ink.
"""
import json


def load(path):
    return json.loads(open(path, "rb").read().decode("utf-8-sig"))


def iter_strings(root):
    """Yield (path, knot, kind, text_without_caret)."""

    def walk(node, path, knot):
        if isinstance(node, list):
            in_tag = in_ev = in_str = False
            pending = []
            last = len(node) - 1
            for i, x in enumerate(node):
                p = f"{path}/{i}" if path else str(i)
                if isinstance(x, str):
                    if x == "#":
                        in_tag = True
                    elif x == "/#":
                        in_tag = False
                    elif x == "ev":
                        in_ev, pending = True, []
                    elif x == "/ev":
                        in_ev = False
                        for (pp, s, tagged) in pending:
                            yield (pp, knot, "tag" if tagged else "logic", s)
                        pending = []
                    elif x == "str":
                        in_str = True
                    elif x == "/str":
                        in_str = False
                    elif x.startswith("^"):
                        if in_str and in_ev:
                            pending.append((p, x[1:], in_tag))
                        elif in_str:
                            yield (p, knot, "logic", x[1:])
                        else:
                            yield (p, knot, "tag" if in_tag else "content", x[1:])
                elif isinstance(x, list):
                    yield from walk(x, p, knot)
                elif isinstance(x, dict) and i == last:
                    # contenu nommé uniquement (sous-conteneurs nommés)
                    for k, v in x.items():
                        if k in ("#f", "#n") or not isinstance(v, list):
                            continue
                        pk = f"{path}/{k}" if path else k
                        yield from walk(v, pk, knot if knot else k)
            for (pp, s, tagged) in pending:
                yield (pp, knot, "logic", s)

    yield from walk(root, "", None)


def fragment_paths(root):
    """Chemins des morceaux de lignes coupées par une variable affichée ({nom}, {nombre}...)."""
    result = set()

    def walk(node, path):
        if isinstance(node, list):
            pieces, has_out, ev = [], False, False
            last = len(node) - 1
            for i, x in enumerate(node):
                p = f"{path}/{i}" if path else str(i)
                if x == "ev":
                    ev = True
                elif x == "/ev":
                    ev = False
                elif x == "\n":
                    if has_out and pieces:
                        result.update(pieces)
                    pieces, has_out = [], False
                elif x == "out":
                    has_out = True
                elif isinstance(x, str) and x.startswith("^") and not ev:
                    pieces.append(p)
                elif isinstance(x, list):
                    walk(x, p)
                elif isinstance(x, dict) and i == last:
                    for k, v in x.items():
                        if isinstance(v, list):
                            walk(v, f"{path}/{k}" if path else k)

    walk(root, "")
    return result
