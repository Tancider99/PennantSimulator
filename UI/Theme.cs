using System.Drawing;
using System.Windows.Forms;

namespace PennantSimulator.UI
{
    internal static class Theme
    {
        public static readonly Color Primary = Color.FromArgb(10, 132, 255);
        public static readonly Color Accent = Color.FromArgb(255, 159, 10);
        public static readonly Color Background = Color.FromArgb(250, 250, 252);
        public static readonly Color Panel = Color.FromArgb(245, 247, 250);
        public static readonly Color Dark = Color.FromArgb(30, 30, 30);
        public static readonly Font TitleFont = new Font("Segoe UI", 16, FontStyle.Bold);
        public static readonly Font UiFont = new Font("Segoe UI", 10);

        public static void StyleButton(Button b)
        {
            b.FlatStyle = FlatStyle.Flat;
            b.FlatAppearance.BorderSize = 0;
            b.BackColor = Primary;
            b.ForeColor = Color.White;
            b.Font = UiFont;
        }

        public static void StyleToolbarButton(ToolStripButton b)
        {
            b.DisplayStyle = ToolStripItemDisplayStyle.Text;
            b.ForeColor = Primary;
            b.Font = UiFont;
        }
    }
}
