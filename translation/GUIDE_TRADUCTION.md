# Guide de traduction — Date Everything en français

Ce guide sert à toute personne qui traduit ou relit, humaine ou IA. Le but : un texte qui sonne **comme s'il avait été écrit en français**, en respectant la voix de chaque personnage.

## 1. Où sont les textes

- `fr/<knot>.po` : un fichier par « knot » du script, c'est-à-dire en général **un personnage** (`abel_table.po` = Abel la table). Les entrées suivent l'ordre du script.
- `fr/_ui.po` : les textes de l'interface (menus, boutons).
- `personnages/<knot>.md` : la **fiche de voix** de chaque personnage. Lisez-la avant de traduire son fichier.
- `GLOSSAIRE.tsv` : les termes du jeu à traduire toujours de la même façon.

Les fichiers PO s'ouvrent avec [Poedit](https://poedit.net/) (gratuit), Weblate, Crowdin ou n'importe quel éditeur de texte.

Dans chaque entrée :
- `msgctxt` : **qui parle**. Un nom de personnage (`Abel`), `Narrator`, `Choix` (ce que le joueur ou la joueuse choisit de dire), `Narration / joueur`, ou `Tag …` pour les textes de menus internes (Date-A-Dex, Roomers, SPECS…).
- `msgid` : l'anglais. **Ne jamais le modifier.**
- `msgstr` : votre traduction. Laissez-le vide s'il n'est pas encore traduit : le jeu affichera l'anglais.
- `#:` : l'emplacement dans le script. Ne pas toucher.

## 2. Règles techniques (sinon la ligne est rejetée)

| Règle | Exemple |
|---|---|
| Garder les balises `<i>…</i>`, `<b>…</b>`, `<w>…</w>` (texte qui tremble) | `Obviously? In <i>love</i>?` → `Évidemment ? <i>Amoureux</i> ?` |
| Ne jamais écrire `::` | |
| Garder les séparateurs `>>>` (descriptions de niveaux SPECS) | même nombre de `>>>` |
| Listes de niveaux SPECS : même nombre de virgules, pas de `:` | |
| Pas de retour à la ligne ni de tabulation | |
| Morceaux de phrases (commentaire « Morceau de phrase coupé par une variable ») | Le jeu insère un nom ou un nombre entre deux morceaux : la traduction doit rester compatible avec cet ordre. |

`tools/build.py` vérifie tout cela et liste les problèmes dans `build_report.txt`.

## 3. Accords selon le genre du joueur ou de la joueuse

Au début de la partie, le jeu demande les pronoms : **il**, **elle** ou **iel**. Le français accorde beaucoup de mots selon ce choix. Écrivez les variantes ainsi :

```
{{masculin|féminin|neutre}}
```

- `Tu es {{prêt|prête|prêt·e}} ?`
- `{{Mon beau|Ma belle|Mon bel être}}, tu m'as manqué.`
- Si le neutre et le masculin sont identiques, deux formes suffisent : `{{seul|seule}}` (le neutre reprend alors la première forme). **Préférez toutefois toujours donner le neutre.**

Pour le neutre, on privilégie d'abord une **reformulation épicène** (« Tu es là ! » plutôt que « Tu es venu·e ! »). Sinon, on utilise le point médian (`prêt·e`, `heureux·se`).

N'utilisez `{{…}}` **que pour le joueur ou la joueuse**. Le genre des personnages est fixe : un personnage reste toujours il, elle ou iel selon sa fiche.

## 4. Ton et style

- **Le jeu est drôle avant tout.** Une blague qui tombe à plat en français doit être réécrite, pas traduite mot à mot. Jeux de mots : on cherche un équivalent français, même s'il s'éloigne du sens littéral. En dernier recours, on garde l'esprit de la blague plutôt que la lettre.
- **Chaque personnage a sa voix** (voir sa fiche) : niveau de langue, tics verbaux, longueur des phrases, vulgarité. Un personnage qui parle mal parle mal en français ; un personnage précieux reste précieux.
- **Grossièretés** : on garde le même niveau (fuck → putain / bordel / merde selon le contexte, pas « zut »).
- **Références culturelles** : on garde les références universelles (films, jeux). On adapte seulement les références très américaines qui ne diraient rien à un public francophone, si c'est possible sans casser la scène.
- **Doublage** : le jeu est entièrement doublé en anglais. Le texte français est un **sous-titre**. Il doit rester à peu près de la même longueur, pour ne pas défiler trop vite ni déborder des bulles.
- **Les noms des personnages ne se traduisent pas** (ils sont prononcés dans le doublage). On peut expliquer un jeu de mots sur un nom si une réplique le commente, mais sans renommer le personnage.

## 5. Tutoiement et vouvoiement

- **Le joueur ou la joueuse tutoie** les objets de sa maison, sauf indication contraire de la fiche.
- **Les personnages tutoient le joueur ou la joueuse** par défaut. La fiche indique les exceptions (personnages précieux, formels, aristocrates, robots de service…). Un passage du vouvoiement au tutoiement peut marquer l'évolution de la relation : c'est permis, à condition d'être cohérent.
- **Le Narrateur vouvoie** le joueur ou la joueuse, narration comprise (« Vous ouvrez la porte »). C'est un narrateur britannique pince-sans-rire : élégant, sarcastique, parfois vulgaire par contraste.
- Les choix (`Choix`) sont des répliques du joueur ou de la joueuse : ils suivent la règle du personnage auquel on parle.

## 6. Typographie

- Guillemets français `« … »` pour les citations. Les apostrophes `'` ou `’` sont acceptées.
- **Tapez des espaces normales** avant `? ! : ;` et à l'intérieur des guillemets : le plugin les transforme automatiquement en espaces insécables.
- Points de suspension : `...` ou `…`, au choix (le jeu utilise `...`).
- Évitez le caractère `œ` : il manque dans les polices du jeu, et le plugin le remplace par `oe`.
- Majuscules accentuées : `À`, `É`, `Ç`… sont disponibles, utilisez-les.

## 7. Relecture

Les entrées traduites par IA portent le commentaire `# Traduction IA – à relire`. Après relecture, supprimez ce commentaire. Un traducteur ou une traductrice qui doute peut marquer l'entrée `fuzzy` : elle ne sera pas utilisée en jeu tant que le marqueur reste.
