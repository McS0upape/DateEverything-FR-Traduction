using System.Collections.Generic;
using System.IO;
using System.Text;
using TMPro;
using UnityEngine;

namespace DateEverythingFR
{
    /// <summary>Traduction des textes d'interface (TextMeshPro) par correspondance exacte, et police de secours pour les accents.</summary>
    internal static class UiTranslator
    {
        public static TranslationData Data;
        public static bool Dump;
        public static string DumpPath;
        public static string FallbackFontName;

        private static readonly HashSet<string> Seen = new HashSet<string>();
        private static readonly List<string> Pending = new List<string>();
        private static bool _fontInstalled;

        public static int Calls, Hits;

        public static string Translate(string text)
        {
            if (string.IsNullOrEmpty(text) || Data == null) return text;
            Calls++;
            if (Data.Ui.TryGetValue(text, out var fr)) { Hits++; return fr; }

            // sans les espaces / espaces de largeur nulle (U+200B, BOM) de début et de fin, réinjectés ensuite
            int start = 0, end = text.Length;
            while (start < end && IsPad(text[start])) start++;
            while (end > start && IsPad(text[end - 1])) end--;
            var trimmed = text.Substring(start, end - start);
            if (trimmed.Length == 0) return text;
            string core = null;
            if (trimmed.Length != text.Length && Data.Ui.TryGetValue(trimmed, out fr)) core = fr;
            if (core == null && trimmed.Length < 300)
            {
                foreach (var kv in Data.UiRegex)
                {
                    var m = kv.Key.Match(trimmed);
                    if (m.Success) { core = m.Result(kv.Value); break; }
                }
            }
            if (core != null)
            {
                Hits++;
                return text.Substring(0, start) + core + text.Substring(end);
            }

            if (Dump && Seen.Add(trimmed))
            {
                lock (Pending) Pending.Add(trimmed);
            }
            return text;
        }

        private static bool IsPad(char c) => char.IsWhiteSpace(c) || c == '​' || c == '﻿';

        public static void FlushDump()
        {
            if (!Dump) return;
            string[] lines;
            lock (Pending)
            {
                if (Pending.Count == 0) return;
                lines = Pending.ToArray();
                Pending.Clear();
            }
            var sb = new StringBuilder();
            foreach (var l in lines)
                sb.Append(l.Replace("\\", "\\\\").Replace("\n", "\\n").Replace("\r", "")).Append('\n');
            File.AppendAllText(DumpPath, sb.ToString(), Encoding.UTF8);
        }

        /// <summary>Ajoute une police contenant les accents aux polices de secours globales de TextMeshPro.</summary>
        public static bool TryInstallFallbackFont()
        {
            if (_fontInstalled) return true;
            TMP_FontAsset fallback = null;
            foreach (var f in Resources.FindObjectsOfTypeAll<TMP_FontAsset>())
            {
                if (f != null && f.name == FallbackFontName) { fallback = f; break; }
            }
            if (fallback == null) return false;
            try
            {
                var list = TMP_Settings.fallbackFontAssets;
                if (list == null) return false;
                if (!list.Contains(fallback)) list.Add(fallback);
                _fontInstalled = true;
                Plugin.Log.LogInfo($"Police de secours installée : {fallback.name}");
            }
            catch (System.Exception e)
            {
                Plugin.Log.LogWarning("Impossible d'installer la police de secours : " + e.Message);
            }
            return _fontInstalled;
        }
    }
}
