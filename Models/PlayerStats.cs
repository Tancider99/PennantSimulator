namespace PennantSimulator.Models
{
    public class PlayerStats
    {
        // Batting stats
        public int AtBats { get; set; }
        public int Hits { get; set; }
        public int HomeRuns { get; set; }
        public int RBIs { get; set; }
        public int Walks { get; set; }
        public int StrikeOuts { get; set; }
        public int Runs { get; set; }
        public int Games { get; set; }
        public int Doubles { get; set; }
        public int Triples { get; set; }
        public int StolenBases { get; set; }

        // Pitching stats
        public int InningsPitched { get; set; } // In thirds (3 = 1 inning)
        public int RunsAllowed { get; set; }
        public int Wins { get; set; }
        public int Losses { get; set; }
        public int Saves { get; set; }
        public int PitcherStrikeOuts { get; set; }
        public int WalksAllowed { get; set; }
        public int HitsAllowed { get; set; }

        public void ResetStats()
        {
            AtBats = Hits = HomeRuns = RBIs = Walks = StrikeOuts = Runs = Games = 0;
            Doubles = Triples = StolenBases = 0;
            InningsPitched = RunsAllowed = Wins = Losses = Saves = 0;
            PitcherStrikeOuts = WalksAllowed = HitsAllowed = 0;
        }

        // Calculated stats
        public double BattingAverage => AtBats == 0 ? 0.0 : (double)Hits / AtBats;
        public double OnBasePercentage => (AtBats + Walks) == 0 ? 0.0 : (double)(Hits + Walks) / (AtBats + Walks);
        public double SluggingPercentage => AtBats == 0 ? 0.0 : (double)(Hits + Doubles + Triples * 2 + HomeRuns * 3) / AtBats;
        public double ERA => InningsPitched == 0 ? 0.0 : (RunsAllowed * 27.0) / InningsPitched;
        public double WHIP => InningsPitched == 0 ? 0.0 : (WalksAllowed + HitsAllowed) * 3.0 / InningsPitched;
    }
}
