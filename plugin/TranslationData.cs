using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace DateEverythingFR
{
    /// <summary>Données de traduction chargées depuis dialogues.tsv et ui.tsv (générés par tools/build.py).</summary>
    internal sealed class TranslationData
    {
        public sealed class Entry
        {
            public string Original;
            public string Translation;
        }

        /// <summary>chemin Ink -> entrée</summary>
        public readonly Dictionary<string, Entry> ByPath = new Dictionary<string, Entry>(StringComparer.Ordinal);

        /// <summary>knot + \u0001 + original -> traduction (secours si le jeu a été mis à jour et les chemins ont bougé)</summary>
        public readonly Dictionary<string, string> ByKnotText = new Dictionary<string, string>(StringComparer.Ordinal);

        /// <summary>texte d'interface anglais -> français</summary>
        public readonly Dictionary<string, string> Ui = new Dictionary<string, string>(StringComparer.Ordinal);

        /// <summary>motif (regex complète) -> remplacement ($1, $2...)</summary>
        public readonly List<KeyValuePair<System.Text.RegularExpressions.Regex, string>> UiRegex =
            new List<KeyValuePair<System.Text.RegularExpressions.Regex, string>>();

        public string SourceHash = "";

        public static string KnotKey(string knot, string original) => knot + "\u0001" + original;

        public static TranslationData Load(string dir, Func<string, string> postProcess)
        {
            var data = new TranslationData();
            var dialogues = Path.Combine(dir, "dialogues.tsv");
            if (File.Exists(dialogues))
            {
                foreach (var line in File.ReadLines(dialogues, Encoding.UTF8))
                {
                    if (line.Length == 0) continue;
                    var cols = line.Split('\t');
                    if (cols[0] == "#DEFR1")
                    {
                        data.SourceHash = cols.Length > 1 ? cols[1] : "";
                        continue;
                    }
                    if (cols.Length != 5) continue;
                    var entry = new Entry { Original = Unescape(cols[3]), Translation = postProcess(Unescape(cols[4])) };
                    data.ByPath[cols[0]] = entry;
                    if (cols[2] == "1")
                        data.ByKnotText[KnotKey(cols[1], entry.Original)] = entry.Translation;
                }
            }

            var uiRegex = Path.Combine(dir, "ui_regex.tsv");
            if (File.Exists(uiRegex))
            {
                foreach (var line in File.ReadLines(uiRegex, Encoding.UTF8))
                {
                    var cols = line.Split('\t');
                    if (cols.Length != 2) continue;
                    try
                    {
                        data.UiRegex.Add(new KeyValuePair<System.Text.RegularExpressions.Regex, string>(
                            new System.Text.RegularExpressions.Regex("^(?:" + Unescape(cols[0]) + ")$",
                                System.Text.RegularExpressions.RegexOptions.Compiled),
                            postProcess(Unescape(cols[1]))));
                    }
                    catch (ArgumentException) { }
                }
            }

            var ui = Path.Combine(dir, "ui.tsv");
            if (File.Exists(ui))
            {
                foreach (var line in File.ReadLines(ui, Encoding.UTF8))
                {
                    var cols = line.Split('\t');
                    if (cols.Length != 2) continue;
                    data.Ui[Unescape(cols[0])] = postProcess(Unescape(cols[1]));
                }
            }
            return data;
        }

        private static string Unescape(string s)
        {
            if (s.IndexOf('\\') < 0) return s;
            var sb = new StringBuilder(s.Length);
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if (c == '\\' && i + 1 < s.Length)
                {
                    char n = s[++i];
                    switch (n)
                    {
                        case 't': sb.Append('\t'); break;
                        case 'n': sb.Append('\n'); break;
                        case 'r': sb.Append('\r'); break;
                        default: sb.Append(n); break;
                    }
                }
                else sb.Append(c);
            }
            return sb.ToString();
        }
    }
}
