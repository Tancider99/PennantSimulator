using System;
using System.Drawing;
using System.IO;
using System.Windows.Forms;
using PennantSimulator.Core;
using PennantSimulator.Data;

namespace PennantSimulator.UI
{
    public class SaveLoadDialog : Form
    {
        private League _league;
        private TextBox _pathBox;

        public SaveLoadDialog(League league)
        {
            _league = league ?? throw new ArgumentNullException(nameof(league));
            Width = 560;
            Height = 160;
            StartPosition = FormStartPosition.CenterParent;
            Text = "Save / Load League";

            var lbl = new Label { Text = "File Path:", Dock = DockStyle.Top };
            _pathBox = new TextBox { Dock = DockStyle.Top, Text = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "league.json") };
            var btnSave = new Button { Text = "Save", Dock = DockStyle.Left, Width = 120 };
            btnSave.Click += (s, e) => { Save(); };
            var btnLoad = new Button { Text = "Load", Dock = DockStyle.Right, Width = 120 };
            btnLoad.Click += (s, e) => { Load(); };

            Controls.Add(btnLoad);
            Controls.Add(btnSave);
            Controls.Add(_pathBox);
            Controls.Add(lbl);
        }

        private void Save()
        {
            try
            {
                SaveService.SaveLeague(_pathBox.Text, _league);
                MessageBox.Show(this, "Saved.", "Save", MessageBoxButtons.OK, MessageBoxIcon.Information);
                DialogResult = DialogResult.OK;
                Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show(this, ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void Load()
        {
            try
            {
                var l = SaveService.LoadLeague(_pathBox.Text);
                if (l == null) { MessageBox.Show(this, "Failed to load.", "Load", MessageBoxButtons.OK, MessageBoxIcon.Warning); return; }
                // copy data into current league reference
                _league.Teams.Clear();
                foreach (var t in l.Teams) _league.Teams.Add(t);
                MessageBox.Show(this, "Loaded.", "Load", MessageBoxButtons.OK, MessageBoxIcon.Information);
                DialogResult = DialogResult.OK;
                Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show(this, ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }
}
