# -*- coding: utf-8 -*-
"""
定数定義ファイル
"""

# 画面設定（デフォルト値）
DEFAULT_SCREEN_WIDTH = 1600
DEFAULT_SCREEN_HEIGHT = 1000

# 実際の画面サイズ（動的に変更可能）
SCREEN_WIDTH = DEFAULT_SCREEN_WIDTH
SCREEN_HEIGHT = DEFAULT_SCREEN_HEIGHT

# 画面サイズオプション
SCREEN_RESOLUTIONS = [
    (1280, 720, "HD"),
    (1600, 900, "HD+"),
    (1600, 1000, "標準"),
    (1920, 1080, "Full HD"),
    (2560, 1440, "QHD")
]

def set_screen_size(width: int, height: int):
    """画面サイズを動的に変更"""
    global SCREEN_WIDTH, SCREEN_HEIGHT
    SCREEN_WIDTH = width
    SCREEN_HEIGHT = height

def get_screen_size():
    """現在の画面サイズを取得"""
    return (SCREEN_WIDTH, SCREEN_HEIGHT)

# カラー定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (30, 30, 35)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
BLUE = (70, 130, 220)
DARK_BLUE = (30, 60, 140)
GREEN = (50, 200, 100)
DARK_GREEN = (30, 120, 60)
RED = (220, 80, 80)
DARK_RED = (140, 30, 30)
GOLD = (255, 215, 0)
ORANGE = (255, 150, 50)
PURPLE = (160, 100, 200)
CYAN = (100, 200, 220)
NAVY = (20, 30, 50)
DARK_NAVY = (10, 15, 25)

# チームカラー
TEAM_COLORS = {
    "東京ビクトリーズ": ((255, 102, 0), (0, 0, 0)),
    "大阪タイタンズ": ((255, 215, 0), (0, 0, 0)),
    "横浜オーシャンズ": ((0, 90, 180), (255, 255, 255)),
    "名古屋ドラグーンズ": ((0, 80, 165), (255, 255, 255)),
    "広島ファイヤーズ": ((200, 0, 0), (255, 255, 255)),
    "神宮スターズ": ((0, 60, 125), (255, 255, 255)),
    "福岡フェニックス": ((255, 215, 0), (0, 0, 0)),
    "千葉マリナーズ": ((0, 0, 0), (255, 255, 255)),
    "埼玉レオンズ": ((0, 70, 135), (255, 255, 255)),
    "仙台イーグルス": ((155, 0, 45), (255, 215, 0)),
    "大阪バッファローズ": ((0, 50, 100), (255, 215, 0)),
    "札幌ベアーズ": ((0, 75, 145), (255, 255, 255)),
}

# チーム略称
TEAM_ABBREVIATIONS = {
    "東京ビクトリーズ": "東京V",
    "大阪タイタンズ": "大阪T",
    "横浜オーシャンズ": "横浜O",
    "名古屋ドラグーンズ": "名古屋",
    "広島ファイヤーズ": "広島F",
    "神宮スターズ": "神宮S",
    "福岡フェニックス": "福岡P",
    "千葉マリナーズ": "千葉M",
    "埼玉レオンズ": "埼玉L",
    "仙台イーグルス": "仙台E",
    "大阪バッファローズ": "大阪B",
    "札幌ベアーズ": "札幌B",
}

# NPB設定
NPB_CENTRAL_TEAMS = [
    "東京ビクトリーズ",
    "大阪タイタンズ",
    "横浜オーシャンズ",
    "名古屋ドラグーンズ",
    "広島ファイヤーズ",
    "神宮スターズ"
]

NPB_PACIFIC_TEAMS = [
    "福岡フェニックス",
    "千葉マリナーズ",
    "埼玉レオンズ",
    "仙台イーグルス",
    "大阪バッファローズ",
    "札幌ベアーズ"
]

# 外国人選手名
FOREIGN_SURNAMES = [
    "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson",
    "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
    "Thompson", "Garcia", "Martinez", "Rodriguez", "Lee", "Walker", "Hall", "Allen",
    "Young", "King", "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker",
    "Gonzalez", "Nelson", "Carter", "Mitchell", "Perez", "Roberts", "Turner", "Phillips",
    "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Sanchez", "Morris"
]

FOREIGN_FIRSTNAMES = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
    "Thomas", "Charles", "Daniel", "Matthew", "Anthony", "Donald", "Mark", "Paul",
    "Steven", "Andrew", "Kenneth", "Joshua", "Kevin", "Brian", "George", "Edward",
    "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan", "Jacob", "Nicholas", "Eric",
    "Tyler", "Austin", "Brandon", "Justin", "Aaron", "Adam", "Nathan", "Zachary",
    "Dylan", "Christian", "Kyle", "Jose", "Juan", "Carlos", "Luis", "Miguel"
]

# 日本人選手名（架空）
JAPANESE_SURNAMES = [
    "青山", "赤井", "秋元", "浅野", "天野", "荒木", "有馬", "安藤", "飯田", "池上",
    "石橋", "磯野", "市川", "岩崎", "上田", "内山", "榎本", "遠藤", "大石", "大川",
    "大野", "岡崎", "奥田", "小野寺", "海老原", "江藤", "太田", "小笠原", "尾崎", "葛西",
    "片桐", "金子", "神山", "川上", "菊池", "北村", "木下", "国分", "熊谷", "倉田",
    "黒田", "桑原", "小池", "河野", "越智", "小松", "坂井", "桜井", "佐久間", "笹本",
    "篠原", "柴田", "島田", "白石", "杉山", "関根", "瀬戸", "高木", "滝沢", "竹内"
]

JAPANESE_FIRSTNAMES = [
    "翔太", "大輝", "健太", "拓海", "颯太", "悠斗", "蓮", "陽翔", "大和", "翼",
    "海斗", "樹", "蒼", "湊", "陸", "駿", "匠", "凌", "航", "颯",
    "悠", "隼人", "優", "誠", "健", "翔", "大樹", "智也", "勇気", "拓也",
    "陽太", "勇人", "亮太", "将太", "龍馬", "雄大", "慎太郎", "圭介", "修平", "康平"
]

# ドラフト設定
DRAFT_ROUNDS = 7
育成_DRAFT_ROUNDS = 5

# ゲーム定数
SEASON_GAMES = 143  # レギュラーシーズン試合数
INTERLEAGUE_GAMES = 24  # 交流戦試合数
ALL_STAR_DATE = 72  # オールスター開催日（シーズン中盤）

# 能力値定数
STAT_MIN = 1
STAT_MAX = 20
STAT_AVERAGE = 10

# 評価ランク閾値
RANK_THRESHOLDS = {
    "S": 18,
    "A": 15,
    "B": 12,
    "C": 9,
    "D": 6,
    "E": 3,
    "F": 1
}

# ========================================
# 球場情報（架空）
# ========================================
NPB_STADIUMS = {
    "東京ビクトリーズ": {
        "name": "メトロポリタンドーム",
        "capacity": 46000,
        "type": "dome",  # dome/open
        "home_run_factor": 1.1,  # ホームラン出やすさ
        "location": "東京都"
    },
    "大阪タイタンズ": {
        "name": "グランドスタジアム大阪",
        "capacity": 47500,
        "type": "open",
        "home_run_factor": 0.9,
        "location": "大阪府"
    },
    "横浜オーシャンズ": {
        "name": "マリンスタジアム横浜",
        "capacity": 34000,
        "type": "open",
        "home_run_factor": 1.05,
        "location": "神奈川県横浜市"
    },
    "名古屋ドラグーンズ": {
        "name": "セントラルドーム名古屋",
        "capacity": 36000,
        "type": "dome",
        "home_run_factor": 0.85,
        "location": "愛知県名古屋市"
    },
    "広島ファイヤーズ": {
        "name": "フェニックススタジアム広島",
        "capacity": 33000,
        "type": "open",
        "home_run_factor": 1.0,
        "location": "広島県広島市"
    },
    "神宮スターズ": {
        "name": "スターライトスタジアム",
        "capacity": 32000,
        "type": "open",
        "home_run_factor": 1.15,
        "location": "東京都"
    },
    "福岡フェニックス": {
        "name": "サンシャインドーム福岡",
        "capacity": 38500,
        "type": "dome",
        "home_run_factor": 0.95,
        "location": "福岡県福岡市"
    },
    "千葉マリナーズ": {
        "name": "オーシャンパーク千葉",
        "capacity": 30000,
        "type": "open",
        "home_run_factor": 0.9,
        "location": "千葉県千葉市"
    },
    "埼玉レオンズ": {
        "name": "ライオンズドーム",
        "capacity": 31500,
        "type": "dome",
        "home_run_factor": 1.0,
        "location": "埼玉県"
    },
    "仙台イーグルス": {
        "name": "イーグルスタジアム仙台",
        "capacity": 29000,
        "type": "open",
        "home_run_factor": 1.0,
        "location": "宮城県仙台市"
    },
    "大阪バッファローズ": {
        "name": "グランドドーム大阪",
        "capacity": 36000,
        "type": "dome",
        "home_run_factor": 0.85,
        "location": "大阪府大阪市"
    },
    "札幌ベアーズ": {
        "name": "ノースフィールド札幌",
        "capacity": 35000,
        "type": "open",  # 開閉式
        "home_run_factor": 1.05,
        "location": "北海道"
    },
}

# ========================================
# NPBタイトル・表彰
# ========================================
NPB_BATTING_TITLES = [
    "首位打者",      # 最高打率
    "本塁打王",      # 最多本塁打
    "打点王",        # 最多打点
    "盗塁王",        # 最多盗塁
    "最多安打",      # 最多安打
    "最高出塁率",    # 最高出塁率
]

NPB_PITCHING_TITLES = [
    "最多勝",        # 最多勝利
    "最優秀防御率",  # 最低防御率
    "最多奪三振",    # 最多奪三振
    "最多セーブ",    # 最多セーブ
    "最優秀中継ぎ",  # 最優秀中継ぎ（ホールドポイント）
]

NPB_AWARDS = [
    "MVP",           # 最優秀選手
    "新人王",        # 最優秀新人
    "ベストナイン",  # 各ポジション最優秀
    "ゴールデングラブ賞",  # 守備最優秀
    "カムバック賞",  # 復活した選手
]

# ========================================
# NPB記録
# ========================================
NPB_RECORDS = {
    # シーズン打撃記録
    "シーズン最多本塁打": 60,  # 王貞治（1964）
    "シーズン最高打率": 0.389,  # ランディ・バース（1986）
    "シーズン最多安打": 214,  # マット・マートン（2010）
    "シーズン最多打点": 161,  # 小鶴誠（1950）
    "シーズン最多盗塁": 106,  # 福本豊（1972）
    
    # シーズン投手記録
    "シーズン最多勝": 42,  # 稲尾和久（1961）、現代では20勝が目安
    "シーズン最低防御率": 0.73,  # 藤本英雄（1943）
    "シーズン最多奪三振": 401,  # 江夏豊（1968）
    "シーズン最多セーブ": 54,  # 藤川球児（2007）など
    
    # 通算記録
    "通算最多本塁打": 868,  # 王貞治
    "通算最多安打": 3085,  # 張本勲
    "通算最多勝": 400,  # 金田正一
    "通算最多奪三振": 4490,  # 金田正一
}

# ========================================
# 交流戦・CS・日本シリーズ
# ========================================
INTERLEAGUE_START_GAME = 50   # 交流戦開始試合数目
INTERLEAGUE_END_GAME = 68     # 交流戦終了試合数目

# クライマックスシリーズ
CS_FIRST_STAGE_GAMES = 3      # CSファーストステージ（先に2勝）
CS_FINAL_STAGE_GAMES = 6      # CSファイナルステージ（先に4勝、1位チームに1勝アドバンテージ）

# 日本シリーズ
JAPAN_SERIES_GAMES = 7        # 日本シリーズ（先に4勝）

# ========================================
# 選手契約・年俸
# ========================================
SALARY_RANGES = {
    "新人": (800, 1500),        # 万円
    "若手": (1000, 5000),
    "中堅": (3000, 20000),
    "ベテラン": (5000, 50000),
    "スター": (20000, 100000),
    "外国人": (5000, 80000),
}

CONTRACT_YEARS_MAX = 7        # 最長契約年数（FA権取得前）
FA_YEARS_REQUIREMENT = 8      # 国内FA権取得必要年数（高卒9年、大卒・社会人7年簡略化）

# ========================================
# ドラフト詳細
# ========================================
DRAFT_TYPES = {
    "高校生": {"age_range": (18, 18), "growth_potential": 1.3},
    "大学生": {"age_range": (22, 22), "growth_potential": 1.1},
    "社会人": {"age_range": (23, 27), "growth_potential": 1.0},
    "独立リーグ": {"age_range": (20, 28), "growth_potential": 1.05},
}

# ========================================
# オールスター
# ========================================
ALL_STAR_GAME_COUNT = 2       # オールスター試合数
ALL_STAR_ROSTER_SIZE = 28     # 各リーグ選出人数

# ========================================
# 順位決定ルール
# ========================================
TIEBREAKER_RULES = [
    "勝率",
    "勝利数",
    "直接対戦成績",
    "セ・パ交流戦勝率",
    "前年順位",
]

