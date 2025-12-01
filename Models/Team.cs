using System.Collections.Generic;
using System.Linq;

namespace PennantSimulator.Models
{
    public class Team
    {
        public string Name { get; }
        public int Wins { get; set; }
        public int Losses { get; set; }
        public int Ties { get; set; }

        // Roster for future expansion. If empty, simulator will generate a default roster.
        public List<Player> Roster { get; } = new List<Player>();

        // Cash balance for the team (e.g., in yen/units)
        public double Cash { get; set; } = 1000000.0;

        // Draft picks held by the team
        public List<DraftPick> DraftPicks { get; } = new List<DraftPick>();

        public Team(string name)
        {
            Name = name;
        }

        public int GamesPlayed => Wins + Losses + Ties;

        public double WinPercentage => GamesPlayed == 0 ? 0.0 : (double)Wins / GamesPlayed;

        public void RecordWin() => Wins++;
        public void RecordLoss() => Losses++;
        public void RecordTie() => Ties++;

        // Average skill across roster (0-100). If no players, default to 50.
        public double Rating
        {
            get
            {
                if (Roster == null || Roster.Count == 0) return 50.0;
                return Roster.Average(p => p.OverallSkill);
            }
        }

        // Team batting rating (average of player batting skills)
        public double BattingRating
        {
            get
            {
                if (Roster == null || Roster.Count == 0) return 50.0;
                return Roster.Average(p => p.BattingSkill);
            }
        }

        // Team pitching rating (average of player pitching skills)
        public double PitchingRating
        {
            get
            {
                if (Roster == null || Roster.Count == 0) return 50.0;
                return Roster.Average(p => p.PitchingSkill);
            }
        }

        // Helper to add a draft pick
        public void AddPick(DraftPick pick)
        {
            if (pick == null) return;
            DraftPicks.Add(pick);
        }

        // Helper to remove a draft pick
        public bool RemovePick(DraftPick pick)
        {
            if (pick == null) return false;
            return DraftPicks.Remove(pick);
        }
    }
}
