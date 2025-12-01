using System;
using System.Collections.Generic;
using System.Linq;
using PennantSimulator.Models;

namespace PennantSimulator.Core
{
    public static class SeasonSimulator
    {
        private static Random _rng = new Random();

        // Simulate a simple season where each team plays `gamesPerTeam` games.
        public static void Simulate(League league, int gamesPerTeam = 143)
        {
            league.ResetStandings();
            var teams = league.Teams;
            int n = teams.Count;

            if (n < 2) return;

            // reset player stats
            foreach (var t in teams)
            {
                foreach (var p in t.Roster) p.ResetStats();
            }

            // Build a simple round-robin schedule list of pairs and repeat until each team reaches gamesPerTeam
            var gamesScheduled = new Dictionary<Team, int>();
            foreach (var t in teams) gamesScheduled[t] = 0;

            // precompute all unique pairs
            var pairs = new List<(Team, Team)>();
            for (int i = 0; i < n; i++)
                for (int j = i + 1; j < n; j++)
                    pairs.Add((teams[i], teams[j]));

            int pairIndex = 0;
            while (true)
            {
                // pick next pair
                var (a, b) = pairs[pairIndex];
                if (gamesScheduled[a] >= gamesPerTeam && gamesScheduled[b] >= gamesPerTeam)
                {
                    // if all teams satisfied, break
                    bool allDone = true;
                    foreach (var t in teams) if (gamesScheduled[t] < gamesPerTeam) { allDone = false; break; }
                    if (allDone) break;
                }

                // only play if both teams still need games
                if (gamesScheduled[a] < gamesPerTeam || gamesScheduled[b] < gamesPerTeam)
                {
                    var result = SimulateGameResult(a, b);
                    ApplyGameResult(a, b, result);
                    // update basic player stats for both teams
                    UpdatePlayerStatsForGame(a, result.RunsA, result.RunsB);
                    UpdatePlayerStatsForGame(b, result.RunsB, result.RunsA);

                    gamesScheduled[a]++;
                    gamesScheduled[b]++;
                }

                pairIndex = (pairIndex + 1) % pairs.Count;
            }
        }

        private static void UpdatePlayerStatsForGame(Team team, int teamRuns, int oppRuns)
        {
            if (team == null || team.Roster == null || team.Roster.Count == 0) return;

            int batters = Math.Min(9, team.Roster.Count);
            for (int i = 0; i < batters; i++)
            {
                var p = team.Roster[i];
                // simulate 3-5 plate appearances
                int pas = _rng.Next(3, 6);
                for (int pa = 0; pa < pas; pa++)
                {
                    double walkProb = 0.07 + (p.Contact - 50) / 1000.0; // small modifier
                    double soProb = 0.18 - (p.Contact - 50) / 1200.0;
                    double hrProb = 0.02 + (p.Power - 50) / 1200.0;
                    double hitProb = 0.13 + (p.Contact - 50) / 600.0;

                    // slightly bias results if the team scored many runs
                    double teamBump = Math.Min(0.1, teamRuns / 10.0);

                    double r = _rng.NextDouble();
                    if (r < walkProb + teamBump * 0.3)
                    {
                        p.Stats.Walks++;
                        p.Stats.Runs += 0;
                    }
                    else
                    {
                        p.Stats.AtBats++;
                        if (r < walkProb + hrProb + teamBump * 0.1)
                        {
                            p.Stats.Hits++;
                            p.Stats.HomeRuns++;
                            p.Stats.Runs += 1;
                            p.Stats.RBIs += _rng.Next(1, 3);
                        }
                        else if (r < walkProb + hrProb + hitProb + teamBump * 0.4)
                        {
                            p.Stats.Hits++;
                            // random RBI chance
                            if (_rng.NextDouble() < 0.25 + teamBump * 0.5) p.Stats.RBIs++;
                            if (_rng.NextDouble() < 0.2 + teamBump * 0.3) p.Stats.Runs++;
                        }
                        else
                        {
                            p.Stats.StrikeOuts++;
                        }
                    }
                }
            }
        }

        // Public method to simulate a single game between two teams (useful for manager actions)
        public static GameResult SimulateSingleGame(Team a, Team b)
        {
            if (a == null || b == null) return null;
            var result = SimulateGameResult(a, b);
            ApplyGameResult(a, b, result);
            UpdatePlayerStatsForGame(a, result.RunsA, result.RunsB);
            UpdatePlayerStatsForGame(b, result.RunsB, result.RunsA);
            return result;
        }

        // Simulate a game's numerical result without applying to standings
        // This version uses team batting/pitching ratings and resolves ties with extra innings (no ties).
        public static GameResult SimulateGameResult(Team a, Team b)
        {
            // use batting vs pitching to compute expected runs
            double offenseA = a.BattingRating;
            double offenseB = b.BattingRating;
            double defenseA = a.PitchingRating;
            double defenseB = b.PitchingRating;

            double baseRuns = 3.8;

            // scale expectations by relative offense/defense. Values around 50 produce baseRuns.
            double expA = baseRuns * (1.0 + (offenseA - defenseB) / 150.0);
            double expB = baseRuns * (1.0 + (offenseB - defenseA) / 150.0);

            // variance increases when mismatch is large (more blowouts possible)
            double stdA = 1.2 + Math.Abs(offenseA - defenseB) / 40.0;
            double stdB = 1.2 + Math.Abs(offenseB - defenseA) / 40.0;

            int runsA = Math.Max(0, (int)Math.Round(SampleNormal(expA, stdA)));
            int runsB = Math.Max(0, (int)Math.Round(SampleNormal(expB, stdB)));

            // If tie, simulate extra innings until a winner is decided.
            if (runsA == runsB)
            {
                // compute a small expected runs per extra inning using the same matchup
                double extraLambdaA = Math.Max(0.05, expA / 9.0);
                double extraLambdaB = Math.Max(0.05, expB / 9.0);

                // play inning by inning
                while (true)
                {
                    int eA = SamplePoisson(extraLambdaA);
                    int eB = SamplePoisson(extraLambdaB);
                    runsA += eA;
                    runsB += eB;
                    if (runsA != runsB) break;
                }
            }

            return new GameResult { RunsA = runsA, RunsB = runsB };
        }

        private static void ApplyGameResult(Team a, Team b, GameResult result)
        {
            if (result.RunsA > result.RunsB)
            {
                a.RecordWin();
                b.RecordLoss();
            }
            else if (result.RunsB > result.RunsA)
            {
                b.RecordWin();
                a.RecordLoss();
            }
            else
            {
                a.RecordTie();
                b.RecordTie();
            }
        }

        // Box-Muller to get normal sample
        private static double SampleNormal(double mean, double stddev)
        {
            // generate two uniforms
            double u1 = 1.0 - _rng.NextDouble();
            double u2 = 1.0 - _rng.NextDouble();
            double randStdNormal = Math.Sqrt(-2.0 * Math.Log(u1)) * Math.Sin(2.0 * Math.PI * u2);
            return mean + stddev * randStdNormal;
        }

        // Simple Poisson sampler for small lambda (Knuth's algorithm)
        private static int SamplePoisson(double lambda)
        {
            if (lambda <= 0) return 0;
            double l = Math.Exp(-lambda);
            int k = 0;
            double p = 1.0;
            while (p > l)
            {
                k++;
                p *= _rng.NextDouble();
                // safety guard
                if (k > 1000) break;
            }
            return k - 1;
        }
    }
}
