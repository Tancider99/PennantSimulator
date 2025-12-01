using System.Collections.Generic;
using System.Linq;
using PennantSimulator.Models;

namespace PennantSimulator.Core
{
    public class League
    {
        public List<Team> Teams { get; set; }

        public League()
        {
            Teams = new List<Team>();
        }

        public League(IEnumerable<Team> teams)
        {
            Teams = teams.ToList();
        }

        public void ResetStandings()
        {
            foreach (var t in Teams)
            {
                t.Wins = 0;
                t.Losses = 0;
                t.Ties = 0;
            }
        }

        public IEnumerable<Team> GetStandings()
        {
            return Teams.OrderByDescending(t => t.Wins)
                        .ThenBy(t => t.Losses)
                        .ThenByDescending(t => t.WinPercentage);
        }
    }
}
