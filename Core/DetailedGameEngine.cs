using System;
using System.Collections.Generic;
using System.Linq;
using PennantSimulator.Models;

namespace PennantSimulator.Core
{
    public class DetailedGameEngine
    {
        private static Random _rng = new Random();

        public class InningResult
        {
            public int Runs { get; set; }
            public int Hits { get; set; }
            public List<string> Events { get; set; } = new List<string>();
        }

        public class DetailedGameResult
        {
            public Team HomeTeam { get; set; }
            public Team AwayTeam { get; set; }
            public int HomeScore { get; set; }
            public int AwayScore { get; set; }
            public List<InningResult> InningResults { get; set; } = new List<InningResult>();
            public List<string> Highlights { get; set; } = new List<string>();
            public Player WinningPitcher { get; set; }
            public Player LosingPitcher { get; set; }
        }

        public static DetailedGameResult SimulateDetailedGame(Team home, Team away)
        {
            var result = new DetailedGameResult
            {
                HomeTeam = home,
                AwayTeam = away
            };

            // Select starting pitchers (best pitching skill)
            var homePitcher = home.Roster.OrderByDescending(p => p.PitchingSkill).FirstOrDefault();
            var awayPitcher = away.Roster.OrderByDescending(p => p.PitchingSkill).FirstOrDefault();

            if (homePitcher == null || awayPitcher == null) return result;

            int[] scores = new int[2]; // 0: Away, 1: Home
            int inning = 1;

            // Play 9 innings (or extra if tied)
            while (inning <= 9 || (inning <= 12 && scores[0] == scores[1]))
            {
                // Top half (away bats)
                var topResult = SimulateHalfInning(away, home, homePitcher, inning, true);
                scores[0] += topResult.Runs;
                result.InningResults.Add(topResult);
                result.Highlights.AddRange(topResult.Events);

                // Bottom half (home bats) - skip if home is winning in bottom of 9th or later
                if (inning >= 9 && scores[1] > scores[0]) break;

                var bottomResult = SimulateHalfInning(home, away, awayPitcher, inning, false);
                scores[1] += bottomResult.Runs;
                result.InningResults.Add(bottomResult);
                result.Highlights.AddRange(bottomResult.Events);

                // Sayonara check
                if (inning >= 9 && scores[1] > scores[0]) break;

                inning++;
            }

            result.HomeScore = scores[1];
            result.AwayScore = scores[0];

            // Determine winner and update stats
            if (scores[1] > scores[0])
            {
                homePitcher.Stats.Wins++;
                awayPitcher.Stats.Losses++;
                home.RecordWin();
                away.RecordLoss();
                result.WinningPitcher = homePitcher;
                result.LosingPitcher = awayPitcher;
            }
            else if (scores[0] > scores[1])
            {
                awayPitcher.Stats.Wins++;
                homePitcher.Stats.Losses++;
                away.RecordWin();
                home.RecordLoss();
                result.WinningPitcher = awayPitcher;
                result.LosingPitcher = homePitcher;
            }
            else
            {
                home.RecordTie();
                away.RecordTie();
            }

            return result;
        }

        private static InningResult SimulateHalfInning(Team offense, Team defense, Player pitcher, int inning, bool isTop)
        {
            var result = new InningResult();
            int outs = 0;
            int runs = 0;
            int hits = 0;
            List<int> runners = new List<int>(); // Base positions (1, 2, 3)

            // Get batting lineup
            var lineup = offense.Roster.Take(9).ToList();
            int batterIdx = (inning - 1) % 9;

            while (outs < 3)
            {
                var batter = lineup[batterIdx];
                batter.Stats.AtBats++;
                batter.Stats.Games = 1; // Mark as played

                // Simulate plate appearance
                var outcome = SimulatePlateAppearance(batter, pitcher);

                switch (outcome)
                {
                    case "HomeRun":
                        batter.Stats.Hits++;
                        batter.Stats.HomeRuns++;
                        int rbi = 1 + runners.Count;
                        batter.Stats.RBIs += rbi;
                        batter.Stats.Runs++;
                        runs += rbi;
                        hits++;
                        pitcher.Stats.RunsAllowed += rbi;
                        pitcher.Stats.HitsAllowed++;
                        runners.Clear();
                        result.Events.Add($"{inning}回{(isTop ? "表" : "裏")}: {batter.Name} {rbi}ランホームラン！");
                        break;

                    case "Triple":
                        batter.Stats.Hits++;
                        batter.Stats.Triples++;
                        runs += runners.Count;
                        batter.Stats.RBIs += runners.Count;
                        hits++;
                        pitcher.Stats.RunsAllowed += runners.Count;
                        pitcher.Stats.HitsAllowed++;
                        runners.Clear();
                        runners.Add(3);
                        break;

                    case "Double":
                        batter.Stats.Hits++;
                        batter.Stats.Doubles++;
                        int scoredOnDouble = runners.Count(r => r >= 2);
                        runs += scoredOnDouble;
                        batter.Stats.RBIs += scoredOnDouble;
                        hits++;
                        pitcher.Stats.RunsAllowed += scoredOnDouble;
                        pitcher.Stats.HitsAllowed++;
                        runners = runners.Where(r => r < 2).Select(r => r + 2).ToList();
                        runners.Add(2);
                        break;

                    case "Single":
                        batter.Stats.Hits++;
                        int scoredOnSingle = runners.Count(r => r >= 2);
                        runs += scoredOnSingle;
                        batter.Stats.RBIs += scoredOnSingle;
                        hits++;
                        pitcher.Stats.RunsAllowed += scoredOnSingle;
                        pitcher.Stats.HitsAllowed++;
                        runners = runners.Where(r => r < 2).Select(r => r + 1).ToList();
                        runners.Add(1);
                        break;

                    case "Walk":
                        batter.Stats.Walks++;
                        pitcher.Stats.WalksAllowed++;
                        // Force runners forward
                        if (runners.Contains(1))
                        {
                            if (runners.Contains(2))
                            {
                                if (runners.Contains(3))
                                {
                                    runs++;
                                    batter.Stats.RBIs++;
                                }
                                else
                                {
                                    runners.Add(3);
                                }
                            }
                            else
                            {
                                runners.Add(2);
                            }
                        }
                        runners.Add(1);
                        break;

                    case "StrikeOut":
                        outs++;
                        batter.Stats.StrikeOuts++;
                        pitcher.Stats.PitcherStrikeOuts++;
                        pitcher.Stats.InningsPitched++;
                        break;

                    default: // Out
                        outs++;
                        pitcher.Stats.InningsPitched++;
                        break;
                }

                batterIdx = (batterIdx + 1) % 9;
            }

            result.Runs = runs;
            result.Hits = hits;
            return result;
        }

        private static string SimulatePlateAppearance(Player batter, Player pitcher)
        {
            // Calculate outcome probabilities based on player skills
            double batterScore = (batter.Contact * 0.6 + batter.Power * 0.4) + _rng.Next(0, 50);
            double pitcherScore = (pitcher.Control * 0.5 + pitcher.Stamina * 0.3 + pitcher.Breaking * 0.2) + _rng.Next(0, 50);

            double diff = batterScore - pitcherScore;

            if (diff > 50) return "HomeRun";
            if (diff > 40) return _rng.NextDouble() < 0.3 ? "Triple" : "Double";
            if (diff > 30) return _rng.NextDouble() < 0.5 ? "Double" : "Single";
            if (diff > 10) return "Single";
            if (diff > 0) return _rng.NextDouble() < 0.5 ? "Single" : "Out";
            if (diff > -20) return "Out";
            if (diff > -40) return "StrikeOut";
            return _rng.NextDouble() < 0.2 ? "Walk" : "StrikeOut";
        }
    }
}
