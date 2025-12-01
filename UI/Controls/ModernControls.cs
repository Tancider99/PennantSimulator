using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;

namespace PennantSimulator.UI.Controls
{
    public class ModernButton : Button
    {
        private Color _hoverColor;
        private Color _normalColor;
        private bool _isHovered = false;
        private int _cornerRadius = 8;

        public int CornerRadius
        {
            get => _cornerRadius;
            set { _cornerRadius = value; Invalidate(); }
        }

        public ModernButton()
        {
            FlatStyle = FlatStyle.Flat;
            FlatAppearance.BorderSize = 0;
            Cursor = Cursors.Hand;
            _normalColor = Theme.Primary;
            _hoverColor = ControlPaint.Light(Theme.Primary, 0.2f);
            BackColor = _normalColor;
            ForeColor = Color.White;
            Font = Theme.UiFont;
        }

        protected override void OnMouseEnter(EventArgs e)
        {
            base.OnMouseEnter(e);
            _isHovered = true;
            BackColor = _hoverColor;
            Invalidate();
        }

        protected override void OnMouseLeave(EventArgs e)
        {
            base.OnMouseLeave(e);
            _isHovered = false;
            BackColor = _normalColor;
            Invalidate();
        }

        protected override void OnPaint(PaintEventArgs pevent)
        {
            pevent.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
            
            using (var path = GetRoundedRectPath(ClientRectangle, _cornerRadius))
            {
                pevent.Graphics.FillPath(new SolidBrush(BackColor), path);
                
                // Add subtle shadow when hovered
                if (_isHovered)
                {
                    using (var shadowBrush = new SolidBrush(Color.FromArgb(30, 0, 0, 0)))
                    {
                        var shadowRect = ClientRectangle;
                        shadowRect.Offset(0, 2);
                        using (var shadowPath = GetRoundedRectPath(shadowRect, _cornerRadius))
                        {
                            pevent.Graphics.FillPath(shadowBrush, shadowPath);
                        }
                    }
                    pevent.Graphics.FillPath(new SolidBrush(BackColor), path);
                }
            }

            TextRenderer.DrawText(pevent.Graphics, Text, Font, ClientRectangle, 
                ForeColor, TextFormatFlags.HorizontalCenter | TextFormatFlags.VerticalCenter);
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
    }

    public class ModernCard : Panel
    {
        private bool _isHovered = false;
        private int _elevation = 2;

        public int Elevation
        {
            get => _elevation;
            set { _elevation = value; Invalidate(); }
        }

        public ModernCard()
        {
            BackColor = Color.White;
            Padding = new Padding(16);
            Cursor = Cursors.Hand;
        }

        protected override void OnMouseEnter(EventArgs e)
        {
            base.OnMouseEnter(e);
            _isHovered = true;
            _elevation = 6;
            Invalidate();
        }

        protected override void OnMouseLeave(EventArgs e)
        {
            base.OnMouseLeave(e);
            _isHovered = false;
            _elevation = 2;
            Invalidate();
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            e.Graphics.SmoothingMode = SmoothingMode.AntiAlias;

            // Draw shadow
            for (int i = 0; i < _elevation; i++)
            {
                var shadowRect = ClientRectangle;
                shadowRect.Inflate(-i, -i);
                shadowRect.Offset(0, i);
                using (var brush = new SolidBrush(Color.FromArgb(10, 0, 0, 0)))
                using (var path = GetRoundedRectPath(shadowRect, 8))
                {
                    e.Graphics.FillPath(brush, path);
                }
            }

            // Draw card background
            using (var path = GetRoundedRectPath(ClientRectangle, 8))
            {
                e.Graphics.FillPath(new SolidBrush(BackColor), path);
                
                // Draw border
                using (var pen = new Pen(Color.FromArgb(230, 230, 230), 1))
                {
                    e.Graphics.DrawPath(pen, path);
                }
            }

            base.OnPaint(e);
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
    }

    public class ProgressBarModern : Control
    {
        private int _value = 0;
        private int _maximum = 100;
        private Color _progressColor = Theme.Primary;

        public int Value
        {
            get => _value;
            set { _value = Math.Min(Math.Max(0, value), _maximum); Invalidate(); }
        }

        public int Maximum
        {
            get => _maximum;
            set { _maximum = Math.Max(1, value); Invalidate(); }
        }

        public Color ProgressColor
        {
            get => _progressColor;
            set { _progressColor = value; Invalidate(); }
        }

        public ProgressBarModern()
        {
            Height = 8;
            BackColor = Color.FromArgb(240, 240, 240);
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            e.Graphics.SmoothingMode = SmoothingMode.AntiAlias;

            // Background
            using (var path = GetRoundedRectPath(ClientRectangle, 4))
            {
                e.Graphics.FillPath(new SolidBrush(BackColor), path);
            }

            // Progress
            if (_value > 0)
            {
                int progressWidth = (int)((double)_value / _maximum * Width);
                var progressRect = new Rectangle(0, 0, progressWidth, Height);
                using (var path = GetRoundedRectPath(progressRect, 4))
                using (var brush = new LinearGradientBrush(progressRect, 
                    _progressColor, 
                    ControlPaint.Light(_progressColor, 0.3f), 
                    LinearGradientMode.Horizontal))
                {
                    e.Graphics.FillPath(brush, path);
                }
            }
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
    }

    public class StatBar : Control
    {
        private string _label = "";
        private int _value = 50;
        private int _maxValue = 100;
        private Color _barColor = Theme.Primary;

        public string Label
        {
            get => _label;
            set { _label = value; Invalidate(); }
        }

        public int Value
        {
            get => _value;
            set { _value = Math.Min(Math.Max(0, value), _maxValue); Invalidate(); }
        }

        public int MaxValue
        {
            get => _maxValue;
            set { _maxValue = Math.Max(1, value); Invalidate(); }
        }

        public Color BarColor
        {
            get => _barColor;
            set { _barColor = value; Invalidate(); }
        }

        public StatBar()
        {
            Height = 32;
            Font = Theme.UiFont;
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            e.Graphics.SmoothingMode = SmoothingMode.AntiAlias;

            // Draw label
            TextRenderer.DrawText(e.Graphics, _label, Font, new Rectangle(0, 0, 100, Height),
                Theme.Dark, TextFormatFlags.VerticalCenter);

            // Draw bar background
            var barRect = new Rectangle(110, 6, Width - 180, 20);
            using (var path = GetRoundedRectPath(barRect, 10))
            {
                e.Graphics.FillPath(new SolidBrush(Color.FromArgb(240, 240, 240)), path);
            }

            // Draw bar fill
            if (_value > 0)
            {
                int fillWidth = (int)((double)_value / _maxValue * barRect.Width);
                var fillRect = new Rectangle(barRect.X, barRect.Y, fillWidth, barRect.Height);
                using (var path = GetRoundedRectPath(fillRect, 10))
                using (var brush = new LinearGradientBrush(fillRect,
                    _barColor,
                    ControlPaint.Light(_barColor, 0.3f),
                    LinearGradientMode.Horizontal))
                {
                    e.Graphics.FillPath(brush, path);
                }
            }

            // Draw value text
            TextRenderer.DrawText(e.Graphics, _value.ToString(), Font, 
                new Rectangle(Width - 60, 0, 60, Height),
                Theme.Dark, TextFormatFlags.VerticalCenter | TextFormatFlags.Right);
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
    }
}
