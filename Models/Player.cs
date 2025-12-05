using System;

namespace PennantSimulator.Models
{
    public enum Position
    {
        Pitcher,
        Catcher,
        FirstBase,
        SecondBase,
        ThirdBase,
        ShortStop,
        LeftField,
        CenterField,
        RightField,
        DesignatedHitter,
        Unknown
    }

    /// <summary>
    /// 投手の役割適性
    /// </summary>
    public enum PitcherRole
    {
        Starter,    // 先発
        Middle,     // 中継ぎ
        Closer      // 抑え
    }

    public class Player
    {
        public string Name { get; set; }
        // Power Pro style attributes (0-100)
        public int Contact { get; set; }    // ミート
        public int Power { get; set; }      // パワー
        public int Speed { get; set; }      // 走力
        public int Arm { get; set; }        // 肩力
        public int Defense { get; set; }    // 守備

        // Pitching-specific
        public int Stamina { get; set; }    // スタミナ (base)
        public int Control { get; set; }    // コントロール
        public int Breaking { get; set; }   // 変化球

        // 投手適性 (0-100): 各役割への適性度
        public int StarterAptitude { get; set; } = 50;  // 先発適性
        public int MiddleAptitude { get; set; } = 50;   // 中継ぎ適性
        public int CloserAptitude { get; set; } = 50;   // 抑え適性
        
        // 投手の推奨役割（最も適性が高い役割）
        public PitcherRole PreferredPitcherRole
        {
            get
            {
                if (StarterAptitude >= MiddleAptitude && StarterAptitude >= CloserAptitude)
                    return PitcherRole.Starter;
                if (CloserAptitude >= MiddleAptitude)
                    return PitcherRole.Closer;
                return PitcherRole.Middle;
            }
        }

        // New RPG-like attributes
        public Position PreferredPosition { get; set; } = Position.Unknown;
        public int Age { get; set; } = 20;
        public int Experience { get; set; } = 0; // general XP
        public int Morale { get; set; } = 50; // 0-100

        // Current stamina in-season (can deplete)
        public int CurrentStamina { get; set; }

        // Injury flag
        public bool IsInjured { get; set; } = false;

        public Player(string name, int contact, int power, int speed, int arm, int defense, int stamina = 50, int control = 50, int breaking = 50,
            int starterAptitude = 50, int middleAptitude = 50, int closerAptitude = 50)
        {
            Name = name;
            Contact = contact;
            Power = power;
            Speed = speed;
            Arm = arm;
            Defense = defense;
            Stamina = stamina;
            Control = control;
            Breaking = breaking;
            StarterAptitude = starterAptitude;
            MiddleAptitude = middleAptitude;
            CloserAptitude = closerAptitude;
            Stats = new PlayerStats();
            CurrentStamina = stamina;
        }

        // Convenience constructor: set all primary attributes to overall
        public Player(string name, int overall)
            : this(name, overall, overall, overall, overall, overall, overall, overall, overall)
        {
        }

        // Batting skill (重み付け): ミートとパワーを重視
        public double BattingSkill => Contact * 0.65 + Power * 0.35;

        // Pitching skill: スタミナ/コントロール/変化球
        public double PitchingSkill => Stamina * 0.4 + Control * 0.4 + Breaking * 0.2;

        // Fielding skill: 守備/肩/走力
        public double FieldingSkill => Defense * 0.5 + Arm * 0.3 + Speed * 0.2;

        // Overall used for team rating (simple average of subsystems)
        public double OverallSkill => (BattingSkill + PitchingSkill + FieldingSkill) / 3.0;

        // Seasonal stats
        public PlayerStats Stats { get; set; }

        public void ResetStats()
        {
            Stats = new PlayerStats();
            CurrentStamina = Stamina;
            IsInjured = false;
            Morale = 50;
            Experience = 0;
        }

        // Apply fatigue after playing some innings or games
        public void ApplyFatigue(int amount)
        {
            CurrentStamina = Math.Max(0, CurrentStamina - amount);
            if (CurrentStamina < 10)
            {
                // increased injury chance handled by higher-level logic
                Morale = Math.Max(0, Morale - 5);
            }
        }

        // Recover stamina during rest/training
        public void Recover(int amount)
        {
            CurrentStamina = Math.Min(100, CurrentStamina + amount);
            Morale = Math.Min(100, Morale + 1);
        }

        // Gain experience and possibly increase attributes slightly
        public void GainExperience(int xp)
        {
            Experience += xp;
            // simple leveling: every 100 xp gives small improvements
            while (Experience >= 100)
            {
                Experience -= 100;
                LevelUpRandom();
            }
        }

        private void LevelUpRandom()
        {
            var rnd = new Random();
            int which = rnd.Next(6);
            int delta = rnd.Next(1, 4);
            switch (which)
            {
                case 0: Contact = Math.Min(100, Contact + delta); break;
                case 1: Power = Math.Min(100, Power + delta); break;
                case 2: Speed = Math.Min(100, Speed + delta); break;
                case 3: Defense = Math.Min(100, Defense + delta); break;
                case 4: Stamina = Math.Min(100, Stamina + delta); CurrentStamina = Math.Min(100, CurrentStamina + delta); break;
                case 5: Control = Math.Min(100, Control + delta); break;
            }
            // morale bump
            Morale = Math.Min(100, Morale + 3);
        }

        // Batting average
        public double GetBattingAverage()
        {
            return Stats.AtBats == 0 ? 0.0 : (double)Stats.Hits / Stats.AtBats;
        }

        // ERA calculation (simplified)
        public double GetERA()
        {
            // Using games as proxy for innings pitched
            return Stats.Games == 0 ? 0.0 : (Stats.RunsAllowed * 9.0) / Stats.Games;
        }
    }
}
