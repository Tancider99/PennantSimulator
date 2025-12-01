using System;
using System.Collections.Generic;
using PennantSimulator.Models;

namespace PennantSimulator.Core
{
    public class PlayByPlayEngine
    {
        private static Random _rng = new Random();

        public enum PlayOutcome
        {
            Single,
            Double,
            Triple,
            HomeRun,
            Walk,
            StrikeOut,
            GroundOut,
            FlyOut,
            PopOut,
            FieldersChoice,
            Error
        }

        public class PlayResult
        {
            public PlayOutcome Outcome { get; set; }
            public Player Batter { get; set; }
            public Player Pitcher { get; set; }
            public int RunsScored { get; set; }
            public int Outs { get; set; }
            public string Description { get; set; } = "";
            public List<string> BaserunnerActions { get; set; } = new List<string>();
        }

        public static PlayResult SimulatePlateAppearance(Player batter, Player pitcher)
        {
            var result = new PlayResult
            {
                Batter = batter,
                Pitcher = pitcher
            };

            // Calculate probabilities based on player skills
            double contactFactor = batter.Contact / 100.0;
            double powerFactor = batter.Power / 100.0;
            double pitchingFactor = pitcher.Control / 100.0;
            double staminaFactor = pitcher.CurrentStamina / 100.0;

            // Base probabilities
            double walkProb = 0.08 + (1.0 - pitchingFactor) * 0.05;
            double soProb = 0.20 + (1.0 - contactFactor) * 0.15 - (1.0 - pitchingFactor) * 0.05;
            double hrProb = 0.03 * powerFactor * (2.0 - pitchingFactor);
            double hitProb = 0.25 * contactFactor * (1.5 - pitchingFactor * 0.5);

            // Fatigue affects pitcher
            if (staminaFactor < 0.5)
            {
                walkProb *= 1.3;
                hitProb *= 1.2;
                hrProb *= 1.3;
            }

            double roll = _rng.NextDouble();
            double cumulative = 0;

            cumulative += walkProb;
            if (roll < cumulative)
            {
                result.Outcome = PlayOutcome.Walk;
                result.Description = $"{batter.Name} walks.";
                batter.Stats.Walks++;
                return result;
            }

            cumulative += soProb;
            if (roll < cumulative)
            {
                result.Outcome = PlayOutcome.StrikeOut;
                result.Outs = 1;
                result.Description = $"{batter.Name} strikes out swinging.";
                batter.Stats.AtBats++;
                batter.Stats.StrikeOuts++;
                return result;
            }

            cumulative += hrProb;
            if (roll < cumulative)
            {
                result.Outcome = PlayOutcome.HomeRun;
                result.RunsScored = 1; // Base runs, adjust for baserunners
                result.Description = $"{batter.Name} hits a home run!";
                batter.Stats.AtBats++;
                batter.Stats.Hits++;
                batter.Stats.HomeRuns++;
                batter.Stats.RBIs++;
                batter.Stats.Runs++;
                return result;
            }

            cumulative += hitProb;
            if (roll < cumulative)
            {
                // Determine hit type
                double hitRoll = _rng.NextDouble();
                if (hitRoll < 0.10)
                {
                    result.Outcome = PlayOutcome.Triple;
                    result.Description = $"{batter.Name} triples!";
                }
                else if (hitRoll < 0.30)
                {
                    result.Outcome = PlayOutcome.Double;
                    result.Description = $"{batter.Name} doubles!";
                }
                else
                {
                    result.Outcome = PlayOutcome.Single;
                    result.Description = $"{batter.Name} singles.";
                }
                batter.Stats.AtBats++;
                batter.Stats.Hits++;
                return result;
            }

            // Otherwise, it's an out
            double outRoll = _rng.NextDouble();
            if (outRoll < 0.5)
            {
                result.Outcome = PlayOutcome.GroundOut;
                result.Description = $"{batter.Name} grounds out.";
            }
            else if (outRoll < 0.9)
            {
                result.Outcome = PlayOutcome.FlyOut;
                result.Description = $"{batter.Name} flies out.";
            }
            else
            {
                result.Outcome = PlayOutcome.PopOut;
                result.Description = $"{batter.Name} pops out.";
            }

            result.Outs = 1;
            batter.Stats.AtBats++;
            return result;
        }

        public static string FormatPlayResult(PlayResult result)
        {
            var baseDesc = result.Description;
            if (result.RunsScored > 0)
                baseDesc += $" {result.RunsScored} run(s) score!";
            if (result.BaserunnerActions.Count > 0)
                baseDesc += " " + string.Join(", ", result.BaserunnerActions);
            return baseDesc;
        }
    }
}
