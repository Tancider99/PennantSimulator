using System;
using PennantSimulator.Core;

namespace PennantSimulator.UI
{
    public static class StandingsPrinter
    {
        public static void Print(League league)
        {
            Console.WriteLine("順位表:");
            Console.WriteLine("Pos | Team                 | W  | L  | T  | PCT");
            Console.WriteLine("----+----------------------+----+----+----+------");
            int pos = 1;
            foreach (var t in league.GetStandings())
            {
                Console.WriteLine($"{pos,3} | {t.Name,-20} | {t.Wins,2} | {t.Losses,2} | {t.Ties,2} | {t.WinPercentage,4:F3}");
                pos++;
            }
        }
    }
}
