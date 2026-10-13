# Consignes : relecture des jeux de mots (agent Opus)

Projet : traduction française de *Date Everything!*. Dossier racine : `C:\Users\mcsou\DateEverything_FR`.

Les agents de traduction ont signalé dans `tmp/jdm/<knot>.tsv` des jeux de mots qu'ils n'ont pas réussi à rendre (colonnes séparées par des tabulations : id, anglais, traduction actuelle, explication).

## Pour chaque fichier .tsv à traiter

1. **Préparer** :
   - lis la fiche `translation/personnages/<knot>.md`, section « Voix en français » ;
   - lis `translation/GLOSSAIRE.tsv` ;
   - lis les règles de `tools/CONSIGNES_COURTES.md`.
2. **Retrouver le contexte de chaque entrée** : les entrées voisines (id ± 5) se trouvent dans `translation/fr/<knot>.po`. L'id est l'index de l'entrée dans le .po (toutes entrées comprises, à partir de 0). Script polib conseillé :
   `python -c "import polib;po=polib.pofile('translation/fr/<knot>.po',wrapwidth=0);[print(i,e.msgctxt,'|',e.msgid,'=>',e.msgstr) for i in range(A,B)]"`
3. **Trouver un vrai jeu de mots français** qui fonctionne et garde la voix du personnage, en restant d'une longueur proche. Si une réplique voisine fait écho au jeu de mots, adapte-la aussi, pour que l'ensemble reste cohérent.
4. **Appliquer** : écris `tmp/work/<knot>_jdm.json` `{"<id>": "nouvelle traduction"}`, puis `cd tools && PYTHONIOENCODING=utf-8 python work.py apply <knot> ../tmp/work/<knot>_jdm.json --ai`. Corrige les REJET éventuels.
5. **Clore** : renomme le .tsv en `.tsv.fait`.

Pas de build, pas de git. Rapport final : par fichier, le nombre d'entrées améliorées et les 3 meilleures trouvailles. Signale les cas encore insatisfaisants.
