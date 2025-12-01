using System;
using System.Windows.Forms;
using PennantSimulator.Models;
using PennantSimulator.Core;
using PennantSimulator.UI;

namespace PennantSimulator
{
    internal static class Program
    {
        [STAThread]
        private static void Main()
        {
            Application.SetHighDpiMode(HighDpiMode.SystemAware);
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            // Start with ModernMainForm directly (modern UI)
            var league = ProgramBootstrap.CreateLeague();
            using var main = new ModernMainForm(league);
            Application.Run(main);
        }
    }
}
