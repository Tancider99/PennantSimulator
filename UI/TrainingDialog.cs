using System;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using PennantSimulator.Models;
using PennantSimulator.Core;

namespace PennantSimulator.UI
{
    public class TrainingDialog : Form
    {
        private Team _team;
        private ComboBox _playerBox;
        private ComboBox _typeBox;
        private TrackBar _intensityBar;
        private Label _intensityLabel;
        private Button _trainButton;
        private TextBox _resultBox;

        public TrainingDialog(Team team)
        {
            _team = team ?? throw new ArgumentNullException(nameof(team));
            Text = $"Training - {team.Name}";
            Width = 560;
            Height = 480;
            StartPosition = FormStartPosition.CenterParent;

            var main = new TableLayoutPanel { Dock = DockStyle.Fill, RowCount = 6, Padding = new Padding(12) };
            main.RowStyles.Add(new RowStyle(SizeType.Absolute, 32));
            main.RowStyles.Add(new RowStyle(SizeType.Absolute, 32));
            main.RowStyles.Add(new RowStyle(SizeType.Absolute, 60));
            main.RowStyles.Add(new RowStyle(SizeType.Absolute, 48));
            main.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
            main.RowStyles.Add(new RowStyle(SizeType.Absolute, 48));
            Controls.Add(main);

            var lblPlayer = new Label { Text = "Select Player:", Dock = DockStyle.Fill };
            _playerBox = new ComboBox { Dock = DockStyle.Fill, DropDownStyle = ComboBoxStyle.DropDownList };
            foreach (var p in team.Roster)
                _playerBox.Items.Add($"{p.Name} (OVR:{(int)p.OverallSkill} STM:{p.CurrentStamina})");
            if (_playerBox.Items.Count > 0) _playerBox.SelectedIndex = 0;
            main.Controls.Add(lblPlayer, 0, 0);
            main.Controls.Add(_playerBox, 0, 1);

            var lblType = new Label { Text = "Training Type:", Dock = DockStyle.Fill };
            _typeBox = new ComboBox { Dock = DockStyle.Fill, DropDownStyle = ComboBoxStyle.DropDownList };
            foreach (var t in Enum.GetValues<TrainingSystem.TrainingType>())
                _typeBox.Items.Add(t.ToString());
            _typeBox.SelectedIndex = 0;
            main.Controls.Add(lblType, 0, 2);

            var intensityPanel = new Panel { Dock = DockStyle.Fill };
            _intensityLabel = new Label { Text = "Intensity: 50", Dock = DockStyle.Top };
            _intensityBar = new TrackBar { Minimum = 10, Maximum = 100, Value = 50, Dock = DockStyle.Fill, TickStyle = TickStyle.Both };
            _intensityBar.ValueChanged += (s, e) => _intensityLabel.Text = $"Intensity: {_intensityBar.Value}";
            intensityPanel.Controls.Add(_intensityBar);
            intensityPanel.Controls.Add(_intensityLabel);
            main.Controls.Add(intensityPanel, 0, 3);

            _trainButton = new Button { Text = "Start Training", Dock = DockStyle.Fill };
            Theme.StyleButton(_trainButton);
            _trainButton.Click += TrainButton_Click;
            main.Controls.Add(_trainButton, 0, 5);

            _resultBox = new TextBox { Multiline = true, ReadOnly = true, Dock = DockStyle.Fill, ScrollBars = ScrollBars.Vertical };
            main.Controls.Add(_resultBox, 0, 4);
        }

        private void TrainButton_Click(object? sender, EventArgs e)
        {
            if (_playerBox.SelectedIndex < 0) return;
            var player = _team.Roster[_playerBox.SelectedIndex];
            var type = Enum.Parse<TrainingSystem.TrainingType>(_typeBox.SelectedItem.ToString());
            int intensity = _intensityBar.Value;

            var result = TrainingSystem.Train(player, type, intensity);

            _resultBox.AppendText($"\r\n{DateTime.Now:HH:mm:ss} - {result.Message}");
            _resultBox.ScrollToCaret();

            // Update player display
            _playerBox.Items[_playerBox.SelectedIndex] = $"{player.Name} (OVR:{(int)player.OverallSkill} STM:{player.CurrentStamina})";

            if (result.Success)
            {
                MessageBox.Show(this, result.Message, "Training Complete", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            else
            {
                MessageBox.Show(this, result.Message, "Training Issue", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
        }
    }
}
