using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;
using System.Threading;

namespace PennantSimulator.UI
{
    public class TitleForm : Form
    {
        private RoundedButton _startButton;
        private RoundedButton _exitButton;

        public TitleForm()
        {
            Text = "Pennant Simulator";
            Width = 900;
            Height = 560;
            StartPosition = FormStartPosition.CenterScreen;
            FormBorderStyle = FormBorderStyle.None;
            BackColor = Color.White;

            // Drop shadow effect (simple)
            this.Padding = new Padding(6);

            // Main panel with rounded corners
            var main = new Panel { Dock = DockStyle.Fill, BackColor = Color.White };
            main.Paint += Main_Paint;
            Controls.Add(main);

            // Left artwork panel
            var art = new Panel { Dock = DockStyle.Left, Width = 420, Padding = new Padding(24) };
            art.Paint += Art_Paint;
            main.Controls.Add(art);

            var title = new Label { Text = "Pennant Simulator", ForeColor = Color.White, Font = new Font("Segoe UI", 28, FontStyle.Bold), Dock = DockStyle.Top, Height = 80, TextAlign = ContentAlignment.MiddleLeft };
            art.Controls.Add(title);

            var subtitle = new Label { Text = "A PowerPro-style pennant manager", ForeColor = Color.FromArgb(220, 235, 245), Font = new Font("Segoe UI", 11), Dock = DockStyle.Top, Height = 32, TextAlign = ContentAlignment.MiddleLeft };
            art.Controls.Add(subtitle);

            _startButton = new RoundedButton { Text = "Start New Game", Width = 260, Height = 56, BackColor = Color.FromArgb(0, 140, 255), ForeColor = Color.White, Font = new Font("Segoe UI", 12, FontStyle.Bold) };
            _startButton.Location = new Point(24, 180);
            _startButton.Click += StartButton_Click;
            art.Controls.Add(_startButton);

            _exitButton = new RoundedButton { Text = "Exit", Width = 120, Height = 40, BackColor = Color.FromArgb(230, 80, 90), ForeColor = Color.White };
            _exitButton.Location = new Point(24, 250);
            _exitButton.Click += (s, e) => Application.Exit();
            art.Controls.Add(_exitButton);

            // Right side quick actions
            var right = new Panel { Dock = DockStyle.Fill, Padding = new Padding(24) };
            main.Controls.Add(right);

            var quick = new Label { Text = "Quick Start", Font = new Font("Segoe UI", 14, FontStyle.Bold), Dock = DockStyle.Top, Height = 36 };
            right.Controls.Add(quick);

            var btnDemo = new RoundedButton { Text = "Start Demo", Width = 180, Height = 44, BackColor = Color.FromArgb(52, 199, 89), ForeColor = Color.White };
            btnDemo.Click += (s, e) => StartDemo();
            btnDemo.Location = new Point(24, 60);
            right.Controls.Add(btnDemo);

            // close button top-right
            var btnClose = new Button { Text = "X", FlatStyle = FlatStyle.Flat, ForeColor = Color.FromArgb(120, 120, 120), BackColor = Color.Transparent, Width = 36, Height = 36 }; 
            btnClose.FlatAppearance.BorderSize = 0;
            btnClose.Location = new Point(Width - 72, 12);
            btnClose.Click += (s, e) => Application.Exit();
            Controls.Add(btnClose);
        }

        private void Main_Paint(object? sender, PaintEventArgs e)
        {
            var g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;
            var rect = new Rectangle(0, 0, ClientSize.Width, ClientSize.Height);
            using (var path = RoundedRect(rect, 14))
            using (var brush = new SolidBrush(Color.White))
            {
                g.FillPath(brush, path);
            }
        }

        private void Art_Paint(object? sender, PaintEventArgs e)
        {
            var panel = sender as Panel;
            var g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;
            var r = panel.ClientRectangle;
            using (var lg = new LinearGradientBrush(r, Color.FromArgb(18, 90, 176), Color.FromArgb(0, 170, 201), 45f))
            {
                g.FillPath(lg, RoundedRect(r, 10));
            }

            // draw a subtle pennant icon
            using (var pen = new Pen(Color.FromArgb(255, 255, 255, 120), 2.5f))
            using (var brush = new SolidBrush(Color.FromArgb(255, 255, 255, 30)))
            {
                var pts = new[] { new Point(r.Left + 24, r.Bottom - 80), new Point(r.Left + 120, r.Top + 40), new Point(r.Left + 160, r.Bottom - 80) };
                g.FillPolygon(brush, pts);
                g.DrawPolygon(pen, pts);
            }
        }

        private void StartButton_Click(object? sender, EventArgs e)
        {
            // Open NewGameDialog to get settings
            using (var dlg = new NewGameDialog())
            {
                if (dlg.ShowDialog(this) == DialogResult.OK)
                {
                    var league = ProgramBootstrap.CreateLeague();
                    var main = ProgramBootstrap.CreateMainForm(league, dlg.SelectedTeamIndex, dlg.StartAsManager, dlg.GamesPerTeam);
                    Hide();
                    main.ShowDialog(this);
                    Close();
                }
            }
        }

        private void StartDemo()
        {
            var league = ProgramBootstrap.CreateLeague();
            var main = ProgramBootstrap.CreateMainForm(league, 0, true, 60);
            Hide();
            main.ShowDialog(this);
            Close();
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

        // RoundedButton helper
        private class RoundedButton : Button
        {
            protected override void OnPaint(PaintEventArgs pevent)
            {
                pevent.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
                using (var path = new GraphicsPath())
                {
                    int r = 10;
                    path.AddArc(0, 0, r * 2, r * 2, 180, 90);
                    path.AddArc(Width - r * 2 - 1, 0, r * 2, r * 2, 270, 90);
                    path.AddArc(Width - r * 2 - 1, Height - r * 2 - 1, r * 2, r * 2, 0, 90);
                    path.AddArc(0, Height - r * 2 - 1, r * 2, r * 2, 90, 90);
                    path.CloseFigure();
                    using (var brush = new SolidBrush(BackColor)) pevent.Graphics.FillPath(brush, path);
                }
                TextRenderer.DrawText(pevent.Graphics, Text, Font, new Rectangle(0, 0, Width, Height), ForeColor, TextFormatFlags.HorizontalCenter | TextFormatFlags.VerticalCenter);
            }
        }
    }
}
