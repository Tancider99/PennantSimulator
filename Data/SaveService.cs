using System;
using System.IO;
using System.Text.Json;
using System.Text.Json.Serialization;
using PennantSimulator.Core;
using PennantSimulator.Models;

namespace PennantSimulator.Data
{
    public static class SaveService
    {
        private static readonly JsonSerializerOptions _options = new JsonSerializerOptions
        {
            WriteIndented = true,
            ReferenceHandler = ReferenceHandler.IgnoreCycles,
            Converters = { new JsonStringEnumConverter() }
        };

        public static void SaveLeague(string path, League league)
        {
            if (league == null) throw new ArgumentNullException(nameof(league));
            var json = JsonSerializer.Serialize(league, _options);
            File.WriteAllText(path, json);
        }

        public static League? LoadLeague(string path)
        {
            if (!File.Exists(path)) return null;
            var json = File.ReadAllText(path);
            try
            {
                var league = JsonSerializer.Deserialize<League>(json, _options);
                return league;
            }
            catch
            {
                return null;
            }
        }
    }
}
