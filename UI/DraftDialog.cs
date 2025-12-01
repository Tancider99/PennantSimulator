using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using PennantSimulator.Models;
using PennantSimulator.Core;

namespace PennantSimulator.UI
{
    public class DraftDialog : Form
    {
        private League _league;
        private ListBox _available;
        private ComboBox _teamBox;
        private Button _draftButton;
        private NumericUpDown _buyUpAmount;

        // simple pool of prospects
        private List<Player> _prospects = new List<Player>();

        public DraftDialog(League league)
        {
            _league = league;
            Text = "Draft Prospects";
            Width = 640;
            Height = 520;
            StartPosition = FormStartPosition.CenterParent;

            var main = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 2 };
            main.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 65));
            main.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 35));
            Controls.Add(main);

            _available = new ListBox { Dock = DockStyle.Fill, Font = new Font("Consolas", 10) };
            var rightPanel = new Panel { Dock = DockStyle.Fill, Padding = new Padding(8) };
            main.Controls.Add(_available, 0, 0);
            main.Controls.Add(rightPanel, 1, 0);

            _teamBox = new ComboBox { Dock = DockStyle.Top, DropDownStyle = ComboBoxStyle.DropDownList };
            foreach (var t in _league.Teams) _teamBox.Items.Add(t.Name);
            _teamBox.SelectedIndex = 0;
            rightPanel.Controls.Add(_teamBox);

            var lblBuy = new Label { Text = "Spend cash to move a prospect up (bid)", Dock = DockStyle.Top, Height = 28 };
            _buyUpAmount = new NumericUpDown { Minimum = 0, Maximum = 1000000, Increment = 10000, Dock = DockStyle.Top, Value = 0 };
            rightPanel.Controls.Add(lblBuy);
            rightPanel.Controls.Add(_buyUpAmount);

            _draftButton = new Button { Text = "Draft Selected", Dock = DockStyle.Bottom, Height = 40, BackColor = Color.FromArgb(0, 123, 255), ForeColor = Color.White };
            _draftButton.Click += DraftButton_Click;
            rightPanel.Controls.Add(_draftButton);

            // generate prospects
            GenerateProspects();
            // initialize basic picks: 1 round, pick order by current standings reverse
            InitializePicks();
            RefreshList();
        }

        private void InitializePicks()
        {
            // Simple one-round draft, overall pick = team position (1 = worst team)
            var ordered = _league.Teams.OrderBy(t => t.WinPercentage).ToList();
            for (int i = 0; i < ordered.Count; i++)
            {
                var team = ordered[i];
                team.DraftPicks.Clear();
                team.AddPick(new DraftPick(1, i + 1));
            }
        }

        private void GenerateProspects()
        {
            var rng = new Random();
            _prospects.Clear();
            for (int i = 0; i < 50; i++)
            {
                int ovr = rng.Next(30, 86);
                int contact = Math.Min(100, Math.Max(1, ovr + rng.Next(-15, 16)));
                int power = Math.Min(100, Math.Max(1, ovr + rng.Next(-20, 21)));
                int speed = Math.Min(100, Math.Max(1, ovr + rng.Next(-25, 26)));
                int arm = Math.Min(100, Math.Max(1, ovr + rng.Next(-25, 26)));
                int defense = Math.Min(100, Math.Max(1, ovr + rng.Next(-25, 26)));
                int stamina = Math.Min(100, Math.Max(1, ovr + rng.Next(-25, 26)));
                int control = Math.Min(100, Math.Max(1, ovr + rng.Next(-25, 26)));
                int breaking = Math.Min(100, Math.Max(1, ovr + rng.Next(-25, 26)));
                var p = new Player($"Prospect_{i+1}", contact, power, speed, arm, defense, stamina, control, breaking);
                _prospects.Add(p);
            }
        }

        private void RefreshList()
        {
            _available.Items.Clear();
            foreach (var p in _prospects.OrderByDescending(x => x.OverallSkill))
            {
                _available.Items.Add($"{p.Name}  O:{p.OverallSkill:F0}  C:{p.Contact} P:{p.Power} STA:{p.Stamina}");
            }
        }

        private void DraftButton_Click(object? sender, EventArgs e)
        {
            if (_teamBox.SelectedIndex < 0 || _available.SelectedIndex < 0) return;
            var team = _league.Teams[_teamBox.SelectedIndex];

            // handle buy-up: if team chooses to spend cash, they can purchase the prospect to top of list
            decimal bid = _buyUpAmount.Value;
            var chosen = _prospects.OrderByDescending(p => p.OverallSkill).ToList()[_available.SelectedIndex];

            if (bid > 0)
            {
                if (team.Cash < (double)bid)
                {
                    MessageBox.Show(this, "Not enough cash.", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return;
                }

                // deduct cash and move prospect to front of list
                team.Cash -= (double)bid;
                // crude mechanism: increase prospect OverallSkill by tiny amount so they sort higher
                // (in real system, an auction would be better)
                // we'll just remove and reinsert at top
                _prospects.Remove(chosen);
                _prospects.Insert(0, chosen);
            }

            // perform draft: add player to team's roster and remove from pool
            team.Roster.Add(chosen);
            _prospects.Remove(chosen);

            // consume one draft pick for team if any
            var pick = team.DraftPicks.FirstOrDefault();
            if (pick != null) team.RemovePick(pick);

            RefreshList();

            MessageBox.Show(this, $"{chosen.Name} drafted to {team.Name}.", "Drafted", MessageBoxButtons.OK, MessageBoxIcon.Information);
            DialogResult = DialogResult.OK;
            Close();
        }
    }
}
