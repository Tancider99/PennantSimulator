using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using PennantSimulator.Models;
using PennantSimulator.Core;
using System.Globalization;

namespace PennantSimulator.UI
{
    public class TradeDialog : Form
    {
        private League _league;
        private ComboBox _teamA;
        private ComboBox _teamB;
        private ListBox _rosterA;
        private ListBox _rosterB;
        private Button _propose;
        private NumericUpDown _cashA;
        private NumericUpDown _cashB;
        private ListBox _picksA;
        private ListBox _picksB;

        public TradeDialog(League league)
        {
            _league = league;
            Text = "Trade Players";
            Width = 700;
            Height = 480;
            StartPosition = FormStartPosition.CenterParent;

            var main = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 3 };
            main.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 45));
            main.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 10));
            main.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 45));
            Controls.Add(main);

            var leftPanel = new Panel { Dock = DockStyle.Fill, Padding = new Padding(8) };
            var centerPanel = new Panel { Dock = DockStyle.Fill, Padding = new Padding(8) };
            var rightPanel = new Panel { Dock = DockStyle.Fill, Padding = new Padding(8) };
            main.Controls.Add(leftPanel, 0, 0);
            main.Controls.Add(centerPanel, 1, 0);
            main.Controls.Add(rightPanel, 2, 0);

            _teamA = new ComboBox { Dock = DockStyle.Top, DropDownStyle = ComboBoxStyle.DropDownList };
            _teamB = new ComboBox { Dock = DockStyle.Top, DropDownStyle = ComboBoxStyle.DropDownList };
            foreach (var t in _league.Teams)
            {
                _teamA.Items.Add(t.Name);
                _teamB.Items.Add(t.Name);
            }
            _teamA.SelectedIndex = 0;
            _teamB.SelectedIndex = Math.Min(1, Math.Max(0, _teamB.Items.Count - 1));

            leftPanel.Controls.Add(_teamA);
            rightPanel.Controls.Add(_teamB);

            _rosterA = new ListBox { Dock = DockStyle.Fill, SelectionMode = SelectionMode.MultiExtended, Font = new Font("Consolas", 10) };
            _rosterB = new ListBox { Dock = DockStyle.Fill, SelectionMode = SelectionMode.MultiExtended, Font = new Font("Consolas", 10) };
            leftPanel.Controls.Add(_rosterA);
            rightPanel.Controls.Add(_rosterB);

            _teamA.SelectedIndexChanged += (s, e) => RefreshRosters();
            _teamB.SelectedIndexChanged += (s, e) => RefreshRosters();

            // cash input and picks list
            var cashALabel = new Label { Text = "Cash A -> B", Dock = DockStyle.Top };
            _cashA = new NumericUpDown { Minimum = 0, Maximum = 10000000, Increment = 10000, Dock = DockStyle.Top, Value = 0 };
            var cashBLabel = new Label { Text = "Cash B -> A", Dock = DockStyle.Top };
            _cashB = new NumericUpDown { Minimum = 0, Maximum = 10000000, Increment = 10000, Dock = DockStyle.Top, Value = 0 };

            centerPanel.Controls.Add(cashALabel);
            centerPanel.Controls.Add(_cashA);
            centerPanel.Controls.Add(cashBLabel);
            centerPanel.Controls.Add(_cashB);

            _picksA = new ListBox { Dock = DockStyle.Top, Height = 80, SelectionMode = SelectionMode.MultiExtended };
            _picksB = new ListBox { Dock = DockStyle.Top, Height = 80, SelectionMode = SelectionMode.MultiExtended };
            leftPanel.Controls.Add(_picksA);
            rightPanel.Controls.Add(_picksB);

            _propose = new Button { Text = "Propose Trade", Dock = DockStyle.Fill, Height = 36, BackColor = Color.FromArgb(40, 167, 69), ForeColor = Color.White };
            _propose.Click += Propose_Click;
            centerPanel.Controls.Add(_propose);

            RefreshRosters();
        }

        private void RefreshRosters()
        {
            _rosterA.Items.Clear();
            _rosterB.Items.Clear();
            _picksA.Items.Clear();
            _picksB.Items.Clear();
            if (_teamA.SelectedIndex < 0 || _teamB.SelectedIndex < 0) return;
            var a = _league.Teams[_teamA.SelectedIndex];
            var b = _league.Teams[_teamB.SelectedIndex];
            foreach (var p in a.Roster) _rosterA.Items.Add(p.Name + $"  O:{p.OverallSkill:F0}");
            foreach (var p in b.Roster) _rosterB.Items.Add(p.Name + $"  O:{p.OverallSkill:F0}");
            foreach (var pk in a.DraftPicks) _picksA.Items.Add(pk.ToString());
            foreach (var pk in b.DraftPicks) _picksB.Items.Add(pk.ToString());
        }

        private void Propose_Click(object? sender, EventArgs e)
        {
            if (_teamA.SelectedIndex == _teamB.SelectedIndex)
            {
                MessageBox.Show(this, "Select two different teams.", "Invalid", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            var a = _league.Teams[_teamA.SelectedIndex];
            var b = _league.Teams[_teamB.SelectedIndex];

            var selA = _rosterA.SelectedIndices.Cast<int>().Select(i => a.Roster[i]).ToList();
            var selB = _rosterB.SelectedIndices.Cast<int>().Select(i => b.Roster[i]).ToList();

            var selPicksA = _picksA.SelectedIndices.Cast<int>().Select(i => a.DraftPicks[i]).ToList();
            var selPicksB = _picksB.SelectedIndices.Cast<int>().Select(i => b.DraftPicks[i]).ToList();

            if (selA.Count == 0 && selB.Count == 0 && selPicksA.Count == 0 && selPicksB.Count == 0 && _cashA.Value == 0 && _cashB.Value == 0)
            {
                MessageBox.Show(this, "Select at least one asset to trade.", "No Selection", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            // basic valuation: sum of OverallSkill + picks valued modestly
            double valA = selA.Sum(p => p.OverallSkill) + selPicksA.Sum(pk => ValuePick(pk));
            double valB = selB.Sum(p => p.OverallSkill) + selPicksB.Sum(pk => ValuePick(pk));

            // include cash as direct value (normalized)
            valA += (double)_cashA.Value / 10000.0;
            valB += (double)_cashB.Value / 10000.0;

            if (selA.Count > 0 || selB.Count > 0 || selPicksA.Count > 0 || selPicksB.Count > 0)
            {
                double ratio = valA / Math.Max(1.0, valB);
                if (ratio < 0.80 || ratio > 1.20)
                {
                    var res = MessageBox.Show(this, "Trade seems uneven. Do you want to force it?", "Uneven Trade", MessageBoxButtons.YesNo, MessageBoxIcon.Question);
                    if (res != DialogResult.Yes) return;
                }
            }

            // perform swap of players
            foreach (var p in selA)
            {
                a.Roster.Remove(p);
                b.Roster.Add(p);
            }
            foreach (var p in selB)
            {
                b.Roster.Remove(p);
                a.Roster.Add(p);
            }

            // transfer picks
            foreach (var pk in selPicksA)
            {
                a.RemovePick(pk);
                b.AddPick(pk);
            }
            foreach (var pk in selPicksB)
            {
                b.RemovePick(pk);
                a.AddPick(pk);
            }

            // transfer cash
            double cashFromAtoB = (double)_cashA.Value;
            double cashFromBtoA = (double)_cashB.Value;
            a.Cash -= cashFromAtoB;
            b.Cash += cashFromAtoB;
            b.Cash -= cashFromBtoA;
            a.Cash += cashFromBtoA;

            MessageBox.Show(this, "Trade completed.", "Success", MessageBoxButtons.OK, MessageBoxIcon.Information);
            DialogResult = DialogResult.OK;
            Close();
        }

        private double ValuePick(DraftPick pk)
        {
            // very rough valuation: earlier picks more valuable
            return Math.Max(1.0, 20.0 / Math.Max(1, pk.Overall));
        }
    }
}
