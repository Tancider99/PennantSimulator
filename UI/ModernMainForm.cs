using System;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using System.Collections.Generic;
using PennantSimulator.Core;
using PennantSimulator.Models;
using PennantSimulator.UI.Controls;

namespace PennantSimulator.UI
{
    public class ModernMainForm : Form
    {
        private League _league;
        private Panel _navPanel;
        private FlowLayoutPanel _teamFlow;
        private TextBox _searchBox;
        private Panel _contentPanel;
        private Label _headerTitle;
        private DataGridView _standingsGrid;
        private FlowLayoutPanel _rosterFlow;
        private SeasonManager? _seasonManager;
        private GameState? _currentGame;
        private ListBox _gameLog;
        private Label _scoreLabel;
        private System.Windows.Forms.Timer _uiUpdateTimer;
        private Team? _selectedTeam;  // 現在選択中のチーム

        private int _gamesPerTeam;

        public ModernMainForm(League league, int initialTeamIndex = 0, bool startManager = false, int gamesPerTeam = 143)
        {
            _league = league ?? throw new ArgumentNullException(nameof(league));
            _gamesPerTeam = gamesPerTeam;

            Text = "Pennant - Professional Edition";
            Width = 1600;
            Height = 1000;
            BackColor = Theme.Background;
            Font = Theme.UiFont;
            FormBorderStyle = FormBorderStyle.Sizable;
            DoubleBuffered = true;

            // UI update timer for animations
            _uiUpdateTimer = new System.Windows.Forms.Timer { Interval = 100 };
            _uiUpdateTimer.Tick += (s, e) => { /* Reserved for future animations */ };
            _uiUpdateTimer.Start();

            InitializeModernLayout();
            PopulateTeams();
            SelectTeam(initialTeamIndex);

            // Show welcome toast
            NotificationToast.Show("Welcome to Pennant Simulator!", 2000);
        }

        private void InitializeModernLayout()
        {
            // Left navigation with gradient background
            _navPanel = new Panel { Dock = DockStyle.Left, Width = 340, BackColor = Theme.Panel, Padding = new Padding(20) };
            _navPanel.Paint += (s, e) =>
            {
                var rect = ((Panel)s).ClientRectangle;
                using (var brush = new System.Drawing.Drawing2D.LinearGradientBrush(
                    rect, Color.FromArgb(25, 25, 30), Color.FromArgb(18, 18, 22), 
                    System.Drawing.Drawing2D.LinearGradientMode.Vertical))
                {
                    e.Graphics.FillRectangle(brush, rect);
                }
            };
            Controls.Add(_navPanel);

            // Header with icon
            var headerPanel = new Panel { Dock = DockStyle.Top, Height = 60, BackColor = Color.Transparent };
            _headerTitle = new Label { 
                Text = "⚾ Pennant Manager", 
                Font = new Font("Segoe UI", 18, FontStyle.Bold), 
                ForeColor = Theme.Text, 
                Dock = DockStyle.Fill,
                TextAlign = ContentAlignment.MiddleLeft,
                BackColor = Color.Transparent
            };
            headerPanel.Controls.Add(_headerTitle);
            _navPanel.Controls.Add(headerPanel);

            // Modern search box
            var searchPanel = new Panel { Dock = DockStyle.Top, Height = 50, Padding = new Padding(0, 10, 0, 10), BackColor = Color.Transparent };
            _searchBox = new TextBox { 
                PlaceholderText = "🔍 Search teams...", 
                Dock = DockStyle.Fill, 
                BackColor = Theme.Background,
                ForeColor = Theme.Text,
                BorderStyle = BorderStyle.None,
                Font = new Font("Segoe UI", 11)
            };
            _searchBox.TextChanged += (s, e) => PopulateTeams(_searchBox.Text);
            searchPanel.Controls.Add(_searchBox);
            _navPanel.Controls.Add(searchPanel);

            // Team cards flow
            _teamFlow = new FlowLayoutPanel { 
                Dock = DockStyle.Fill, 
                AutoScroll = true, 
                FlowDirection = FlowDirection.TopDown, 
                WrapContents = false,
                BackColor = Color.Transparent
            };
            _navPanel.Controls.Add(_teamFlow);

            // Modern action buttons
            var actions = new FlowLayoutPanel { 
                Dock = DockStyle.Bottom, 
                Height = 250, 
                FlowDirection = FlowDirection.TopDown, 
                Padding = new Padding(0, 10, 0, 10),
                BackColor = Color.Transparent
            };

            var btnNew = CreateActionButton("🎮 New Game", Theme.Primary);
            btnNew.Click += (s, e) => OpeningNewGame();

            var btnOrder = CreateActionButton("📋 オーダー設定", Color.FromArgb(0, 150, 136));
            btnOrder.Click += (s, e) => OpenOrderDialog();

            var btnTrade = CreateActionButton("💼 Trade", Color.FromArgb(255, 193, 7));
            btnTrade.Click += (s, e) => OpenTradeDialog();

            var btnDraft = CreateActionButton("🎯 Draft", Color.FromArgb(76, 175, 80));
            btnDraft.Click += (s, e) => OpenDraftDialog();

            var btnTraining = CreateActionButton("💪 Training", Color.FromArgb(156, 39, 176));
            btnTraining.Click += (s, e) => OpenTrainingDialog();

            var btnSave = CreateActionButton("💾 Save/Load", Color.FromArgb(33, 150, 243));
            btnSave.Click += (s, e) => { 
                using var dlg = new SaveLoadDialog(_league); 
                dlg.ShowDialog(this); 
                PopulateTeams(_searchBox.Text); 
                NotificationToast.Show("Save/Load operation completed!");
            };

            var btnStats = CreateActionButton("📊 Statistics", Color.FromArgb(103, 58, 183));
            btnStats.Click += (s, e) => ShowStatisticsDialog();

            actions.Controls.AddRange(new Control[] { btnNew, btnOrder, btnTrade, btnDraft, btnTraining, btnSave, btnStats });
            _navPanel.Controls.Add(actions);

            // Main content area
            _contentPanel = new Panel { Dock = DockStyle.Fill, Padding = new Padding(30), BackColor = Theme.Background };
            Controls.Add(_contentPanel);

            // Top bar with stats summary
            var topBar = CreateTopBar();
            _contentPanel.Controls.Add(topBar);

            // Tabs with modern styling
            var tabs = CreateModernTabs();
            _contentPanel.Controls.Add(tabs);
        }

        private ModernButton CreateActionButton(string text, Color color)
        {
            var btn = new ModernButton
            {
                Text = text,
                Width = 300,
                Height = 48,
                BackColor = color,
                ForeColor = Color.White, // High-contrast for colored buttons
                Font = new Font("Segoe UI", 11, FontStyle.Bold),
                Margin = new Padding(0, 5, 0, 5),
                CornerRadius = 10
            };
            return btn;
        }

        private Panel CreateTopBar()
        {
            var topBar = new Panel { Dock = DockStyle.Top, Height = 100, BackColor = Color.Transparent };
            
            var titleLabel = new Label { 
                Text = "🏆 Pennant Simulator - Professional Edition", 
                Font = new Font("Segoe UI", 24, FontStyle.Bold), 
                ForeColor = Theme.Text, 
                Dock = DockStyle.Top, 
                Height = 50 
            };
            topBar.Controls.Add(titleLabel);

            var statsFlow = new FlowLayoutPanel { 
                Dock = DockStyle.Fill, 
                FlowDirection = FlowDirection.LeftToRight,
                Padding = new Padding(0, 10, 0, 0)
            };

            // Add stat cards
            statsFlow.Controls.Add(CreateStatCard("Teams", _league.Teams.Count.ToString(), Theme.Primary));
            statsFlow.Controls.Add(CreateStatCard("Players", _league.Teams.Sum(t => t.Roster.Count).ToString(), Theme.Accent));
            statsFlow.Controls.Add(CreateStatCard("Season", $"{_gamesPerTeam} games", Color.FromArgb(76, 175, 80)));

            topBar.Controls.Add(statsFlow);
            return topBar;
        }

        private ModernCard CreateStatCard(string label, string value, Color color)
        {
            var card = new ModernCard { Width = 160, Height = 70, Margin = new Padding(5), Elevation = 2, BackColor = Theme.Panel };
            
            var valueLabel = new Label { 
                Text = value, 
                Font = new Font("Segoe UI", 20, FontStyle.Bold), 
                ForeColor = color,
                Dock = DockStyle.Top, 
                Height = 40,
                TextAlign = ContentAlignment.MiddleCenter,
                BackColor = Color.Transparent
            };
            
            var labelText = new Label { 
                Text = label, 
                Font = Theme.UiFont, 
                ForeColor = Theme.Text,
                Dock = DockStyle.Top, 
                Height = 20,
                TextAlign = ContentAlignment.MiddleCenter,
                BackColor = Color.Transparent
            };

            card.Controls.Add(labelText);
            card.Controls.Add(valueLabel);
            return card;
        }

        private TabControl CreateModernTabs()
        {
            var tabs = new TabControl { 
                Dock = DockStyle.Fill, 
                Font = new Font("Segoe UI", 11),
                Padding = new Point(20, 5)
            };

            var tabDashboard = new TabPage("📊 Dashboard") { BackColor = Theme.Background };
            var tabStandings = new TabPage("🏅 Standings") { BackColor = Theme.Background };
            var tabRoster = new TabPage("👥 Roster") { BackColor = Theme.Background };
            var tabManager = new TabPage("⚡ Manager") { BackColor = Theme.Background };

            tabs.TabPages.AddRange(new[] { tabDashboard, tabStandings, tabRoster, tabManager });

            InitializeDashboardTab(tabDashboard);
            InitializeStandingsTab(tabStandings);
            InitializeRosterTab(tabRoster);
            InitializeManagerTab(tabManager);

            return tabs;
        }

        private void InitializeDashboardTab(TabPage tab)
        {
            var welcomeCard = new ModernCard { Dock = DockStyle.Fill, Padding = new Padding(30), BackColor = Theme.Panel };
            
            var title = new Label { 
                Text = "Welcome to Your Season", 
                Font = new Font("Segoe UI", 20, FontStyle.Bold), 
                Dock = DockStyle.Top, 
                Height = 50,
                ForeColor = Theme.Text,
                BackColor = Color.Transparent
            };
            
            var desc = new Label { 
                Text = "Manage your team, train players, make trades, and lead your franchise to championship glory!\n\n" +
                       "🎮 Use the Manager tab to play matches\n" +
                       "💼 Trade with other teams\n" +
                       "🎯 Draft new talent\n" +
                       "💪 Train your players\n" +
                       "💾 Save your progress", 
                Dock = DockStyle.Fill,
                Font = new Font("Segoe UI", 12),
                ForeColor = Theme.Text,
                BackColor = Color.Transparent
            };

            welcomeCard.Controls.Add(desc);
            welcomeCard.Controls.Add(title);
            tab.Controls.Add(welcomeCard);
        }

        private void InitializeStandingsTab(TabPage tab)
        {
            _standingsGrid = new DataGridView { 
                Dock = DockStyle.Fill, 
                ReadOnly = true, 
                BorderStyle = BorderStyle.None, 
                BackgroundColor = Theme.Panel,
                GridColor = Theme.Background,
                AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill,
                RowHeadersVisible = false,
                AllowUserToAddRows = false,
                SelectionMode = DataGridViewSelectionMode.FullRowSelect,
                EnableHeadersVisualStyles = false
            };
            
            _standingsGrid.DefaultCellStyle.BackColor = Theme.Panel;
            _standingsGrid.DefaultCellStyle.ForeColor = Theme.Text;
            _standingsGrid.DefaultCellStyle.SelectionBackColor = Theme.Primary;
            _standingsGrid.DefaultCellStyle.SelectionForeColor = Color.White;
            _standingsGrid.DefaultCellStyle.Font = new Font("Segoe UI", 10);
            _standingsGrid.ColumnHeadersDefaultCellStyle.BackColor = Theme.Background;
            _standingsGrid.ColumnHeadersDefaultCellStyle.ForeColor = Theme.Text;
            _standingsGrid.ColumnHeadersDefaultCellStyle.Font = new Font("Segoe UI", 11, FontStyle.Bold);
            _standingsGrid.ColumnHeadersHeight = 40;
            _standingsGrid.RowTemplate.Height = 35;

            tab.Controls.Add(_standingsGrid);
            RenderStandings();
        }

        private void InitializeRosterTab(TabPage tab)
        {
            _rosterFlow = new FlowLayoutPanel { 
                Dock = DockStyle.Fill, 
                AutoScroll = true, 
                FlowDirection = FlowDirection.LeftToRight, 
                WrapContents = true, 
                Padding = new Padding(20),
                BackColor = Theme.Background
            };
            tab.Controls.Add(_rosterFlow);
        }

        private void InitializeManagerTab(TabPage tab)
        {
            var managerCard = new ModernCard { Dock = DockStyle.Fill, Padding = new Padding(20), BackColor = Theme.Panel };

            var btnPanel = new FlowLayoutPanel { 
                Dock = DockStyle.Top, 
                Height = 70, 
                FlowDirection = FlowDirection.LeftToRight, 
                Padding = new Padding(5),
                BackColor = Color.Transparent
            };

            var btnPlayMatch = new ModernButton { Text = "▶️ Play Full Match", Width = 180, Height = 50 };
            btnPlayMatch.Click += (s, e) => PlayNextMatchForSelectedTeam();

            var btnStepHalf = new ModernButton { Text = "⏯️ Play Half-Inning", Width = 180, Height = 50 };
            btnStepHalf.Click += (s, e) => PlayNextHalfInCurrentGame();

            btnPanel.Controls.Add(btnPlayMatch);
            btnPanel.Controls.Add(btnStepHalf);
            managerCard.Controls.Add(btnPanel);

            var splitContainer = new SplitContainer { Dock = DockStyle.Fill, Orientation = Orientation.Horizontal, SplitterDistance = 400 };
            
            _gameLog = new ListBox { 
                Dock = DockStyle.Fill, 
                Font = new Font("Consolas", 11),
                BackColor = Theme.Panel,
                ForeColor = Theme.Text,
                BorderStyle = BorderStyle.None
            };
            splitContainer.Panel1.Controls.Add(_gameLog);

            var scorePanel = new ModernCard { Dock = DockStyle.Fill, Padding = new Padding(20), BackColor = Theme.Panel };
            _scoreLabel = new Label { 
                Text = "Score: 0 - 0", 
                Font = new Font("Segoe UI", 28, FontStyle.Bold), 
                ForeColor = Theme.Primary,
                Dock = DockStyle.Fill,
                TextAlign = ContentAlignment.MiddleCenter,
                BackColor = Color.Transparent
            };
            scorePanel.Controls.Add(_scoreLabel);
            splitContainer.Panel2.Controls.Add(scorePanel);

            managerCard.Controls.Add(splitContainer);
            tab.Controls.Add(managerCard);
        }

        private void PopulateTeams(string filter = "")
        {
            _teamFlow.SuspendLayout();
            _teamFlow.Controls.Clear();
            
            var teams = _league.Teams
                .Where(t => string.IsNullOrEmpty(filter) || t.Name.IndexOf(filter, StringComparison.OrdinalIgnoreCase) >= 0)
                .OrderByDescending(t => t.Rating);

            foreach (var t in teams)
            {
                var card = CreateEnhancedTeamCard(t);
                _teamFlow.Controls.Add(card);
            }
            
            _teamFlow.ResumeLayout();
        }

        private ModernCard CreateEnhancedTeamCard(Team t)
        {
            var card = new ModernCard { 
                Width = 300, 
                Height = 110, 
                Margin = new Padding(5),
                BackColor = Theme.Panel
            };

            var nameLabel = new Label { 
                Text = $"⚾ {t.Name}", 
                Font = new Font("Segoe UI", 13, FontStyle.Bold), 
                ForeColor = Theme.Text,
                Dock = DockStyle.Top, 
                Height = 35,
                Padding = new Padding(5),
                BackColor = Color.Transparent
            };
            card.Controls.Add(nameLabel);

            var statsLabel = new Label { 
                Text = $"Record: {t.Wins}W-{t.Losses}L-{t.Ties}T", 
                Font = Theme.UiFont, 
                ForeColor = Theme.Text,
                Dock = DockStyle.Top, 
                Height = 25,
                Padding = new Padding(5),
                BackColor = Color.Transparent
            };
            card.Controls.Add(statsLabel);

            var ratingBar = new ProgressBarModern { 
                Dock = DockStyle.Top, 
                Height = 10, 
                Value = (int)t.Rating,
                Maximum = 100,
                ProgressColor = GetRatingColor(t.Rating),
                Margin = new Padding(5)
            };
            card.Controls.Add(ratingBar);

            var btnSelect = new ModernButton { 
                Text = "Select", 
                Width = 100, 
                Height = 28, 
                Dock = DockStyle.Right,
                CornerRadius = 6
            };
            btnSelect.Click += (s, e) => SelectTeam(_league.Teams.IndexOf(t));
            card.Controls.Add(btnSelect);

            card.Click += (s, e) => SelectTeam(_league.Teams.IndexOf(t));

            return card;
        }

        private Color GetRatingColor(double rating)
        {
            if (rating >= 75) return Color.FromArgb(76, 175, 80); // Green
            if (rating >= 60) return Color.FromArgb(255, 193, 7); // Amber
            return Color.FromArgb(244, 67, 54); // Red
        }

        private void SelectTeam(int index)
        {
            if (index < 0 || index >= _league.Teams.Count) return;
            var team = _league.Teams[index];
            _selectedTeam = team;
            
            RenderRosterForTeam(team);
            RenderStandings();
            NotificationToast.Show($"Selected: {team.Name}");
        }

        private void OpenOrderDialog()
        {
            if (_selectedTeam == null)
            {
                NotificationToast.Show("チームを選択してください");
                return;
            }
            
            using var dlg = new OrderDialog(_selectedTeam);
            if (dlg.ShowDialog(this) == DialogResult.OK)
            {
                RenderRosterForTeam(_selectedTeam);
                PopulateTeams(_searchBox.Text);
                NotificationToast.Show("オーダーを保存しました");
            }
        }

        private void RenderRosterForTeam(Team team)
        {
            _rosterFlow.Controls.Clear();
            foreach (var p in team.Roster)
            {
                var card = CreateEnhancedPlayerCard(p);
                _rosterFlow.Controls.Add(card);
            }
        }

        private ModernCard CreateEnhancedPlayerCard(Player p)
        {
            var card = new ModernCard { Width = 300, Height = 200, Margin = new Padding(10), BackColor = Theme.Panel };

            var nameLabel = new Label { 
                Text = $"👤 {p.Name}", 
                Font = new Font("Segoe UI", 12, FontStyle.Bold), 
                Dock = DockStyle.Top, 
                Height = 35,
                ForeColor = Theme.Text,
                BackColor = Color.Transparent
            };
            card.Controls.Add(nameLabel);

            var posLabel = new Label { 
                Text = $"Position: {p.PreferredPosition}  Age: {p.Age}", 
                Font = Theme.UiFont, 
                ForeColor = Theme.Text,
                Dock = DockStyle.Top, 
                Height = 25,
                BackColor = Color.Transparent
            };
            card.Controls.Add(posLabel);

            // Stat bars
            var statsPanel = new Panel { Dock = DockStyle.Fill, Padding = new Padding(5), BackColor = Color.Transparent };
            
            var bars = new[]
            {
                new { Label = "Contact", Value = p.Contact, Color = Theme.Primary },
                new { Label = "Power", Value = p.Power, Color = Theme.Accent },
                new { Label = "Speed", Value = p.Speed, Color = Color.FromArgb(76, 175, 80) },
            };

            int y = 0;
            foreach (var stat in bars)
            {
                var bar = new StatBar { 
                    Label = stat.Label, 
                    Value = stat.Value, 
                    BarColor = stat.Color,
                    Width = 280,
                    Location = new Point(5, y),
                    ForeColor = Theme.Text,
                    BackColor = Color.Transparent
                };
                statsPanel.Controls.Add(bar);
                y += 35;
            }

            card.Controls.Add(statsPanel);

            var btnDetails = new ModernButton { 
                Text = "Details", 
                Dock = DockStyle.Bottom, 
                Height = 32,
                CornerRadius = 6
            };
            btnDetails.Click += (s, e) => ShowPlayerDetails(p);
            card.Controls.Add(btnDetails);

            return card;
        }

        private void ShowPlayerDetails(Player p)
        {
            var dlg = new Form { 
                Width = 500, 
                Height = 600, 
                StartPosition = FormStartPosition.CenterParent, 
                Text = $"Player Details - {p.Name}",
                BackColor = Theme.Background,
                ForeColor = Theme.Text
            };

            var mainCard = new ModernCard { Dock = DockStyle.Fill, Padding = new Padding(20), BackColor = Theme.Panel };

            var title = new Label { 
                Text = $"👤 {p.Name}", 
                Font = new Font("Segoe UI", 20, FontStyle.Bold),
                Dock = DockStyle.Top, 
                Height = 50,
                ForeColor = Theme.Text,
                BackColor = Color.Transparent
            };
            mainCard.Controls.Add(title);

            var statsPanel = new Panel { Dock = DockStyle.Fill, BackColor = Color.Transparent };
            var statsToShow = new[]
            {
                ("Contact", p.Contact), ("Power", p.Power), ("Speed", p.Speed),
                ("Defense", p.Defense), ("Arm", p.Arm), ("Stamina", p.Stamina),
                ("Control", p.Control), ("Breaking", p.Breaking)
            };

            int yPos = 10;
            foreach (var (label, value) in statsToShow)
            {
                var bar = new StatBar { 
                    Label = label, 
                    Value = value, 
                    BarColor = Theme.Primary,
                    Width = 440,
                    Location = new Point(10, yPos),
                    ForeColor = Theme.Text,
                    BackColor = Color.Transparent
                };
                statsPanel.Controls.Add(bar);
                yPos += 40;
            }

            mainCard.Controls.Add(statsPanel);

            var btnClose = new ModernButton { 
                Text = "Close", 
                Dock = DockStyle.Bottom, 
                Height = 40 
            };
            btnClose.Click += (s, e) => dlg.Close();
            mainCard.Controls.Add(btnClose);

            dlg.Controls.Add(mainCard);
            dlg.ShowDialog(this);
        }



        private void RenderStandings()
        {
            var list = _league.GetStandings().Select((t, i) => new { 
                Rank = $"#{i + 1}", 
                Team = t.Name, 
                Wins = t.Wins, 
                Losses = t.Losses,
                Ties = t.Ties,
                PCT = t.WinPercentage.ToString("F3"),
                Rating = $"{t.Rating:F1}"
            }).ToList();
            _standingsGrid.DataSource = list;
            _standingsGrid.ClearSelection();
        }

        private void PlayNextMatchForSelectedTeam()
        {
            var sel = _teamFlow.Controls.OfType<ModernCard>().FirstOrDefault();
            if (sel == null) return;
            
            int idx = _teamFlow.Controls.IndexOf(sel);
            if (idx < 0) idx = 0;
            PlayNextMatchFor(_league.Teams[idx]);
        }

        private void PlayNextMatchFor(Team team)
        {
            if (_seasonManager == null) _seasonManager = SeasonManager.CreateSchedule(_league, _gamesPerTeam);
            var match = _seasonManager.GetNextMatchFor(team);
            
            if (match == null) 
            { 
                NotificationToast.Show("No more scheduled matches!");
                return; 
            }

            var home = match.Home; 
            var away = match.Away;
            _currentGame = new GameState(home, away);
            _gameLog.Items.Clear();
            _scoreLabel.Text = "Score: 0 - 0";

            while (!_currentGame.Finished)
            {
                var (runs, summary) = _currentGame.PlayNextHalf();
                _gameLog.Items.Add(summary);
            }

            var (hs, ascore) = _currentGame.GetScore();
            _gameLog.Items.Add($"⚾ FINAL: {home.Name} {hs} - {away.Name} {ascore}");
            _currentGame.ApplyResultToTeams();
            _seasonManager.MarkPlayed(match);
            
            RenderStandings();
            PopulateTeams(_searchBox.Text);
            NotificationToast.Show($"Match completed: {home.Name} {hs} - {away.Name} {ascore}", 4000);
        }

        private void PlayNextHalfInCurrentGame()
        {
            if (_currentGame == null) 
            { 
                NotificationToast.Show("No game in progress!");
                return; 
            }

            var (runs, summary) = _currentGame.PlayNextHalf();
            _gameLog.Items.Add(summary);
            var (h, a) = _currentGame.GetScore();
            _scoreLabel.Text = $"Score: {h} - {a}";

            if (_currentGame.Finished)
            {
                var home = _currentGame.Home; 
                var away = _currentGame.Away; 
                var (hs, ascore) = _currentGame.GetScore();
                _gameLog.Items.Add($"⚾ FINAL: {home.Name} {hs} - {away.Name} {ascore}");
                _currentGame.ApplyResultToTeams();
                
                var m = _seasonManager?.Matches.FirstOrDefault(x => x.Home == home && x.Away == away && !x.Played);
                if (m != null) _seasonManager.MarkPlayed(m);
                
                RenderStandings();
                PopulateTeams(_searchBox.Text);
                NotificationToast.Show($"Game Over: {home.Name} {hs} - {away.Name} {ascore}");
            }
        }

        private void OpeningNewGame()
        {
            using var dlg = new NewGameDialog();
            if (dlg.ShowDialog(this) == DialogResult.OK)
            {
                var league = ProgramBootstrap.CreateLeague();
                var frm = new ModernMainForm(league, dlg.SelectedTeamIndex, dlg.StartAsManager, dlg.GamesPerTeam);
                Hide();
                frm.ShowDialog(this);
                Close();
            }
        }

        private void OpenTradeDialog()
        {
            using var dlg = new TradeDialog(_league);
            dlg.ShowDialog(this);
            PopulateTeams(_searchBox.Text);
            NotificationToast.Show("Trade completed!");
        }

        private void OpenDraftDialog()
        {
            using var dlg = new DraftDialog(_league);
            dlg.ShowDialog(this);
            PopulateTeams(_searchBox.Text);
            NotificationToast.Show("Draft completed!");
        }

        private void OpenTrainingDialog()
        {
            var sel = _teamFlow.Controls.OfType<ModernCard>().FirstOrDefault();
            int idx = sel != null ? _teamFlow.Controls.IndexOf(sel) : 0;
            if (idx < 0) idx = 0;
            
            using var dlg = new TrainingDialog(_league.Teams[idx]);
            dlg.ShowDialog(this);
            PopulateTeams(_searchBox.Text);
            NotificationToast.Show("Training session completed!");
        }

        private void ShowStatisticsDialog()
        {
            var dlg = new Form
            {
                Text = "Season Statistics & Leaderboards",
                Width = 1000,
                Height = 700,
                StartPosition = FormStartPosition.CenterParent,
                BackColor = Theme.Background
            };

            var tabs = new TabControl { Dock = DockStyle.Fill, Font = new Font("Segoe UI", 11) };

            // Batting Leaders
            var battingTab = new TabPage("🏏 Batting Leaders") { BackColor = Theme.Background };
            var battingGrid = CreateLeaderboardGrid();
            var batters = _league.Teams.SelectMany(t => t.Roster)
                .Where(p => p.Stats.AtBats >= 50)
                .OrderByDescending(p => p.GetBattingAverage())
                .Take(20)
                .Select((p, i) => new
                {
                    Rank = i + 1,
                    Player = p.Name,
                    AVG = p.GetBattingAverage().ToString("F3"),
                    AB = p.Stats.AtBats,
                    H = p.Stats.Hits,
                    HR = p.Stats.HomeRuns,
                    RBI = p.Stats.RBIs,
                    R = p.Stats.Runs
                }).ToList();
            battingGrid.DataSource = batters;
            battingTab.Controls.Add(battingGrid);

            // Home Run Leaders
            var hrTab = new TabPage("💪 Home Runs") { BackColor = Theme.Background };
            var hrGrid = CreateLeaderboardGrid();
            var sluggers = _league.Teams.SelectMany(t => t.Roster)
                .Where(p => p.Stats.HomeRuns > 0)
                .OrderByDescending(p => p.Stats.HomeRuns)
                .Take(20)
                .Select((p, i) => new
                {
                    Rank = i + 1,
                    Player = p.Name,
                    HR = p.Stats.HomeRuns,
                    RBI = p.Stats.RBIs,
                    AVG = p.GetBattingAverage().ToString("F3"),
                    AB = p.Stats.AtBats
                }).ToList();
            hrGrid.DataSource = sluggers;
            hrTab.Controls.Add(hrGrid);

            // RBI Leaders
            var rbiTab = new TabPage("🎯 RBIs") { BackColor = Theme.Background };
            var rbiGrid = CreateLeaderboardGrid();
            var rbiLeaders = _league.Teams.SelectMany(t => t.Roster)
                .Where(p => p.Stats.RBIs > 0)
                .OrderByDescending(p => p.Stats.RBIs)
                .Take(20)
                .Select((p, i) => new
                {
                    Rank = i + 1,
                    Player = p.Name,
                    RBI = p.Stats.RBIs,
                    HR = p.Stats.HomeRuns,
                    AVG = p.GetBattingAverage().ToString("F3")
                }).ToList();
            rbiGrid.DataSource = rbiLeaders;
            rbiTab.Controls.Add(rbiGrid);

            // Pitching ERA Leaders
            var eraTab = new TabPage("🎯 ERA") { BackColor = Theme.Background };
            var eraGrid = CreateLeaderboardGrid();
            var pitchers = _league.Teams.SelectMany(t => t.Roster)
                .Where(p => p.Stats.InningsPitched >= 30)
                .OrderBy(p => p.Stats.ERA)
                .Take(20)
                .Select((p, i) => new
                {
                    Rank = i + 1,
                    Player = p.Name,
                    ERA = p.Stats.ERA.ToString("F2"),
                    W = p.Stats.Wins,
                    L = p.Stats.Losses,
                    IP = (p.Stats.InningsPitched / 3.0).ToString("F1"),
                    SO = p.Stats.PitcherStrikeOuts
                }).ToList();
            eraGrid.DataSource = pitchers;
            eraTab.Controls.Add(eraGrid);

            // Wins Leaders
            var winsTab = new TabPage("🏆 Wins") { BackColor = Theme.Background };
            var winsGrid = CreateLeaderboardGrid();
            var winLeaders = _league.Teams.SelectMany(t => t.Roster)
                .Where(p => p.Stats.Wins > 0)
                .OrderByDescending(p => p.Stats.Wins)
                .Take(20)
                .Select((p, i) => new
                {
                    Rank = i + 1,
                    Player = p.Name,
                    W = p.Stats.Wins,
                    L = p.Stats.Losses,
                    ERA = p.Stats.ERA.ToString("F2"),
                    SO = p.Stats.PitcherStrikeOuts
                }).ToList();
            winsGrid.DataSource = winLeaders;
            winsTab.Controls.Add(winsGrid);

            // Strikeout Leaders
            var soTab = new TabPage("⚡ Strikeouts") { BackColor = Theme.Background };
            var soGrid = CreateLeaderboardGrid();
            var soLeaders = _league.Teams.SelectMany(t => t.Roster)
                .Where(p => p.Stats.PitcherStrikeOuts > 0)
                .OrderByDescending(p => p.Stats.PitcherStrikeOuts)
                .Take(20)
                .Select((p, i) => new
                {
                    Rank = i + 1,
                    Player = p.Name,
                    SO = p.Stats.PitcherStrikeOuts,
                    W = p.Stats.Wins,
                    ERA = p.Stats.ERA.ToString("F2")
                }).ToList();
            soGrid.DataSource = soLeaders;
            soTab.Controls.Add(soGrid);

            tabs.TabPages.AddRange(new[] { battingTab, hrTab, rbiTab, eraTab, winsTab, soTab });
            dlg.Controls.Add(tabs);

            var closeBtn = new ModernButton { Text = "Close", Dock = DockStyle.Bottom, Height = 44 };
            closeBtn.Click += (s, e) => dlg.Close();
            dlg.Controls.Add(closeBtn);

            dlg.ShowDialog(this);
        }

        private DataGridView CreateLeaderboardGrid()
        {
            var grid = new DataGridView
            {
                Dock = DockStyle.Fill,
                ReadOnly = true,
                BorderStyle = BorderStyle.None,
                BackgroundColor = Theme.Panel,
                GridColor = Theme.Background,
                AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill,
                RowHeadersVisible = false,
                AllowUserToAddRows =.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
s, e) => dlg.Close();
            dlg.Controls.Add(closeBtn);

            dlg.ShowDialog(this);
        }

        private DataGridView CreateLeaderboardGrid()
        {
            var grid = new DataGridView
            {
                Dock = DockStyle.Fill,
                ReadOnly = true,
                BorderStyle = BorderStyle.None,
                BackgroundColor = Theme.Panel,
                GridColor = Theme.Background,
                AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill,
                RowHeadersVisible = false,
                AllowUserToAddRows = false,
                SelectionMode = DataGridViewSelectionMode.FullRowSelect,
                EnableHeadersVisualStyles = false
            };

            grid.DefaultCellStyle.BackColor = Theme.Panel;
            grid.DefaultCellStyle.ForeColor = Theme.Text;

            grid.DefaultCellStyle.SelectionBackColor = Theme.Primary;
            grid.DefaultCellStyle.SelectionForeColor = Color.White;
            grid.DefaultCellStyle.Font = new Font("Segoe UI", 10);

            grid.ColumnHeadersDefaultCellStyle.BackColor = Theme.Background;
            grid.ColumnHeadersDefaultCellStyle.ForeColor = Theme.Text;
            grid.ColumnHeadersDefaultCellStyle.Font = new Font("Segoe UI", 11, FontStyle.Bold);
            grid.ColumnHeadersHeight = 40;
            grid.RowTemplate.Height = 35;

            return grid;
        }

        private void Dispose(bool disposing)
        {
            if (disposing)
            {
                _uiUpdateTimer?.Dispose();
            }
            base.Dispose(disposing);
        }
    }
}
