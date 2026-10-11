using System.Text.RegularExpressions;

namespace DateEverythingFR
{
    /// <summary>Typographie française : espaces insécables (U+00A0) là où le français met une espace avant la ponctuation.</summary>
    internal static class Typography
    {
        private const string Nbsp = " ";

        // espace normale avant ? ! ; : » (mais pas "::", séparateur du nom du personnage)
        private static readonly Regex BeforePunct = new Regex(@" (?=[?!;»]|:(?!:))", RegexOptions.Compiled);
        private static readonly Regex AfterOpenQuote = new Regex(@"« ", RegexOptions.Compiled);

        public static string Apply(string s)
        {
            if (s.IndexOf(' ') < 0) return s;
            s = BeforePunct.Replace(s, Nbsp);
            s = AfterOpenQuote.Replace(s, "«" + Nbsp);
            return s;
        }
    }
}
