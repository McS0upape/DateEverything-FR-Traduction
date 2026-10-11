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

        public static string Translate(string text)
        {
            if (string.IsNullOrEmpty(text) || Data == null) return text;
            if (Data.Ui.TryGetValue(text, out var fr)) return fr;

            // essaie sans les espaces de début/fin, puis réinjecte-les
            var trimmed = text.Trim();
            if (trimmed.Length != text.Length && trimmed.Length > 0 && Data.Ui.TryGetValue(trimmed, out fr))
            {
                int start = text.IndexOf(trimmed, System.StringComparison.Ordinal);
                return text.Substring(0, start) + fr + text.Substring(start + trimmed.Length);
            }

            if (Dump && trimmed.Length > 0 && Seen.Add(trimmed))
            {
                lock (Pending) Pending.Add(trimmed);
            }
            return text;
        }

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
