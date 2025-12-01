using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;

namespace PennantSimulator.UI.Controls
{
    public class AnimatedPanel : Panel
    {
        private System.Windows.Forms.Timer _timer;
        private float _opacity = 0f;
        private bool _fadeIn = true;

        public AnimatedPanel()
        {
            _timer = new System.Windows.Forms.Timer { Interval = 16 }; // ~60fps
            _timer.Tick += Timer_Tick;
            DoubleBuffered = true;
        }

        public void FadeIn()
        {
            _fadeIn = true;
            _opacity = 0f;
            _timer.Start();
        }

        public void FadeOut()
        {
            _fadeIn = false;
            _opacity = 1f;
            _timer.Start();
        }

        private void Timer_Tick(object? sender, EventArgs e)
        {
            if (_fadeIn)
            {
                _opacity += 0.05f;
                if (_opacity >= 1f)
                {
                    _opacity = 1f;
                    _timer.Stop();
                }
            }
            else
            {
                _opacity -= 0.05f;
                if (_opacity <= 0f)
                {
                    _opacity = 0f;
                    _timer.Stop();
                }
            }
            
            Invalidate();
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            if (_opacity < 1f)
            {
                using (var brush = new SolidBrush(Color.FromArgb((int)(255 * _opacity), BackColor)))
                {
                    e.Graphics.FillRectangle(brush, ClientRectangle);
                }
            }
            else
            {
                base.OnPaint(e);
            }
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                _timer?.Dispose();
            }
            base.Dispose(disposing);
        }
    }

    public class SlidePanel : Panel
    {
        private System.Windows.Forms.Timer _timer;
        private int _targetY;
        private int _currentY;
        private bool _isAnimating = false;

        public SlidePanel()
        {
            _timer = new System.Windows.Forms.Timer { Interval = 16 };
            _timer.Tick += Timer_Tick;
        }

        public void SlideIn()
        {
            _targetY = 0;
            _currentY = -Height;
            Top = _currentY;
            _isAnimating = true;
            _timer.Start();
        }

        public void SlideOut()
        {
            _targetY = -Height;
            _currentY = Top;
            _isAnimating = true;
            _timer.Start();
        }

        private void Timer_Tick(object? sender, EventArgs e)
        {
            if (!_isAnimating) return;

            int delta = (_targetY - _currentY) / 5;
            if (Math.Abs(delta) < 1)
            {
                _currentY = _targetY;
                _isAnimating = false;
                _timer.Stop();
            }
            else
            {
                _currentY += delta;
            }

            Top = _currentY;
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                _timer?.Dispose();
            }
            base.Dispose(disposing);
        }
    }

    public class PulseButton : ModernButton
    {
        private System.Windows.Forms.Timer _pulseTimer;
        private float _pulseScale = 1.0f;
        private bool _pulseGrowing = true;

        public bool EnablePulse { get; set; } = false;

        public PulseButton()
        {
            _pulseTimer = new System.Windows.Forms.Timer { Interval = 50 };
            _pulseTimer.Tick += PulseTimer_Tick;
        }

        private void PulseTimer_Tick(object? sender, EventArgs e)
        {
            if (!EnablePulse) return;

            if (_pulseGrowing)
            {
                _pulseScale += 0.02f;
                if (_pulseScale >= 1.1f)
                {
                    _pulseScale = 1.1f;
                    _pulseGrowing = false;
                }
            }
            else
            {
                _pulseScale -= 0.02f;
                if (_pulseScale <= 1.0f)
                {
                    _pulseScale = 1.0f;
                    _pulseGrowing = true;
                }
            }

            Invalidate();
        }

        public void StartPulse()
        {
            EnablePulse = true;
            _pulseTimer.Start();
        }

        public void StopPulse()
        {
            EnablePulse = false;
            _pulseTimer.Stop();
            _pulseScale = 1.0f;
            Invalidate();
        }

        protected override void OnPaint(PaintEventArgs pevent)
        {
            if (_pulseScale != 1.0f)
            {
                pevent.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
                var matrix = new Matrix();
                matrix.Scale(_pulseScale, _pulseScale);
                matrix.Translate((Width * (1 - _pulseScale)) / 2, (Height * (1 - _pulseScale)) / 2);
                pevent.Graphics.Transform = matrix;
            }

            base.OnPaint(pevent);
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                _pulseTimer?.Dispose();
            }
            base.Dispose(disposing);
        }
    }

    public class NotificationToast : Form
    {
        private System.Windows.Forms.Timer _displayTimer;
        private System.Windows.Forms.Timer _fadeTimer;
        private float _opacity = 0f;

        public NotificationToast(string message, int displayMs = 3000)
        {
            FormBorderStyle = FormBorderStyle.None;
            StartPosition = FormStartPosition.Manual;
            ShowInTaskbar = false;
            TopMost = true;
            BackColor = Theme.Dark;
            ForeColor = Color.White;
            Size = new Size(300, 80);
            Opacity = 0;

            // Position at bottom-right of screen
            var screen = Screen.PrimaryScreen.WorkingArea;
            Location = new Point(screen.Right - Width - 20, screen.Bottom - Height - 20);

            var label = new Label
            {
                Text = message,
                Dock = DockStyle.Fill,
                TextAlign = ContentAlignment.MiddleCenter,
                Font = Theme.UiFont,
                ForeColor = Color.White
            };
            Controls.Add(label);

            _displayTimer = new System.Windows.Forms.Timer { Interval = displayMs };
            _displayTimer.Tick += (s, e) => { _displayTimer.Stop(); FadeOut(); };

            _fadeTimer = new System.Windows.Forms.Timer { Interval = 16 };
            _fadeTimer.Tick += FadeTimer_Tick;

            Paint += (s, e) =>
            {
                e.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
                using (var path = GetRoundedRectPath(ClientRectangle, 8))
                {
                    e.Graphics.FillPath(new SolidBrush(BackColor), path);
                }
            };

            FadeIn();
        }

        private void FadeIn()
        {
            _fadeTimer.Start();
            _displayTimer.Start();
        }

        private void FadeOut()
        {
            _fadeTimer.Start();
        }

        private void FadeTimer_Tick(object? sender, EventArgs e)
        {
            if (_displayTimer.Enabled) // Fading in
            {
                _opacity += 0.1f;
                if (_opacity >= 1f)
                {
                    _opacity = 1f;
                    _fadeTimer.Stop();
                }
            }
            else // Fading out
            {
                _opacity -= 0.1f;
                if (_opacity <= 0f)
                {
                    _opacity = 0f;
                    _fadeTimer.Stop();
                    Close();
                }
            }

            Opacity = _opacity;
        }

        private GraphicsPath GetRoundedRectPath(Rectangle rect, int radius)
        {
            var path = new GraphicsPath();
            int diameter = radius * 2;
            var arc = new Rectangle(rect.Location, new Size(diameter, diameter));

            path.AddArc(arc, 180, 90);
            arc.X = rect.Right - diameter;
            path.AddArc(arc, 270, 90);
            arc.Y = rect.Bottom - diameter;
            path.AddArc(arc, 0, 90);
            arc.X = rect.Left;
            path.AddArc(arc, 90, 90);
            path.CloseFigure();

            return path;
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                _displayTimer?.Dispose();
                _fadeTimer?.Dispose();
            }
            base.Dispose(disposing);
        }

        public static void Show(string message, int displayMs = 3000)
        {
            var toast = new NotificationToast(message, displayMs);
            toast.Show();
        }
    }
}
