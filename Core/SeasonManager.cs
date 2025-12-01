using System;
using System.Collections.Generic;
using System.Linq;
using PennantSimulator.Models;

namespace PennantSimulator.Core
{
    public class SeasonMatch
    {
        public Team Home { get; }
        public Team Away { get; }
        public bool Played { get; set; }

        public SeasonMatch(Team home, Team away)
        {
            Home = home;
            Away = away;
            Played = false;
        }
    }

    public class SeasonManager
    {
        public List<SeasonMatch> Matches { get; } = new List<SeasonMatch>();

        // Create a simple schedule by repeating unique pairs until each team reaches gamesPerTeam
        public static SeasonManager CreateSchedule(League league, int gamesPerTeam)
        {
            if (league == null) throw new ArgumentNullException(nameof(league));
            var mgr = new SeasonManager();
            var teams = league.Teams.ToList();
            int n = teams.Count;
            if (n < 2) return mgr;

            // all unique pairs
            var pairs = new List<(Team, Team)>();
            for (int i = 0; i < n; i++)
                for (int j = i + 1; j < n; j++)
                    pairs.Add((teams[i], teams[j]));

            var gamesScheduled = teams.ToDictionary(t => t, t => 0);
            int pairIndex = 0;
            while (gamesScheduled.Values.Any(v => v < gamesPerTeam))
            {
                var (a, b) = pairs[pairIndex];
                if (gamesScheduled[a] < gamesPerTeam || gamesScheduled[b] < gamesPerTeam)
                {
                    mgr.Matches.Add(new SeasonMatch(a, b));
                    gamesScheduled[a]++;
                    gamesScheduled[b]++;
                }
                pairIndex = (pairIndex + 1) % pairs.Count;
            }

            return mgr;
        }

        public SeasonMatch? GetNextMatchFor(Team team)
        {
            return Matches.FirstOrDefault(m => !m.Played && (m.Home == team || m.Away == team));
        }

        public void MarkPlayed(SeasonMatch match)
        {
            if (match == null) return;
            match.Played = true;
        }
    }
}
