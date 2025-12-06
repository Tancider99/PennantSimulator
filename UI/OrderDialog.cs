using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using PennantSimulator.Models;

namespace PennantSimulator.UI
{
    /// <summary>
    /// オーダー設定ダイアログ
    /// 野手の打順、投手のローテーション（先発・中継ぎ・抑え）、ベンチメンバーを設定可能
    /// ポジション（打順番号）をクリックして選択→別のポジションをクリックして入れ替え
    /// </summary>
    public class OrderDialog : Form
    {
        private Team _team;
        
        // タブコントロール
        private TabControl _tabControl;
        private TabPage _batterTab;
        private TabPage _pitcherTab;
        private TabPage _benchTab;
        
        // 野手オーダー用 - ポジション（打順）ボタン
        private Button[] _batterPositionButtons = new Button[9];
        private Label[] _batterPositionLabels = new Label[9];
        private Panel _batterOrderPanel;
        private ListBox _batterBenchList;  // 野手ベンチ
        private int _selectedBatterPosition = -1;  // 選択中の打順ポジション(0-8)
        private bool _isBatterSwapMode = false;
        
        // 投手オーダー用 - ポジションボタン
        private Button[] _starterButtons = new Button[5];
        private Button[] _middleButtons = new Button[4];
        private Button _closerButton;
        private ListBox _pitcherBenchList;  // 投手ベンチ
        private string _selectedPitcherRole = null;  // "starter", "middle", "closer"
        private int _selectedPitcherPosition = -1;
        private bool _isPitcherSwapMode = false;
        
        // ベンチ用
        private ListBox _benchList;
        private ListBox _allPlayersList;
        private int _selectedBenchIndex = -1;
        private bool _isBenchSwapMode = false;
        
        // 内部データ
        private List<Player> _batterOrder = new List<Player>();      // 打順 (9人)
        private List<Player> _starterRotation = new List<Player>();  // 先発ローテ (5人)
        private List<Player> _middleRelievers = new List<Player>();  // 中継ぎ (4人)
        private List<Player> _closers = new List<Player>();          // 抑え (1人)
        private List<Player> _benchPlayers = new List<Player>();     // ベンチ入り
        
        private Button _saveButton;
        private Button _cancelButton;
        private Button _autoOrderButton;
        private Label _statusLabel;

        public OrderDialog(Team team)
        {
            _team = team ?? throw new ArgumentNullException(nameof(team));
            Text = $"オーダー設定 - {_team.Name}";
            Width = 900;
            Height = 700;
            StartPosition = FormStartPosition.CenterParent;
            
            InitializeData();
            InitializeUI();
            RefreshAllLists();
        }
        
        private void InitializeData()
        {
            // 初期状態で自動オーダーを組む
            AutoArrangeOrder();
        }
        
        /// <summary>
        /// 自動でオーダーを組む
        /// </summary>
        private void AutoArrangeOrder()
        {
            if (_team.Roster == null || _team.Roster.Count == 0) return;
            
            // 投手と野手を分離
            var pitchers = _team.Roster.Where(p => p.PreferredPosition == Position.Pitcher).ToList();
            var batters = _team.Roster.Where(p => p.PreferredPosition != Position.Pitcher).ToList();
            
            // 投手が足りない場合は野手から補充
            if (pitchers.Count < 10)
            {
                var neededPitchers = 10 - pitchers.Count;
                var extraPitchers = batters.OrderByDescending(p => p.PitchingSkill).Take(neededPitchers).ToList();
                pitchers.AddRange(extraPitchers);
                batters = batters.Except(extraPitchers).ToList();
            }
            
            // 野手が足りない場合は投手から補充
            if (batters.Count < 9)
            {
                var neededBatters = 9 - batters.Count;
                var extraBatters = pitchers.OrderByDescending(p => p.BattingSkill).Take(neededBatters).ToList();
                batters.AddRange(extraBatters);
                pitchers = pitchers.Except(extraBatters).ToList();
            }
            
            // 先発ローテーション (先発適性順で上位5人)
            _starterRotation = pitchers
                .OrderByDescending(p => p.StarterAptitude)
                .ThenByDescending(p => p.PitchingSkill)
                .Take(5)
                .ToList();
            
            var remainingPitchers = pitchers.Except(_starterRotation).ToList();
            
            // 抑え (抑え適性が最も高い1人)
            _closers = remainingPitchers
                .OrderByDescending(p => p.CloserAptitude)
                .ThenByDescending(p => p.PitchingSkill)
                .Take(1)
                .ToList();
            
            remainingPitchers = remainingPitchers.Except(_closers).ToList();
            
            // 中継ぎ (残りから中継ぎ適性順で4人)
            _middleRelievers = remainingPitchers
                .OrderByDescending(p => p.MiddleAptitude)
                .ThenByDescending(p => p.PitchingSkill)
                .Take(4)
                .ToList();
            
            remainingPitchers = remainingPitchers.Except(_middleRelievers).ToList();
            
            // 打順 (打撃力順で上位9人)
            _batterOrder = batters
                .OrderByDescending(p => p.BattingSkill)
                .Take(9)
                .ToList();
            
            var remainingBatters = batters.Except(_batterOrder).ToList();
            
            // ベンチ (残りの選手)
            _benchPlayers = remainingBatters.Concat(remainingPitchers).ToList();
        }
        
        private void InitializeUI()
        {
            var mainLayout = new TableLayoutPanel 
            { 
                Dock = DockStyle.Fill, 
                RowCount = 3,
                Padding = new Padding(10)
            };
            mainLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 40));
            mainLayout.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
            mainLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 60));
            Controls.Add(mainLayout);
            
            // ヘッダー
            var headerPanel = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.LeftToRight };
            _statusLabel = new Label 
            { 
                Text = "ポジション（番号ボタン）をクリックして選択し、入れ替え先をクリックしてください", 
                AutoSize = true,
                Font = new Font("Yu Gothic UI", 10),
                ForeColor = Color.DarkBlue
            };
            _autoOrderButton = new Button 
            { 
                Text = "自動編成", 
                Width = 100, 
                Height = 30,
                BackColor = Color.FromArgb(108, 117, 125),
                ForeColor = Color.White
            };
            _autoOrderButton.Click += AutoOrderButton_Click;
            headerPanel.Controls.Add(_statusLabel);
            headerPanel.Controls.Add(new Panel { Width = 20 });
            headerPanel.Controls.Add(_autoOrderButton);
            mainLayout.Controls.Add(headerPanel, 0, 0);
            
            // タブコントロール
            _tabControl = new TabControl { Dock = DockStyle.Fill, Font = new Font("Yu Gothic UI", 10) };
            
            // 野手タブ
            _batterTab = new TabPage("野手オーダー");
            InitializeBatterTab();
            _tabControl.TabPages.Add(_batterTab);
            
            // 投手タブ
            _pitcherTab = new TabPage("投手オーダー");
            InitializePitcherTab();
            _tabControl.TabPages.Add(_pitcherTab);
            
            // ベンチタブ
            _benchTab = new TabPage("ベンチ入りメンバー");
            InitializeBenchTab();
            _tabControl.TabPages.Add(_benchTab);
            
            mainLayout.Controls.Add(_tabControl, 0, 1);
            
            // ボタンパネル
            var buttonPanel = new FlowLayoutPanel 
            { 
                Dock = DockStyle.Fill, 
                FlowDirection = FlowDirection.RightToLeft,
                Padding = new Padding(8)
            };
            
            _cancelButton = new Button 
            { 
                Text = "キャンセル", 
                Width = 100, 
                Height = 40,
                BackColor = Color.FromArgb(108, 117, 125),
                ForeColor = Color.White
            };
            _cancelButton.Click += (s, e) => { DialogResult = DialogResult.Cancel; Close(); };
            
            _saveButton = new Button 
            { 
                Text = "保存", 
                Width = 120, 
                Height = 40,
                BackColor = Color.FromArgb(40, 167, 69),
                ForeColor = Color.White
            };
            _saveButton.Click += SaveButton_Click;
            
            buttonPanel.Controls.Add(_cancelButton);
            buttonPanel.Controls.Add(new Panel { Width = 10 });
            buttonPanel.Controls.Add(_saveButton);
            mainLayout.Controls.Add(buttonPanel, 0, 2);
        }
        
        private void InitializeBatterTab()
        {
            var layout = new TableLayoutPanel 
            { 
                Dock = DockStyle.Fill, 
                ColumnCount = 2,
                Padding = new Padding(5)
            };
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 60));
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 40));
            
            // 打順パネル（ポジションボタン方式）
            _batterOrderPanel = new Panel { Dock = DockStyle.Fill };
            var orderLabel = new Label 
            { 
                Text = "打順 (1-9番) - クリックで選択→クリックで入れ替え", 
                Dock = DockStyle.Top, 
                Height = 25,
                Font = new Font("Yu Gothic UI", 10, FontStyle.Bold)
            };
            
            var batterGridPanel = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                RowCount = 9,
                ColumnCount = 2,
                Padding = new Padding(5)
            };
            batterGridPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 50));
            batterGridPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
            
            for (int i = 0; i < 9; i++)
            {
                batterGridPanel.RowStyles.Add(new RowStyle(SizeType.Percent, 11.1f));
                
                // 打順番号ボタン（ポジション選択用）
                _batterPositionButtons[i] = new Button
                {
                    Text = $"{i + 1}",
                    Dock = DockStyle.Fill,
                    Font = new Font("Yu Gothic UI", 12, FontStyle.Bold),
                    BackColor = Color.FromArgb(52, 73, 94),
                    ForeColor = Color.White,
                    FlatStyle = FlatStyle.Flat,
                    Tag = i
                };
                _batterPositionButtons[i].FlatAppearance.BorderSize = 1;
                _batterPositionButtons[i].Click += BatterPositionButton_Click;
                batterGridPanel.Controls.Add(_batterPositionButtons[i], 0, i);
                
                // 選手情報ラベル
                _batterPositionLabels[i] = new Label
                {
                    Text = "(空き)",
                    Dock = DockStyle.Fill,
                    Font = new Font("Consolas", 9),
                    TextAlign = ContentAlignment.MiddleLeft,
                    BackColor = Color.White,
                    BorderStyle = BorderStyle.FixedSingle,
                    Padding = new Padding(5, 0, 0, 0)
                };
                batterGridPanel.Controls.Add(_batterPositionLabels[i], 1, i);
            }
            
            _batterOrderPanel.Controls.Add(batterGridPanel);
            _batterOrderPanel.Controls.Add(orderLabel);
            layout.Controls.Add(_batterOrderPanel, 0, 0);
            
            // 野手ベンチリスト
            var availablePanel = new Panel { Dock = DockStyle.Fill };
            var availableLabel = new Label 
            { 
                Text = "野手ベンチ (入れ替え対象)", 
                Dock = DockStyle.Top, 
                Height = 25,
                Font = new Font("Yu Gothic UI", 10, FontStyle.Bold)
            };
            _batterBenchList = CreateListBox();
            _batterBenchList.Click += BatterBenchList_Click;
            _batterBenchList.Dock = DockStyle.Fill;
            availablePanel.Controls.Add(_batterBenchList);
            availablePanel.Controls.Add(availableLabel);
            layout.Controls.Add(availablePanel, 1, 0);
            
            _batterTab.Controls.Add(layout);
        }
        
        private void InitializePitcherTab()
        {
            var layout = new TableLayoutPanel 
            { 
                Dock = DockStyle.Fill, 
                ColumnCount = 4,
                Padding = new Padding(5)
            };
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 28));
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 24));
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 18));
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 30));
            
            // 先発ローテーション（ポジションボタン方式）
            var starterPanel = new Panel { Dock = DockStyle.Fill };
            var starterLabel = new Label 
            { 
                Text = "先発ローテ (5人)", 
                Dock = DockStyle.Top, 
                Height = 25,
                Font = new Font("Yu Gothic UI", 10, FontStyle.Bold)
            };
            var starterGrid = new TableLayoutPanel { Dock = DockStyle.Fill, RowCount = 5, ColumnCount = 1 };
            for (int i = 0; i < 5; i++)
            {
                starterGrid.RowStyles.Add(new RowStyle(SizeType.Percent, 20));
                _starterButtons[i] = CreatePitcherPositionButton($"先発{i + 1}", "starter", i);
                starterGrid.Controls.Add(_starterButtons[i], 0, i);
            }
            starterPanel.Controls.Add(starterGrid);
            starterPanel.Controls.Add(starterLabel);
            layout.Controls.Add(starterPanel, 0, 0);
            
            // 中継ぎ（ポジションボタン方式）
            var middlePanel = new Panel { Dock = DockStyle.Fill };
            var middleLabel = new Label 
            { 
                Text = "中継ぎ (4人)", 
                Dock = DockStyle.Top, 
                Height = 25,
                Font = new Font("Yu Gothic UI", 10, FontStyle.Bold)
            };
            var middleGrid = new TableLayoutPanel { Dock = DockStyle.Fill, RowCount = 4, ColumnCount = 1 };
            for (int i = 0; i < 4; i++)
            {
                middleGrid.RowStyles.Add(new RowStyle(SizeType.Percent, 25));
                _middleButtons[i] = CreatePitcherPositionButton($"中継{i + 1}", "middle", i);
                middleGrid.Controls.Add(_middleButtons[i], 0, i);
            }
            middlePanel.Controls.Add(middleGrid);
            middlePanel.Controls.Add(middleLabel);
            layout.Controls.Add(middlePanel, 1, 0);
            
            // 抑え（ポジションボタン方式）
            var closerPanel = new Panel { Dock = DockStyle.Fill };
            var closerLabel = new Label 
            { 
                Text = "抑え (1人)", 
                Dock = DockStyle.Top, 
                Height = 25,
                Font = new Font("Yu Gothic UI", 10, FontStyle.Bold)
            };
            var closerGrid = new TableLayoutPanel { Dock = DockStyle.Fill, RowCount = 1, ColumnCount = 1 };
            closerGrid.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
            _closerButton = CreatePitcherPositionButton("抑え", "closer", 0);
            closerGrid.Controls.Add(_closerButton, 0, 0);
            closerPanel.Controls.Add(closerGrid);
            closerPanel.Controls.Add(closerLabel);
            layout.Controls.Add(closerPanel, 2, 0);
            
            // 投手ベンチ
            var availablePanel = new Panel { Dock = DockStyle.Fill };
            var availableLabel = new Label 
            { 
                Text = "投手ベンチ (入れ替え対象)", 
                Dock = DockStyle.Top, 
                Height = 25,
                Font = new Font("Yu Gothic UI", 10, FontStyle.Bold)
            };
            _pitcherBenchList = CreateListBox();
            _pitcherBenchList.Click += PitcherBenchList_Click;
            _pitcherBenchList.Dock = DockStyle.Fill;
            availablePanel.Controls.Add(_pitcherBenchList);
            availablePanel.Controls.Add(availableLabel);
            layout.Controls.Add(availablePanel, 3, 0);
            
            _pitcherTab.Controls.Add(layout);
        }
        
        private Button CreatePitcherPositionButton(string text, string role, int index)
        {
            var btn = new Button
            {
                Text = $"{text}: (空き)",
                Dock = DockStyle.Fill,
                Font = new Font("Yu Gothic UI", 9),
                BackColor = Color.FromArgb(52, 73, 94),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                TextAlign = ContentAlignment.MiddleLeft,
                Padding = new Padding(5, 0, 0, 0),
                Tag = new Tuple<string, int>(role, index)
            };
            btn.FlatAppearance.BorderSize = 1;
            btn.Click += PitcherPositionButton_Click;
            return btn;
        }
        
        private void InitializeBenchTab()
        {
            var layout = new TableLayoutPanel 
            { 
                Dock = DockStyle.Fill, 
                ColumnCount = 2,
                Padding = new Padding(5)
            };
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50));
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50));
            
            // ベンチ入りメンバー
            var benchPanel = new Panel { Dock = DockStyle.Fill };
            var benchLabel = new Label 
            { 
                Text = "ベンチ入りメンバー", 
                Dock = DockStyle.Top, 
                Height = 25,
                Font = new Font("Yu Gothic UI", 10, FontStyle.Bold)
            };
            _benchList = CreateListBox();
            _benchList.Click += BenchList_Click;
            _benchList.Dock = DockStyle.Fill;
            benchPanel.Controls.Add(_benchList);
            benchPanel.Controls.Add(benchLabel);
            layout.Controls.Add(benchPanel, 0, 0);
            
            // 全選手リスト
            var allPanel = new Panel { Dock = DockStyle.Fill };
            var allLabel = new Label 
            { 
                Text = "登録外選手", 
                Dock = DockStyle.Top, 
                Height = 25,
                Font = new Font("Yu Gothic UI", 10, FontStyle.Bold)
            };
            _allPlayersList = CreateListBox();
            _allPlayersList.Click += AllPlayersList_Click;
            _allPlayersList.Dock = DockStyle.Fill;
            allPanel.Controls.Add(_allPlayersList);
            allPanel.Controls.Add(allLabel);
            layout.Controls.Add(allPanel, 1, 0);
            
            _benchTab.Controls.Add(layout);
        }
        
        private ListBox CreateListBox()
        {
            return new ListBox 
            { 
                Font = new Font("Consolas", 9),
                SelectionMode = SelectionMode.One,
                IntegralHeight = false
            };
        }
        
        private void RefreshAllLists()
        {
            RefreshBatterLists();
            RefreshPitcherLists();
            RefreshBenchLists();
        }
        
        private void RefreshBatterLists()
        {
            // 打順ボタンとラベルを更新
            for (int i = 0; i < 9; i++)
            {
                if (i < _batterOrder.Count && _batterOrder[i] != null)
                {
                    var p = _batterOrder[i];
                    string posStr = GetPositionShortString(p.PreferredPosition);
                    _batterPositionLabels[i].Text = $"{p.Name} [{posStr}] C:{p.Contact} P:{p.Power} OVR:{p.BattingSkill:F0}";
                    _batterPositionLabels[i].BackColor = Color.White;
                }
                else
                {
                    _batterPositionLabels[i].Text = "(空き)";
                    _batterPositionLabels[i].BackColor = Color.LightGray;
                }
                
                // 選択中のポジションをハイライト
                if (_isBatterSwapMode && _selectedBatterPosition == i)
                {
                    _batterPositionButtons[i].BackColor = Color.FromArgb(46, 204, 113);  // 緑
                    _batterPositionLabels[i].BackColor = Color.FromArgb(200, 255, 200);
                }
                else
                {
                    _batterPositionButtons[i].BackColor = Color.FromArgb(52, 73, 94);
                }
            }
            
            // 野手ベンチリストを更新
            _batterBenchList.Items.Clear();
            var battersInOrder = new HashSet<Player>(_batterOrder);
            var benchBatters = _benchPlayers
                .Where(p => !battersInOrder.Contains(p))
                .OrderByDescending(p => p.PreferredPosition != Position.Pitcher)  // 野手優先
                .ThenByDescending(p => p.BattingSkill)
                .ToList();
            
            foreach (var p in benchBatters)
            {
                string posStr = GetPositionShortString(p.PreferredPosition);
                string typeStr = p.PreferredPosition == Position.Pitcher ? "投" : "野";
                _batterBenchList.Items.Add($"{p.Name} [{posStr}] {typeStr} C:{p.Contact} P:{p.Power}");
            }
        }
        
        private void RefreshPitcherLists()
        {
            // 先発ローテボタンを更新
            for (int i = 0; i < 5; i++)
            {
                if (i < _starterRotation.Count && _starterRotation[i] != null)
                {
                    var p = _starterRotation[i];
                    _starterButtons[i].Text = $"先発{i + 1}: {p.Name}\n先:{p.StarterAptitude} OVR:{p.PitchingSkill:F0}";
                }
                else
                {
                    _starterButtons[i].Text = $"先発{i + 1}: (空き)";
                }
                
                // 選択中をハイライト
                if (_isPitcherSwapMode && _selectedPitcherRole == "starter" && _selectedPitcherPosition == i)
                {
                    _starterButtons[i].BackColor = Color.FromArgb(46, 204, 113);
                }
                else
                {
                    _starterButtons[i].BackColor = Color.FromArgb(52, 73, 94);
                }
            }
            
            // 中継ぎボタンを更新
            for (int i = 0; i < 4; i++)
            {
                if (i < _middleRelievers.Count && _middleRelievers[i] != null)
                {
                    var p = _middleRelievers[i];
                    _middleButtons[i].Text = $"中継{i + 1}: {p.Name}\n中:{p.MiddleAptitude} OVR:{p.PitchingSkill:F0}";
                }
                else
                {
                    _middleButtons[i].Text = $"中継{i + 1}: (空き)";
                }
                
                if (_isPitcherSwapMode && _selectedPitcherRole == "middle" && _selectedPitcherPosition == i)
                {
                    _middleButtons[i].BackColor = Color.FromArgb(46, 204, 113);
                }
                else
                {
                    _middleButtons[i].BackColor = Color.FromArgb(52, 73, 94);
                }
            }
            
            // 抑えボタンを更新
            if (_closers.Count > 0 && _closers[0] != null)
            {
                var p = _closers[0];
                _closerButton.Text = $"抑え: {p.Name}\n抑:{p.CloserAptitude} OVR:{p.PitchingSkill:F0}";
            }
            else
            {
                _closerButton.Text = "抑え: (空き)";
            }
            
            if (_isPitcherSwapMode && _selectedPitcherRole == "closer")
            {
                _closerButton.BackColor = Color.FromArgb(46, 204, 113);
            }
            else
            {
                _closerButton.BackColor = Color.FromArgb(52, 73, 94);
            }
            
            // 投手ベンチリストを更新
            _pitcherBenchList.Items.Clear();
            var assignedPitchers = new HashSet<Player>(_starterRotation.Concat(_middleRelievers).Concat(_closers));
            var benchPitchers = _benchPlayers
                .Where(p => !assignedPitchers.Contains(p))
                .OrderByDescending(p => p.PreferredPosition == Position.Pitcher)  // 投手優先
                .ThenByDescending(p => p.PitchingSkill)
                .ToList();
            
            foreach (var p in benchPitchers)
            {
                string posStr = GetPositionShortString(p.PreferredPosition);
                string typeStr = p.PreferredPosition == Position.Pitcher ? "投" : "野";
                _pitcherBenchList.Items.Add($"{p.Name} [{posStr}] {typeStr} 先:{p.StarterAptitude} 中:{p.MiddleAptitude} 抑:{p.CloserAptitude}");
            }
        }
        
        private void RefreshBenchLists()
        {
            _benchList.Items.Clear();
            foreach (var p in _benchPlayers)
            {
                string posStr = GetPositionShortString(p.PreferredPosition);
                string typeStr = p.PreferredPosition == Position.Pitcher ? "投" : "野";
                _benchList.Items.Add($"{p.Name} [{posStr}] {typeStr} OVR:{p.OverallSkill:F0}");
            }
            
            // 登録外選手（スタメン・ローテ・リリーフ・ベンチのどれにも入っていない選手）
            _allPlayersList.Items.Clear();
            var registeredPlayers = new HashSet<Player>(
                _batterOrder.Concat(_starterRotation).Concat(_middleRelievers).Concat(_closers).Concat(_benchPlayers)
            );
            var unregistered = _team.Roster.Where(p => !registeredPlayers.Contains(p)).ToList();
            
            foreach (var p in unregistered)
            {
                string posStr = GetPositionShortString(p.PreferredPosition);
                string typeStr = p.PreferredPosition == Position.Pitcher ? "投" : "野";
                _allPlayersList.Items.Add($"{p.Name} [{posStr}] {typeStr} OVR:{p.OverallSkill:F0}");
            }
        }
        
        private string GetPositionShortString(Position pos)
        {
            return pos switch
            {
                Position.Pitcher => "投",
                Position.Catcher => "捕",
                Position.FirstBase => "一",
                Position.SecondBase => "二",
                Position.ThirdBase => "三",
                Position.ShortStop => "遊",
                Position.LeftField => "左",
                Position.CenterField => "中",
                Position.RightField => "右",
                Position.DesignatedHitter => "DH",
                _ => "?"
            };
        }
        
        #region 野手オーダーのクリック処理
        
        /// <summary>
        /// 打順ポジションボタンがクリックされた時の処理
        /// </summary>
        private void BatterPositionButton_Click(object sender, EventArgs e)
        {
            var btn = sender as Button;
            if (btn == null) return;
            
            int positionIndex = (int)btn.Tag;
            
            if (!_isBatterSwapMode)
            {
                // 最初の選択 - このポジションを選択
                _selectedBatterPosition = positionIndex;
                _isBatterSwapMode = true;
                string playerName = positionIndex < _batterOrder.Count ? _batterOrder[positionIndex]?.Name ?? "(空き)" : "(空き)";
                _statusLabel.Text = $"打順 {positionIndex + 1}番 ({playerName}) を選択中。入れ替え先のポジションかベンチ選手をクリック。";
                _statusLabel.ForeColor = Color.DarkGreen;
                RefreshBatterLists();  // ハイライト更新
            }
            else
            {
                // 2回目のクリック - 入れ替え実行
                if (_selectedBatterPosition != positionIndex)
                {
                    // 両方のポジションに選手がいる場合のみ入れ替え（空白を作らない）
                    if (_selectedBatterPosition < _batterOrder.Count && positionIndex < _batterOrder.Count &&
                        _batterOrder[_selectedBatterPosition] != null && _batterOrder[positionIndex] != null)
                    {
                        var temp = _batterOrder[_selectedBatterPosition];
                        _batterOrder[_selectedBatterPosition] = _batterOrder[positionIndex];
                        _batterOrder[positionIndex] = temp;
                    }
                }
                ResetBatterSelection();
                RefreshBatterLists();
            }
        }
        
        /// <summary>
        /// 野手ベンチリストがクリックされた時の処理
        /// </summary>
        private void BatterBenchList_Click(object sender, EventArgs e)
        {
            int idx = _batterBenchList.SelectedIndex;
            if (idx < 0) return;
            
            // ベンチ選手リストを取得
            var battersInOrder = new HashSet<Player>(_batterOrder);
            var benchBatters = _benchPlayers
                .Where(p => !battersInOrder.Contains(p))
                .OrderByDescending(p => p.PreferredPosition != Position.Pitcher)
                .ThenByDescending(p => p.BattingSkill)
                .ToList();
            
            if (idx >= benchBatters.Count) return;
            var selectedBenchPlayer = benchBatters[idx];
            
            if (_isBatterSwapMode && _selectedBatterPosition >= 0 && _selectedBatterPosition < _batterOrder.Count)
            {
                // 打順のポジションとベンチ選手を入れ替え
                var oldPlayer = _batterOrder[_selectedBatterPosition];
                if (oldPlayer != null)
                {
                    _batterOrder[_selectedBatterPosition] = selectedBenchPlayer;
                    _benchPlayers.Remove(selectedBenchPlayer);
                    _benchPlayers.Add(oldPlayer);
                }
            }
            
            ResetBatterSelection();
            RefreshBatterLists();
            RefreshBenchLists();
        }
        
        private void ResetBatterSelection()
        {
            _isBatterSwapMode = false;
            _selectedBatterPosition = -1;
            _statusLabel.Text = "ポジション（番号ボタン）をクリックして選択し、入れ替え先をクリックしてください";
            _statusLabel.ForeColor = Color.DarkBlue;
            RefreshBatterLists();  // ハイライト解除
        }
        
        #endregion
        
        #region 投手オーダーのクリック処理
        
        /// <summary>
        /// 投手ポジションボタンがクリックされた時の処理
        /// </summary>
        private void PitcherPositionButton_Click(object sender, EventArgs e)
        {
            var btn = sender as Button;
            if (btn == null) return;
            
            var tagData = btn.Tag as Tuple<string, int>;
            if (tagData == null) return;
            
            string role = tagData.Item1;
            int positionIndex = tagData.Item2;
            
            if (!_isPitcherSwapMode)
            {
                // 最初の選択
                _selectedPitcherRole = role;
                _selectedPitcherPosition = positionIndex;
                _isPitcherSwapMode = true;
                
                var sourceList = GetPitcherListByTag(role);
                string playerName = (sourceList != null && positionIndex < sourceList.Count) ? sourceList[positionIndex]?.Name ?? "(空き)" : "(空き)";
                string roleName = role == "starter" ? "先発" : (role == "middle" ? "中継ぎ" : "抑え");
                _statusLabel.Text = $"{roleName} {positionIndex + 1}番 ({playerName}) を選択中。入れ替え先のポジションかベンチ選手をクリック。";
                _statusLabel.ForeColor = Color.DarkGreen;
                RefreshPitcherLists();  // ハイライト更新
            }
            else
            {
                // 2回目のクリック - 入れ替え実行
                var sourceList = GetPitcherListByTag(_selectedPitcherRole);
                var targetList = GetPitcherListByTag(role);
                
                if (sourceList != null && targetList != null)
                {
                    bool isSameRole = (_selectedPitcherRole == role);
                    bool isSamePosition = (_selectedPitcherPosition == positionIndex);
                    
                    if (!isSameRole || !isSamePosition)
                    {
                        // 両方に選手がいる場合のみ入れ替え（空白を作らない）
                        if (_selectedPitcherPosition < sourceList.Count && positionIndex < targetList.Count &&
                            sourceList[_selectedPitcherPosition] != null && targetList[positionIndex] != null)
                        {
                            var temp = sourceList[_selectedPitcherPosition];
                            sourceList[_selectedPitcherPosition] = targetList[positionIndex];
                            targetList[positionIndex] = temp;
                        }
                    }
                }
                
                ResetPitcherSelection();
                RefreshPitcherLists();
            }
        }
        
        /// <summary>
        /// 投手ベンチリストがクリックされた時の処理
        /// </summary>
        private void PitcherBenchList_Click(object sender, EventArgs e)
        {
            int idx = _pitcherBenchList.SelectedIndex;
            if (idx < 0) return;
            
            var assignedPitchers = new HashSet<Player>(_starterRotation.Concat(_middleRelievers).Concat(_closers));
            var benchPitchers = _benchPlayers
                .Where(p => !assignedPitchers.Contains(p))
                .OrderByDescending(p => p.PreferredPosition == Position.Pitcher)
                .ThenByDescending(p => p.PitchingSkill)
                .ToList();
            
            if (idx >= benchPitchers.Count) return;
            var selectedBenchPlayer = benchPitchers[idx];
            
            if (_isPitcherSwapMode && _selectedPitcherRole != null && _selectedPitcherPosition >= 0)
            {
                var sourceList = GetPitcherListByTag(_selectedPitcherRole);
                if (sourceList != null && _selectedPitcherPosition < sourceList.Count)
                {
                    var oldPlayer = sourceList[_selectedPitcherPosition];
                    if (oldPlayer != null)
                    {
                        sourceList[_selectedPitcherPosition] = selectedBenchPlayer;
                        _benchPlayers.Remove(selectedBenchPlayer);
                        _benchPlayers.Add(oldPlayer);
                    }
                }
            }
            
            ResetPitcherSelection();
            RefreshPitcherLists();
            RefreshBenchLists();
        }
        
        private List<Player> GetPitcherListByTag(string tag)
        {
            return tag switch
            {
                "starter" => _starterRotation,
                "middle" => _middleRelievers,
                "closer" => _closers,
                _ => null
            };
        }
        
        private void ResetPitcherSelection()
        {
            _isPitcherSwapMode = false;
            _selectedPitcherRole = null;
            _selectedPitcherPosition = -1;
            _statusLabel.Text = "ポジション（ボタン）をクリックして選択し、入れ替え先をクリックしてください";
            _statusLabel.ForeColor = Color.DarkBlue;
            RefreshPitcherLists();  // ハイライト解除
        }
        
        #endregion
        
        #region ベンチのクリック処理
        
        private void BenchList_Click(object sender, EventArgs e)
        {
            int idx = _benchList.SelectedIndex;
            if (idx < 0 || idx >= _benchPlayers.Count) return;
            
            if (!_isBenchSwapMode)
            {
                _selectedBenchIndex = idx;
                _isBenchSwapMode = true;
                _statusLabel.Text = $"ベンチ {_benchPlayers[idx].Name} を選択中。入れ替え先をクリックしてください。";
                _statusLabel.ForeColor = Color.DarkGreen;
            }
            else
            {
                // ベンチ内での入れ替え
                if (_selectedBenchIndex != idx)
                {
                    var temp = _benchPlayers[_selectedBenchIndex];
                    _benchPlayers[_selectedBenchIndex] = _benchPlayers[idx];
                    _benchPlayers[idx] = temp;
                }
                ResetBenchSelection();
                RefreshBenchLists();
            }
        }
        
        private void AllPlayersList_Click(object sender, EventArgs e)
        {
            int idx = _allPlayersList.SelectedIndex;
            if (idx < 0) return;
            
            var registeredPlayers = new HashSet<Player>(
                _batterOrder.Concat(_starterRotation).Concat(_middleRelievers).Concat(_closers).Concat(_benchPlayers)
            );
            var unregistered = _team.Roster.Where(p => !registeredPlayers.Contains(p)).ToList();
            
            if (idx >= unregistered.Count) return;
            var selectedPlayer = unregistered[idx];
            
            if (_isBenchSwapMode && _selectedBenchIndex >= 0 && _selectedBenchIndex < _benchPlayers.Count)
            {
                // ベンチの選手と登録外選手を入れ替え
                var oldPlayer = _benchPlayers[_selectedBenchIndex];
                _benchPlayers[_selectedBenchIndex] = selectedPlayer;
                // oldPlayerは登録外になる（何もしない）
            }
            else
            {
                // ベンチに追加
                _benchPlayers.Add(selectedPlayer);
            }
            
            ResetBenchSelection();
            RefreshAllLists();
        }
        
        private void ResetBenchSelection()
        {
            _isBenchSwapMode = false;
            _selectedBenchIndex = -1;
            _statusLabel.Text = "ポジション（番号ボタン）をクリックして選択し、入れ替え先をクリックしてください";
            _statusLabel.ForeColor = Color.DarkBlue;
        }
        
        #endregion
        
        private void AutoOrderButton_Click(object sender, EventArgs e)
        {
            AutoArrangeOrder();
            RefreshAllLists();
            _statusLabel.Text = "自動編成を適用しました";
            _statusLabel.ForeColor = Color.DarkBlue;
        }
        
        private void SaveButton_Click(object sender, EventArgs e)
        {
            // オーダーをチームに反映
            // 打順の9人を先頭に配置
            var newRoster = new List<Player>();
            newRoster.AddRange(_batterOrder.Take(9));
            
            // 投手ローテーションを追加
            newRoster.AddRange(_starterRotation);
            newRoster.AddRange(_middleRelievers);
            newRoster.AddRange(_closers);
            
            // ベンチを追加
            newRoster.AddRange(_benchPlayers);
            
            // 残りの登録外選手を追加
            var allAssigned = new HashSet<Player>(newRoster);
            var remaining = _team.Roster.Where(p => !allAssigned.Contains(p)).ToList();
            newRoster.AddRange(remaining);
            
            // ロースターを更新
            _team.Roster.Clear();
            _team.Roster.AddRange(newRoster);
            
            DialogResult = DialogResult.OK;
            Close();
        }
    }
}
