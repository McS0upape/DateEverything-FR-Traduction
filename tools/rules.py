"""Règles de traduction : ce qui se traduit, et quelle partie de la chaîne est protégée.

decompose(knot, kind, text) renvoie None si la chaîne ne doit pas être traduite, sinon un Segment :
  prefix  : partie technique conservée telle quelle (ex. "Abel:: ", "Desc: ", "dex 3: ")
  body    : texte à traduire (sans espaces de début/fin)
  suffix  : espaces de fin conservés
  ctxt    : contexte PO (nom du personnage, "Choix", "Narration", "Tag Desc"...)
"""
import re
from dataclasses import dataclass

# Knots de debug / logique pure : jamais traduits
SKIP_KNOTS = {"qa_debug", "tresta_test", "critical_path_sorter", "expressionista_list", "global decl"}

# Chaînes comparées en dur par le code C# du jeu
SKIP_EXACT = {
    "You are in your own house. Everything is alive and sexy. What do you do?",
    "You are in your own house. Everything is alive and sexy.  What do you do?",
}

SPEAKER_RE = re.compile(r"^(\s*)([^:\n]{0,48}?)(::\s*)(.*?)(\s*)$", re.S)

# Tags porteurs de texte affiché : (knots concernés ou None = tous, regex préfixe, étiquette)
TAG_RULES = [
    (None, re.compile(r"^(\s*null_hate_phrase\s+)"), "Phrase objet (neutre/haine)"),
    (None, re.compile(r"^(\s*love_friend_phrase\s+)"), "Phrase objet (ami/amour)"),
    (None, re.compile(r"^(\s*realized_phrase\s+)"), "Phrase objet (réalisé)"),
    (None, re.compile(r"^(\s*main_text\s*:?\s*)"), "Nom d'objet (MAJUSCULES)"),
    (None, re.compile(r"^(\s*loading_entry_title\s+)"), "Titre écran de chargement"),
    (None, re.compile(r"^(\s*loading_entry\s+)"), "Anecdote écran de chargement"),
    ({"roomers"}, re.compile(r"^(\s*(?:Title|Desc|Clue\d*|Skylar)\s*:\s*)"), "Roomers"),
    ({"healpth"}, re.compile(r"^(\s*(?:title|description)\s*:\s*)"), "Conseil santé"),
    ({"specs"}, re.compile(r"^(\s*(?:description|levels|level descriptions)\s*:\s*)"), "SPECS"),
    ({"DateADex"}, re.compile(r"^(\s*(?:objname|likes|dislikes|didyouknow|dex \d+|collectable\d+(?:desc|hint)?)\s*:\s*)"), "Date-A-Dex"),
    (None, re.compile(r"^(\s*(?:Status|Category)\s*:\s*)"), "Appli"),
]

# Contenu (hors tags) avec préfixe technique lu par le code
CONTENT_PREFIX_RULES = [
    ({"DateADex"}, re.compile(r"^(\s*(?:dex \d+|collectable\d+(?:desc|hint)?)\s*:\s*)")),
]

WORDLIKE = re.compile(r"[A-Za-z]")


@dataclass
class Segment:
    prefix: str
    body: str
    suffix: str
    ctxt: str

    def compose(self, new_body):
        return self.prefix + new_body + self.suffix


def _split_ws(s):
    stripped = s.rstrip()
    suffix = s[len(stripped):]
    core = stripped.lstrip()
    lead = stripped[: len(stripped) - len(core)]
    return lead, core, suffix


def _is_choice_path(path):
    # le texte d'un choix est stocké dans un sous-conteneur nommé "s"
    return "/s/" in path or path.endswith("/s")


def decompose(path, knot, kind, text):
    if kind == "logic" or knot in SKIP_KNOTS or knot is None:
        return None
    if text.strip() in SKIP_EXACT:
        return None

    if kind == "tag":
        for knots, rx, label in TAG_RULES:
            if knots is not None and knot not in knots:
                continue
            m = rx.match(text)
            if m:
                prefix = m.group(1)
                lead, core, suffix = _split_ws(text[len(prefix):])
                if not WORDLIKE.search(core):
                    return None
                return Segment(prefix + lead, core, suffix, f"Tag {label}")
        return None

    # contenu
    for knots, rx in CONTENT_PREFIX_RULES:
        if knots is None or knot in knots:
            m = rx.match(text)
            if m:
                prefix = m.group(1)
                lead, core, suffix = _split_ws(text[len(prefix):])
                if not WORDLIKE.search(core):
                    return None
                return Segment(prefix + lead, core, suffix, "Date-A-Dex")

    m = SPEAKER_RE.match(text)
    if m and m.group(3):
        lead, speaker, sep, core, suffix = m.groups()
        if not WORDLIKE.search(core):
            return None
        return Segment(lead + speaker + sep, core, suffix, speaker.strip() or "(sans nom)")

    lead, core, suffix = _split_ws(text)
    if not WORDLIKE.search(core):
        return None
    return Segment(lead, core, suffix, "Choix" if _is_choice_path(path) else "Narration / joueur")
