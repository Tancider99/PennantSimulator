using System;
using PennantSimulator.Models;
using PennantSimulator.Core;

namespace PennantSimulator.UI
{
    public static class ProgramBootstrap
    {
        public static League CreateLeague()
        {
            var teams = new[] {
                new Team("Tokyo Tigers"),
                new Team("Osaka Dragons"),
                new Team("Yokohama Marina"),
                new Team("Sapporo Snow"),
                new Team("Fukuoka Falcons"),
                new Team("Nagoya Knights")
            };

            // generate some dummy roster data to make ratings varied
            var rng = new Random();
            foreach (var team in teams)
            {
                for (int i = 0; i < 25; i++)
                {
                    int overall = rng.Next(40, 91); // players between 40 and 90
                    // map overall to detailed stats with some randomness
                    int contact = Math.Min(100, Math.Max(1, overall + rng.Next(-10, 11)));
                    int power = Math.Min(100, Math.Max(1, overall + rng.Next(-15, 16)));
                    int speed = Math.Min(100, Math.Max(1, overall + rng.Next(-20, 21)));
                    int arm = Math.Min(100, Math.Max(1, overall + rng.Next(-20, 21)));
                    int defense = Math.Min(100, Math.Max(1, overall + rng.Next(-20, 21)));
                    int stamina = Math.Min(100, Math.Max(1, overall + rng.Next(-20, 21)));
                    int control = Math.Min(100, Math.Max(1, overall + rng.Next(-20, 21)));
                    int breaking = Math.Min(100, Math.Max(1, overall + rng.Next(-20, 21)));

                    var p = new Player($"{team.Name}_P{i+1}", contact, power, speed, arm, defense, stamina, control, breaking);
                    team.Roster.Add(p);
                }
            }

            var league = new League(teams);
            return league;
        }

        public static MainForm CreateMainForm()
        {
            var league = CreateLeague();
            return new MainForm(league);
        }

        public static MainForm CreateMainForm(League league, int initialTeamIndex = 0, bool startManager = false, int gamesPerTeam = 143)
        {
            return new MainForm(league, initialTeamIndex, startManager, gamesPerTeam);
        }
    }
}
