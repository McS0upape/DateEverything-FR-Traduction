# Consignes condensées : traduire un fichier (agent)

Projet : traduction française de *Date Everything!* (jeu de drague où l'on sort avec les objets d'une maison). Dossier racine : `C:\Users\mcsou\DateEverything_FR`.
Ce fichier remplace la lecture de `CONSIGNES_AGENT.md`, de `GUIDE_TRADUCTION.md` et des fichiers exemples. Lis aussi `translation/GLOSSAIRE.tsv` (court, termes imposés).

## Commandes

À lancer depuis `C:\Users\mcsou\DateEverything_FR\tools`, avec `PYTHONIOENCODING=utf-8 python` (sans `-I`) :

```
python work.py next <knot> 250                    # id|locuteur|anglais des entrées non traduites
python work.py apply <knot> <fichier.json> --ai   # fichier.json = {"<id>": "traduction", ...}
```

## Méthode

1. **Fiche de voix** (`translation/personnages/<knot>.md`) :
   - Si la section « Voix en français » est déjà remplie, lis-la et respecte-la. La mention « À compléter » dans le commentaire HTML d'en-tête est normale.
   - Sinon, lis seulement les ~300 premières entrées (`next <knot> 300`), puis remplis cette section, brièvement : genre (il / elle / iel), tutoiement ou vouvoiement envers le joueur ou la joueuse, registre et tics, équivalents des jeux de mots récurrents, 3 exemples. Ne touche pas aux autres sections.
2. **S'il y a déjà des traductions dans le .po**, jettes-y un œil rapide (grep de quelques `msgstr`) pour la cohérence. Ne relis pas tout.
3. **Traduis par lots de ~250 entrées** :
   - écris le JSON dans `tmp/work/<knot>_<n>.json`, puis lance `apply` ;
   - corrige les `REJET` éventuels, puis relance `next` ;
   - continue jusqu'à « 0 entrées restantes ».

## Règles

- **Locuteurs** :
  - `Choix` : réplique du joueur ou de la joueuse, qui tutoie les objets ;
  - `Narrator` : **vouvoie** le joueur ou la joueuse, y compris dans la narration (« Vous ouvrez la porte ») ; britannique pince-sans-rire ;
  - les autres personnages **tutoient**, sauf si la fiche dit le contraire.
- **Genre du joueur ou de la joueuse** : `{{prêt|prête|prêt·e}}` (masc|fém|neutre), seulement quand les formes diffèrent. Préfère une reformulation épicène.
  - Les **surnoms adressés au joueur ou à la joueuse** (« buddy », « boy-o », « girl », « dude »…) doivent être épicènes ou passer par `{{…}}`.
  - Le genre des personnages est fixe : jamais de `{{…}}` pour eux.
- **Balises** : garder exactement `<i>`, `</i>`, `<b>`, `<w>`. Garder les `>>>` (même nombre).
- **Interdits de format** : pas de `::`, pas de retour à la ligne, pas de tabulation.
- `[fragment]` : le jeu colle un nom ou un nombre à la suite ; garde un ordre compatible et n'écris pas « [fragment] ».
- **Tags** :
  - `Tag Nom d'objet (MAJUSCULES)` : nom en MAJUSCULES, sans `:` ;
  - `Tag Phrase objet…` : phrases d'examen d'objet ;
  - `Tag Date-A-Dex` et `Tag Roomers` : textes de menus.
- **Noms propres** des personnages : ne pas les traduire. Tout le reste se traduit, y compris les noms d'objets.
- **Typographie** : espaces normales avant `? ! : ;` (le plugin les rend insécables), guillemets « », pas de `œ` (écrire `oe`).
- **Répliques identiques en anglais** : elles restent identiques en français.
- **Sous-titres d'un jeu doublé** : longueur proche de l'original, et même niveau de vulgarité (fuck → putain / bordel, pas « zut »).

Exemples (ton attendu) :
- Narrator : « The very air you breathe has taken form, and <i>what form</i>. » → « L'air même que vous respirez a pris forme, et <i>quelle forme</i>. »
- Choix : « I thought I was doing okay with the no talking thing. » → « Je pensais m'en sortir pas mal avec le coup du silence. »

## Jeux de mots (priorité qualité)

Le jeu est drôle avant tout.
- Chaque jeu de mots doit être **réécrit en français** (un équivalent qui fonctionne, même éloigné du sens littéral), jamais traduit mot à mot.
- Si une réplique suivante commente le jeu de mots, garde la cohérence avec elle.
- Si tu n'es **pas satisfait** de ta solution (jeu de mots perdu, faible, ou qui dépend d'un contexte plus large), traduis quand même au mieux, puis ajoute une ligne dans `tmp/jdm/<knot>.tsv` (crée le fichier ; une ligne par entrée, séparateur tabulation) :

```
<id>	<anglais>	<ta traduction>	<explication courte du jeu de mots>
```

Une passe de relecture dédiée reprendra ces entrées. N'y mets pas les jeux de mots que tu as bien rendus.

## Interdits

- Ne modifie que :
  - `translation/fr/<knot>.po`, via `work.py apply` ;
  - `translation/personnages/<knot>.md` ;
  - `tmp/work/` et `tmp/jdm/`.
- Pas de `build.py`, pas de `git`, ne touche pas au dossier du jeu, ne lance pas `translate_llm.py`.

## Rapport final (court)

- nombre d'entrées traduites ;
- rejets non résolus ;
- nombre d'entrées dans `tmp/jdm/<knot>.tsv` ;
- 3 à 5 choix notables ;
- propositions de glossaire (sans modifier `GLOSSAIRE.tsv`).
