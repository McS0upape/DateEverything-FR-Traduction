"""Assemble l'archive pour les joueurs : BepInEx + plugin + données de traduction.

Usage : python release.py <version>     (après build.py et dotnet build -c Release)
Produit dist/DateEverything_FR_v<version>.zip, à extraire dans le dossier du jeu.
"""
import os
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
        z.write(PLUGIN_DLL, f"{PLUGIN_DIR}/DateEverythingFR.dll")
        for f in ("dialogues.tsv", "ui.tsv"):
            z.write(os.path.join(DATA, f), f"{PLUGIN_DIR}/fr/{f}")
        z.writestr(f"{PLUGIN_DIR}/LISEZMOI.txt",
                   "Traduction française communautaire de Date Everything!\n"
                   "Pour désinstaller : supprimer winhttp.dll, doorstop_config.ini, .doorstop_version et le dossier BepInEx.\n")
    print(out, os.path.getsize(out) // 1024, "Ko")


if __name__ == "__main__":
    main(sys.argv[1])
