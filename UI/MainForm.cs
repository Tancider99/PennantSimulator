using System;
using System.Drawing;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using PennantSimulator.Core;
using PennantSimulator.Models;
using System.Collections.Generic;

namespace PennantSimulator.UI
{
    public class MainForm : Form
    {
        private League _league;
        private Panel _leftPanel;
        private TextBox _searchBox;
        private ListBox _teamList;
        private ToolStrip _toolBar;
        private ToolStripButton _newBtn;
        private ToolStripButton _tradeBtn;
        private ToolStripButton _draftBtn;
        private ToolStripButton _simulateBtn;
        private TabControl _tabs;
        private TabPage _dashTab;
        private TabPage _standingsTab;
        private TabPage _rosterTab;
        private TabPage _managerTab;
        private DataGridView _standingsGrid;
        private DataGridView _rosterGrid;
        private Label _dashTitle;
        private StatusStrip _status;
        private ToolStripStatusLabel _statusLabel;
        private CancellationTokenSource? _simCts;

        private int _initialTeamIndex;
        private bool _startManager;
        private int _gamesPerTeam;

        private SeasonManager? _seasonManager;
        private GameState? _currentGame;
        private ListBox _gameLog;
        private Label _scoreLabel;

        public MainForm(League league)
            : this(league, 0, false, 143)
        {
        }

        public MainForm(League league, int initialTeamIndex, bool startManager, int gamesPerTeam)
        {
            _league = league ?? throw new ArgumentNullException(nameof(league));
            _initialTeamIndex = initialTeamIndex;
            _startManager = startManager;
            _gamesPerTeam = gamesPerTeam;

            Text = "Pennant Simulator";
            Width = 1200;
            Height = 800;
            BackColor = Theme.Background;
            Font = Theme.UiFont;

            FormBorderStyle = FormBorderStyle.Sizable;

            InitializeToolbar();
            InitializeLeftPanel();
            InitializeTabs();
            InitializeStatus();

            // layout
            var main = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 2 };
            main.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 300));
            main.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
            main.RowCount = 2;
            main.RowStyles.Add(new RowStyle(SizeType.Absolute, 40));
            main.RowStyles.Add(new RowStyle(SizeType.Percent, 100));

            main.Controls.Add(_toolBar, 0, 0);
            main.SetColumnSpan(_toolBar, 2);
            main.Controls.Add(_leftPanel, 0, 1);
            main.Controls.Add(_tabs, 1, 1);

            Controls.Add(main);
            Controls.Add(_status);

            // initial selection
            if (_league.Teams.Any())
            {
                _teamList.Items.Clear();
                foreach (var t in _league.Teams) _teamList.Items.Add(t.Name);
                _teamList.SelectedIndex = Math.Min(Math.Max(0, _initialTeamIndex), _league.Teams.Count - 1);
            }

            if (_startManager)
            {
                _tabs.SelectedTab = _managerTab;
            }

            RenderDashboard();
        }

        private void InitializeToolbar()
        {
            _toolBar = new ToolStrip { Dock = DockStyle.None, GripStyle = ToolStripGripStyle.Hidden, BackColor = Theme.Panel, Padding = new Padding(8) };

            _newBtn = new ToolStripButton("New Game");
            _newBtn.Click += (s, e) => StartButton_Click(s, e);
            _tradeBtn = new ToolStripButton("Trade");
            _tradeBtn.Click += (s, e) => OpenTradeDialog();
            _draftBtn = new ToolStripButton("Draft");
            _draftBtn.Click += (s, e) => OpenDraftDialog();
            _simulateBtn = new ToolStripButton("Simulate Season");
            _simulateBtn.Click += async (s, e) => await SimulateSeasonAsync(_gamesPerTeam);

            foreach (var b in new[] { _newBtn, _tradeBtn, _draftBtn, _simulateBtn }) Theme.StyleToolbarButton(b);

            _toolBar.Items.Add(_newBtn);
            _toolBar.Items.Add(new ToolStripSeparator());
            _toolBar.Items.Add(_tradeBtn);
            _toolBar.Items.Add(_draftBtn);
            _toolBar.Items.Add(new ToolStripSeparator());
            _toolBar.Items.Add(_simulateBtn);
            // place search on the right
            // create search box and host it in toolstrip (right aligned)
            _searchBox = new TextBox { Width = 200 };
            _searchBox.TextChanged += (s, e) => FilterTeams(_searchBox.Text);
            var searchLabel = new ToolStripLabel("Search:") { Alignment = ToolStripItemAlignment.Right };
            var host = new ToolStripControlHost(_searchBox) { Alignment = ToolStripItemAlignment.Right };
            _toolBar.Items.Add(searchLabel);
            _toolBar.Items.Add(host);
        }

        private void InitializeLeftPanel()
        {
            _leftPanel = new Panel { Dock = DockStyle.Fill, BackColor = Theme.Panel, Padding = new Padding(12) };

            var title = new Label { Text = "Teams", Font = Theme.TitleFont, Dock = DockStyle.Top, Height = 36 };
            _leftPanel.Controls.Add(title);

            _teamList = new ListBox { Dock = DockStyle.Fill, Font = Theme.UiFont, BackColor = Color.White, ForeColor = Theme.Dark }; 
            _teamList.SelectedIndexChanged += TeamList_SelectedIndexChanged;
            _leftPanel.Controls.Add(_teamList);

            var money = new Label { Text = "", Dock = DockStyle.Bottom, Height = 24, TextAlign = ContentAlignment.MiddleLeft };
            _leftPanel.Controls.Add(money);
        }

        private void InitializeTabs()
        {
            _tabs = new TabControl { Dock = DockStyle.Fill, Font = Theme.UiFont };
            _dashTab = new TabPage("Dashboard");
            _standingsTab = new TabPage("Standings");
            _rosterTab = new TabPage("Roster");
            _managerTab = new TabPage("Manager");

            _tabs.TabPages.AddRange(new[] { _dashTab, _standingsTab, _rosterTab, _managerTab });
            _tabs.SelectedIndexChanged += (s, e) => { if (_tabs.SelectedTab == _standingsTab) RenderStandings(); };

            // Dashboard
            _dashTitle = new Label { Text = "Welcome to Pennant Simulator", Font = Theme.TitleFont, Dock = DockStyle.Top, Height = 40 };
            var dashBody = new TextBox { Multiline = true, ReadOnly = true, Dock = DockStyle.Fill, BackColor = Theme.Background, BorderStyle = BorderStyle.None, Text = "Use the toolbar to start a new game, manage trades, and run simulations.\r\nSelect a team to view roster and manager options." };
            _dashTab.Controls.Add(dashBody);
            _dashTab.Controls.Add(_dashTitle);

            // Standings
            _standingsGrid = new DataGridView { Dock = DockStyle.Fill, ReadOnly = true, AllowUserToAddRows = false, AllowUserToDeleteRows = false, AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill };
            _standingsTab.Controls.Add(_standingsGrid);

            // Roster
            _rosterGrid = new DataGridView { Dock = DockStyle.Fill, ReadOnly = true, AllowUserToAddRows = false, AllowUserToDeleteRows = false, AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill };
            _rosterTab.Controls.Add(_rosterGrid);

            // Manager
            var mgrPanel = new FlowLayoutPanel { Dock = DockStyle.Top, Height = 220, FlowDirection = FlowDirection.LeftToRight, Padding = new Padding(8) };
            var playBtn = new Button { Text = "Play Next Match (Full)", Width = 160, Height = 36 };
            Theme.StyleButton(playBtn);
            playBtn.Click += (s, e) => { if (_teamList.SelectedIndex >= 0) PlayNextMatchFor(_league.Teams[_teamList.SelectedIndex]); };
            var stepBtn = new Button { Text = "Play Next Half-Inning", Width = 160, Height = 36 };
            Theme.StyleButton(stepBtn);
            stepBtn.Click += (s, e) => { if (_currentGame != null) PlayNextHalfInCurrentGame(); };
            var setLineupBtn = new Button { Text = "Set Lineup", Width = 120, Height = 36 };
            Theme.StyleButton(setLineupBtn);
            setLineupBtn.Click += (s, e) => { if (_teamList.SelectedIndex >= 0) { using var dlg = new OrderDialog(_league.Teams[_teamList.SelectedIndex]); if (dlg.ShowDialog(this) == DialogResult.OK) RenderRoster(); } };
            var simOneBtn = new Button { Text = "Simulate One Game", Width = 160, Height = 36 };
            Theme.StyleButton(simOneBtn);
            simOneBtn.Click += (s, e) => { if (_teamList.SelectedIndex >= 0) SimulateSingleGameForSelected(); };

            mgrPanel.Controls.Add(playBtn);
            mgrPanel.Controls.Add(stepBtn);
            mgrPanel.Controls.Add(setLineupBtn);
            mgrPanel.Controls.Add(simOneBtn);
            _managerTab.Controls.Add(mgrPanel);

            // game log and scoreboard
            _gameLog = new ListBox { Dock = DockStyle.Left, Width = 420, Font = new Font("Consolas", 10), BackColor = Color.White };
            _managerTab.Controls.Add(_gameLog);
            var rightPanel = new Panel { Dock = DockStyle.Fill, Padding = new Padding(8) };
            _scoreLabel = new Label { Text = "Score: 0 - 0", Font = Theme.TitleFont, Dock = DockStyle.Top, Height = 48 };
            rightPanel.Controls.Add(_scoreLabel);
            _managerTab.Controls.Add(rightPanel);

            // team details placeholder under manager
            var mgrDetails = new Panel { Dock = DockStyle.Fill, Padding = new Padding(8) };
            _managerTab.Controls.Add(mgrDetails);
        }

        private void InitializeStatus()
        {
            _status = new StatusStrip();
            _statusLabel = new ToolStripStatusLabel("Ready");
            _status.Items.Add(_statusLabel);
        }

        private void FilterTeams(string q)
        {
            _teamList.BeginUpdate();
            _teamList.Items.Clear();
            foreach (var t in _league.Teams.Where(x => string.IsNullOrEmpty(q) || x.Name.IndexOf(q, StringComparison.OrdinalIgnoreCase) >= 0)) _teamList.Items.Add(t.Name);
            _teamList.EndUpdate();
        }

        private void TeamList_SelectedIndexChanged(object? sender, EventArgs e)
        {
            RenderRoster();
            RenderManagerView();
        }

        private void RenderDashboard()
        {
            _tabs.SelectedTab = _dashTab;
            _statusLabel.Text = "Ready";
        }

        private void RenderStandings()
        {
            var list = _league.GetStandings().Select((t, i) => new { Pos = i + 1, t.Name, t.Wins, t.Losses, t.Ties, Pct = t.WinPercentage }).ToList();
            _standingsGrid.DataSource = list;
            _tabs.SelectedTab = _standingsTab;
            _statusLabel.Text = "Standings updated";
        }

        private void RenderRoster()
        {
            if (_teamList.SelectedIndex < 0) return;
            var team = _league.Teams[_teamList.SelectedIndex];
            var rows = team.Roster.Select(p => new { p.Name, OVR = (int)Math.Round(p.OverallSkill), p.Contact, p.Power, p.Speed, p.Stamina }).ToList();
            _rosterGrid.DataSource = rows;
            _tabs.SelectedTab = _rosterTab;
            _statusLabel.Text = $"Showing roster for {team.Name}";
        }

        private void RenderManagerView()
        {
            if (_teamList.SelectedIndex < 0) return;
            var team = _league.Teams[_teamList.SelectedIndex];
            _tabs.SelectedTab = _managerTab;
            _statusLabel.Text = $"Manager - {team.Name}";
        }

        private void StartButton_Click(object? sender, EventArgs e)
        {
            using var dlg = new NewGameDialog();
            if (dlg.ShowDialog(this) == DialogResult.OK)
            {
                var league = ProgramBootstrap.CreateLeague();
                var main = new MainForm(league, dlg.SelectedTeamIndex, dlg.StartAsManager, dlg.GamesPerTeam);
                Hide();
                main.ShowDialog(this);
                Close();
            }
        }

        private async Task SimulateSeasonAsync(int gamesPerTeam)
        {
            if (_simCts != null)
            {
                // already running
                _statusLabel.Text = "Simulation already running";
                return;
            }

            _simCts = new CancellationTokenSource();
            _statusLabel.Text = "Simulating season...";
            _simulateBtn.Enabled = false;

            try
            {
                await Task.Run(() => SeasonSimulator.Simulate(_league, gamesPerTeam), _simCts.Token);
                _statusLabel.Text = "Simulation complete";
                RenderStandings();
            }
            catch (OperationCanceledException)
            {
                _statusLabel.Text = "Simulation cancelled";
            }
            finally
            {
                _simulateBtn.Enabled = true;
                _simCts = null;
            }
        }

        private void OpenTradeDialog()
        {
            using (var dlg = new TradeDialog(_league))
            {
                if (dlg.ShowDialog(this) == DialogResult.OK)
                {
                    RenderRoster();
                }
            }
        }

        private void OpenDraftDialog()
        {
            using (var dlg = new DraftDialog(_league))
            {
                if (dlg.ShowDialog(this) == DialogResult.OK)
                {
                    RenderRoster();
                }
            }
        }

        private void PlayNextMatchFor(Team team)
        {
            if (_seasonManager == null) _seasonManager = SeasonManager.CreateSchedule(_league, _gamesPerTeam);
            var match = _seasonManager.GetNextMatchFor(team);
            if (match == null)
            {
                MessageBox.Show(this, "No more scheduled matches for this team.", "Schedule", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            // pick home/away as scheduled
            var home = match.Home;
            var away = match.Away;

            _currentGame = new GameState(home, away);
            _gameLog.Items.Clear();
            _scoreLabel.Text = "Score: 0 - 0";

            // play full game sequentially
            while (!_currentGame.Finished)
            {
                var (runs, summary) = _currentGame.PlayNextHalf();
                _gameLog.Items.Add(summary);
            }

            var (homeScore, awayScore) = _currentGame.GetScore();
            _gameLog.Items.Add($"Final: {home.Name} {homeScore} - {away.Name} {awayScore}");
            _currentGame.ApplyResultToTeams();
            _seasonManager.MarkPlayed(match);
            RenderStandings();
            RenderRoster();
        }

        private void PlayNextHalfInCurrentGame()
        {
            if (_currentGame == null)
            {
                MessageBox.Show(this, "No game in progress.", "Game", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            var (runs, summary) = _currentGame.PlayNextHalf();
            _gameLog.Items.Add(summary);
            var (h, a) = _currentGame.GetScore();
            _scoreLabel.Text = $"Score: {h} - {a}";

            if (_currentGame.Finished)
            {
                var home = _currentGame.Home; var away = _currentGame.Away;
                var (homeScore, awayScore) = _currentGame.GetScore();
                _gameLog.Items.Add($"Final: {home.Name} {homeScore} - {away.Name} {awayScore}");
                _currentGame.ApplyResultToTeams();
                _seasonManager?.MarkPlayed(_seasonManager.GetNextMatchFor(home) ?? _seasonManager.Matches.FirstOrDefault(m => m.Home == home && m.Away == away));
                RenderStandings();
                RenderRoster();
            }
        }

        private void SimulateSingleGameForSelected()
        {
            if (_teamList.SelectedIndex < 0) return;
            var team = _league.Teams[_teamList.SelectedIndex];

            using var dlg = new Form { Width = 420, Height = 220, Text = "Select Opponent", StartPosition = FormStartPosition.CenterParent };
            var cb = new ComboBox { Dock = DockStyle.Top, DropDownStyle = ComboBoxStyle.DropDownList };
            foreach (var t in _league.Teams.Where(t => t != team)) cb.Items.Add(t.Name);
            if (cb.Items.Count == 0) return;
            cb.SelectedIndex = 0;
            dlg.Controls.Add(cb);
            var ok = new Button { Text = "OK", Dock = DockStyle.Bottom, Height = 36 };
            ok.Click += (s, e) => { dlg.DialogResult = DialogResult.OK; dlg.Close(); };
            dlg.Controls.Add(ok);
            if (dlg.ShowDialog(this) == DialogResult.OK)
            {
                var oppName = cb.SelectedItem.ToString();
                var opp = _league.Teams.First(t => t.Name == oppName);
                var result = SeasonSimulator.SimulateSingleGame(team, opp);

                // Log result
                _gameLog.Items.Clear();
                _gameLog.Items.Add($"{team.Name} {result.RunsA} - {opp.Name} {result.RunsB}");
                _scoreLabel.Text = $"Score: {result.RunsA} - {result.RunsB}";

                RenderStandings();
                RenderRoster();
            }
        }

    }
}
