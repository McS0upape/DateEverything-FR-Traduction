# Consignes : traduire un fichier de personnage (agent ou bénévole)

Projet : traduction française de *Date Everything!*. Dossier racine : `C:\Users\mcsou\DateEverything_FR`.

## À lire avant de commencer

1. `translation/GUIDE_TRADUCTION.md` : règles de style, accords `{{masc|fém|neutre}}`, tutoiement, typographie.
2. `translation/GLOSSAIRE.tsv` : termes imposés (Réaliser, Éveiller, datable, Dateviators, D.A.T.E., SPECS = Savoir / Prestance / Empathie / Charme / Sarcasme, fins Amour / Amitié / Haine, Affaires à démeubler…).
3. `translation/personnages/airyn_air.md` et `translation/personnages/skylar_specs.md` : exemples de fiches de voix terminées.
4. `translation/fr/airyn_air.po` : exemple de fichier traduit (pour le niveau de qualité attendu).

## Méthode

Toutes les commandes se lancent depuis `C:\Users\mcsou\DateEverything_FR\tools`, avec la variable `PYTHONIOENCODING=utf-8` et `python` (sans l'option `-I`) :

```
cd /c/Users/mcsou/DateEverything_FR/tools
PYTHONIOENCODING=utf-8 python work.py next <knot> 200     # affiche id|locuteur|anglais des entrées non traduites
PYTHONIOENCODING=utf-8 python work.py apply <knot> <fichier.json> --ai
```

1. **Lire tout le fichier d'abord**, en enchaînant `next` (par exemple `next <knot> 400`, puis la suite). L'objectif est de cerner la voix du personnage principal et des intervenants secondaires.
2. **Rédiger la section « Voix en français »** de `translation/personnages/<knot>.md`, en remplaçant les « À compléter » sur le modèle d'Airyn ou de Skylar :
   - genre grammatical (il / elle / iel, d'après le texte) ;
   - tutoiement ou vouvoiement envers le joueur ou la joueuse ;
   - registre, personnalité, tics verbaux ;
   - jeux de mots liés à l'objet, avec leurs équivalents français ;
   - 4 ou 5 exemples de répliques traduites.

   Ne modifie pas les autres sections de la fiche.
3. **Traduire par lots d'environ 150 à 200 entrées.** Écris un JSON `{"<id>": "traduction", ...}` dans `tmp/work/<knot>_<n>.json` (avec l'outil d'écriture de fichiers), puis lance `apply`. Les ids sont ceux affichés par `next`. Comme `next` n'affiche que les entrées restantes, relance-le après chaque `apply`.
4. **Si `apply` affiche des `REJET`**, corrige ces entrées et réapplique-les. Recommence jusqu'à ce que `next` affiche « 0 entrées restantes ».

## Règles essentielles (rappel)

- **Noms propres** des personnages : ne pas les traduire. **Noms d'objets** et texte courant : tout traduire.
- **Locuteurs** :
  - `Choix` = réplique du joueur ou de la joueuse, qui tutoie les objets ;
  - `Narrator` = Narrateur, qui **vouvoie** le joueur ou la joueuse, narration comprise (« Vous ouvrez la porte ») ;
  - les autres personnages tutoient par défaut, sauf si leur personnalité impose le vouvoiement (à noter dans la fiche).
- **Accords du joueur ou de la joueuse** : `{{prêt|prête|prêt·e}}`. N'utilise la syntaxe que si les formes diffèrent, sinon écris le mot directement. Elle ne sert **jamais** pour le genre des personnages, qui est fixe.
- **Conserver exactement** les balises `<i>`, `</i>`, `<b>`, `<w>`… Ne jamais écrire `::`.
- `[fragment]` signale un morceau de phrase : le jeu insère un nom ou un nombre à la suite. Garde un ordre compatible, et n'écris pas « [fragment] » dans la traduction.
- **Tags** :
  - `Tag Nom d'objet (MAJUSCULES)` : nom de l'objet en MAJUSCULES, sans `:` ;
  - `Tag Phrase objet…` : phrases d'examen d'objet ;
  - `Tag Date-A-Dex` / `Tag Roomers` : textes de menus.
- **Typographie** : espaces normales avant `? ! : ;` (le plugin les rend insécables), guillemets « ».
- **Le ton avant tout** : humour adapté plutôt que traduit mot à mot, jeux de mots réécrits, même niveau de vulgarité, longueur proche de l'original (ce sont des sous-titres).
- Les répliques **identiques en anglais** (choix répétés, etc.) doivent rester identiques en français.

## Interdits

- Ne modifier **aucun autre fichier** que `translation/fr/<knot>.po` (via `work.py apply`), `translation/personnages/<knot>.md` et tes JSON dans `tmp/work/`.
- Pas de `build.py`, pas de `git`, ne pas toucher au dossier du jeu.
- Ne pas lancer `translate_llm.py`.

## Rapport final

Indique :
- le nombre d'entrées traduites ;
- les rejets non résolus éventuels ;
- les choix de traduction notables (jeux de mots, noms d'objets) ;
- les termes que tu proposes d'ajouter au glossaire (sans modifier `GLOSSAIRE.tsv` toi-même).
