using System;
using System.Collections.Generic;
using System.Linq;
using PennantSimulator.Models;

namespace PennantSimulator.Core
{
    public class GameState
    {
        public Team Home { get; }
        public Team Away { get; }

        private Random _rng = new Random();

        public List<int> HomeRuns { get; } = new List<int>();
        public List<int> AwayRuns { get; } = new List<int>();

        public int Inning { get; private set; } = 1; // 1-based
        public bool TopOfInning { get; private set; } = true; // true = top, away bats
        public bool Finished { get; private set; } = false;

        public GameState(Team home, Team away)
        {
            Home = home ?? throw new ArgumentNullException(nameof(home));
            Away = away ?? throw new ArgumentNullException(nameof(away));
        }

        public (int runsThisHalf, string summary) PlayNextHalf()
        {
            if (Finished) throw new InvalidOperationException("Game already finished");

            double offense = TopOfInning ? Away.BattingRating : Home.BattingRating;
            double defense = TopOfInning ? Home.PitchingRating : Away.PitchingRating;

            double baseRuns = 3.8;
            double expRuns = baseRuns * (1.0 + (offense - defense) / 150.0);
            // per-half-inning lambda
            double lambda = Math.Max(0.01, expRuns / 9.0);

            int runs = SamplePoisson(lambda);

            if (TopOfInning)
            {
                AwayRuns.Add(runs);
            }
            else
            {
                HomeRuns.Add(runs);
            }

            string summary = TopOfInning
                ? $"Top {Inning}: {Away.Name} scored {runs}"
                : $"Bottom {Inning}: {Home.Name} scored {runs}";

            // advance inning/half
            if (!TopOfInning)
            {
                // completed both halves of this inning
                // check for end condition (9+ innings and not tied) or if before 9th and any team leads after bottom
                int totalHome = HomeRuns.Sum();
                int totalAway = AwayRuns.Sum();

                if (Inning >= 9 && totalHome != totalAway)
                {
                    Finished = true;
                }
                else if (Inning < 9)
                {
                    // after bottom of inning before 9th, game continues normally
                    // no early termination logic needed in our simplified sim
                }

                Inning++;
                TopOfInning = true;
            }
            else
            {
                TopOfInning = false;
            }

            // If finished because winner decided in the bottom, mark finished. Otherwise, if game tied after a completed 9th, it will continue next halves.
            // Extra innings will be handled by continuing PlayNextHalf calls until Finished is set.

            return (runs, summary);
        }

        public (int home, int away) GetScore()
        {
            return (HomeRuns.Sum(), AwayRuns.Sum());
        }

        public void ApplyResultToTeams()
        {
            var (home, away) = GetScore();
            if (home > away)
            {
                Home.RecordWin();
                Away.RecordLoss();
            }
            else if (away > home)
            {
                Away.RecordWin();
                Home.RecordLoss();
            }
            else
            {
                Home.RecordTie();
                Away.RecordTie();
            }
        }

        // Knuth poisson sampler (suitable for small lambda)
        private int SamplePoisson(double lambda)
        {
            if (lambda <= 0) return 0;
            double l = Math.Exp(-lambda);
            int k = 0;
            double p = 1.0;
            while (p > l)
            {
                k++;
                p *= _rng.NextDouble();
                if (k > 10000) break;
            }
            return k - 1;
        }
    }
}
