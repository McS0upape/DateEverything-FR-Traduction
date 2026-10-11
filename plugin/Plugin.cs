using System;
using System.Collections;
using System.IO;
using BepInEx;
using BepInEx.Configuration;
using BepInEx.Logging;
using HarmonyLib;
using Ink.Runtime;
using TMPro;
using UnityEngine;
using UnityEngine.SceneManagement;
using Path = System.IO.Path;

namespace DateEverythingFR
{
    [BepInPlugin(Guid, "Date Everything - Traduction FR", Version)]
    public class Plugin : BaseUnityPlugin
    {
        public const string Guid = "fr.communaute.dateeverything.traduction";
        public const string Version = "0.1.0";

        internal static ManualLogSource Log;
        internal static TranslationData Data;

        private ConfigEntry<bool> _enabled;
        private ConfigEntry<bool> _replaceOe;
        private ConfigEntry<bool> _dumpUi;
        private ConfigEntry<bool> _frenchTypography;
        private ConfigEntry<string> _fallbackFont;

        private void Awake()
        {
            Log = Logger;
            _enabled = Config.Bind("General", "Enabled", true, "Active la traduction française.");
            _replaceOe = Config.Bind("Texte", "ReplaceOE", true,
                "Remplace œ/Œ par oe/OE (les polices du jeu ne contiennent pas ce caractère).");
            _dumpUi = Config.Bind("Outils", "DumpUntranslatedUI", false,
                "Enregistre les textes d'interface non traduits dans ui_untranslated.txt (pour les traducteurs).");
            _frenchTypography = Config.Bind("Texte", "FrenchTypography", true,
                "Espaces insécables automatiques avant ? ! : ; et à l'intérieur des guillemets « ».");
            _fallbackFont = Config.Bind("Texte", "FallbackFont", "RadioCanada-Regular SDF",
                "Police du jeu utilisée pour les caractères accentués absents de certaines polices.");

            if (!_enabled.Value)
            {
                Log.LogInfo("Traduction désactivée dans la configuration.");
                return;
            }

            var dir = Path.Combine(Path.GetDirectoryName(Info.Location), "fr");
            bool replaceOe = _replaceOe.Value;
            bool typo = _frenchTypography.Value;
            Data = TranslationData.Load(dir, s =>
            {
                if (replaceOe) s = s.Replace("œ", "oe").Replace("Œ", "OE");
                if (typo) s = Typography.Apply(s);
                return s;
            });
            Log.LogInfo($"Traductions chargées : {Data.ByPath.Count} chaînes de dialogue, {Data.Ui.Count} textes d'interface.");

            UiTranslator.Data = Data;
            UiTranslator.Dump = _dumpUi.Value;
            UiTranslator.DumpPath = Path.Combine(Path.GetDirectoryName(Info.Location), "ui_untranslated.txt");
            UiTranslator.FallbackFontName = _fallbackFont.Value;

            new Harmony(Guid).PatchAll(typeof(Plugin).Assembly);
            SceneManager.sceneLoaded += (s, m) => UiTranslator.TryInstallFallbackFont();
            StartCoroutine(Housekeeping());
        }

        private IEnumerator Housekeeping()
        {
            var wait = new WaitForSecondsRealtime(5f);
            while (true)
            {
                UiTranslator.TryInstallFallbackFont();
                try { UiTranslator.FlushDump(); }
                catch (Exception e) { Log.LogWarning("Dump UI : " + e.Message); }
                yield return wait;
            }
        }

        private void OnApplicationQuit()
        {
            try { UiTranslator.FlushDump(); } catch { }
        }
    }

    /// <summary>Le script Ink est construit sur un thread d'arrière-plan : on traduit juste après la construction.</summary>
    [HarmonyPatch(typeof(Story), MethodType.Constructor, typeof(string))]
    internal static class StoryCtorPatch
    {
        private static void Postfix(Story __instance)
        {
            if (Plugin.Data == null) return;
            try
            {
                var sw = System.Diagnostics.Stopwatch.StartNew();
                var st = InkTranslator.Apply(__instance, Plugin.Data);
                Plugin.Log.LogInfo($"Script Ink traduit en {sw.ElapsedMilliseconds} ms : {st.ByPath} par chemin, " +
                                   $"{st.ByFallback} par texte (secours), {st.Mismatch} chemins dont l'anglais a changé.");
            }
            catch (Exception e)
            {
                Plugin.Log.LogError("Échec de la traduction du script Ink : " + e);
            }
        }
    }

    /// <summary>Pronoms du joueur : 1 = il, 2 = elle, autre = iel.</summary>
    [HarmonyPatch(typeof(Save.SaveData), nameof(Save.SaveData.SetPlayerPronounsInk))]
    internal static class PronounsPatch
    {
        private static void Postfix(Save.SaveData __instance)
        {
            try
            {
                int pronouns = Traverse.Create(__instance).Field("PlayerData").Field("Pronouns").GetValue<int>();
                var g = pronouns == 1 ? InkTranslator.Gender.Masculine
                      : pronouns == 2 ? InkTranslator.Gender.Feminine
                      : InkTranslator.Gender.Neutral;
                InkTranslator.SetGender(g);
                Plugin.Log.LogInfo($"Accords du joueur : {g}");
            }
            catch (Exception e)
            {
                Plugin.Log.LogWarning("Lecture des pronoms impossible : " + e.Message);
            }
        }
    }

    [HarmonyPatch(typeof(TMP_Text), nameof(TMP_Text.text), MethodType.Setter)]
    internal static class TmpTextSetterPatch
    {
        private static void Prefix(ref string value) => value = UiTranslator.Translate(value);
    }

    [HarmonyPatch(typeof(TMP_Text), nameof(TMP_Text.SetText), typeof(string), typeof(bool))]
    internal static class TmpSetTextPatch
    {
        private static void Prefix(ref string sourceText) => sourceText = UiTranslator.Translate(sourceText);
    }

    /// <summary>Textes posés directement dans les scènes/prefabs : traduits à l'activation.</summary>
    [HarmonyPatch]
    internal static class TmpOnEnablePatch
    {
        private static System.Collections.Generic.IEnumerable<System.Reflection.MethodBase> TargetMethods()
        {
            yield return AccessTools.Method(typeof(TextMeshProUGUI), "OnEnable");
            yield return AccessTools.Method(typeof(TextMeshPro), "OnEnable");
        }

        private static void Prefix(TMP_Text __instance)
        {
            var t = __instance.text;
            var fr = UiTranslator.Translate(t);
            if (!ReferenceEquals(fr, t)) __instance.text = fr;
        }
    }
}
