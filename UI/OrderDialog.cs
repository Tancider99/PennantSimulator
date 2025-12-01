using System;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using PennantSimulator.Models;

namespace PennantSimulator.UI
{
    public class OrderDialog : Form
    {
        private Team _team;
        private ListBox _orderList;
        private Button _upButton;
        private Button _downButton;
        private Button _saveButton;
        private Button _cancelButton;

        public OrderDialog(Team team)
        {
            _team = team ?? throw new ArgumentNullException(nameof(team));
            Text = $"Set Lineup - {_team.Name}";
            Width = 480;
            Height = 640;
            StartPosition = FormStartPosition.CenterParent;

            var main = new TableLayoutPanel { Dock = DockStyle.Fill, RowCount = 3 };
            main.RowStyles.Add(new RowStyle(SizeType.Absolute, 40));
            main.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
            main.RowStyles.Add(new RowStyle(SizeType.Absolute, 60));
            Controls.Add(main);

            var header = new Label { Text = "Drag or use Up/Down to arrange batting order. Top 9 are starters.", Dock = DockStyle.Fill, TextAlign = ContentAlignment.MiddleLeft, Padding = new Padding(8) };
            main.Controls.Add(header, 0, 0);

            _orderList = new ListBox { Dock = DockStyle.Fill, Font = new Font("Consolas", 10), AllowDrop = true, SelectionMode = SelectionMode.One };
            _orderList.MouseDown += OrderList_MouseDown;
            _orderList.DragOver += OrderList_DragOver;
            _orderList.DragDrop += OrderList_DragDrop;
            main.Controls.Add(_orderList, 0, 1);

            var ctlPanel = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.LeftToRight, Padding = new Padding(8) };
            _upButton = new Button { Text = "Up", Width = 80, Height = 36 };
            _downButton = new Button { Text = "Down", Width = 80, Height = 36 };
            _saveButton = new Button { Text = "Save", Width = 120, Height = 40, BackColor = Color.FromArgb(40, 167, 69), ForeColor = Color.White }; _saveButton.Click += SaveButton_Click;
            _cancelButton = new Button { Text = "Cancel", Width = 100, Height = 36 }; _cancelButton.Click += (s, e) => { DialogResult = DialogResult.Cancel; Close(); };

            _upButton.Click += UpButton_Click;
            _downButton.Click += DownButton_Click;

            ctlPanel.Controls.Add(_upButton);
            ctlPanel.Controls.Add(_downButton);
            ctlPanel.Controls.Add(new Panel { Width = 20 });
            ctlPanel.Controls.Add(_saveButton);
            ctlPanel.Controls.Add(_cancelButton);

            main.Controls.Add(ctlPanel, 0, 2);

            RefreshList();
        }

        private void RefreshList()
        {
            _orderList.Items.Clear();
            if (_team.Roster == null) return;
            for (int i = 0; i < _team.Roster.Count; i++)
            {
                var p = _team.Roster[i];
                string role = i < 9 ? i + 1 + "." : "Bench ";
                _orderList.Items.Add($"{role} {p.Name}  OVR:{p.OverallSkill:F0}  C:{p.Contact} P:{p.Power}");
            }
        }

        private void UpButton_Click(object? sender, EventArgs e)
        {
            int idx = _orderList.SelectedIndex;
            if (idx > 0)
            {
                var item = _team.Roster[idx];
                _team.Roster.RemoveAt(idx);
                _team.Roster.Insert(idx - 1, item);
                RefreshList();
                _orderList.SelectedIndex = idx - 1;
            }
        }

        private void DownButton_Click(object? sender, EventArgs e)
        {
            int idx = _orderList.SelectedIndex;
            if (idx >= 0 && idx < _team.Roster.Count - 1)
            {
                var item = _team.Roster[idx];
                _team.Roster.RemoveAt(idx);
                _team.Roster.Insert(idx + 1, item);
                RefreshList();
                _orderList.SelectedIndex = idx + 1;
            }
        }

        private void SaveButton_Click(object? sender, EventArgs e)
        {
            // roster already modified in-place by up/down and drag-drop
            DialogResult = DialogResult.OK;
            Close();
        }

        // drag-drop support
        private int _dragIndex = -1;
        private void OrderList_MouseDown(object? sender, MouseEventArgs e)
        {
            int idx = _orderList.IndexFromPoint(e.Location);
            if (idx >= 0 && idx < _orderList.Items.Count)
            {
                _dragIndex = idx;
                _orderList.DoDragDrop(_orderList.Items[idx], DragDropEffects.Move);
            }
        }

        private void OrderList_DragOver(object? sender, DragEventArgs e)
        {
            e.Effect = DragDropEffects.Move;
        }

        private void OrderList_DragDrop(object? sender, DragEventArgs e)
        {
            var point = _orderList.PointToClient(new Point(e.X, e.Y));
            int idx = _orderList.IndexFromPoint(point);
            if (idx < 0) idx = _orderList.Items.Count - 1;
            if (_dragIndex < 0 || _dragIndex >= _team.Roster.Count) return;
            if (idx == _dragIndex) return;

            var item = _team.Roster[_dragIndex];
            _team.Roster.RemoveAt(_dragIndex);
            _team.Roster.Insert(idx, item);
            RefreshList();
            _orderList.SelectedIndex = idx;
            _dragIndex = -1;
        }
    }
}
