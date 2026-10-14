# Date Everything! — Traduction française (non officielle)

Traduction française communautaire de [Date Everything!](https://store.steampowered.com/app/2201320/) (Sassy Chap Games / Team17).
Projet de fans, non affilié aux développeurs. Il faut posséder le jeu.

Traduction faite à l'aide de l'IA en essayant de rester le plus fidèle possible aux textes originaux : plus d'un million de mots traduits ou en cours de traduction et de correction.

## État d'avancement

**~94 % des textes traduits** (environ 942 000 mots sur 1 000 000), au 15 octobre 2026.

| Partie | État |
|---|---|
| Interface, tutoriels, menus | ✅ traduits |
| Date-A-Dex, fins, épilogue | ✅ traduits |
| Dialogues : la grande majorité des personnages | ✅ traduits, jeux de mots repris à part |
| benhwa_sextoys, connie_console, vaughn_mousetrap | 🟡 en cours (37 à 51 %) |
| penelope_stationery, mikey_micro, monique_money, lux_lamp, koa_couch et quelques autres | ⬜ pas encore commencés |

Les textes pas encore traduits s'affichent en anglais, le jeu reste jouable. La traduction est une **première passe faite par IA** (Claude), avec des fiches de voix par personnage, un glossaire commun et une passe dédiée aux jeux de mots. Elle n'a **pas encore été relue entièrement par des humains** : attendez-vous à des maladresses, et n'hésitez pas à les signaler (onglet *Issues*).

Pour l'avancement exact, fichier par fichier : `python tools/work.py status`.

## Pour les joueurs : installation

1. Téléchargez la dernière archive `DateEverything_FR_vX.Y.zip` (onglet Releases).
2. Ouvrez le dossier du jeu : sur Steam, clic droit sur le jeu → *Gérer* → *Parcourir les fichiers locaux*.
3. Extrayez **tout le contenu** de l'archive dans ce dossier, à côté de `Date Everything.exe`.
4. Lancez le jeu normalement.

Au premier lancement, BepInEx (le chargeur de mods) prépare ses fichiers, ce qui peut prendre quelques secondes de plus. Le texte s'affiche ensuite en français ; les passages pas encore traduits restent en anglais.

**Sans archive (installation depuis les sources)** :
1. Installez [BepInEx 5.4.23 x64](https://github.com/BepInEx/BepInEx/releases) dans le dossier du jeu et lancez le jeu une fois, puis fermez-le.
2. Copiez `release_extra/BepInEx/config/BepInEx.cfg` dans `BepInEx/config/` (indispensable : sans ce réglage, le jeu détruit le plugin).
3. Compilez le plugin (`dotnet build -c Release` dans `plugin/`) et générez les données : `python tools/extract_ink.py` (le script Ink extrait de votre jeu n'est pas fourni dans ce dépôt), puis `python tools/build.py extracted/main_resources.json translation/fr dist/fr` (voir plus bas).
4. Copiez `DateEverythingFR.dll` dans `BepInEx/plugins/DateEverythingFR/`, et le contenu de `dist/fr/` dans `BepInEx/plugins/DateEverythingFR/fr/`.

**Désinstaller** : supprimez `winhttp.dll`, `doorstop_config.ini`, `.doorstop_version` et le dossier `BepInEx`. Le jeu n'est jamais modifié : aucun fichier d'origine n'est touché.

**Steam Deck / Linux (Proton)** : ajoutez `WINEDLLOVERRIDES="winhttp=n,b" %command%` aux options de lancement du jeu.

**Options** (`BepInEx/config/fr.communaute.dateeverything.traduction.cfg`) :
- `Enabled` : active ou désactive la traduction.
- `FrenchTypography` : espaces insécables automatiques avant `? ! : ;`.
- `ReplaceOE` : remplace `œ` par `oe` (caractère absent des polices du jeu).
- `DumpUntranslatedUI` : enregistre les textes d'interface non traduits (outil pour les traducteurs).

Le jeu vous demande vos pronoms au début de la partie : la traduction accorde le texte en fonction (il, elle ou iel).

## Pour les traducteurs et traductrices : contribuer

Tout ce qu'il faut savoir est dans [translation/GUIDE_TRADUCTION.md](translation/GUIDE_TRADUCTION.md).

- `translation/fr/*.po` : les textes, un fichier par personnage, à éditer avec [Poedit](https://poedit.net/) ou un éditeur de texte.
- `translation/personnages/*.md` : la fiche de voix de chaque personnage.
- `translation/GLOSSAIRE.tsv` : les termes du jeu ; les choix encore en débat sont dans `translation/PROPOSITIONS_GLOSSAIRE.md`.
- `tools/CONSIGNES_*.md` : les consignes données aux agents IA (ton, accords, balises à conserver).

Conventions principales : le narrateur vouvoie le joueur ou la joueuse, les personnages le tutoient ; les accords passent par `{{masc|fém|neutre}}` (jamais d'écriture inclusive « ·e » brute pour le joueur) ; les balises `<i>`, `<w>`… doivent être conservées ; le français parlé dans la VO devient de l'italien.

Une première passe est traduite par IA (commentaire `Traduction IA – à relire`). Le travail le plus précieux, c'est la **relecture en jeu** : repérer les tournures maladroites, les blagues qui tombent à plat, les incohérences de ton ou de tutoiement.

## Pour les développeurs : fonctionnement

Le jeu (Unity 2022.3, Mono) stocke tous ses dialogues dans un unique script [Ink](https://www.inklestudios.com/ink/) compilé. Le plugin BepInEx (`plugin/`) :

1. intercepte la construction de l'histoire Ink (`Story(string)`) et remplace chaque chaîne par sa traduction. Une chaîne est retrouvée par son chemin dans le script, et l'anglais d'origine sert de vérification ; en cas de mise à jour du jeu, le plugin se rabat sur une correspondance par texte ;
2. résout les accords `{{masc|fém|neutre}}` selon les pronoms du joueur ou de la joueuse, et les met à jour s'ils changent ;
3. traduit les textes d'interface TextMeshPro par correspondance exacte (`_ui.po`) ;
4. ajoute une police de secours pour les caractères accentués absents de certaines polices.

Les outils Python (`tools/`) :

| Script | Rôle |
|---|---|
| `extract_ink.py` | extrait le script Ink `main` des fichiers du jeu |
| `extract.py` | script Ink → fichiers PO (conserve les traductions existantes) |
| `build.py` | PO → `dialogues.tsv` / `ui.tsv` pour le plugin, avec validation (`build_report.txt`) |
| `work.py` | traduction lot par lot (`status`, `next`, `apply`) |
| `make_cards.py` | crée les fiches personnages à partir du Date-A-Dex |
| `ui_dump_to_po.py` | ajoute les textes d'interface collectés en jeu dans `_ui.po` |
| `release.py` | assemble l'archive pour les joueurs |
| `pseudo.py` | pseudo-traduction `[FR] …` pour tester la couverture |

Prérequis : Python 3.10+ (`pip install UnityPy polib`), SDK .NET 8 pour le plugin (`dotnet build -c Release` dans `plugin/`, avec `-p:GameDir=...` si le jeu n'est pas dans `D:\SteamLibrary`).

Après une mise à jour du jeu : `extract_ink.py` → `extract.py` (les traductions sont conservées, les lignes modifiées réapparaissent vides) → `build.py`.

## Droits

Les textes originaux appartiennent à leurs auteurs (Sassy Chap Games / Team17). Ce dépôt ne contient que des traductions et des outils ; l'archive distribuée ne contient aucun fichier du jeu. Si les ayants droit le demandent, le projet sera retiré.
