"""Assemble l'archive pour les joueurs : BepInEx + plugin + données de traduction.

Usage : python release.py <version>     (après build.py et dotnet build -c Release)
Produit dist/DateEverything_FR_v<version>.zip, à extraire dans le dossier du jeu.
"""
import os
import shutil
import sys
import zipfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BEPINEX = os.path.join(ROOT, "downloads", "bepinex")
PLUGIN_DLL = os.path.join(ROOT, "plugin", "bin", "Release", "DateEverythingFR.dll")
DATA = os.path.join(ROOT, "dist", "fr")
PLUGIN_DIR = "BepInEx/plugins/DateEverythingFR"


def main(version):
    out = os.path.join(ROOT, "dist", f"DateEverything_FR_v{version}.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(BEPINEX):
            for f in files:
                full = os.path.join(base, f)
                z.write(full, os.path.relpath(full, BEPINEX).replace(os.sep, "/"))
        # BepInEx.cfg avec HideManagerGameObject = true (le jeu détruit sinon l'objet du plugin)
        z.write(os.path.join(ROOT, "release_extra", "BepInEx", "config", "BepInEx.cfg"), "BepInEx/config/BepInEx.cfg")
        z.write(PLUGIN_DLL, f"{PLUGIN_DIR}/DateEverythingFR.dll")
        for f in ("dialogues.tsv", "ui.tsv"):
            z.write(os.path.join(DATA, f), f"{PLUGIN_DIR}/fr/{f}")
        z.writestr(f"{PLUGIN_DIR}/LISEZMOI.txt",
                   "Traduction française communautaire de Date Everything!\n"
                   "Pour désinstaller : supprimer winhttp.dll, doorstop_config.ini, .doorstop_version et le dossier BepInEx.\n")
        z.writestr("LISEZMOI - Traduction FR.txt", INSTRUCTIONS.format(version=version).replace("\n", "\r\n"))
    print(out, os.path.getsize(out) // 1024, "Ko")
    # Même contenu en dossier décompressé, prêt à copier
    folder = out[:-4]
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    with zipfile.ZipFile(out) as z:
        z.extractall(folder)
    print(folder)


INSTRUCTIONS = """Date Everything! - Traduction française communautaire (v{version})
Projet de fans non officiel. Il faut posséder le jeu.

INSTALLATION
1. Sur Steam : clic droit sur Date Everything! > Gérer > Parcourir les fichiers locaux.
   Le dossier qui s'ouvre contient "Date Everything.exe".
2. Copiez-y TOUT le contenu de ce dossier (BepInEx, winhttp.dll, doorstop_config.ini,
   .doorstop_version...). Si Windows demande de fusionner ou remplacer, acceptez.
3. Lancez le jeu normalement. Le premier lancement prend quelques secondes de plus.

Les textes pas encore traduits restent en anglais.

STEAM DECK / LINUX (Proton)
Dans les propriétés du jeu sur Steam, options de lancement :
  WINEDLLOVERRIDES="winhttp=n,b" %command%

DÉSINSTALLATION
Supprimez winhttp.dll, doorstop_config.ini, .doorstop_version et le dossier BepInEx.
Aucun fichier d'origine du jeu n'est modifié.

OPTIONS (après un premier lancement)
BepInEx/config/fr.communaute.dateeverything.traduction.cfg
  Enabled = false  -> remet le jeu en anglais
"""


if __name__ == "__main__":
    main(sys.argv[1])
