"""Traduction automatique (première passe) des fichiers PO avec Claude.

Chaque requête contient :
  - system (mis en cache) : guide de traduction + glossaire, puis la fiche du personnage
  - user : quelques répliques précédentes (contexte, en anglais) + un lot d'entrées à traduire
La réponse est un JSON structuré {"translations": [{"id", "fr"}]}, validé avec les règles de build.py.
Les traductions sont écrites dans les PO avec le commentaire « Traduction IA – à relire ».
Seules les entrées vides sont traitées : le script peut être relancé sans risque.

Exemples :
  python translate_llm.py estimate                       # coût estimé, aucun appel
  python translate_llm.py direct airyn_air               # traduit un fichier tout de suite (test)
  python translate_llm.py batch-submit                   # envoie tout via l'API Batches (-50 %)
  python translate_llm.py batch-status                   # état des lots envoyés
  python translate_llm.py batch-collect                  # récupère et écrit les résultats
  python translate_llm.py cards                          # remplit les fiches de voix (« À compléter »)
Options : --model claude-opus-5-5 | claude-sonnet-5-5   --effort low|medium|high
"""
import argparse
import json
import os
import re
import sys
import time

import anthropic
import polib
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

import build

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PO_DIR = os.path.join(ROOT, "translation", "fr")
CARDS_DIR = os.path.join(ROOT, "translation", "personnages")
STATE = os.path.join(ROOT, "tmp", "batches.json")

CHUNK = 60          # entrées par requête
CONTEXT = 12        # répliques précédentes données en contexte
AI_COMMENT = "Traduction IA – à relire"

PRICES = {  # $ / million de tokens (entrée, sortie), tarif standard
    "claude-opus-5-5": (4.0, 20.0),
    "claude-sonnet-5-5": (2.0, 10.0),
}

INSTRUCTIONS = """Tu es traducteur·rice professionnel·le de jeux vidéo, spécialisé·e dans la localisation \
de jeux narratifs humoristiques de l'anglais vers le français. Tu traduis « Date Everything! », un jeu de \
drague où l'on séduit les objets de sa maison. Le jeu est entièrement doublé en anglais : ta traduction sert \
de sous-titres.

Tu reçois un lot d'entrées extraites du script. Chaque entrée a un identifiant, un locuteur et le texte anglais. \
Locuteurs spéciaux : « Choix » = ce que dit le joueur ou la joueuse ; « Narration / joueur » = narration ou \
réplique du joueur ou de la joueuse ; « Narrator » = le Narrateur ; « Tag … » = textes de menus du jeu.

Exigences :
- Respecte scrupuleusement le guide, le glossaire et la fiche du personnage ci-dessous.
- Le texte doit sonner comme écrit directement en français : réécris les blagues et jeux de mots pour qu'ils \
fonctionnent en français, garde le niveau de langue et la vulgarité du personnage.
- Conserve exactement les balises (<i>, </i>, <b>, <w>…), les séparateurs >>> et le nombre de virgules des \
listes de niveaux. N'écris jamais « :: ».
- Accorde tout ce qui concerne le joueur ou la joueuse avec la syntaxe {{masculin|féminin|neutre}}, en \
préférant une reformulation épicène quand elle est naturelle.
- Une entrée signalée « fragment » est un morceau de phrase : le jeu insère une valeur (nom, nombre) entre ce \
morceau et le suivant. Traduis-la pour que l'assemblage reste correct.
- Traduis chaque entrée demandée, une seule fois, avec son identifiant. Ne traduis pas le contexte.

=== GUIDE DE TRADUCTION ===
{guide}

=== GLOSSAIRE (anglais → français, statut, note) ===
{glossary}
"""

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "translations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"id": {"type": "integer"}, "fr": {"type": "string"}},
                "required": ["id", "fr"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["translations"],
    "additionalProperties": False,
}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def system_blocks(knot):
    """Deux blocs : le socle commun (identique pour toutes les requêtes) puis la fiche du personnage."""
    common = INSTRUCTIONS.format(
        guide=read(os.path.join(ROOT, "translation", "GUIDE_TRADUCTION.md")),
        glossary=read(os.path.join(ROOT, "translation", "GLOSSAIRE.tsv")),
    )
    card_path = os.path.join(CARDS_DIR, f"{knot}.md")
    card = read(card_path) if os.path.exists(card_path) else f"(pas de fiche pour {knot})"
    return [
        {"type": "text", "text": common, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": "=== FICHE DU PERSONNAGE / DU FICHIER ===\n" + card,
         "cache_control": {"type": "ephemeral"}},
    ]


def entry_line(i, e):
    flag = " [fragment]" if e.comment and "Morceau" in e.comment else ""
    return json.dumps({"id": i, "locuteur": e.msgctxt, "en": e.msgid + flag}, ensure_ascii=False)


def plan(knot):
    """Découpe un PO en lots des entrées non traduites. Renvoie (po, [(chunk_index, [ids])])."""
    po = polib.pofile(os.path.join(PO_DIR, f"{knot}.po"))
    todo = [i for i, e in enumerate(po) if not e.obsolete and not e.msgstr.strip()]
    chunks = [todo[k:k + CHUNK] for k in range(0, len(todo), CHUNK)]
    return po, list(enumerate(chunks))


def user_message(po, ids, extra=""):
    first = ids[0]
    ctx = [po[j] for j in range(max(0, first - CONTEXT), first)]
    parts = []
    if ctx:
        parts.append("Contexte (répliques précédentes, NE PAS traduire) :")
        for e in ctx:
            done = f" → déjà traduit : {e.msgstr}" if e.msgstr else ""
            parts.append(f"- [{e.msgctxt}] {e.msgid}{done}")
        parts.append("")
    parts.append("Entrées à traduire (JSON, une par ligne) :")
    parts.extend(entry_line(i, po[i]) for i in ids)
    if extra:
        parts.append("")
        parts.append(extra)
    return "\n".join(parts)


def params(knot, po, ids, model, effort, extra=""):
    return dict(
        model=model,
        max_tokens=32000,
        system=system_blocks(knot),
        output_config={"effort": effort, "format": {"type": "json_schema", "schema": OUTPUT_SCHEMA}},
        messages=[{"role": "user", "content": user_message(po, ids, extra)}],
    )


def apply_result(po, ids, text):
    """Écrit les traductions valides dans le PO. Renvoie les ids à refaire avec leurs erreurs."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {i: ["réponse JSON illisible"] for i in ids}
    got = {t["id"]: t["fr"] for t in data.get("translations", []) if t.get("id") in ids}
    retry = {}
    for i in ids:
        fr = got.get(i)
        if fr is None:
            retry[i] = ["entrée manquante dans la réponse"]
            continue
        fr = fr.strip()
        errors, _ = build.validate(po[i], fr)
        if errors:
            retry[i] = errors
            continue
        po[i].msgstr = fr
        po[i].tcomment = AI_COMMENT
    return retry


def text_of(message):
    if message.stop_reason == "refusal":
        return None
    return next((b.text for b in message.content if b.type == "text"), None)


# ---------------------------------------------------------------- modes


def cmd_direct(client, args):
    for knot in args.knots:
        po, chunks = plan(knot)
        print(f"{knot} : {sum(len(c) for _, c in chunks)} entrées, {len(chunks)} requêtes")
        for n, ids in chunks:
            extra = ""
            for attempt in range(3):
                with client.messages.stream(**params(knot, po, ids, args.model, args.effort, extra)) as stream:
                    msg = stream.get_final_message()
                u = msg.usage
                print(f"  lot {n} essai {attempt}: in={u.input_tokens} cache_lu={u.cache_read_input_tokens} "
                      f"cache_écrit={u.cache_creation_input_tokens} out={u.output_tokens} stop={msg.stop_reason}")
                text = text_of(msg)
                retry = apply_result(po, ids, text) if text else {i: ["refus du modèle"] for i in ids}
                po.save()
                if not retry:
                    break
                ids = list(retry)
                extra = "Corrige ces entrées, la version précédente était invalide :\n" + "\n".join(
                    f"- id {i} : {'; '.join(errs)}" for i, errs in retry.items())
            else:
                print(f"  ! {len(ids)} entrées non traduites après 3 essais : {ids}")


def all_knots():
    return sorted(n[:-3] for n in os.listdir(PO_DIR) if n.endswith(".po") and not n.startswith("_"))


def cmd_estimate(client, args):
    knots = args.knots or all_knots()
    cin = cout = 0
    nreq = 0
    for knot in knots:
        po, chunks = plan(knot)
        for _, ids in chunks:
            nreq += 1
            cin += len(user_message(po, ids)) / 3.2       # ~3,2 caractères/token (JSON + anglais)
            cout += sum(len(po[i].msgid) for i in ids) * 1.2 / 3.0 + 12 * len(ids)
    sys_tokens = len(system_blocks(knots[0])[0]["text"]) / 3.2 + 1500
    pin, pout = PRICES.get(args.model, PRICES["claude-opus-5-5"])
    think = 1.5  # réflexion adaptative (effort medium) : marge sur la sortie
    base = cin * pin / 1e6 + cout * think * pout / 1e6
    cache = nreq * sys_tokens * pin * 0.1 / 1e6     # lectures du cache
    cache_worst = nreq * sys_tokens * pin * 1.25 / 1e6
    print(f"{len(knots)} fichiers, {nreq} requêtes, ~{cin/1e6:.2f} M tokens d'entrée, "
          f"~{cout/1e6:.2f} M tokens de sortie (hors réflexion)")
    print(f"Modèle {args.model} — tarif standard : ~${base + cache:.0f} (cache efficace) à ~${base + cache_worst:.0f}")
    print(f"Avec l'API Batches (-50 %) : ~${(base + cache) / 2:.0f} à ~${(base + cache_worst) / 2:.0f}")


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE, encoding="utf-8"))
    return {"batches": []}


def save_state(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def cmd_batch_submit(client, args):
    st = load_state()
    pending = {(r["knot"], i) for b in st["batches"] if not b.get("collected") for r in b["requests"].values()
               for i in r["ids"]}
    requests, meta = [], {}
    for knot in args.knots or all_knots():
        po, chunks = plan(knot)
        for n, ids in chunks:
            ids = [i for i in ids if (knot, i) not in pending]
            if not ids:
                continue
            cid = f"{len(st['batches'])}-{len(requests)}"
            requests.append(Request(custom_id=cid, params=MessageCreateParamsNonStreaming(
                **params(knot, po, ids, args.model, args.effort))))
            meta[cid] = {"knot": knot, "ids": ids}
    if not requests:
        print("Rien à envoyer.")
        return
    # plusieurs lots si nécessaire (limite 100 000 requêtes / 256 Mo)
    for k in range(0, len(requests), 2000):
        part = requests[k:k + 2000]
        batch = client.messages.batches.create(requests=part)
        st["batches"].append({"id": batch.id, "model": args.model,
                              "requests": {r["custom_id"]: meta[r["custom_id"]] for r in part}})
        save_state(st)
        print(f"Lot {batch.id} envoyé : {len(part)} requêtes")


def cmd_batch_status(client, args):
    for b in load_state()["batches"]:
        if b.get("collected"):
            continue
        r = client.messages.batches.retrieve(b["id"])
        c = r.request_counts
        print(f"{b['id']} : {r.processing_status} — en cours {c.processing}, ok {c.succeeded}, "
              f"erreurs {c.errored}, expirées {c.expired}")


def cmd_batch_collect(client, args):
    st = load_state()
    for b in st["batches"]:
        if b.get("collected"):
            continue
        if client.messages.batches.retrieve(b["id"]).processing_status != "ended":
            print(f"{b['id']} pas encore terminé")
            continue
        pos, failed = {}, 0
        for res in client.messages.batches.results(b["id"]):
            info = b["requests"][res.custom_id]
            knot = info["knot"]
            if knot not in pos:
                pos[knot] = polib.pofile(os.path.join(PO_DIR, f"{knot}.po"))
            if res.result.type != "succeeded":
                failed += len(info["ids"])
                continue
            text = text_of(res.result.message)
            if text is None:
                failed += len(info["ids"])
                continue
            # le PO a pu changer d'ordre si extract.py a été relancé : on vérifie le msgid
            failed += len(apply_result(pos[knot], info["ids"], text))
        for po in pos.values():
            po.save()
        b["collected"] = True
        save_state(st)
        print(f"{b['id']} récupéré ({failed} entrées à refaire : relancez batch-submit)")


CARD_PROMPT = """Voici la fiche d'un personnage de « Date Everything! » et un échantillon de ses répliques \
(dans l'ordre du script). Complète UNIQUEMENT la section « Voix en français », en français, de façon concise \
et concrète, pour guider des traducteurs. Remplace chaque « À compléter » :
- genre grammatical du personnage (il / elle / iel, d'après les répliques) ;
- tutoie ou vouvoie le joueur ou la joueuse (et pourquoi), et si cela peut évoluer avec la relation ;
- registre (familier, soutenu, argotique, précieux…) ;
- personnalité et manière de parler (longueur des phrases, ponctuation, rythme, vulgarité) ;
- tics verbaux, expressions récurrentes, jeux de mots liés à l'objet, avec des propositions d'équivalents français ;
- 4 à 6 exemples : réplique anglaise → traduction française de référence.
Réponds uniquement avec le contenu Markdown de la section, à partir de la ligne « ## Voix en français »."""


def cmd_cards(client, args):
    for knot in args.knots or all_knots():
        path = os.path.join(CARDS_DIR, f"{knot}.md")
        if not os.path.exists(path):
            continue
        card = read(path)
        if "## Voix en français" not in card or "À compléter" not in card.split("## Voix en français")[1]:
            continue
        po = polib.pofile(os.path.join(PO_DIR, f"{knot}.po"))
        sample = "\n".join(f"[{e.msgctxt}] {e.msgid}" for e in po if not e.obsolete)[:60000]
        msg = client.messages.create(
            model=args.model, max_tokens=16000, output_config={"effort": args.effort},
            system=[{"type": "text", "text": system_blocks(knot)[0]["text"], "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": f"{CARD_PROMPT}\n\n=== FICHE ===\n{card}\n\n=== RÉPLIQUES ===\n{sample}"}],
        )
        text = text_of(msg)
        if not text or "## Voix en français" not in text:
            print(f"{knot} : réponse inutilisable ({msg.stop_reason})")
            continue
        head = card.split("## Voix en français")[0]
        new = head + text[text.index("## Voix en français"):].rstrip() + "\n\n<!-- Section générée par IA – à relire -->\n"
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        print(f"{knot} : fiche complétée")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["estimate", "direct", "batch-submit", "batch-status", "batch-collect", "cards"])
    ap.add_argument("knots", nargs="*", help="fichiers à traiter (sans .po) ; par défaut tous")
    ap.add_argument("--model", default="claude-opus-5-5")
    ap.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    args = ap.parse_args()
    if args.command == "direct" and not args.knots:
        ap.error("direct : précisez au moins un fichier")
    client = None if args.command == "estimate" else anthropic.Anthropic(max_retries=5)
    {"estimate": cmd_estimate, "direct": cmd_direct, "batch-submit": cmd_batch_submit,
     "batch-status": cmd_batch_status, "batch-collect": cmd_batch_collect, "cards": cmd_cards}[args.command](client, args)


if __name__ == "__main__":
    main()
