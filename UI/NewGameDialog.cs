using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Linq;
using System.Windows.Forms;

namespace PennantSimulator.UI
{
    public class NewGameDialog : Form
    {
        private FlowLayoutPanel _teamFlow;
        private NumericUpDown _gamesInput;
        private ToggleSwitch _startManagerSwitch;
        private RoundedButton _ok;
        private RoundedButton _cancel;

        private LeaguePreview[] _teamPreviews;
        private int _selectedIndex = 0;

        public int SelectedTeamIndex => _selectedIndex;
        public int GamesPerTeam => (int)_gamesInput.Value;
        public bool StartAsManager => _startManagerSwitch.Checked;

        public NewGameDialog()
        {
            Text = "New Game Settings";
            Width = 620;
            Height = 420;
            StartPosition = FormStartPosition.CenterParent;
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            BackColor = Color.FromArgb(245, 247, 250);

            // Header
            var header = new Panel { Dock = DockStyle.Top, Height = 110, Padding = new Padding(20) };
            header.Paint += (s, e) =>
            {
                using (var lg = new LinearGradientBrush(header.ClientRectangle, Color.FromArgb(24, 90, 192), Color.FromArgb(0, 172, 193), 45f))
                {
                    e.Graphics.FillRectangle(lg, header.ClientRectangle);
                }
                using (var sf = new StringFormat { Alignment = StringAlignment.Near, LineAlignment = StringAlignment.Center })
                using (var f = new Font("Segoe UI", 18, FontStyle.Bold))
                using (var brush = new SolidBrush(Color.White))
                {
                    e.Graphics.DrawString("Pennant Simulator", f, brush, new RectangleF(24, 0, header.Width - 48, header.Height), sf);
                }
            };
            Controls.Add(header);

            // Main area
            var main = new Panel { Dock = DockStyle.Fill, Padding = new Padding(20) };
            Controls.Add(main);

            // Left: team selection
            var left = new Panel { Width = 320, Dock = DockStyle.Left, Padding = new Padding(10) };
            main.Controls.Add(left);

            var lblTeam = new Label { Text = "Choose Your Team", Font = new Font("Segoe UI", 12, FontStyle.Bold), Dock = DockStyle.Top, Height = 28 };
            left.Controls.Add(lblTeam);

            _teamFlow = new FlowLayoutPanel { Dock = DockStyle.Fill, AutoScroll = true, FlowDirection = FlowDirection.TopDown, WrapContents = false, Padding = new Padding(6) };
            left.Controls.Add(_teamFlow);

            // Right: settings
            var right = new Panel { Dock = DockStyle.Fill, Padding = new Padding(10) };
            main.Controls.Add(right);

            var lblSettings = new Label { Text = "Game Settings", Font = new Font("Segoe UI", 12, FontStyle.Bold), Dock = DockStyle.Top, Height = 28 };
            right.Controls.Add(lblSettings);

            var settingsPanel = new TableLayoutPanel { Dock = DockStyle.Top, Height = 160, ColumnCount = 1, RowCount = 3, Padding = new Padding(8) };
            settingsPanel.RowStyles.Add(new RowStyle(SizeType.Absolute, 60));
            settingsPanel.RowStyles.Add(new RowStyle(SizeType.Absolute, 60));
            settingsPanel.RowStyles.Add(new RowStyle(SizeType.Absolute, 40));
            right.Controls.Add(settingsPanel);

            // Games per team control (trackbar + numeric)
            var gamesPanel = new Panel { Dock = DockStyle.Fill, Padding = new Padding(6) };
            var lblGames = new Label { Text = "Games per team", Font = new Font("Segoe UI", 9), Dock = DockStyle.Top, Height = 18 };
            gamesPanel.Controls.Add(lblGames);
            var tb = new TrackBar {
                Minimum = 10,
                Maximum = 200,
                Value = 143,
                TickStyle = TickStyle.None,
                Dock = DockStyle.Top,
                Height = 40,
                BackColor = gamesPanel.BackColor // 透明を使わない
};
            _gamesInput = new NumericUpDown { Minimum = 10, Maximum = 200, Value = 143, Width = 80, Anchor = AnchorStyles.Top | AnchorStyles.Right, Location = new Point(gamesPanel.Width - 90, 22) };
            _gamesInput.ValueChanged += (s, e) => { tb.Value = (int)_gamesInput.Value; };
            tb.Scroll += (s, e) => { _gamesInput.Value = tb.Value; };
            gamesPanel.Controls.Add(_gamesInput);
            gamesPanel.Controls.Add(tb);
            settingsPanel.Controls.Add(gamesPanel);

            // Start as manager toggle
            var startPanel = new Panel { Dock = DockStyle.Fill, Padding = new Padding(6) };
            var lblStart = new Label { Text = "Start as manager", Font = new Font("Segoe UI", 9), Dock = DockStyle.Left, Width = 160, TextAlign = ContentAlignment.MiddleLeft };
            _startManagerSwitch = new ToggleSwitch { Checked = true, Location = new Point(170, 10) };
            startPanel.Controls.Add(lblStart);
            startPanel.Controls.Add(_startManagerSwitch);
            settingsPanel.Controls.Add(startPanel);

            // Spacer
            settingsPanel.Controls.Add(new Panel());

            // Footer buttons
            var footer = new Panel { Dock = DockStyle.Bottom, Height = 64, Padding = new Padding(12) };
            Controls.Add(footer);

            _ok = new RoundedButton { Text = "Start", Width = 140, Height = 40, BackColor = Color.FromArgb(0, 120, 215), ForeColor = Color.White }; _ok.Click += Ok_Click;
            _cancel = new RoundedButton { Text = "Cancel", Width = 100, Height = 36, BackColor = Color.FromArgb(200, 200, 200), ForeColor = Color.Black }; _cancel.Click += (s, e) => { DialogResult = DialogResult.Cancel; Close(); };

            _ok.Location = new Point(Width - 200, 8);
            _cancel.Location = new Point(Width - 320, 12);
            footer.Controls.Add(_cancel);
            footer.Controls.Add(_ok);

            // Build team preview cards
            var league = ProgramBootstrap.CreateLeague();
            _teamPreviews = league.Teams.Select((t, i) => new LeaguePreview(t.Name, i)).ToArray();
            foreach (var card in _teamPreviews)
            {
                card.Width = _teamFlow.ClientSize.Width - 24;
                card.Margin = new Padding(6);
                card.Click += TeamCard_Click;
                _teamFlow.Controls.Add(card);
            }

            // Select first
            SelectTeamCard(0);

            // Resize handlers to reposition controls nicely
            _teamFlow.Resize += (s, e) => { foreach (var c in _teamPreviews) c.Width = _teamFlow.ClientSize.Width - 24; };
            this.Shown += (s, e) => { _ok.Focus(); };
        }

        private void TeamCard_Click(object? sender, EventArgs e)
        {
            if (sender is LeaguePreview p) SelectTeamCard(p.Index);
        }

        private void SelectTeamCard(int index)
        {
            _selectedIndex = index;
            for (int i = 0; i < _teamPreviews.Length; i++) _teamPreviews[i].Selected = (i == index);
        }

        private void Ok_Click(object? sender, EventArgs e)
        {
            DialogResult = DialogResult.OK;
            Close();
        }

        // Small helper: stylized rounded button
        private class RoundedButton : Button
        {
            protected override void OnPaint(PaintEventArgs pevent)
            {
                pevent.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
                using (var path = RoundedRect(new Rectangle(0, 0, Width - 1, Height - 1), 8))
                using (var brush = new SolidBrush(BackColor))
                {
                    pevent.Graphics.FillPath(brush, path);
                }
                TextRenderer.DrawText(pevent.Graphics, Text, Font, new Rectangle(0, 0, Width, Height), ForeColor, TextFormatFlags.HorizontalCenter | TextFormatFlags.VerticalCenter);
            }

            private GraphicsPath RoundedRect(Rectangle bounds, int radius)
            {
                var path = new GraphicsPath();
                int diam = radius * 2;
                path.AddArc(bounds.Left, bounds.Top, diam, diam, 180, 90);
                path.AddArc(bounds.Right - diam, bounds.Top, diam, diam, 270, 90);
                path.AddArc(bounds.Right - diam, bounds.Bottom - diam, diam, diam, 0, 90);
                path.AddArc(bounds.Left, bounds.Bottom - diam, diam, diam, 90, 90);
                path.CloseFigure();
                return path;
            }
        }

        // Simple toggle switch control
        private class ToggleSwitch : Control
        {
            public bool Checked { get; set; } = true;
            public event EventHandler? CheckedChanged;

            public ToggleSwitch()
            {
                Width = 64;
                Height = 28;
                this.Cursor = Cursors.Hand;
                this.Click += (s, e) => { Checked = !Checked; CheckedChanged?.Invoke(this, EventArgs.Empty); this.Invalidate(); };
            }

            protected override void OnPaint(PaintEventArgs e)
            {
                e.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
                var rect = new Rectangle(0, 0, Width, Height);
                Color back = Checked ? Color.FromArgb(0, 150, 136) : Color.FromArgb(200, 200, 200);
                using (var brush = new SolidBrush(back))
                    e.Graphics.FillRoundedRectangle(brush, rect, Height / 2);

                int diameter = Height - 6;
                int x = Checked ? Width - diameter - 3 : 3;
                var thumb = new Rectangle(x, 3, diameter, diameter);
                using (var brush = new SolidBrush(Color.White))
                    e.Graphics.FillEllipse(brush, thumb);
            }
        }

        // Team preview card
        private class LeaguePreview : Panel
        {
            private Label _nameLabel;
            private Panel _logoPanel;
            public int Index { get; }
            private bool _selected;
            public bool Selected
            {
                get => _selected;
                set { _selected = value; Invalidate(); }
            }

            public LeaguePreview(string name, int index)
            {
                Index = index;
                Height = 64;
                BackColor = Color.White;
                Padding = new Padding(8);
                BorderStyle = BorderStyle.None;

                _logoPanel = new Panel { Width = 48, Height = 48, BackColor = RandomColor(index), Dock = DockStyle.Left, Margin = new Padding(0, 0, 8, 0) };
                Controls.Add(_logoPanel);
                _nameLabel = new Label { Text = name, Font = new Font("Segoe UI", 10, FontStyle.Bold), Dock = DockStyle.Fill, TextAlign = ContentAlignment.MiddleLeft, ForeColor = Color.FromArgb(30,30,30) };
                Controls.Add(_nameLabel);

                this.Paint += LeaguePreview_Paint;
                this.Cursor = Cursors.Hand;
            }

            private void LeaguePreview_Paint(object? sender, PaintEventArgs e)
            {
                e.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
                var r = ClientRectangle;
                r.Inflate(-1, -1);
                using (var gp = new GraphicsPath())
                {
                    gp.AddRectangle(r);
                    using (var pen = new Pen(Selected ? Color.FromArgb(0, 120, 215) : Color.FromArgb(220, 220, 220), 2))
                    {
                        e.Graphics.DrawPath(pen, gp);
                    }
                }
            }

            private static Color RandomColor(int seed)
            {
                var rng = new Random(seed * 7919);
                return Color.FromArgb(200, rng.Next(60, 200), rng.Next(60, 200), rng.Next(60, 200));
            }
        }
    }

    // Extension helper for rounded rectangle fill
    internal static class GraphicsExtensions
    {
        public static void FillRoundedRectangle(this Graphics g, Brush b, Rectangle r, int radius)
        {
            using (var path = new GraphicsPath())
            {
                int d = radius * 2;
                path.AddArc(r.Left, r.Top, d, d, 180, 90);
                path.AddArc(r.Right - d, r.Top, d, d, 270, 90);
                path.AddArc(r.Right - d, r.Bottom - d, d, d, 0, 90);
                path.AddArc(r.Left, r.Bottom - d, d, d, 90, 90);
                path.CloseFigure();
                g.FillPath(b, path);
            }
        }
    }
}
