using System;
using System.Linq;
using System.Threading.Tasks;
using System.Collections.Generic;
using PennantSimulator.Models;

namespace PennantSimulator.Core
{
    public class FullSeasonSimulator
    {
        public class SeasonSchedule
        {
            public List<ScheduledGame> Games { get; set; } = new List<ScheduledGame>();
            public int CurrentDay { get; set; } = 0;
        }

        public class ScheduledGame
        {
            public int Day { get; set; }
            public Team Home { get; set; }
            public Team Away { get; set; }
            public bool Completed { get; set; }
            public int HomeScore { get; set; }
            public int AwayScore { get; set; }
        }

        public static SeasonSchedule CreateSchedule(League league, int gamesPerTeam)
        {
            var schedule = new SeasonSchedule();
            var teams = league.Teams.ToList();
            int day = 1;

            // Simple round-robin scheduling
            int totalRounds = gamesPerTeam / (teams.Count - 1);
            
            for (int round = 0; round < totalRounds; round++)
            {
                for (int i = 0; i < teams.Count; i++)
                {
                    for (int j = i + 1; j < teams.Count; j++)
                    {
                        // Home/away alternates
                        if (round % 2 == 0)
                        {
                            schedule.Games.Add(new ScheduledGame
                            {
                                Day = day,
                                Home = teams[i],
                                Away = teams[j]
                            });
                        }
                        else
                        {
                            schedule.Games.Add(new ScheduledGame
                            {
                                Day = day,
                                Home = teams[j],
                                Away = teams[i]
                            });
                        }
                        day++;
                    }
                }
            }

            return schedule;
        }

        public static void SimulateDay(SeasonSchedule schedule, Action<ScheduledGame, DetailedGameEngine.DetailedGameResult> onGameComplete = null)
        {
            schedule.CurrentDay++;
            var todaysGames = schedule.Games.Where(g => g.Day == schedule.CurrentDay && !g.Completed).ToList();

            foreach (var game in todaysGames)
            {
                var result = DetailedGameEngine.SimulateDetailedGame(game.Home, game.Away);
                game.HomeScore = result.HomeScore;
                game.AwayScore = result.AwayScore;
                game.Completed = true;

                onGameComplete?.Invoke(game, result);
            }
        }

        public static async Task SimulateSeasonAsync(League league, int gamesPerTeam, 
            Action<int, int> progressCallback = null,
            Action<ScheduledGame, DetailedGameEngine.DetailedGameResult> onGameComplete = null)
        {
            var schedule = CreateSchedule(league, gamesPerTeam);
            int totalGames = schedule.Games.Count;
            int completed = 0;

            await Task.Run(() =>
            {
                while (schedule.CurrentDay < schedule.Games.Max(g => g.Day))
                {
                    SimulateDay(schedule, (game, result) =>
                    {
                        completed++;
                        progressCallback?.Invoke(completed, totalGames);
                        onGameComplete?.Invoke(game, result);
                    });
                }
            });
        }

        public static void SimulateSeasonFast(League league, int gamesPerTeam)
        {
            var schedule = CreateSchedule(league, gamesPerTeam);
            
            foreach (var game in schedule.Games)
            {
                var result = DetailedGameEngine.SimulateDetailedGame(game.Home, game.Away);
                game.HomeScore = result.HomeScore;
                game.AwayScore = result.AwayScore;
                game.Completed = true;
            }
        }
    }
}
