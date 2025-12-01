using System;
using System.Collections.Generic;
using PennantSimulator.Models;

namespace PennantSimulator.Core
{
    public class InjurySystem
    {
        private static Random _rng = new Random();

        public enum InjuryType
        {
            None,
            Minor,      // 1-3 days
            Moderate,   // 4-7 days
            Severe,     // 8-21 days
            Career      // Season ending
        }

        public class Injury
        {
            public InjuryType Type { get; set; }
            public string Description { get; set; } = "";
            public int DaysRemaining { get; set; }
            public DateTime InjuryDate { get; set; }

            public bool IsHealed => DaysRemaining <= 0;
        }

        public static Injury? CheckForInjury(Player player, bool inGame = false)
        {
            if (player == null || player.IsInjured) return null;

            double baseRisk = 0.01; // 1% base risk
            
            // Fatigue increases risk
            if (player.CurrentStamina < 30)
                baseRisk *= 2.0;
            if (player.CurrentStamina < 15)
                baseRisk *= 2.0;

            // Age factor
            if (player.Age > 32)
                baseRisk *= 1.5;
            if (player.Age > 36)
                baseRisk *= 2.0;

            // In-game risk is slightly higher
            if (inGame)
                baseRisk *= 1.2;

            if (_rng.NextDouble() < baseRisk)
            {
                return GenerateInjury(player);
            }

            return null;
        }

        private static Injury GenerateInjury(Player player)
        {
            // Determine severity
            double roll = _rng.NextDouble();
            InjuryType type;
            int days;
            string desc;

            if (roll < 0.60) // 60% minor
            {
                type = InjuryType.Minor;
                days = _rng.Next(1, 4);
                desc = GetRandomInjuryDescription(type);
            }
            else if (roll < 0.85) // 25% moderate
            {
                type = InjuryType.Moderate;
                days = _rng.Next(4, 8);
                desc = GetRandomInjuryDescription(type);
            }
            else if (roll < 0.98) // 13% severe
            {
                type = InjuryType.Severe;
                days = _rng.Next(8, 22);
                desc = GetRandomInjuryDescription(type);
            }
            else // 2% career-threatening
            {
                type = InjuryType.Career;
                days = _rng.Next(60, 180);
                desc = GetRandomInjuryDescription(type);
            }

            player.IsInjured = true;
            player.Morale = Math.Max(0, player.Morale - 15);

            return new Injury
            {
                Type = type,
                Description = desc,
                DaysRemaining = days,
                InjuryDate = DateTime.Now
            };
        }

        private static string GetRandomInjuryDescription(InjuryType type)
        {
            var minor = new[] { "Muscle soreness", "Minor bruise", "Slight strain", "Fatigue" };
            var moderate = new[] { "Pulled muscle", "Sprained ankle", "Finger jam", "Back stiffness" };
            var severe = new[] { "Torn ligament", "Fractured bone", "Shoulder injury", "Knee injury" };
            var career = new[] { "ACL tear", "Tommy John surgery needed", "Severe back injury", "Career-threatening injury" };

            return type switch
            {
                InjuryType.Minor => minor[_rng.Next(minor.Length)],
                InjuryType.Moderate => moderate[_rng.Next(moderate.Length)],
                InjuryType.Severe => severe[_rng.Next(severe.Length)],
                InjuryType.Career => career[_rng.Next(career.Length)],
                _ => "Unknown injury"
            };
        }

        public static void AdvanceRecovery(Player player, Injury injury, int days = 1)
        {
            if (injury == null || injury.IsHealed) return;

            injury.DaysRemaining = Math.Max(0, injury.DaysRemaining - days);

            if (injury.IsHealed)
            {
                player.IsInjured = false;
                player.Morale = Math.Min(100, player.Morale + 10);
                player.CurrentStamina = Math.Min(player.Stamina, player.CurrentStamina + 20);
            }
        }
    }
}
