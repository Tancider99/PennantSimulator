using System;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using PennantSimulator.Models;
using PennantSimulator.Core;

namespace PennantSimulator.UI
{
    public class SubstitutionDialog : Form
    {
        private SubstitutionManager _manager;
        private DataGridView _lineupGrid;
        private ListBox _benchList;
        private Button _subButton;
        private Button _changePitcherButton;

        public SubstitutionDialog(SubstitutionManager manager)
        {
            _manager = manager ?? throw new ArgumentNullException(nameof(manager));
            Text = "Substitutions & Lineup";
            Width = 720;
            Height = 560;
            StartPosition = FormStartPosition.CenterParent;

            var main = new SplitContainer { Dock = DockStyle.Fill, Orientation = Orientation.Vertical, SplitterDistance = 400 };
            Controls.Add(main);

            // Left: Current Lineup
            var leftPanel = new Panel { Dock = DockStyle.Fill, Padding = new Padding(8) };
            var lblLineup = new Label { Text = "Current Lineup", Font = Theme.TitleFont, Dock = DockStyle.Top, Height = 32 };
            _lineupGrid = new DataGridView { Dock = DockStyle.Fill, ReadOnly = true, AllowUserToAddRows = false, AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill };
            leftPanel.Controls.Add(_lineupGrid);
            leftPanel.Controls.Add(lblLineup);
            main.Panel1.Controls.Add(leftPanel);

            // Right: Bench + Actions
            var rightPanel = new Panel { Dock = DockStyle.Fill, Padding = new Padding(8) };
            var lblBench = new Label { Text = "Bench", Font = Theme.TitleFont, Dock = DockStyle.Top, Height = 32 };
            _benchList = new ListBox { Dock = DockStyle.Fill, Font = new Font("Consolas", 10) };
            var actions = new FlowLayoutPanel { Dock = DockStyle.Bottom, Height = 80, FlowDirection = FlowDirection.LeftToRight, Padding = new Padding(4) };

            _subButton = new Button { Text = "Substitute Batter", Width = 140, Height = 36 };
            Theme.StyleButton(_subButton);
            _subButton.Click += SubButton_Click;

            _changePitcherButton = new Button { Text = "Change Pitcher", Width = 140, Height = 36 };
            Theme.StyleButton(_changePitcherButton);
            _changePitcherButton.Click += ChangePitcherButton_Click;

            actions.Controls.Add(_subButton);
            actions.Controls.Add(_changePitcherButton);

            rightPanel.Controls.Add(actions);
            rightPanel.Controls.Add(_benchList);
            rightPanel.Controls.Add(lblBench);
            main.Panel2.Controls.Add(rightPanel);

            RefreshDisplay();
        }

        private void RefreshDisplay()
        {
            // Populate lineup
            var lineupData = _manager.Lineup.Select(s => new
            {
                Order = s.Order,
                Player = s.Player.Name,
                Position = s.FieldPosition.ToString(),
                OVR = (int)s.Player.OverallSkill,
                Stamina = s.Player.CurrentStamina
            }).ToList();
            _lineupGrid.DataSource = lineupData;

            // Populate bench
            _benchList.Items.Clear();
            foreach (var p in _manager.Bench)
                _benchList.Items.Add($"{p.Name} (OVR:{(int)p.OverallSkill} STM:{p.CurrentStamina})");
        }

        private void SubButton_Click(object? sender, EventArgs e)
        {
            if (_lineupGrid.SelectedRows.Count == 0 || _benchList.SelectedIndex < 0)
            {
                MessageBox.Show(this, "Select a lineup position and a bench player.", "Selection Required", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            int lineupPos = (int)_lineupGrid.SelectedRows[0].Cells["Order"].Value;
            var newPlayer = _manager.Bench[_benchList.SelectedIndex];

            if (_manager.SubstituteBatter(lineupPos, newPlayer))
            {
                MessageBox.Show(this, $"{newPlayer.Name} substituted into lineup position {lineupPos}.", "Substitution Complete", MessageBoxButtons.OK, MessageBoxIcon.Information);
                RefreshDisplay();
            }
        }

        private void ChangePitcherButton_Click(object? sender, EventArgs e)
        {
            if (_benchList.SelectedIndex < 0)
            {
                MessageBox.Show(this, "Select a pitcher from the bench.", "Selection Required", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            var newPitcher = _manager.Bench[_benchList.SelectedIndex];
            if (_manager.ChangePitcher(newPitcher))
            {
                MessageBox.Show(this, $"{newPitcher.Name} is now pitching. Pitch count reset.", "Pitcher Changed", MessageBoxButtons.OK, MessageBoxIcon.Information);
                RefreshDisplay();
            }
        }
    }
}
