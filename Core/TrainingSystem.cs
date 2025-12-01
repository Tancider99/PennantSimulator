using System;
using PennantSimulator.Models;

namespace PennantSimulator.Core
{
    public class TrainingSystem
    {
        private static Random _rng = new Random();

        public enum TrainingType
        {
            Batting,
            Pitching,
            Fielding,
            Speed,
            Mental,
            Recovery
        }

        public static TrainingResult Train(Player player, TrainingType type, int intensity = 50)
        {
            if (player == null) throw new ArgumentNullException(nameof(player));

            var result = new TrainingResult { Type = type, Success = false };

            // Check fatigue - high fatigue reduces effectiveness
            if (player.CurrentStamina < 20 && type != TrainingType.Recovery)
            {
                result.Message = $"{player.Name} is too tired to train effectively.";
                player.Morale = Math.Max(0, player.Morale - 2);
                return result;
            }

            // Apply training effects
            int gain = 0;
            switch (type)
            {
                case TrainingType.Batting:
                    gain = _rng.Next(1, 4) + (intensity / 25);
                    player.Contact = Math.Min(100, player.Contact + gain / 2);
                    player.Power = Math.Min(100, player.Power + gain / 2);
                    player.GainExperience(10 + intensity / 5);
                    result.AttributeGains["Contact"] = gain / 2;
                    result.AttributeGains["Power"] = gain / 2;
                    break;

                case TrainingType.Pitching:
                    gain = _rng.Next(1, 4) + (intensity / 25);
                    player.Control = Math.Min(100, player.Control + gain / 2);
                    player.Breaking = Math.Min(100, player.Breaking + gain / 2);
                    player.GainExperience(10 + intensity / 5);
                    result.AttributeGains["Control"] = gain / 2;
                    result.AttributeGains["Breaking"] = gain / 2;
                    break;

                case TrainingType.Fielding:
                    gain = _rng.Next(1, 3) + (intensity / 30);
                    player.Defense = Math.Min(100, player.Defense + gain);
                    player.Arm = Math.Min(100, player.Arm + gain / 2);
                    player.GainExperience(8 + intensity / 6);
                    result.AttributeGains["Defense"] = gain;
                    result.AttributeGains["Arm"] = gain / 2;
                    break;

                case TrainingType.Speed:
                    gain = _rng.Next(1, 3) + (intensity / 30);
                    player.Speed = Math.Min(100, player.Speed + gain);
                    player.GainExperience(8 + intensity / 6);
                    result.AttributeGains["Speed"] = gain;
                    break;

                case TrainingType.Mental:
                    player.Morale = Math.Min(100, player.Morale + 10 + intensity / 10);
                    player.GainExperience(5);
                    result.AttributeGains["Morale"] = 10 + intensity / 10;
                    break;

                case TrainingType.Recovery:
                    int recovery = 15 + intensity / 5;
                    player.Recover(recovery);
                    result.AttributeGains["Stamina"] = recovery;
                    result.Message = $"{player.Name} recovered {recovery} stamina.";
                    result.Success = true;
                    return result;
            }

            // Apply fatigue
            int fatigue = Math.Max(5, intensity / 10);
            player.ApplyFatigue(fatigue);

            // Check for injury risk during intense training
            if (intensity > 70 && _rng.NextDouble() < 0.05)
            {
                player.IsInjured = true;
                result.Message = $"{player.Name} was injured during training!";
                result.Success = false;
                return result;
            }

            result.Success = true;
            result.Message = $"{player.Name} trained {type}. Gained: {string.Join(", ", result.AttributeGains)}";
            return result;
        }
    }

    public class TrainingResult
    {
        public TrainingSystem.TrainingType Type { get; set; }
        public bool Success { get; set; }
        public string Message { get; set; } = "";
        public Dictionary<string, int> AttributeGains { get; set; } = new Dictionary<string, int>();
    }
}
