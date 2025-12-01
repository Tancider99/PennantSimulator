namespace PennantSimulator.Models
{
    public class DraftPick
    {
        // simple representation: round and overall pick number (1-based)
        public int Round { get; set; }
        public int Overall { get; set; }

        public DraftPick(int round, int overall)
        {
            Round = round;
            Overall = overall;
        }

        public override string ToString()
        {
            return $"R{Round}-P{Overall}";
        }
    }
}
