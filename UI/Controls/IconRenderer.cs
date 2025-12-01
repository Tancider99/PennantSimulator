using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;

namespace PennantSimulator.UI.Controls
{
    public static class IconRenderer
    {
        // Simple icon drawing using Graphics paths
        public static void DrawBaseballIcon(Graphics g, Rectangle bounds, Color color)
        {
            g.SmoothingMode = SmoothingMode.AntiAlias;
            
            // Draw baseball circle
            using (var brush = new SolidBrush(color))
            {
                g.FillEllipse(brush, bounds);
            }

            // Draw stitches
            using (var pen = new Pen(ControlPaint.Light(color, 0.3f), 2))
            {
                var centerY = bounds.Top + bounds.Height / 2;
                var arcRect = new Rectangle(bounds.Left + 5, centerY - 10, bounds.Width - 10, 20);
                g.DrawArc(pen, arcRect, -30, 60);
                g.DrawArc(pen, arcRect, 150, 60);
            }
        }

        public static void DrawBatIcon(Graphics g, Rectangle bounds, Color color)
        {
            g.SmoothingMode = SmoothingMode.AntiAlias;
            
            using (var pen = new Pen(color, 3))
            {
                // Draw bat shape
                var points = new[]
                {
                    new Point(bounds.Left + 5, bounds.Bottom - 5),
                    new Point(bounds.Right - 5, bounds.Top + 5)
                };
                g.DrawLine(pen, points[0], points[1]);
                
                // Draw handle
                g.DrawEllipse(pen, bounds.Right - 8, bounds.Top + 2, 6, 6);
            }
        }

        public static void DrawTrophyIcon(Graphics g, Rectangle bounds, Color color)
        {
            g.SmoothingMode = SmoothingMode.AntiAlias;
            
            using (var brush = new SolidBrush(color))
            {
                // Cup
                var cupRect = new Rectangle(bounds.Left + bounds.Width / 4, bounds.Top + 5, 
                    bounds.Width / 2, bounds.Height / 2);
                g.FillRectangle(brush, cupRect);
                
                // Handles
                g.DrawArc(new Pen(color, 2), bounds.Left + 2, bounds.Top + 8, 10, 10, 90, 180);
                g.DrawArc(new Pen(color, 2), bounds.Right - 12, bounds.Top + 8, 10, 10, 270, 180);
                
                // Base
                var baseRect = new Rectangle(bounds.Left + bounds.Width / 3, bounds.Bottom - 10, 
                    bounds.Width / 3, 8);
                g.FillRectangle(brush, baseRect);
            }
        }

        public static void DrawStarIcon(Graphics g, Rectangle bounds, Color color)
        {
            g.SmoothingMode = SmoothingMode.AntiAlias;
            
            var centerX = bounds.Left + bounds.Width / 2f;
            var centerY = bounds.Top + bounds.Height / 2f;
            var radius = Math.Min(bounds.Width, bounds.Height) / 2f;
            
            var points = new PointF[10];
            for (int i = 0; i < 10; i++)
            {
                double angle = i * Math.PI / 5 - Math.PI / 2;
                float r = (i % 2 == 0) ? radius : radius * 0.4f;
                points[i] = new PointF(
                    centerX + (float)(r * Math.Cos(angle)),
                    centerY + (float)(r * Math.Sin(angle))
                );
            }
            
            using (var brush = new SolidBrush(color))
            {
                g.FillPolygon(brush, points);
            }
        }

        public static void DrawHeartIcon(Graphics g, Rectangle bounds, Color color)
        {
            g.SmoothingMode = SmoothingMode.AntiAlias;
            
            using (var path = new GraphicsPath())
            {
                var centerX = bounds.Left + bounds.Width / 2f;
                var top = bounds.Top + bounds.Height * 0.3f;
                
                // Left side
                path.AddArc(bounds.Left, bounds.Top, bounds.Width / 2, bounds.Height / 2, 180, 180);
                // Right side
                path.AddArc(centerX, bounds.Top, bounds.Width / 2, bounds.Height / 2, 180, 180);
                // Bottom point
                path.AddLine(bounds.Right, top, centerX, bounds.Bottom);
                path.AddLine(centerX, bounds.Bottom, bounds.Left, top);
                
                using (var brush = new SolidBrush(color))
                {
                    g.FillPath(brush, path);
                }
            }
        }

        public static void DrawLightningIcon(Graphics g, Rectangle bounds, Color color)
        {
            g.SmoothingMode = SmoothingMode.AntiAlias;
            
            var points = new[]
            {
                new Point(bounds.Right - 5, bounds.Top),
                new Point(bounds.Left + bounds.Width / 2, bounds.Top + bounds.Height / 2),
                new Point(bounds.Right - 3, bounds.Top + bounds.Height / 2),
                new Point(bounds.Left + 5, bounds.Bottom),
                new Point(bounds.Left + bounds.Width / 2, bounds.Top + bounds.Height / 2 + 2),
                new Point(bounds.Left + 3, bounds.Top + bounds.Height / 2),
            };
            
            using (var brush = new SolidBrush(color))
            {
                g.FillPolygon(brush, points);
            }
        }

        public static void DrawChartIcon(Graphics g, Rectangle bounds, Color color)
        {
            g.SmoothingMode = SmoothingMode.AntiAlias;
            
            using (var pen = new Pen(color, 2))
            {
                // Bars
                int barWidth = bounds.Width / 4;
                g.DrawLine(pen, bounds.Left + 5, bounds.Bottom - 5, bounds.Left + 5, bounds.Bottom - 15);
                g.DrawLine(pen, bounds.Left + 5 + barWidth, bounds.Bottom - 5, bounds.Left + 5 + barWidth, bounds.Bottom - 25);
                g.DrawLine(pen, bounds.Left + 5 + barWidth * 2, bounds.Bottom - 5, bounds.Left + 5 + barWidth * 2, bounds.Bottom - 20);
                g.DrawLine(pen, bounds.Right - 5, bounds.Bottom - 5, bounds.Right - 5, bounds.Bottom - 30);
            }
        }

        public static void DrawGearIcon(Graphics g, Rectangle bounds, Color color)
        {
            g.SmoothingMode = SmoothingMode.AntiAlias;
            
            var centerX = bounds.Left + bounds.Width / 2f;
            var centerY = bounds.Top + bounds.Height / 2f;
            var radius = Math.Min(bounds.Width, bounds.Height) / 2f;
            
            using (var pen = new Pen(color, 2))
            {
                // Outer circle with teeth
                for (int i = 0; i < 8; i++)
                {
                    double angle1 = i * Math.PI / 4;
                    double angle2 = (i + 0.5) * Math.PI / 4;
                    
                    g.DrawLine(pen,
                        centerX + (float)(radius * 0.7 * Math.Cos(angle1)),
                        centerY + (float)(radius * 0.7 * Math.Sin(angle1)),
                        centerX + (float)(radius * Math.Cos(angle1)),
                        centerY + (float)(radius * Math.Sin(angle1))
                    );
                }
                
                // Inner circle
                g.DrawEllipse(pen, centerX - radius * 0.4f, centerY - radius * 0.4f, 
                    radius * 0.8f, radius * 0.8f);
            }
        }
    }
}
