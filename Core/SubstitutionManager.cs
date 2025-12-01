using System;
using System.Collections.Generic;
using System.Linq;
using PennantSimulator.Models;

namespace PennantSimulator.Core
{
    public class SubstitutionManager
    {
        public class LineupSlot
        {
            public int Order { get; set; } // 1-9 for batting order
            public Player Player { get; set; }
            public Position FieldPosition { get; set; }
            public bool HasBatted { get; set; }
        }

        private List<LineupSlot> _lineup = new List<LineupSlot>();
        private List<Player> _bench = new List<Player>();
        private Player? _currentPitcher;
        private int _pitcherPitchCount = 0;

        public SubstitutionManager(Team team)
        {
            InitializeLineup(team);
        }

        private void InitializeLineup(Team team)
        {
            _lineup.Clear();
            _bench.Clear();

            // First 9 players are starters
            for (int i = 0; i < Math.Min(9, team.Roster.Count); i++)
            {
                _lineup.Add(new LineupSlot
                {
                    Order = i + 1,
                    Player = team.Roster[i],
                    FieldPosition = DeterminePosition(i),
                    HasBatted = false
                });
            }

            // Rest go to bench
            for (int i = 9; i < team.Roster.Count; i++)
            {
                _bench.Add(team.Roster[i]);
            }

            // Set starting pitcher (player with highest pitching skill)
            _currentPitcher = team.Roster.OrderByDescending(p => p.PitchingSkill).FirstOrDefault();
        }

        private Position DeterminePosition(int order)
        {
            return order switch
            {
                0 => Position.Pitcher,
                1 => Position.Catcher,
                2 => Position.FirstBase,
                3 => Position.SecondBase,
                4 => Position.ThirdBase,
                5 => Position.ShortStop,
                6 => Position.LeftField,
                7 => Position.CenterField,
                8 => Position.RightField,
                _ => Position.Unknown
            };
        }

        public bool SubstituteBatter(int lineupPosition, Player newPlayer)
        {
            if (lineupPosition < 1 || lineupPosition > 9) return false;
            
            var slot = _lineup.FirstOrDefault(s => s.Order == lineupPosition);
            if (slot == null) return false;

            var oldPlayer = slot.Player;
            slot.Player = newPlayer;
            slot.HasBatted = false;

            // Move old player to bench
            if (!_bench.Contains(oldPlayer))
                _bench.Add(oldPlayer);

            // Remove new player from bench
            _bench.Remove(newPlayer);

            return true;
        }

        public bool ChangePitcher(Player newPitcher)
        {
            if (newPitcher == null) return false;

            var oldPitcher = _currentPitcher;
            _currentPitcher = newPitcher;
            _pitcherPitchCount = 0;

            // Handle lineup changes
            _bench.Remove(newPitcher);
            if (oldPitcher != null && !_bench.Contains(oldPitcher))
                _bench.Add(oldPitcher);

            return true;
        }

        public void RecordPitch()
        {
            _pitcherPitchCount++;
        }

        public bool ShouldConsiderPitcherChange()
        {
            if (_currentPitcher == null) return false;

            // Consider change if:
            // - High pitch count (100+)
            // - Low stamina
            // - Poor performance (not implemented here)
            
            if (_pitcherPitchCount > 100) return true;
            if (_currentPitcher.CurrentStamina < 30) return true;

            return false;
        }

        public Player? CurrentPitcher => _currentPitcher;
        public int PitchCount => _pitcherPitchCount;
        public IReadOnlyList<LineupSlot> Lineup => _lineup.AsReadOnly();
        public IReadOnlyList<Player> Bench => _bench.AsReadOnly();
    }
}
