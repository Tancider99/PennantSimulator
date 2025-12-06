using System.Drawing;
using System.Windows.Forms;

namespace PennantSimulator.UI
{
    internal static class Theme
    {
        // OOTP-inspired Dark Theme
        public static readonly Color Primary = Color.FromArgb(0, 122, 204);      // A strong blue for accents and primary actions
        public static readonly Color Accent = Color.FromArgb(204, 140, 0);       // Muted gold/orange for highlights
        public static readonly Color Background = Color.FromArgb(28, 28, 28);      // Very dark grey, for main window backgrounds
        public static readonly Color Panel = Color.FromArgb(45, 45, 48);           // Lighter dark grey, for cards, panels, and controls
        public static readonly Color Text = Color.FromArgb(241, 241, 241);           // Off-white for body text and labels

        public static readonly Font TitleFont = new Font("Segoe UI", 16, FontStyle.Bold);
        public static readonly Font UiFont = new Font("Segoe UI", 10);

        public static void StyleButton(Button b)
        {
            b.FlatStyle = FlatStyle.Flat;
            b.FlatAppearance.BorderSize = 0;
            b.BackColor = Panel; // Use Panel color for button background
            b.ForeColor = Text;   // Use Text color for button foreground
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
