using System.Collections.Generic;
using System.Text.RegularExpressions;
using Ink.Runtime;

namespace DateEverythingFR
{
    /// <summary>
    /// Remplace les chaînes du script Ink chargé en mémoire.
    /// Les chemins suivent la même convention que tools/inklib.py :
    /// index dans Container.content, ou nom pour le contenu nommé, séparés par "/".
    /// </summary>
    internal static class InkTranslator
    {
        public enum Gender { Masculine = 0, Feminine = 1, Neutral = 2 }

        private static readonly Regex GenderRe = new Regex(@"\{\{(.*?)\}\}", RegexOptions.Compiled);

        // chaînes contenant des accords {{masc|fém|neutre}} : rendues à nouveau quand le joueur choisit ses pronoms
        private static readonly List<KeyValuePair<StringValue, string>> Templates = new List<KeyValuePair<StringValue, string>>();
        private static readonly object Lock = new object();

        public static Gender CurrentGender = Gender.Neutral;

        public struct Stats
        {
            public int ByPath, ByFallback, Mismatch;
        }

        public static Stats Apply(Story story, TranslationData data)
        {
            var stats = new Stats();
            lock (Lock)
            {
                Templates.Clear();
                Walk(story.mainContentContainer, "", null, data, ref stats);
            }
            return stats;
        }

        private static void Walk(Container container, string path, string knot, TranslationData data, ref Stats stats)
        {
            var content = container.content;
            for (int i = 0; i < content.Count; i++)
            {
                var obj = content[i];
                if (obj is StringValue sv)
                {
                    if (knot == null) continue;
                    var p = path.Length == 0 ? i.ToString() : path + "/" + i;
                    Translate(sv, p, knot, data, ref stats);
                }
                else if (obj is Container child)
                {
                    Walk(child, path.Length == 0 ? i.ToString() : path + "/" + i, knot, data, ref stats);
                }
            }
            var named = container.namedOnlyContent;
            if (named == null) return;
            foreach (var kv in named)
            {
                if (kv.Value is Container child)
                {
                    var p = path.Length == 0 ? kv.Key : path + "/" + kv.Key;
                    Walk(child, p, knot ?? kv.Key, data, ref stats);
                }
            }
        }

        private static void Translate(StringValue sv, string path, string knot, TranslationData data, ref Stats stats)
        {
            var original = sv.value;
            if (string.IsNullOrEmpty(original) || sv.isNewline) return;

            string translation = null;
            if (data.ByPath.TryGetValue(path, out var entry))
            {
                if (entry.Original == original)
                {
                    translation = entry.Translation;
                    stats.ByPath++;
                }
                else stats.Mismatch++;
            }
            if (translation == null && data.ByKnotText.TryGetValue(TranslationData.KnotKey(knot, original), out var fb))
            {
                translation = fb;
                stats.ByFallback++;
            }
            if (translation == null) return;

            if (translation.IndexOf("{{", System.StringComparison.Ordinal) >= 0)
            {
                Templates.Add(new KeyValuePair<StringValue, string>(sv, translation));
                sv.value = Render(translation, CurrentGender);
            }
            else sv.value = translation;
        }

        /// <summary>{{masc|fém|neutre}} -> variante selon le genre ; sans neutre, le masculin est utilisé.</summary>
        public static string Render(string template, Gender gender)
        {
            return GenderRe.Replace(template, m =>
            {
                var parts = m.Groups[1].Value.Split('|');
                int idx = (int)gender;
                if (idx >= parts.Length) idx = 0;
                return parts[idx];
            });
        }

        public static void SetGender(Gender gender)
        {
            lock (Lock)
            {
                CurrentGender = gender;
                foreach (var kv in Templates)
                    kv.Key.value = Render(kv.Value, gender);
            }
        }
    }
}
