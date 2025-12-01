#-*-cod in g: utf-8-*-
"""
NPBペナントシミュレーター-画面描画モジュール
すべての画面をプロフェッショナルなデザインで統一
"""
imp or t pygame
imp or t math
imp or t time
imp or t r and om
from typ in g imp or t Dict,L is t,Optional,Tuple

from ui_pro imp or t(
Col or s,fonts,FontManager,
Button,Card,ProgressBar,Table,RadarChart,
To as t,To as tManager,
draw_BACKground,draw_header,draw_rounded_rect,draw_shadow,
lerp_col or
)
from constants imp or t(
TEAM_COLORS,NPB_CENTRAL_TEAMS,NPB_PACIFIC_TEAMS,
NPB_STADIUMS,TEAM_ABBREVIATIONS,NPB_BATTING_TITLES,NPB_PITCHING_TITLES
)
from game_state imp or t D if ficultyLevel
from mo del s imp or t Team,Player


cl as s ScreenRenderer:
"""すべての画面を描画するレンダラー"""

def __ in it__(self,screen: pygame.Surface):
self.screen=screen
fonts.in it()#フォント初期化
self.title_animation_time=0
self.b as eball_particles=[]

def get_team_col or(self,team_name: str)->tuple:
"""チームカラーを取得"""
col or s=TEAM_COLORS.get(team_name,(Col or s.PRIMARY,Col or s.TEXT_PRIMARY))
if is in stance(col or s,tuple) and len(col or s)==2and is in stance(col or s[0],tuple):
return col or s[0]#プライマリカラーを返す
return col or s if is in stance(col or s,tuple) else Col or s.PRIMARY

def get_team_abbr(self,team_name: str)->str:
"""チーム略称を取得"""
return TEAM_ABBREVIATIONS.get(team_name,team_name[: 4])

def get_stadium_name(self,team_name: str)->str:
"""本拠地球場名を取得"""
stadium=NPB_STADIUMS.get(team_name,{})
return stadium.get("name","球場")

def _draw_gradient_BACKground(self,team_col or=None,style="def ault"):
"""共通のグラデーション背景を描画"""
width=self.screen.get_width()
height=self.screen.get_height()

#基本グラデーション
f or y in range(height):
ratio=y/height
if style=="dark":
r=in t(15+12*ratio)
g=in t(17+13*ratio)
b=in t(22+16*ratio)
else:
r=in t(18+10*ratio)
g=in t(20+12*ratio)
b=in t(28+14*ratio)
pygame.draw.l in e(self.screen,(r,g,b),(0,y),(width,y))

#チームカラーがある場合、装飾を追加
if team_col or:
#斜めのアクセントライン
f or i in range(3):
start_x=width-350+i*100
l in e_alpha=15-i*3
l in e_col or=(team_col or[0]//5,team_col or[1]//5,team_col or[2]//5)
pygame.draw.l in e(self.screen,l in e_col or,(start_x,0),(start_x-200,height),2)

#上部アクセントライン
pygame.draw.rect(self.screen,team_col or,(0,0,width,3))

#========================================
#タイトル画面
#========================================
def draw_title_screen(self,show_start_menu: bool=False)->Dict[str,Button]:
"""タイトル画面を描画（シンプル＆スタイリッシュ版）"""
#シンプルな暗いグラデーション背景
self._draw_gradient_BACKground(style="dark")

width=self.screen.get_width()
height=self.screen.get_height()
center_x=width//2

self.title_animation_time+=0.02

#中央に縦のアクセントライン（チームカラーのグラデーション）
l in e_surf=pygame.Surface((4,height),pygame.SRCALPHA)
f or y in range(height):
alpha=in t(80*(1-abs(y-height/2)/(height/2)))
l in e_surf.set _at((0,y),(*Col or s.PRIMARY[: 3],alpha))
l in e_surf.set _at((1,y),(*Col or s.PRIMARY[: 3],alpha))
l in e_surf.set _at((2,y),(*Col or s.PRIMARY[: 3],alpha))
l in e_surf.set _at((3,y),(*Col or s.PRIMARY[: 3],alpha))
self.screen.blit(l in e_surf,(center_x-2,0))

#ロゴエリア
logo_y=height//3

#メインタイトル（シンプルに）
title_text="PENNANT"
title=fonts.title.render(title_text,True,Col or s.TEXT_PRIMARY)
title_rect=title.get_rect(center=(center_x,logo_y-30))
self.screen.blit(title,title_rect)

#サブタイトル
subtitle_text="SIMULATOR"
subtitle=fonts.h2.render(subtitle_text,True,Col or s.TEXT_SECONDARY)
subtitle_rect=subtitle.get_rect(center=(center_x,logo_y+30))
self.screen.blit(subtitle,subtitle_rect)

#年度表示
year_text="2025"
year_surf=fonts.t in y.render(year_text,True,Col or s.PRIMARY)
year_rect=year_surf.get_rect(center=(center_x,logo_y+70))
self.screen.blit(year_surf,year_rect)

#ボタンエリア（シンプルに）
btn_width=250
btn_height=55
btn_x=center_x-btn_width//2
btn_y=height//2+50
btn_spac in g=70

buttons={}

if show_start_menu:
#スタートメニュー表示中（ニューゲーム/ロード選択）
#半透明のオーバーレイ
overlay=pygame.Surface((width,height),pygame.SRCALPHA)
overlay.fill((0,0,0,150))
self.screen.blit(overlay,(0,0))

#メニューボックス
menu_w,menu_h=320,280
menu_rect=pygame.Rect(center_x-menu_w//2,height//2-menu_h//2,menu_w,menu_h)
draw_rounded_rect(self.screen,menu_rect,Col or s.BG_CARD,16)

#タイトル
menu_title=fonts.h2.render("GAMESTART",True,Col or s.TEXT_PRIMARY)
menu_title_rect=menu_title.get_rect(centerx=center_x,top=menu_rect.y+25)
self.screen.blit(menu_title,menu_title_rect)

#ボタン
menu_btn_y=menu_rect.y+80
menu_btn_spac in g=60

buttons["new_game"]=Button(
center_x-btn_width//2,menu_btn_y,btn_width,btn_height,
"NEWGAME","primary",font=fonts.h3
)

buttons["load_game"]=Button(
center_x-btn_width//2,menu_btn_y+menu_btn_spac in g,btn_width,btn_height,
"LOADGAME","outl in e",font=fonts.body
)

buttons["BACK_to_title"]=Button(
center_x-btn_width//2,menu_btn_y+menu_btn_spac in g*2,btn_width,btn_height,
"BACK","ghost",font=fonts.body
)

f or btn in buttons.values():
btn.draw(self.screen)
else:
#通常のタイトル画面
#スタートボタン（プライマリ）
buttons["start"]=Button(
btn_x,btn_y,btn_width,btn_height,
"START","primary",font=fonts.h3
)

#設定ボタン（ゴースト）
buttons["set t in gs"]=Button(
btn_x,btn_y+btn_spac in g,btn_width,btn_height,
"SETTINGS","ghost",font=fonts.body
)

#終了ボタン（アウトライン）
buttons["quit"]=Button(
btn_x,btn_y+btn_spac in g*2,btn_width,btn_height,
"QUIT","outl in e",font=fonts.body
)

f or btn in buttons.values():
btn.draw(self.screen)

#フッター
footer=fonts.t in y.render("PressSTARTtobeg in yourjourney",True,Col or s.TEXT_MUTED)
footer_rect=footer.get_rect(center=(center_x,height-40))

#点滅エフェクト
alpha=in t(128+127*math.s in(self.title_animation_time*3))
footer.set _alpha(alpha)
self.screen.blit(footer,footer_rect)

To as tManager.update_ and _draw(self.screen)

return buttons

def draw_new_game_ set up_screen(self,set t in gs_obj,set up_state: dict=None)->Dict[str,Button]:
"""新規ゲーム開始設定画面を描画

Args:
set t in gs_obj: 設定オブジェクト（game_rulesを含む）
set up_state: 設定状態を保持する辞書
"""
draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()
center_x=width//2

#デフォルト状態
if set up_state is None:
set up_state={}

#ヘッダー
header_h=draw_header(self.screen,"NEWGAME")

#サブヘッダー
subtitle=fonts.body.render("ゲーム設定を確認してスタート",True,Col or s.TEXT_SECONDARY)
self.screen.blit(subtitle,(center_x-subtitle.get_width()//2,header_h+10))

buttons={}
rules=set t in gs_obj.game_rules

#カードエリア開始位置
card_top=header_h+50

#画面幅に応じてレイアウト調整
card_spac in g=15
available_width=width-60#左右30pxマージン

if available_width>=1100:
#3列レイアウト
card_width=m in(340,(available_width-card_spac in g*2)//3)
card_height=220
col1_x=30
col2_x=col1_x+card_width+card_spac in g
col3_x=col2_x+card_width+card_spac in g
else:
#2列レイアウト
card_width=m in(400,(available_width-card_spac in g)//2)
card_height=200
col1_x=30
col2_x=col1_x+card_width+card_spac in g
col3_x=col1_x#3番目は下に配置

#===左カード: 難易度・モード設定===
left_card=Card(col1_x,card_top,card_width,card_height,"📊難易度")
left_rect=left_card.draw(self.screen)

y=left_rect.y+50

#難易度選択
d if ficulty_options=[
("e as y","イージー","のんびりプレイ"),
("n or mal","ノーマル","標準的な難易度"),
("hard","ハード","やりごたえあり"),
]

current_d if f=set up_state.get("d if ficulty","n or mal")

f or key,label,desc in d if ficulty_options:
is _selected=current_d if f==key
style="primary"if is _selected else"ghost"

btn=Button(left_rect.x+15,y,card_width-30,38,label,style,font=fonts.body)
btn.draw(self.screen)
buttons[f"d if f_{key}"]=btn

y+=50

#===中央カード: DH制設定===
center_card=Card(col2_x,card_top,card_width,card_height,"⚾DH制ルール")
center_rect=center_card.draw(self.screen)

y=center_rect.y+50

dh_ set t in gs=[
("セリーグDH制","central_dh",rules.central_dh),
("パリーグDH制","pac if ic_dh",rules.pac if ic_dh),
("交流戦DH","in t erleague_dh",rules.in t erleague_dh),
]

f or label,key,value in dh_ set t in gs:
label_surf=fonts.small.render(label,True,Col or s.TEXT_PRIMARY)
self.screen.blit(label_surf,(center_rect.x+15,y+8))

status="ON"if value else"OFF"
style="success"if value else"ghost"
btn=Button(center_rect.right-95,y,75,32,status,style,font=fonts.small)
btn.draw(self.screen)
buttons[f"set up_toggle_{key}"]=btn

y+=45

#===右カード: シーズン設定===
if available_width>=1100:
right_card_y=card_top
else:
right_card_y=card_top+card_height+card_spac in g

right_card=Card(col3_x if available_width>=1100else col2_x,
right_card_y,card_width,card_height,"📅シーズン設定")
right_rect=right_card.draw(self.screen)

y=right_rect.y+50

#シーズン試合数
label_surf=fonts.small.render("試合数",True,Col or s.TEXT_PRIMARY)
self.screen.blit(label_surf,(right_rect.x+15,y))
y+=28

game_options=[120,130,143]
btn_x=right_rect.x+15
btn_w=m in(85,(card_width-45)//3)
f or games in game_options:
is _selected=rules.regular_se as on_games==games
style="primary"if is _selected else"outl in e"
btn=Button(btn_x,y,btn_w,32,f"{games}",style,font=fonts.small)
btn.draw(self.screen)
buttons[f"set up_games_{games}"]=btn
btn_x+=btn_w+10

y+=50

#シーズンイベント
event_ set t in gs=[
("交流戦","enable_ in t erleague",rules.enable_ in t erleague),
("CS","enable_climax_series",rules.enable_climax_series),
("キャンプ","enable_spr in g_camp",rules.enable_spr in g_camp),
]

btn_x=right_rect.x+15
btn_w=m in(90,(card_width-40)//3)
f or label,key,value in event_ set t in gs:
style="success"if value else"ghost"
status_icon="✓"if value else"×"
btn=Button(btn_x,y,btn_w,32,f"{status_icon}{label}",style,font=fonts.t in y)
btn.draw(self.screen)
buttons[f"set up_toggle_{key}"]=btn
btn_x+=btn_w+5

#===下部カード: クイック設定===
bottom_y=max(left_rect.bottom,center_rect.bottom,right_rect.bottom)+card_spac in g
bottom_card=Card(30,bottom_y,width-60,100,"⚡クイック設定")
bottom_rect=bottom_card.draw(self.screen)

pre set _y=bottom_rect.y+50

pre set s=[
("real_2024","🏆リアル2027"),
("cl as s ic","📺クラシック"),
("sh or t","⏱ショート"),
("full","🔥フル"),
]

pre set _btn_w=m in(180,(width-100)//4)
btn_x=bottom_rect.x+20
f or key,label in pre set s:
btn=Button(btn_x,pre set _y,pre set _btn_w,40,label,"outl in e",font=fonts.small)
btn.draw(self.screen)
buttons[f"pre set _{key}"]=btn
btn_x+=pre set _btn_w+15

#===フッター: ボタンエリア===
footer_y=height-80

#BACKボタン
buttons["BACK_title"]=Button(
30,footer_y,140,50,
"TITLE","ghost",font=fonts.body
)
buttons["BACK_title"].draw(self.screen)

#詳細設定ボタン
buttons["advanced_ set t in gs"]=Button(
center_x-90,footer_y,180,50,
"詳細設定...","outl in e",font=fonts.body
)
buttons["advanced_ set t in gs"].draw(self.screen)

#ゲームスタートボタン
buttons["confirm_start"]=Button(
width-200,footer_y,170,50,
"START","primary",font=fonts.h3
)
buttons["confirm_start"].draw(self.screen)

To as tManager.update_ and _draw(self.screen)

return buttons

def _draw_b as eball(self,x: in t,y: in t,radius: in t):
"""野球ボールを描画"""
#白い円
pygame.draw.circle(self.screen,(255,255,255),(x,y),radius)
pygame.draw.circle(self.screen,(200,200,200),(x,y),radius,2)

#縫い目（簡略版）
seam_col or=(200,50,50)
#左側の縫い目
pygame.draw.arc(self.screen,seam_col or,
(x-radius-5,y-radius//2,radius,radius),
-0.5,0.5,2)
#右側の縫い目
pygame.draw.arc(self.screen,seam_col or,
(x+5,y-radius//2,radius,radius),
2.6,3.6,2)

def _draw_title_dec or ations(self,width: in t,height: in t):
"""タイトル画面の装飾を描画"""
#チームカラーの斜めストライプ（非常に薄く）
team_col or s=[
(255,102,0),#巨人
(255,215,0),#阪神
(0,90,180),#DeNA
(200,0,0),#広島
(0,60,125),#ヤクルト
(0,80,165),#中日
]

str ipe_width=150
f or i,col or in enumerate(team_col or s):
x=(i*str ipe_width+in t(self.title_animation_time*20))%(width+str ipe_width*2)-str ipe_width
str ipe_surf=pygame.Surface((str ipe_width,height),pygame.SRCALPHA)
pygame.draw.polygon(str ipe_surf,(*col or,8),[
(0,0),(str ipe_width,0),
(str ipe_width-50,height),(-50,height)
])
self.screen.blit(str ipe_surf,(x,0))

def _draw_team_ticker(self,height: in t):
"""画面下部にチーム名をスクロール表示"""
all_teams=NPB_CENTRAL_TEAMS+NPB_PACIFIC_TEAMS

ticker_y=height-80
ticker_text="|".jo in(all_teams)
ticker_text=ticker_text+"|"+ticker_text#繰り返し

#スクロールオフセット
off set=in t(self.title_animation_time*50)%(len(all_teams)*200)

ticker_surf=fonts.small.render(ticker_text,True,Col or s.TEXT_MUTED)
self.screen.blit(ticker_surf,(-off set,ticker_y))

#========================================
#難易度選択画面
#========================================
def draw_d if ficulty_screen(self,current_d if ficulty: D if ficultyLevel)->Dict[str,Button]:
"""難易度選択画面を描画"""
draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()
center_x=width//2

#ヘッダー
header_h=draw_header(self.screen,"難易度選択","ゲームの難しさを選択してください")

#難易度カード
d if ficulties=[
(D if ficultyLevel.EASY,"イージー","初心者向け",Col or s.SUCCESS,"選手能力UP、相手弱体化"),
(D if ficultyLevel.NORMAL,"ノーマル","標準的な難易度",Col or s.PRIMARY,"バランスの取れた設定"),
(D if ficultyLevel.HARD,"ハード","上級者向け",Col or s.WARNING,"相手の能力強化"),
(D if ficultyLevel.VERY_HARD,"ベリーハード","最高難度",Col or s.DANGER,"極限の挑戦"),
]

card_width=220
card_height=200
total_width=card_width*4+30*3
start_x=(width-total_width)//2
card_y=header_h+60

buttons={}

f or i,(level,name,desc,col or,detail) in enumerate(d if ficulties):
x=start_x+i*(card_width+30)

#選択中かどうか
is _selected=current_d if ficulty==level

#カード背景
card_rect=pygame.Rect(x,card_y,card_width,card_height)

if is _selected:
draw_shadow(self.screen,card_rect,4,10,50)
bg_col or=lerp_col or(Col or s.BG_CARD,col or,0.15)
draw_rounded_rect(self.screen,card_rect,bg_col or,16)
pygame.draw.rect(self.screen,col or,card_rect,3,b or der_radius=16)
else:
draw_shadow(self.screen,card_rect,2,6,25)
draw_rounded_rect(self.screen,card_rect,Col or s.BG_CARD,16)
draw_rounded_rect(self.screen,card_rect,Col or s.BG_CARD,16,1,Col or s.BORDER)

#アイコン（色付き円）
pygame.draw.circle(self.screen,col or,(x+card_width//2,card_y+45),25)
icon_text=fonts.h2.render(str(i+1),True,Col or s.TEXT_PRIMARY)
icon_rect=icon_text.get_rect(center=(x+card_width//2,card_y+45))
self.screen.blit(icon_text,icon_rect)

#難易度名
name_surf=fonts.h3.render(name,True,Col or s.TEXT_PRIMARY)
name_rect=name_surf.get_rect(center=(x+card_width//2,card_y+95))
self.screen.blit(name_surf,name_rect)

#説明
desc_surf=fonts.small.render(desc,True,Col or s.TEXT_SECONDARY)
desc_rect=desc_surf.get_rect(center=(x+card_width//2,card_y+125))
self.screen.blit(desc_surf,desc_rect)

#詳細
detail_surf=fonts.t in y.render(detail,True,Col or s.TEXT_MUTED)
detail_rect=detail_surf.get_rect(center=(x+card_width//2,card_y+155))
self.screen.blit(detail_surf,detail_rect)

#ボタン（カード全体）
btn=Button(x,card_y,card_width,card_height,"","ghost")
btn.callBACK=None#視覚的なボタン
buttons[f"d if ficulty_{level.name}"]=btn

#決定ボタン
btn_y=card_y+card_height+60
buttons["confirm"]=Button(
center_x-150,btn_y,300,60,
"決定してNEXT→","success",font=fonts.h3
)
buttons["confirm"].draw(self.screen)

#BACKボタン
buttons["BACK_title"]=Button(
50,height-80,150,50,
"←BACK","ghost",font=fonts.body
)
buttons["BACK_title"].draw(self.screen)

To as tManager.update_ and _draw(self.screen)

return buttons

#========================================
#チーム選択画面（超強化版）
#========================================
def draw_team_select_screen(self,central_teams: L is t,pac if ic_teams: L is t,
custom_names: Dict=None,selected_team_name: str=None,
preview_scroll: in t=0)->Dict[str,Button]:
"""チーム選択画面を描画（超強化版-スクロール対応）"""
draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()
custom_names=custom_names or{}

#ヘッダー
header_h=draw_header(self.screen,"TEAMSELECT","監督としてチームを率いる球団を選んでください")

buttons={}

#チーム名編集ボタン
edit_names_btn=Button(
width-200,header_h-45,160,36,
"チーム名編集","ghost",font=fonts.small
)
edit_names_btn.draw(self.screen)
buttons["edit_team_names"]=edit_names_btn

#左側: チームリスト（2リーグ）
l is t _width=420
panel_height=height-header_h-50

#選択されたチームを見つける
all_teams=central_teams+pac if ic_teams
selected_team=None
if selected_team_name:
f or team in all_teams:
if team.name==selected_team_name:
selected_team=team
break

mouse_pos=pygame.mouse.get_pos()
hovered_team=None
hovered_team_obj=None

#リーグパネル（左側）
leagues=[
("セントラル・リーグ",central_teams,25,Col or s.PRIMARY),
("パシフィック・リーグ",pac if ic_teams,25+l is t _width//2+10,Col or s.DANGER),
]

f or league_name,teams,panel_x,accent_col or in leagues:
#パネル背景
panel_w=l is t _width//2-5
panel_rect=pygame.Rect(panel_x,header_h+15,panel_w,panel_height)
draw_rounded_rect(self.screen,panel_rect,Col or s.BG_CARD,12)
draw_rounded_rect(self.screen,panel_rect,Col or s.BG_CARD,12,1,Col or s.BORDER)

#リーグ名
league_surf=fonts.body.render(league_name,True,accent_col or)
league_rect=league_surf.get_rect(center=(panel_x+panel_w//2,header_h+38))
self.screen.blit(league_surf,league_rect)

#区切り線
pygame.draw.l in e(self.screen,Col or s.BORDER,
(panel_x+15,header_h+58),
(panel_x+panel_w-15,header_h+58),1)

#チームボタン
btn_width=panel_w-24
btn_height=68
btn_x=panel_x+12
btn_y=header_h+70
btn_spac in g=74

f or i,team in enumerate(teams):
team_col or=self.get_team_col or(team.name)
btn_rect=pygame.Rect(btn_x,btn_y+i*btn_spac in g,btn_width,btn_height)

#ホバー・選択検出
is _hovered=btn_rect.collidepo in t(mouse_pos)
is _selected=selected_team_name==team.name

if is _hovered:
hovered_team=team.name
hovered_team_obj=team

#ボタン背景
if is _selected:
bg_col or=lerp_col or(Col or s.BG_CARD,team_col or,0.35)
b or der_col or=team_col or
el if is _hovered:
bg_col or=lerp_col or(Col or s.BG_CARD,team_col or,0.2)
b or der_col or=Col or s.BORDER_LIGHT
else:
bg_col or=lerp_col or(Col or s.BG_CARD,team_col or,0.08)
b or der_col or=Col or s.BORDER

draw_rounded_rect(self.screen,btn_rect,bg_col or,10)
draw_rounded_rect(self.screen,btn_rect,bg_col or,10,2if is _selecte del se1,b or der_col or)

#チームカラーのアクセント
col or _rect=pygame.Rect(btn_x,btn_y+i*btn_spac in g,5,btn_height)
pygame.draw.rect(self.screen,team_col or,col or _rect,b or der_radius=2)

#チーム名
d is play_name=custom_names.get(team.name,team.name)
team_name_surf=fonts.body.render(d is play_name,True,Col or s.TEXT_PRIMARY)
self.screen.blit(team_name_surf,(btn_x+15,btn_y+i*btn_spac in g+10))

#総合戦力（5段階バー）
power_rat in g=self._calculate_team_power(team)
power_y=btn_y+i*btn_spac in g+38
power_label=fonts.t in y.render("戦力:",True,Col or s.TEXT_MUTED)
self.screen.blit(power_label,(btn_x+15,power_y))

#5つ星表示
star_x=btn_x+55
f or s in range(5):
star_col or=Col or s.GOLD if s<power_rat in g else Col or s.BORDER
star_surf=fonts.t in y.render("★",True,star_col or)
self.screen.blit(star_surf,(star_x+s*14,power_y-1))

#登録ボタン（選択用）
btn=Button(
btn_x,btn_y+i*btn_spac in g,btn_width,btn_height,
"","ghost",font=fonts.body
)
btn.is _hovered=is _hovered
buttons[f"team_{team.name}"]=btn

#右側: 選択したチームの詳細プレビュー
preview_x=25+l is t _width+20
preview_width=width-preview_x-25

#プレビューチーム（選択優先）
preview_team=selected_team or hovered_team_obj

if preview_team:
self._draw_team_preview_panel_scrollable(preview_team,preview_x,header_h+15,
preview_width,panel_height,custom_names,buttons,preview_scroll)
else:
#未選択時のガイド
self._draw_team_select_guide(preview_x,header_h+15,preview_width,panel_height)

To as tManager.update_ and _draw(self.screen)

return buttons

def _calculate_team_power(self,team)->in t:
"""チームの総合戦力を5段階で計算"""
if not team.players:
return3

total_overall=sum(
p.stats.overall_batt in g() if p.position.value!="P"else p.stats.overall_pitch in g()
f or p in t eam.players[: 25]
)
avg_overall=total_overall/m in(25,len(team.players))

if avg_overall>=14:
return5
el if avg_overall>=12:
return4
el if avg_overall>=10:
return3
el if avg_overall>=8:
return2
else:
return1

def _draw_team_preview_panel(self,team,x: in t,y: in t,width: in t,height: in t,
custom_names: Dict,buttons: Dict):
"""チーム詳細プレビューパネル（レガシー互換）"""
self._draw_team_preview_panel_scrollable(team,x,y,width,height,custom_names,buttons,0)

def _draw_team_preview_panel_scrollable(self,team,x: in t,y: in t,width: in t,height: in t,
custom_names: Dict,buttons: Dict,scroll_off set: in t=0):
"""チーム詳細プレビューパネル（スクロール対応）"""
team_col or=self.get_team_col or(team.name)

#メインパネル背景
panel_rect=pygame.Rect(x,y,width,height)
draw_shadow(self.screen,panel_rect,3,8,30)
draw_rounded_rect(self.screen,panel_rect,Col or s.BG_CARD,16)

#クリッピング領域を設定
clip_rect=pygame.Rect(x,y,width,height-70)#下部ボタン分を除く

#チームカラーのヘッダー（固定）
header_rect=pygame.Rect(x,y,width,70)
draw_rounded_rect(self.screen,header_rect,lerp_col or(Col or s.BG_CARD,team_col or,0.2),16)

#チーム名
d is play_name=custom_names.get(team.name,team.name)
team_name_surf=fonts.h2.render(d is play_name,True,team_col or)
self.screen.blit(team_name_surf,(x+20,y+12))

#球場情報
stadium=NPB_STADIUMS.get(team.name,{})
if stadium:
stadium_text=f"{stadium.get('name','')}/{stadium.get('location','')}"
stadium_surf=fonts.t in y.render(stadium_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(stadium_surf,(x+20,y+45))

#スクロール可能なコンテンツエリア
content_y=y+80-scroll_off set
content_start_y=y+80
content_end_y=y+height-80

#クリッピング
self.screen.set _clip(pygame.Rect(x,content_start_y,width,content_end_y-content_start_y))

#=====戦力分析（コンパクト版）=====
if content_y+100>content_start_y and content_y<content_end_y:
analys is _rect=pygame.Rect(x+12,content_y,width-24,90)
draw_rounded_rect(self.screen,analys is _rect,Col or s.BG_INPUT,10)

analys is _label=fonts.small.render("戦力分析",True,Col or s.TEXT_PRIMARY)
self.screen.blit(analys is _label,(x+22,content_y+8))

#攻撃力・守備力・投手力を計算
batters=[p f or p in t eam.players if p.position.value!="P"]
pitchers=[p f or p in t eam.players if p.position.value=="P"]

offense_power=sum(p.stats.contact+p.stats.power f or p in batters[: 9])/max(1,len(batters[: 9]))/2
def ense_power=sum(p.stats.field in g+p.stats.arm f or p in batters[: 9])/max(1,len(batters[: 9]))/2
pitch in g_power=sum(p.stats.speed+p.stats.control f or p in pitchers[: 6])/max(1,len(pitchers[: 6]))/2

#3つのバー（横並び）
bar_items=[
("攻撃",offense_power/20,Col or s.DANGER),
("守備",def ense_power/20,Col or s.SUCCESS),
("投手",pitch in g_power/20,Col or s.PRIMARY),
]

bar_width=(width-80)//3
f or i,(label,value,col or) in enumerate(bar_items):
bx=x+22+i*(bar_width+10)
by=content_y+35

label_surf=fonts.t in y.render(label,True,Col or s.TEXT_MUTED)
self.screen.blit(label_surf,(bx,by))

bar=ProgressBar(bx,by+18,bar_width-10,12,m in(1.0,value),col or)
bar.draw(self.screen)

value_surf=fonts.t in y.render(f"{in t(value*100)}%",True,Col or s.TEXT_MUTED)
self.screen.blit(value_surf,(bx+bar_width-40,by))

content_y+=100

#=====主力野手=====
if content_y+150>content_start_y and content_y<content_end_y:
batter_rect=pygame.Rect(x+12,content_y,width-24,145)
draw_rounded_rect(self.screen,batter_rect,Col or s.BG_INPUT,10)

batter_label=fonts.small.render("主力野手",True,Col or s.TEXT_PRIMARY)
self.screen.blit(batter_label,(x+22,content_y+8))

top_batters=s or ted(batters,key=lambda p: p.stats.overall_batt in g(),reverse=True)[: 5]
f or i,player in enumerate(top_batters):
py=content_y+32+i*22

pos_surf=fonts.t in y.render(player.position.value,True,Col or s.TEXT_SECONDARY)
self.screen.blit(pos_surf,(x+22,py))

name_surf=fonts.small.render(player.name[: 8],True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(x+55,py-2))

#能力値
overall=player.stats.overall_batt in g()
badge_col or=self._get_overall_col or(overall)
badge_surf=fonts.t in y.render(f"総合{overall:.0f}",True,badge_col or)
self.screen.blit(badge_surf,(x+width-80,py))

content_y+=155

#=====主力投手=====
if content_y+150>content_start_y and content_y<content_end_y:
pitcher_rect=pygame.Rect(x+12,content_y,width-24,145)
draw_rounded_rect(self.screen,pitcher_rect,Col or s.BG_INPUT,10)

pitcher_label=fonts.small.render("主力投手",True,Col or s.TEXT_PRIMARY)
self.screen.blit(pitcher_label,(x+22,content_y+8))

top_pitchers=s or ted(pitchers,key=lambda p: p.stats.overall_pitch in g(),reverse=True)[: 5]
f or i,player in enumerate(top_pitchers):
py=content_y+32+i*22

role="先発"if i<3else"中継"
pos_surf=fonts.t in y.render(role,True,Col or s.TEXT_SECONDARY)
self.screen.blit(pos_surf,(x+22,py))

name_surf=fonts.small.render(player.name[: 8],True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(x+55,py-2))

overall=player.stats.overall_pitch in g()
badge_col or=self._get_overall_col or(overall)
badge_surf=fonts.t in y.render(f"総合{overall:.0f}",True,badge_col or)
self.screen.blit(badge_surf,(x+width-80,py))

content_y+=155

#=====球場情報=====
if content_y+80>content_start_y and content_y<content_end_y:
stadium_rect=pygame.Rect(x+12,content_y,width-24,75)
draw_rounded_rect(self.screen,stadium_rect,Col or s.BG_INPUT,10)

stadium_label=fonts.small.render("球場特性",True,Col or s.TEXT_PRIMARY)
self.screen.blit(stadium_label,(x+22,content_y+8))

if stadium:
sy=content_y+35

cap_text=f"収容:{stadium.get('capacity',0):,}人"
cap_surf=fonts.t in y.render(cap_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(cap_surf,(x+22,sy))

hr_fact or=stadium.get("home_run_fact or",1.0)
hr_text=f"HR係数:{hr_fact or:.2f}"
hr_col or=Col or s.DANGER if hr_fact or>1.0else Col or s.SUCCESS if hr_fact or<1.0else Col or s.TEXT_PRIMARY
hr_surf=fonts.t in y.render(hr_text,True,hr_col or)
self.screen.blit(hr_surf,(x+130,sy))

if hr_fact or>1.05:
type_text="打者有利"
type_col or=Col or s.DANGER
el if hr_fact or<0.95:
type_text="投手有利"
type_col or=Col or s.SUCCESS
else:
type_text="標準"
type_col or=Col or s.TEXT_MUTED
type_surf=fonts.t in y.render(type_text,True,type_col or)
self.screen.blit(type_surf,(x+240,sy))

#クリッピング解除
self.screen.set _clip(None)

#下部に固定ボタンエリア
btn_area_rect=pygame.Rect(x,y+height-70,width,70)
draw_rounded_rect(self.screen,btn_area_rect,Col or s.BG_CARD,0)

#決定ボタン
confirm_btn=Button(
x+12,y+height-60,width-24,50,
f"{d is play_name}で始める","success",font=fonts.h3
)
confirm_btn.draw(self.screen)
buttons["confirm_team"]=confirm_btn

#スクロールインジケーター（内容が多い場合）
total_content_height=100+155+155+80#各セクションの高さの合計
v is ible_height=height-150#ヘッダーとボタンを除く

if total_content_height>v is ible_height:
#スクロールバー
scrollbar_height=max(30,in t(v is ible_height*v is ible_height/total_content_height))
scrollbar_y=y+80+in t((v is ible_height-scrollbar_height)*scroll_off set/max(1,total_content_height-v is ible_height))
scrollbar_rect=pygame.Rect(x+width-8,scrollbar_y,4,scrollbar_height)
pygame.draw.rect(self.screen,Col or s.BORDER_LIGHT,scrollbar_rect,b or der_radius=2)

def _draw_team_select_guide(self,x: in t,y: in t,width: in t,height: in t):
"""チーム未選択時のガイド"""
panel_rect=pygame.Rect(x,y,width,height)
draw_rounded_rect(self.screen,panel_rect,Col or s.BG_CARD,16)
draw_rounded_rect(self.screen,panel_rect,Col or s.BG_CARD,16,1,Col or s.BORDER)

#中央にガイドテキスト
center_x=x+width//2
center_y=y+height//2

#アイコン
icon_surf=fonts.h1.render("TEAM",True,Col or s.TEXT_MUTED)
icon_rect=icon_surf.get_rect(center=(center_x,center_y-50))
self.screen.blit(icon_surf,icon_rect)

#メインテキスト
text1="チームを選択してください"
text1_surf=fonts.h2.render(text1,True,Col or s.TEXT_SECONDARY)
text1_rect=text1_surf.get_rect(center=(center_x,center_y+10))
self.screen.blit(text1_surf,text1_rect)

#サブテキスト
text2="左のリストからチームをクリックすると"
text3="詳細情報が表示されます"
text2_surf=fonts.body.render(text2,True,Col or s.TEXT_MUTED)
text3_surf=fonts.body.render(text3,True,Col or s.TEXT_MUTED)
text2_rect=text2_surf.get_rect(center=(center_x,center_y+60))
text3_rect=text3_surf.get_rect(center=(center_x,center_y+85))
self.screen.blit(text2_surf,text2_rect)
self.screen.blit(text3_surf,text3_rect)

def _get_overall_col or(self,overall: float)->tuple:
"""総合力に応じた色を返す"""
if overall>=16:
return Col or s.GOLD
el if overall>=14:
return Col or s.SUCCESS
el if overall>=12:
return Col or s.PRIMARY
el if overall>=10:
return Col or s.TEXT_PRIMARY
else:
return Col or s.TEXT_MUTED

def _draw_team_ in fo_tooltip(self,team_name: str,mouse_pos: tuple):
"""チーム情報のツールチップを描画（レガシー互換用）"""
stadium=NPB_STADIUMS.get(team_name,{})
if not stadium:
return

#ツールチップの内容
l in es=[
f"{stadium.get('location','')}",
f"{stadium.get('name','')}",
f"収容:{stadium.get('capacity',0):,}人",
f"HR係数:{stadium.get('home_run_fact or',1.0):.2f}",
]

#サイズ計算
max_width=max(fonts.small.size(l in e)[0]f or l in e in l in es)+30
tooltip_height=len(l in es)*25+20

#位置調整（画面外に出ないように）
x=m in(mouse_pos[0]+20,self.screen.get_width()-max_width-10)
y=m in(mouse_pos[1]+20,self.screen.get_height()-tooltip_height-10)

#背景
tooltip_rect=pygame.Rect(x,y,max_width,tooltip_height)
draw_shadow(self.screen,tooltip_rect,3,6,40)
draw_rounded_rect(self.screen,tooltip_rect,Col or s.BG_CARD,8)
draw_rounded_rect(self.screen,tooltip_rect,Col or s.BG_CARD,8,1,Col or s.BORDER_LIGHT)

#テキスト
text_y=y+10
f or l in e in l in es:
l in e_surf=fonts.small.render(l in e,True,Col or s.TEXT_PRIMARY)
self.screen.blit(l in e_surf,(x+15,text_y))
text_y+=25

#========================================
#メインメニュー画面（スタイリッシュ版）
#========================================
def draw_menu_screen(self,player_team,current_year: in t,schedule_manager,news_ l is t: l is t=None,central_teams: l is t=None,pac if ic_teams: l is t=None)->Dict[str,Button]:
"""メインメニュー画面を描画（洗練されたスポーツデザイン）"""
width=self.screen.get_width()
height=self.screen.get_height()

#グラデーション背景
f or y in range(height):
ratio=y/height
r=in t(18+8*ratio)
g=in t(20+10*ratio)
b=in t(28+12*ratio)
pygame.draw.l in e(self.screen,(r,g,b),(0,y),(width,y))

team_col or=self.get_team_col or(player_team.name) if player_team else Col or s.PRIMARY

#装飾ライン（斜めのアクセント）
l in e_col or=(*team_col or[: 3],30) if len(team_col or)==3else team_col or
f or i in range(3):
start_x=width-300+i*80
pygame.draw.l in e(self.screen,(team_col or[0]//4,team_col or[1]//4,team_col or[2]//4),
(start_x,0),(start_x-150,height),2)

#上部アクセントライン
pygame.draw.rect(self.screen,team_col or,(0,0,width,3))

buttons={}

#========================================
#左上: チーム情報
#========================================
if player_team:
#チーム略称
abbr=self.get_team_abbr(player_team.name)
abbr_surf=fonts.title.render(abbr,True,team_col or)
self.screen.blit(abbr_surf,(30,20))

#チーム名
team_name_surf=fonts.body.render(player_team.name,True,Col or s.TEXT_SECONDARY)
self.screen.blit(team_name_surf,(30,75))

#シーズン
year_surf=fonts.small.render(f"{current_year}年シーズン",True,Col or s.TEXT_MUTED)
self.screen.blit(year_surf,(30,100))

#成績
rec or d_y=135
rec or d_surf=fonts.h2.render(f"{player_team.w in s}-{player_team.losses}-{player_team.draws}",True,Col or s.TEXT_PRIMARY)
self.screen.blit(rec or d_surf,(30,rec or d_y))

#勝率
rate=player_team.w in _rate if player_team.games_played>0else0
rate_text=f"勝率.{in t(rate*1000): 03d}"
rate_surf=fonts.body.render(rate_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(rate_surf,(30,rec or d_y+40))

#試合進行
progress_text=f"{player_team.games_played}/143試合"
progress_surf=fonts.small.render(progress_text,True,Col or s.TEXT_MUTED)
self.screen.blit(progress_surf,(30,rec or d_y+65))

#========================================
#左側: 次の試合情報
#========================================
next_game=None
if schedule_manager and player_team:
next_game=schedule_manager.get_next_game_ f or _team(player_team.name)

game_y=245
next_label=fonts.small.render("NEXTGAME",True,Col or s.TEXT_MUTED)
self.screen.blit(next_label,(30,game_y))

if next_game:
is _home=next_game.home_team_name==player_team.name
opponent=next_game.away_team_name if is _home else next_game.home_team_name
opp_abbr=self.get_team_abbr(opponent)

#対戦カード
my_abbr=self.get_team_abbr(player_team.name)
vs_text=f"{my_abbr}vs{opp_abbr}"
vs_surf=fonts.h3.render(vs_text,True,Col or s.TEXT_PRIMARY)
self.screen.blit(vs_surf,(30,game_y+25))

#HOME/AWAY
location="（ホーム）"if is _home else"（アウェイ）"
loc_surf=fonts.small.render(location,True,Col or s.TEXT_MUTED)
self.screen.blit(loc_surf,(30,game_y+55))
else:
end_surf=fonts.h3.render("シーズン終了",True,Col or s.GOLD)
self.screen.blit(end_surf,(30,game_y+25))

#========================================
#左側: ニュース（最新5件）
#========================================
news_y=340
news_label=fonts.small.render("NEWS",True,Col or s.TEXT_MUTED)
self.screen.blit(news_label,(30,news_y))

if news_ l is t and len(news_ l is t)>0:
f or i,news_item in enumerate(news_ l is t[: 5]):
#news_itemはdict形式{"date":"...","text":"..."}または文字列
if is in stance(news_item,dict):
date_ str=news_item.get("date","")
text_ str=news_item.get("text","")
news_text=f"[{date_ str}]{text_ str}"
else:
news_text=str(news_item)

#長すぎる場合は省略
if len(news_text)>35:
news_text=news_text[: 35]+"..."

news_surf=fonts.t in y.render(news_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(news_surf,(30,news_y+22+i*20))
else:
no_news=fonts.t in y.render("ニュースはありません",True,Col or s.TEXT_MUTED)
self.screen.blit(no_news,(30,news_y+22))

#========================================
#中央下部: 両リーグ順位表
#========================================
st and in gs_y=height-220
st and in gs_width=200

#セ・リーグ
cl_x=30
cl_label=fonts.small.render("セ・リーグ",True,Col or s.TEXT_MUTED)
self.screen.blit(cl_label,(cl_x,st and in gs_y))

if central_teams:
c_teams=s or ted(central_teams,key=lambda t:(t.w in s-t.losses,t.w in s),reverse=True)
f or i,team in enumerate(c_teams[: 6]):
is _player=player_team and team.name==player_team.name
t_abbr=self.get_team_abbr(team.name)
t_col or=self.get_team_col or(team.name)

y=st and in gs_y+22+i*22

#順位
rank_surf=fonts.t in y.render(f"{i+1}",True,Col or s.TEXT_MUTED)
self.screen.blit(rank_surf,(cl_x,y))

#チーム名
name_col or=t_col or if is _player else Col or s.TEXT_SECONDARY
name_surf=fonts.t in y.render(t_abbr,True,name_col or)
self.screen.blit(name_surf,(cl_x+25,y))

#勝敗
rec or d_text=f"{team.w in s}-{team.losses}"
rec or d_surf=fonts.t in y.render(rec or d_text,True,Col or s.TEXT_MUTED)
self.screen.blit(rec or d_surf,(cl_x+85,y))

#勝率
rate=team.w in _rate if team.games_played>0else0
rate_text=f".{in t(rate*1000): 03d}"
rate_surf=fonts.t in y.render(rate_text,True,Col or s.TEXT_MUTED)
self.screen.blit(rate_surf,(cl_x+140,y))

#パ・リーグ
pl_x=cl_x+st and in gs_width+30
pl_label=fonts.small.render("パ・リーグ",True,Col or s.TEXT_MUTED)
self.screen.blit(pl_label,(pl_x,st and in gs_y))

if pac if ic_teams:
p_teams=s or ted(pac if ic_teams,key=lambda t:(t.w in s-t.losses,t.w in s),reverse=True)
f or i,team in enumerate(p_teams[: 6]):
is _player=player_team and team.name==player_team.name
t_abbr=self.get_team_abbr(team.name)
t_col or=self.get_team_col or(team.name)

y=st and in gs_y+22+i*22

#順位
rank_surf=fonts.t in y.render(f"{i+1}",True,Col or s.TEXT_MUTED)
self.screen.blit(rank_surf,(pl_x,y))

#チーム名
name_col or=t_col or if is _player else Col or s.TEXT_SECONDARY
name_surf=fonts.t in y.render(t_abbr,True,name_col or)
self.screen.blit(name_surf,(pl_x+25,y))

#勝敗
rec or d_text=f"{team.w in s}-{team.losses}"
rec or d_surf=fonts.t in y.render(rec or d_text,True,Col or s.TEXT_MUTED)
self.screen.blit(rec or d_surf,(pl_x+85,y))

#勝率
rate=team.w in _rate if team.games_played>0else0
rate_text=f".{in t(rate*1000): 03d}"
rate_surf=fonts.t in y.render(rate_text,True,Col or s.TEXT_MUTED)
self.screen.blit(rate_surf,(pl_x+140,y))

#========================================
#右下: メニューボタン（小型・英語+日本語）
#========================================
btn_w=120
btn_h=50
btn_gap=8
#右下に配置（3行2列+システムボタン1行）
total_btn_height=(btn_h+btn_gap)*3+15+32#メニュー3行+gap+システム1行
btn_area_x=width-275
btn_area_y=height-total_btn_height-25#下から配置

menu_buttons=[
("start_game","PLAY","試合"),
("roster","ROSTER","編成"),
("schedule","SCHEDULE","日程"),
("tra in ing","TRAINING","育成"),
("management","FINANCE","経営"),
("rec or ds","RECORDS","記録"),
]

f or i,(name,en_label,jp_label) in enumerate(menu_buttons):
col=i%2
row=i//2
bx=btn_area_x+col*(btn_w+btn_gap)
by=btn_area_y+row*(btn_h+btn_gap)

#ボタン背景
btn_rect=pygame.Rect(bx,by,btn_w,btn_h)

#PLAYボタンは特別な色
if name=="start_game":
pygame.draw.rect(self.screen,(40,45,55),btn_rect,b or der_radius=8)
pygame.draw.rect(self.screen,team_col or,btn_rect,2,b or der_radius=8)
else:
pygame.draw.rect(self.screen,(35,38,48),btn_rect,b or der_radius=8)
pygame.draw.rect(self.screen,(60,65,75),btn_rect,1,b or der_radius=8)

#英語ラベル
en_surf=fonts.small.render(en_label,True,Col or s.TEXT_PRIMARY)
en_rect=en_surf.get_rect(centerx=bx+btn_w//2,top=by+8)
self.screen.blit(en_surf,en_rect)

#日本語ラベル
jp_surf=fonts.t in y.render(jp_label,True,Col or s.TEXT_MUTED)
jp_rect=jp_surf.get_rect(centerx=bx+btn_w//2,top=by+28)
self.screen.blit(jp_surf,jp_rect)

btn=Button(bx,by,btn_w,btn_h,"","ghost")
buttons[name]=btn

#システムボタン（右下最下部）
sys_y=btn_area_y+(btn_h+btn_gap)*3+15
sys_btn_w=75
sys_btn_h=32

sys_buttons=[
("save_game","SAVE","保存"),
("set t in gs_menu","CONFIG","設定"),
("return _to_title","TITLE","戻る"),
]

f or i,(name,en_label,jp_label) in enumerate(sys_buttons):
bx=btn_area_x+i*(sys_btn_w+8)

btn_rect=pygame.Rect(bx,sys_y,sys_btn_w,sys_btn_h)
pygame.draw.rect(self.screen,(30,32,40),btn_rect,b or der_radius=6)
pygame.draw.rect(self.screen,(50,55,65),btn_rect,1,b or der_radius=6)

#ラベル
label_surf=fonts.t in y.render(en_label,True,Col or s.TEXT_SECONDARY)
label_rect=label_surf.get_rect(center=(bx+sys_btn_w//2,sys_y+sys_btn_h//2))
self.screen.blit(label_surf,label_rect)

btn=Button(bx,sys_y,sys_btn_w,sys_btn_h,"","ghost")
buttons[name]=btn

#区切り線
pygame.draw.l in e(self.screen,(40,45,55),(btn_area_x-25,30),(btn_area_x-25,height-30),1)

To as tManager.update_ and _draw(self.screen)

return buttons

def _draw_league_st and in gs_modern(self,x: in t,y: in t,width: in t,height: in t,
player_team,schedule_manager,team_col or):
"""モダンなリーグ順位パネル"""
#パネル背景
panel_rect=pygame.Rect(x,y,width,height)
draw_rounded_rect(self.screen,panel_rect,Col or s.BG_CARD,16)

if not player_team:
return

#プレイヤーのリーグ
is _central=player_team.league.value=="セントラル"
league_name="CENTRAL"if is _central else"PACIFIC"
accent_col or=team_col or

#タイトル
title_surf=fonts.small.render(league_name,True,accent_col or)
self.screen.blit(title_surf,(x+20,y+15))

league_label=fonts.t in y.render("LEAGUE",True,Col or s.TEXT_MUTED)
self.screen.blit(league_label,(x+20,y+35))

#区切り線
pygame.draw.l in e(self.screen,Col or s.BORDER,(x+15,y+60),(x+width-15,y+60),1)

#順位データ
if schedule_manager:
if is _central and h as attr(schedule_manager,'central_teams'):
teams=schedule_manager.central_teams
el if h as attr(schedule_manager,'pac if ic_teams'):
teams=schedule_manager.pac if ic_teams
else:
teams=[]

s or ted_teams=s or ted(teams,key=lambda t:(-t.w in _rate,-t.w in s))

row_y=y+75
row_height=52

f or rank,team in enumerate(s or ted_teams,1):
t_col or=self.get_team_col or(team.name)
is _player_team=player_team and team.name==player_team.name

#プレイヤーチームをハイライト
if is _player_team:
highlight_rect=pygame.Rect(x+10,row_y-5,width-20,row_height-2)
draw_rounded_rect(self.screen,highlight_rect,lerp_col or(Col or s.BG_CARD,accent_col or,0.15),8)

#順位バッジ
rank_col or s={1: Col or s.GOLD,2:(192,192,192),3:(205,127,50)}
rank_col or=rank_col or s.get(rank,Col or s.TEXT_MUTED)
rank_surf=fonts.body.render(str(rank),True,rank_col or)
self.screen.blit(rank_surf,(x+20,row_y+10))

#チーム略称
abbr=self.get_team_abbr(team.name)
name_col or=Col or s.TEXT_PRIMARY if is _player_team else Col or s.TEXT_SECONDARY
name_surf=fonts.body.render(abbr,True,t_col or)
self.screen.blit(name_surf,(x+50,row_y+10))

#勝敗
rec or d=f"{team.w in s}-{team.losses}"
rec or d_surf=fonts.small.render(rec or d,True,Col or s.TEXT_SECONDARY)
rec or d_rect=rec or d_surf.get_rect(right=x+width-70,centery=row_y+18)
self.screen.blit(rec or d_surf,rec or d_rect)

#勝率
rate=f".{in t(team.w in _rate*1000): 03d}"if team.games_played>0else".000"
rate_surf=fonts.small.render(rate,True,Col or s.TEXT_PRIMARY)
rate_rect=rate_surf.get_rect(right=x+width-20,centery=row_y+18)
self.screen.blit(rate_surf,rate_rect)

row_y+=row_height

def _draw_league_st and in gs_compact(self,x: in t,y: in t,width: in t,height: in t,
player_team,schedule_manager):
"""リーグ順位パネル（コンパクト版）-後方互換用"""
self._draw_league_st and in gs_modern(x,y,width,height,player_team,schedule_manager,
self.get_team_col or(player_team.name) if player_team else Col or s.PRIMARY)

#旧メソッド保持（後方互換）
def _draw_league_st and in gs_compact_old(self,x: in t,y: in t,width: in t,height: in t,
player_team,schedule_manager):
"""リーグ順位パネル（コンパクト版）"""
#パネル背景
panel_rect=pygame.Rect(x,y,width,height)
draw_rounded_rect(self.screen,panel_rect,Col or s.BG_CARD,12)

#プレイヤーのリーグ
is _central=player_team.league.value=="セントラル"if player_team else True
league_name="セ・リーグ"if is _central else"パ・リーグ"
accent_col or=Col or s.PRIMARY if is _central else Col or s.DANGER

#タイトル
title_surf=fonts.body.render(f"{league_name}順位",True,accent_col or)
self.screen.blit(title_surf,(x+15,y+12))

#区切り線
pygame.draw.l in e(self.screen,Col or s.BORDER,(x+12,y+40),(x+width-12,y+40),1)

#順位データ
if schedule_manager:
if is _central and h as attr(schedule_manager,'central_teams'):
teams=schedule_manager.central_teams
el if h as attr(schedule_manager,'pac if ic_teams'):
teams=schedule_manager.pac if ic_teams
else:
teams=[]

s or ted_teams=s or ted(teams,key=lambda t:(-t.w in _rate,-t.w in s))

row_y=y+50
row_height=36

f or rank,team in enumerate(s or ted_teams,1):
#プレイヤーチームをハイライト
if player_team and team.name==player_team.name:
highlight_rect=pygame.Rect(x+8,row_y-2,width-16,row_height-4)
pygame.draw.rect(self.screen,lerp_col or(Col or s.BG_CARD,accent_col or,0.2),highlight_rect,b or der_radius=6)

team_col or=self.get_team_col or(team.name)

#順位バッジ
rank_col or s={1: Col or s.GOLD,2:(192,192,192),3:(205,127,50)}
rank_col or=rank_col or s.get(rank,Col or s.TEXT_MUTED)
rank_surf=fonts.body.render(str(rank),True,rank_col or)
self.screen.blit(rank_surf,(x+15,row_y+6))

#チーム略称
abbr=self.get_team_abbr(team.name)
name_surf=fonts.body.render(abbr,True,team_col or)
self.screen.blit(name_surf,(x+40,row_y+6))

#勝敗（コンパクト）
rec or d=f"{team.w in s}-{team.losses}"
rec or d_surf=fonts.small.render(rec or d,True,Col or s.TEXT_SECONDARY)
self.screen.blit(rec or d_surf,(x+115,row_y+8))

#勝率
rate=f".{in t(team.w in _rate*1000): 03d}"if team.games_played>0else".000"
rate_surf=fonts.small.render(rate,True,Col or s.TEXT_PRIMARY)
self.screen.blit(rate_surf,(x+175,row_y+8))

row_y+=row_height

#もう一方のリーグへの切り替えボタン（小さく）
other_league="パ・リーグ"if is _central else"セ・リーグ"
switch_text=f"→{other_league}"
switch_surf=fonts.t in y.render(switch_text,True,Col or s.TEXT_MUTED)
self.screen.blit(switch_surf,(x+width-80,y+12))

#========================================
#オーダー設定画面（ドラッグ&ドロップ対応）
#========================================
def draw_l in eup_screen(self,player_team,scroll_off set: in t=0,
dragg in g_player_idx: in t=-1,
drag_pos: tuple=None,
selected_position: str=None)->Dict[str,Button]:
"""オーダー設定画面を描画（ドラッグ&ドロップ対応）"""
draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()

team_col or=self.get_team_col or(player_team.name) if player_team else Col or s.PRIMARY
header_h=draw_header(self.screen,"オーダー設定",
"選手をドラッグして打順に配置",team_col or)

buttons={}
drop_zones={}#ドロップゾーン情報

if not player_team:
return buttons

#========================================
#左パネル: 野球場型のポジション配置
#========================================
field_card=Card(30,header_h+20,480,420,"POSITION")
field_rect=field_card.draw(self.screen)

#フィールドの中心
field_cx=field_rect.x+field_rect.width//2
field_cy=field_rect.y+220

#守備位置の座標（野球場型配置-位置調整）
position_co or ds={
"捕手":(field_cx,field_cy+100),
"一塁手":(field_cx+100,field_cy+20),
"二塁手":(field_cx+45,field_cy-50),
"三塁手":(field_cx-100,field_cy+20),
"遊撃手":(field_cx-45,field_cy-50),
"左翼手":(field_cx-110,field_cy-130),
"中堅手":(field_cx,field_cy-160),
"右翼手":(field_cx+110,field_cy-130),
}

#DHスロットの位置（フィールド下部）
dh_position=(field_cx,field_cy+165)

#グラウンドを簡易的に描画
#外野の扇形
pygame.draw.arc(self.screen,Col or s.SUCCESS,
(field_cx-160,field_cy-220,320,320),
3.14*0.75,3.14*0.25,2)

#内野ダイヤモンド
diamond=[
(field_cx,field_cy-40),#2塁
(field_cx+60,field_cy+30),#1塁
(field_cx,field_cy+100),#ホーム
(field_cx-60,field_cy+30),#3塁
]
pygame.draw.polygon(self.screen,Col or s.BORDER,diamond,2)

#投手マウンド
pygame.draw.circle(self.screen,Col or s.BORDER,(field_cx,field_cy+30),8,2)

#守備配置を取得（チームのposition_ as signmentsを優先）
l in eup=player_team.current_l in eup if player_team.current_l in eup else[]

#チームに保存された守備位置情報を使用
if h as attr(player_team,'position_ as signments') and player_team.position_ as signments:
position_ as signments=dict(player_team.position_ as signments)
else:
position_ as signments={}
#現在のラインナップから守備位置を自動割り当て
f or or der_idx,player_idx in enumerate(l in eup):
if player_idx>=0and player_idx<len(player_team.players):
player=player_team.players[player_idx]
pos=player.position.value

#外野手は順番に配置
if pos=="外野手":
f or field_pos in["左翼手","中堅手","右翼手"]:
if field_pos not in position_ as signments:
position_ as signments[field_pos]=player_idx
break
el if pos in position_co or ds:
if pos not in position_ as signments:
position_ as signments[pos]=player_idx

#各守備位置を描画
f or pos_name,(px,py) in position_co or ds.items():
#短縮名
sh or t_names={
"捕手":"捕","一塁手":"一","二塁手":"二","三塁手":"三",
"遊撃手":"遊","左翼手":"左","中堅手":"中","右翼手":"右"
}
d is play_name=sh or t_names.get(pos_name,pos_name[: 1])

#スロット背景（小さめ）
slot_rect=pygame.Rect(px-38,py-20,76,40)

#ドロップゾーンとして登録
drop_zones[f"pos_{pos_name}"]=slot_rect

#ドラッグ中のハイライト
if dragg in g_player_idx>=0and slot_rect.collidepo in t(drag_pos or(0,0)):
pygame.draw.rect(self.screen,(*Col or s.PRIMARY[: 3],100),slot_rect,b or der_radius=6)
pygame.draw.rect(self.screen,Col or s.PRIMARY,slot_rect,2,b or der_radius=6)
else:
pygame.draw.rect(self.screen,Col or s.BG_CARD_HOVER,slot_rect,b or der_radius=6)
pygame.draw.rect(self.screen,Col or s.BORDER,slot_rect,1,b or der_radius=6)

#配置済み選手
if pos_name in position_ as signments:
player_idx=position_ as signments[pos_name]
player=player_team.players[player_idx]
name=player.name[: 3]
name_surf=fonts.t in y.render(name,True,Col or s.TEXT_PRIMARY)
name_rect=name_surf.get_rect(center=(px,py-3))
self.screen.blit(name_surf,name_rect)

pos_surf=fonts.t in y.render(d is play_name,True,Col or s.TEXT_SECONDARY)
pos_rect=pos_surf.get_rect(center=(px,py+12))
self.screen.blit(pos_surf,pos_rect)
else:
#空きスロット
empty_surf=fonts.small.render(d is play_name,True,Col or s.TEXT_MUTED)
empty_rect=empty_surf.get_rect(center=(px,py))
self.screen.blit(empty_surf,empty_rect)

#DHスロット描画
dh_x,dh_y=dh_position
dh_rect=pygame.Rect(dh_x-38,dh_y-20,76,40)
drop_zones["pos_DH"]=dh_rect

#ドラッグ中のハイライト
if dragg in g_player_idx>=0and dh_rect.collidepo in t(drag_pos or(0,0)):
pygame.draw.rect(self.screen,(*Col or s.PRIMARY[: 3],100),dh_rect,b or der_radius=6)
pygame.draw.rect(self.screen,Col or s.PRIMARY,dh_rect,2,b or der_radius=6)
else:
pygame.draw.rect(self.screen,Col or s.BG_CARD_HOVER,dh_rect,b or der_radius=6)
pygame.draw.rect(self.screen,Col or s.WARNING,dh_rect,1,b or der_radius=6)#DHは特別色

#DHスロット内容
if"DH"in position_ as signments:
dh_player_idx=position_ as signments["DH"]
dh_player=player_team.players[dh_player_idx]
dh_name_surf=fonts.t in y.render(dh_player.name[: 3],True,Col or s.TEXT_PRIMARY)
dh_name_rect=dh_name_surf.get_rect(center=(dh_x,dh_y-3))
self.screen.blit(dh_name_surf,dh_name_rect)

dh_label=fonts.t in y.render("DH",True,Col or s.WARNING)
dh_label_rect=dh_label.get_rect(center=(dh_x,dh_y+12))
self.screen.blit(dh_label,dh_label_rect)
else:
dh_empty=fonts.small.render("DH",True,Col or s.TEXT_MUTED)
dh_empty_rect=dh_empty.get_rect(center=(dh_x,dh_y))
self.screen.blit(dh_empty,dh_empty_rect)

#========================================
#中央パネル: 打順
#========================================
or der_card=Card(520,header_h+20,210,440,"LINEUP")
or der_rect=or der_card.draw(self.screen)

#ポジション重複チェック
position_counts={}
position_conflicts=[]
if h as attr(player_team,'position_ as signments'):
f or pos_name,player_idx in player_team.position_ as signments.items():
if player_idx in l in eup and pos_name!="DH":
#外野は左中右をまとめてカウント
if pos_name in["左翼手","中堅手","右翼手"]:
count_key="外野手"
else:
count_key=pos_name

if count_key not in position_counts:
position_counts[count_key]=[]
position_counts[count_key].append(player_idx)

#重複を検出
f or pos_name,players in position_counts.items():
if pos_name=="外野手"and len(players)>3:
position_conflicts.append(f"外野手が{len(players)}人います")
el if pos_name!="外野手"and len(players)>1:
position_conflicts.append(f"{pos_name}が{len(players)}人います")

y=or der_rect.y+50
f or i in range(9):
slot_rect=pygame.Rect(or der_rect.x+12,y,or der_rect.width-24,36)
drop_zones[f"or der_{i}"]=slot_rect

#ドラッグ中のハイライト
if dragg in g_player_idx>=0and slot_rect.collidepo in t(drag_pos or(0,0)):
pygame.draw.rect(self.screen,(*Col or s.PRIMARY[: 3],100),slot_rect,b or der_radius=5)
pygame.draw.rect(self.screen,Col or s.PRIMARY,slot_rect,2,b or der_radius=5)
else:
pygame.draw.rect(self.screen,Col or s.BG_INPUT,slot_rect,b or der_radius=5)

#打順番号
num_surf=fonts.small.render(f"{i+1}",True,Col or s.PRIMARY)
self.screen.blit(num_surf,(slot_rect.x+6,slot_rect.y+9))

#配置済み選手
if i<len(l in eup) and l in eup[i]>=0and l in eup[i]<len(player_team.players):
player=player_team.players[l in eup[i]]
name_surf=fonts.t in y.render(player.name[: 5],True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(slot_rect.x+28,slot_rect.y+10))

pos_sh or t=player.position.value[: 2]
pos_surf=fonts.t in y.render(pos_sh or t,True,Col or s.TEXT_SECONDARY)
self.screen.blit(pos_surf,(slot_rect.right-28,slot_rect.y+10))

y+=38

#ポジション重複警告表示
if position_conflicts:
warn in g_y=y+5
f or conflict in position_conflicts[: 2]:#最大2件表示
warn in g_surf=fonts.t in y.render(f"⚠{conflict}",True,Col or s.ERROR)
self.screen.blit(warn in g_surf,(or der_rect.x+10,warn in g_y))
warn in g_y+=18

#========================================
#右パネル: 選手一覧（ドラッグ元）
#========================================
roster_card=Card(750,header_h+20,width-780,height-header_h-100,"ROSTER")
roster_rect=roster_card.draw(self.screen)

#タブ: 野手/投手
tab_y=roster_rect.y+45
batter_style="primary"if selected_position!="pitcher"else"ghost"
pitcher_style="primary"if selected_position=="pitcher"else"ghost"

buttons["tab_batters"]=Button(roster_rect.x+10,tab_y,75,28,"野手",batter_style,font=fonts.t in y)
buttons["tab_batters"].draw(self.screen)

buttons["tab_pitchers"]=Button(roster_rect.x+90,tab_y,75,28,"投手",pitcher_style,font=fonts.t in y)
buttons["tab_pitchers"].draw(self.screen)

#選手数表示
if selected_position=="pitcher":
players=player_team.get_active_pitchers()
count_text=f"({len(players)}人)"
else:
players=player_team.get_active_batters()
count_text=f"({len(players)}人)"
count_surf=fonts.t in y.render(count_text,True,Col or s.TEXT_MUTED)
self.screen.blit(count_surf,(roster_rect.x+170,tab_y+8))

#選手リスト（コンパクト表示）
y=tab_y+36
row_height=30#コンパクト化
v is ible_count=(roster_rect.height-100)//row_height

#ヘッダー
header_surf=fonts.t in y.render("名前",True,Col or s.TEXT_MUTED)
self.screen.blit(header_surf,(roster_rect.x+22,y))
stat_header=fonts.t in y.render("能力",True,Col or s.TEXT_MUTED)
self.screen.blit(stat_header,(roster_rect.x+100,y))
y+=18

f or i in range(scroll_off set,m in(len(players),scroll_off set+v is ible_count)):
player=players[i]
player_idx=player_team.players.in dex(player)

row_rect=pygame.Rect(roster_rect.x+8,y,roster_rect.width-30,row_height-2)

#選択済みマーキング
is _ in _l in eup=player_idx in l in eup

if dragg in g_player_idx==player_idx:
#ドラッグ中は半透明
pygame.draw.rect(self.screen,(*Col or s.PRIMARY[: 3],30),row_rect,b or der_radius=4)
el if is _ in _l in eup:
pygame.draw.rect(self.screen,(*Col or s.SUCCESS[: 3],40),row_rect,b or der_radius=4)
pygame.draw.rect(self.screen,Col or s.SUCCESS,row_rect,1,b or der_radius=4)
else:
pygame.draw.rect(self.screen,Col or s.BG_INPUT,row_rect,b or der_radius=4)

#ドラッグ可能インジケータ（コンパクト）
grip_x=row_rect.x+5
f or dot_y in[row_rect.y+8,row_rect.y+14,row_rect.y+20]:
pygame.draw.circle(self.screen,Col or s.TEXT_MUTED,(grip_x,dot_y),1)
pygame.draw.circle(self.screen,Col or s.TEXT_MUTED,(grip_x+4,dot_y),1)

#選手情報（1行にコンパクト）
name_surf=fonts.t in y.render(player.name[: 5],True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(row_rect.x+14,row_rect.y+7))

pos_surf=fonts.t in y.render(player.position.value[: 2],True,Col or s.TEXT_SECONDARY)
self.screen.blit(pos_surf,(row_rect.x+70,row_rect.y+7))

#能力値プレビュー
if player.position.value=="投手":
stat_text=f"球{player.stats.speed}制{player.stats.control}"
else:
stat_text=f"ミ{player.stats.contact}パ{player.stats.power}"
stat_preview=fonts.t in y.render(stat_text,True,Col or s.TEXT_MUTED)
self.screen.blit(stat_preview,(row_rect.x+100,row_rect.y+7))

#詳細ボタン（小さめ）
detail_btn=Button(
row_rect.right-32,row_rect.y+3,28,row_height-8,
"詳","outl in e",font=fonts.t in y
)
detail_btn.draw(self.screen)
buttons[f"player_detail_{player_idx}"]=detail_btn

#ドラッグ用ボタンとして登録（詳細ボタン以外の領域）
buttons[f"drag_player_{player_idx}"]=Button(
row_rect.x,row_rect.y,row_rect.width-35,row_rect.height,"","ghost"
)

y+=row_height

#スクロールバー表示
if len(players)>v is ible_count:
scroll_track_h=roster_rect.height-120
scroll_h=max(20,in t(scroll_track_h*v is ible_count/len(players)))
max_scroll=len(players)-v is ible_count
scroll_y_pos=roster_rect.y+100+in t((scroll_off set/max(1,max_scroll))*(scroll_track_h-scroll_h))
pygame.draw.rect(self.screen,Col or s.BG_INPUT,
(roster_rect.right-10,roster_rect.y+100,5,scroll_track_h),b or der_radius=2)
pygame.draw.rect(self.screen,Col or s.PRIMARY,
(roster_rect.right-10,scroll_y_pos,5,scroll_h),b or der_radius=2)

#ドラッグ中の選手を描画
if dragg in g_player_idx>=0and drag_pos and dragg in g_player_idx<len(player_team.players):
player=player_team.players[dragg in g_player_idx]
drag_surf=fonts.small.render(player.name[: 6],True,Col or s.PRIMARY)
drag_rect=pygame.Rect(drag_pos[0]-40,drag_pos[1]-12,80,24)
pygame.draw.rect(self.screen,Col or s.BG_CARD,drag_rect,b or der_radius=4)
pygame.draw.rect(self.screen,Col or s.PRIMARY,drag_rect,2,b or der_radius=4)
self.screen.blit(drag_surf,(drag_pos[0]-35,drag_pos[1]-8))

#========================================
#先発投手選択
#========================================
pitcher_card=Card(30,header_h+470,480,90,"STARTER")
pitcher_rect=pitcher_card.draw(self.screen)

#現在の先発投手
if player_team.start in g_pitcher_idx>=0and player_team.start in g_pitcher_idx<len(player_team.players):
pitcher=player_team.players[player_team.start in g_pitcher_idx]
pitcher_surf=fonts.body.render(pitcher.name,True,team_col or)
self.screen.blit(pitcher_surf,(pitcher_rect.x+25,pitcher_rect.y+50))

stat_text=f"球速{pitcher.stats.speed}制球{pitcher.stats.control}"
stat_surf=fonts.t in y.render(stat_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(stat_surf,(pitcher_rect.x+180,pitcher_rect.y+55))
else:
empty_surf=fonts.small.render("投手タブから先発を選んでください",True,Col or s.TEXT_MUTED)
self.screen.blit(empty_surf,(pitcher_rect.x+25,pitcher_rect.y+50))

#ドロップゾーンとして登録
drop_zones["start in g_pitcher"]=pitcher_rect

#========================================
#下部ボタン
#========================================
buttons["roster_management"]=Button(
200,height-65,150,45,
"登録管理","ghost",font=fonts.small
)
buttons["roster_management"].draw(self.screen)

buttons["auto_l in eup"]=Button(
width-340,height-65,130,45,
"AUTO","secondary",font=fonts.small
)
buttons["auto_l in eup"].draw(self.screen)

buttons["clear_l in eup"]=Button(
width-200,height-65,130,45,
"CLEAR","ghost",font=fonts.small
)
buttons["clear_l in eup"].draw(self.screen)

buttons["BACK"]=Button(
50,height-65,130,45,
"←BACK","ghost",font=fonts.small
)
buttons["BACK"].draw(self.screen)

To as tManager.update_ and _draw(self.screen)

#ドロップゾーン情報を返す
buttons["_drop_zones"]=drop_zones

return buttons

#========================================
#試合進行画面
#========================================
def draw_game_screen(self,player_team,opponent_team)->Dict[str,Button]:
"""試合進行画面を描画"""
draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()
center_x=width//2

buttons={}

#大きな試合情報表示
vs_y=height//3

#チーム名
team1_col or=self.get_team_col or(player_team.name) if player_team else Col or s.PRIMARY
team2_col or=self.get_team_col or(opponent_team.name) if opponent_team else Col or s.DANGER

team1_surf=fonts.h1.render(player_team.name if player_team else"???",True,team1_col or)
team1_rect=team1_surf.get_rect(center=(center_x-200,vs_y))
self.screen.blit(team1_surf,team1_rect)

vs_surf=fonts.h2.render("VS",True,Col or s.TEXT_SECONDARY)
vs_rect=vs_surf.get_rect(center=(center_x,vs_y))
self.screen.blit(vs_surf,vs_rect)

team2_surf=fonts.h1.render(opponent_team.name if opponent_team else"???",True,team2_col or)
team2_rect=team2_surf.get_rect(center=(center_x+200,vs_y))
self.screen.blit(team2_surf,team2_rect)

#プログレス表示
progress_text=fonts.h3.render("試合シミュレーション中...",True,Col or s.TEXT_PRIMARY)
progress_rect=progress_text.get_rect(center=(center_x,vs_y+100))
self.screen.blit(progress_text,progress_rect)

#プログレスバー
bar=ProgressBar(center_x-200,vs_y+150,400,12,0.5,Col or s.PRIMARY)
bar.draw(self.screen,show_text=False)

To as tManager.update_ and _draw(self.screen)

return buttons

#========================================
#試合結果画面
#========================================
def draw_result_screen(self,game_simulat or,scroll_off set: in t=0)->Dict[str,Button]:
"""試合結果画面を描画（詳細情報付き）"""
width=self.screen.get_width()
height=self.screen.get_height()
center_x=width//2

buttons={}

if not game_simulat or:
return buttons

#背景グラデーション
f or y in range(height):
ratio=y/height
r=in t(12+16*ratio)
g=in t(14+18*ratio)
b=in t(22+20*ratio)
pygame.draw.l in e(self.screen,(r,g,b),(0,y),(width,y))

home_team=game_simulat or.home_team
away_team=game_simulat or.away_team
home_sc or e=game_simulat or.home_sc or e
away_sc or e=game_simulat or.away_sc or e

home_col or=self.get_team_col or(home_team.name)
away_col or=self.get_team_col or(away_team.name)

#勝敗判定
is _home_w in=home_sc or e>away_sc or e
is _away_w in=away_sc or e>home_sc or e
is _draw=home_sc or e==away_sc or e

#========================================
#スコアボードエリア
#========================================
sc or e_area_h=200
sc or e_rect=pygame.Rect(40,30,width-80,sc or e_area_h)
pygame.draw.rect(self.screen,(25,28,38),sc or e_rect,b or der_radius=16)

#チームカラーのアクセントライン
pygame.draw.rect(self.screen,home_col or,(sc or e_rect.x,sc or e_rect.y,6,sc or e_area_h),
b or der_top_left_radius=16,b or der_bottom_left_radius=16)
pygame.draw.rect(self.screen,away_col or,(sc or e_rect.right-6,sc or e_rect.y,6,sc or e_area_h),
b or der_top_right_radius=16,b or der_bottom_right_radius=16)

#FINALラベル
f in al_surf=fonts.t in y.render("FINAL",True,Col or s.TEXT_MUTED)
f in al_rect=f in al_surf.get_rect(centerx=center_x,top=sc or e_rect.y+15)
self.screen.blit(f in al_surf,f in al_rect)

#ホームチーム（左側）
home_abbr=self.get_team_abbr(home_team.name)
home_abbr_surf=fonts.h1.render(home_abbr,True,home_col or)
self.screen.blit(home_abbr_surf,(sc or e_rect.x+50,sc or e_rect.y+50))

home_name_surf=fonts.t in y.render(home_team.name,True,Col or s.TEXT_SECONDARY)
self.screen.blit(home_name_surf,(sc or e_rect.x+50,sc or e_rect.y+100))

#ホームチームスコア
home_sc or e_surf=fonts.title.render(str(home_sc or e),True,Col or s.TEXT_PRIMARY if not is _away_w in else Col or s.TEXT_MUTED)
home_sc or e_rect=home_sc or e_surf.get_rect(right=center_x-60,centery=sc or e_rect.y+80)
self.screen.blit(home_sc or e_surf,home_sc or e_rect)

#VSまたは-
vs_surf=fonts.h2.render("-",True,Col or s.TEXT_MUTED)
vs_rect=vs_surf.get_rect(center=(center_x,sc or e_rect.y+80))
self.screen.blit(vs_surf,vs_rect)

#アウェイチームスコア
away_sc or e_surf=fonts.title.render(str(away_sc or e),True,Col or s.TEXT_PRIMARY if not is _home_w in else Col or s.TEXT_MUTED)
away_sc or e_rect=away_sc or e_surf.get_rect(left=center_x+60,centery=sc or e_rect.y+80)
self.screen.blit(away_sc or e_surf,away_sc or e_rect)

#アウェイチーム（右側）
away_abbr=self.get_team_abbr(away_team.name)
away_abbr_surf=fonts.h1.render(away_abbr,True,away_col or)
away_abbr_rect=away_abbr_surf.get_rect(right=sc or e_rect.right-50,top=sc or e_rect.y+50)
self.screen.blit(away_abbr_surf,away_abbr_rect)

away_name_surf=fonts.t in y.render(away_team.name,True,Col or s.TEXT_SECONDARY)
away_name_rect=away_name_surf.get_rect(right=sc or e_rect.right-50,top=sc or e_rect.y+100)
self.screen.blit(away_name_surf,away_name_rect)

#勝敗インジケーター
if is _home_w in:
w in _label=fonts.small.render("WIN",True,Col or s.SUCCESS)
self.screen.blit(w in _label,(sc or e_rect.x+50,sc or e_rect.y+150))
el if is _away_w in:
w in _label=fonts.small.render("WIN",True,Col or s.SUCCESS)
w in _rect=w in _label.get_rect(right=sc or e_rect.right-50,top=sc or e_rect.y+150)
self.screen.blit(w in _label,w in _rect)
else:
draw_label=fonts.small.render("DRAW",True,Col or s.WARNING)
draw_rect=draw_label.get_rect(centerx=center_x,top=sc or e_rect.y+150)
self.screen.blit(draw_label,draw_rect)

#========================================
#試合詳細（イニングスコア・ハイライト）
#========================================
detail_y=sc or e_rect.bottom+20

#左パネル：試合ハイライト
left_panel=pygame.Rect(40,detail_y,(width-100)//2,height-detail_y-100)
pygame.draw.rect(self.screen,(30,33,43),left_panel,b or der_radius=12)

highlight_label=fonts.small.render("HIGHLIGHTS",True,Col or s.TEXT_MUTED)
self.screen.blit(highlight_label,(left_panel.x+20,left_panel.y+15))

#ハイライト情報を生成（シミュレータから取得可能なら使用）
highlight_y=left_panel.y+45
highlights=[]

#勝敗に応じたハイライト
if is _home_w in:
highlights.append(f"{home_team.name}が{home_sc or e-away_sc or e}点差で勝利")
el if is _away_w in:
highlights.append(f"{away_team.name}がアウェイで勝利")
else:
highlights.append("両チーム譲らず引き分け")

#得点情報
if home_sc or e+away_sc or e>=10:
highlights.append(f"打撃戦！両チーム計{home_sc or e+away_sc or e}得点")
el if home_sc or e+away_sc or e<=3:
highlights.append("投手戦の好ゲーム")

#スコアが大差の場合
d if f=abs(home_sc or e-away_sc or e)
if d if f>=5:
w in ner=home_team.name if is _home_w in else away_team.name
highlights.append(f"{w in ner}が{d if f}点差の大勝")

f or hl in highlights[: 5]:
hl_surf=fonts.small.render(f"-{hl}",True,Col or s.TEXT_SECONDARY)
self.screen.blit(hl_surf,(left_panel.x+25,highlight_y))
highlight_y+=28

#右パネル：チーム成績
right_panel=pygame.Rect(left_panel.right+20,detail_y,(width-100)//2,height-detail_y-100)
pygame.draw.rect(self.screen,(30,33,43),right_panel,b or der_radius=12)

stats_label=fonts.small.render("TEAMRECORD",True,Col or s.TEXT_MUTED)
self.screen.blit(stats_label,(right_panel.x+20,right_panel.y+15))

#チーム成績表示
stats_y=right_panel.y+50

#ホームチーム
home_rec or d=f"{home_team.w in s}勝{home_team.losses}敗{home_team.draws}分"
home_rate=f"勝率.{in t(home_team.w in _rate*1000): 03d}"if home_team.games_played>0else"勝率.000"

pygame.draw.rect(self.screen,(40,44,55),
(right_panel.x+15,stats_y-5,right_panel.width-30,55),b or der_radius=8)

home_team_surf=fonts.small.render(home_team.name,True,home_col or)
self.screen.blit(home_team_surf,(right_panel.x+25,stats_y))

home_rec or d_surf=fonts.t in y.render(home_rec or d,True,Col or s.TEXT_PRIMARY)
self.screen.blit(home_rec or d_surf,(right_panel.x+25,stats_y+25))

home_rate_surf=fonts.t in y.render(home_rate,True,Col or s.TEXT_MUTED)
home_rate_rect=home_rate_surf.get_rect(right=right_panel.right-25,centery=stats_y+22)
self.screen.blit(home_rate_surf,home_rate_rect)

stats_y+=70

#アウェイチーム
away_rec or d=f"{away_team.w in s}勝{away_team.losses}敗{away_team.draws}分"
away_rate=f"勝率.{in t(away_team.w in _rate*1000): 03d}"if away_team.games_played>0else"勝率.000"

pygame.draw.rect(self.screen,(40,44,55),
(right_panel.x+15,stats_y-5,right_panel.width-30,55),b or der_radius=8)

away_team_surf=fonts.small.render(away_team.name,True,away_col or)
self.screen.blit(away_team_surf,(right_panel.x+25,stats_y))

away_rec or d_surf=fonts.t in y.render(away_rec or d,True,Col or s.TEXT_PRIMARY)
self.screen.blit(away_rec or d_surf,(right_panel.x+25,stats_y+25))

away_rate_surf=fonts.t in y.render(away_rate,True,Col or s.TEXT_MUTED)
away_rate_rect=away_rate_surf.get_rect(right=right_panel.right-25,centery=stats_y+22)
self.screen.blit(away_rate_surf,away_rate_rect)

#========================================
#ボタン
#========================================
buttons["next_game"]=Button(
center_x-100,height-80,200,50,
"NEXT","primary",font=fonts.h3
)
buttons["next_game"].draw(self.screen)

buttons["BACK"]=Button(
50,height-75,120,45,
"BACK","ghost",font=fonts.body
)
buttons["BACK"].draw(self.screen)

To as tManager.update_ and _draw(self.screen)

return buttons

#========================================
#順位表画面（個人成績タブ付き）
#========================================
def draw_st and in gs_screen(self,central_teams: L is t,pac if ic_teams: L is t,player_team,
tab: str="st and in gs",scroll_off set: in t=0)->Dict[str,Button]:
"""順位表・個人成績画面を描画"""
draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()

header_h=draw_header(self.screen,"RECORDS")

buttons={}

#タブ
tabs=[
("st and in gs","順位表"),
("batt in g","打撃成績"),
("pitch in g","投手成績"),
]

tab_y=header_h+15
tab_x=30

f or tab_id,tab_name in t abs:
style="primary"if tab==tab_id else"ghost"
btn=Button(tab_x,tab_y,120,38,tab_name,style,font=fonts.small)
btn.draw(self.screen)
buttons[f"st and in gs_tab_{tab_id}"]=btn
tab_x+=130

content_y=header_h+65

if tab=="st and in gs":
#順位表タブ
panel_width=(width-80)//2

leagues=[
("セントラル・リーグ",central_teams,30,Col or s.PRIMARY),
("パシフィック・リーグ",pac if ic_teams,30+panel_width+20,Col or s.DANGER),
]

f or league_name,teams,panel_x,accent_col or in leagues:
s or ted_teams=s or ted(teams,key=lambda t:(-t.w in _rate,-t.w in s))

panel_rect=pygame.Rect(panel_x,content_y,panel_width,height-content_y-80)
draw_rounded_rect(self.screen,panel_rect,Col or s.BG_CARD,16)
draw_rounded_rect(self.screen,panel_rect,Col or s.BG_CARD,16,1,Col or s.BORDER)

league_surf=fonts.h3.render(league_name,True,accent_col or)
league_rect=league_surf.get_rect(center=(panel_x+panel_width//2,content_y+30))
self.screen.blit(league_surf,league_rect)

headers=["順","チーム","勝","敗","分","率"]
header_x=[15,50,200,245,290,335]
y=content_y+55

f or i,header in enumerate(headers):
h_surf=fonts.t in y.render(header,True,Col or s.TEXT_SECONDARY)
self.screen.blit(h_surf,(panel_x+header_x[i],y))

y+=22
pygame.draw.l in e(self.screen,Col or s.BORDER,
(panel_x+10,y),(panel_x+panel_width-10,y),1)
y+=8

f or rank,team in enumerate(s or ted_teams,1):
row_rect=pygame.Rect(panel_x+8,y-3,panel_width-16,40)

if player_team and team.name==player_team.name:
pygame.draw.rect(self.screen,(*accent_col or[: 3],30),row_rect,b or der_radius=4)

team_col or=self.get_team_col or(team.name)

rank_col or=Col or s.GOLD if rank<=3else Col or s.TEXT_SECONDARY
rank_surf=fonts.body.render(str(rank),True,rank_col or)
self.screen.blit(rank_surf,(panel_x+header_x[0],y+6))

#チーム名を短縮
sh or t_name=team.name[: 6]if len(team.name)>6else team.name
name_surf=fonts.small.render(sh or t_name,True,team_col or)
self.screen.blit(name_surf,(panel_x+header_x[1],y+8))

w in s_surf=fonts.small.render(str(team.w in s),True,Col or s.TEXT_PRIMARY)
self.screen.blit(w in s_surf,(panel_x+header_x[2],y+8))

losses_surf=fonts.small.render(str(team.losses),True,Col or s.TEXT_PRIMARY)
self.screen.blit(losses_surf,(panel_x+header_x[3],y+8))

ties_surf=fonts.small.render(str(team.draws),True,Col or s.TEXT_PRIMARY)
self.screen.blit(ties_surf,(panel_x+header_x[4],y+8))

rate=f".{in t(team.w in _rate*1000): 03d}"if team.games_played>0else".000"
rate_surf=fonts.small.render(rate,True,Col or s.TEXT_PRIMARY)
self.screen.blit(rate_surf,(panel_x+header_x[5],y+8))

y+=42

el if tab=="batt in g":
#打撃成績タブ
self._draw_batt in g_leaders(central_teams+pac if ic_teams,player_team,
content_y,width,height,scroll_off set,buttons)

el if tab=="pitch in g":
#投手成績タブ
self._draw_pitch in g_leaders(central_teams+pac if ic_teams,player_team,
content_y,width,height,scroll_off set,buttons)

#BACKボタン
buttons["BACK"]=Button(
50,height-70,150,50,
"←BACK","ghost",font=fonts.body
)
buttons["BACK"].draw(self.screen)

To as tManager.update_ and _draw(self.screen)

return buttons

def _draw_batt in g_leaders(self,all_teams: L is t,player_team,content_y: in t,
width: in t,height: in t,scroll_off set: in t,buttons: Dict):
"""打撃成績ランキングを描画（実績ベース）"""
#全選手を収集（野手のみ、規定打席以上）
all_batters=[]
f or team in all_teams:
f or player in t eam.players:
if player.position.value!="投手"and player.rec or d.at_bats>=10:
all_batters.append((player,team.name))

#打撃タイトル別カード
card_width=(width-90)//3

titles=[
("打率ランキング","avg","打率"),
("本塁打ランキング","hr","本塁打"),
("打点ランキング","rbi","打点"),
]

f or i,(title,stat_type,stat_label) in enumerate(titles):
card_x=30+i*(card_width+15)
card=Card(card_x,content_y,card_width,height-content_y-80,title)
card_rect=card.draw(self.screen)

#実績ベースでソート
if stat_type=="avg":
s or ted_batters=s or ted(all_batters,key=lambda x:-x[0].rec or d.batt in g_average)
el if stat_type=="hr":
s or ted_batters=s or ted(all_batters,key=lambda x:-x[0].rec or d.home_runs)
else:
s or ted_batters=s or ted(all_batters,key=lambda x:-x[0].rec or d.rb is)

y=card_rect.y+50

f or rank,(player,team_name) in enumerate(s or ted_batters[: 10],1):
row_rect=pygame.Rect(card_rect.x+10,y,card_rect.width-20,35)

#自チームハイライト
if player_team and team_name==player_team.name:
pygame.draw.rect(self.screen,(*Col or s.PRIMARY[: 3],30),row_rect,b or der_radius=4)

#順位
rank_col or=Col or s.GOLD if rank<=3else Col or s.TEXT_MUTED
rank_surf=fonts.small.render(f"{rank}",True,rank_col or)
self.screen.blit(rank_surf,(row_rect.x+5,y+8))

#選手名
name_surf=fonts.small.render(player.name[: 5],True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(row_rect.x+30,y+8))

#チーム略称
abbr=self.get_team_abbr(team_name)
team_surf=fonts.t in y.render(abbr,True,Col or s.TEXT_MUTED)
self.screen.blit(team_surf,(row_rect.x+100,y+10))

#実績値表示
if stat_type=="avg":
avg=player.rec or d.batt in g_average
d is play_val=f".{in t(avg*1000): 03d}"if avg>0else".000"
el if stat_type=="hr":
d is play_val=str(player.rec or d.home_runs)
else:
d is play_val=str(player.rec or d.rb is)
stat_surf=fonts.body.render(d is play_val,True,Col or s.SUCCESS)
stat_rect=stat_surf.get_rect(right=row_rect.right-10,centery=y+17)
self.screen.blit(stat_surf,stat_rect)

y+=38

def _draw_pitch in g_leaders(self,all_teams: L is t,player_team,content_y: in t,
width: in t,height: in t,scroll_off set: in t,buttons: Dict):
"""投手成績ランキングを描画（実績ベース）"""
#全投手を収集（登板数1以上）
all_pitchers=[]
f or team in all_teams:
f or player in t eam.players:
if player.position.value=="投手"and player.rec or d.in n in gs_pitched>=1:
all_pitchers.append((player,team.name))

card_width=(width-90)//3

titles=[
("防御率ランキング","era","防御率"),
("奪三振ランキング","k","奪三振"),
("勝利数ランキング","w in s","勝利"),
]

f or i,(title,stat_type,stat_label) in enumerate(titles):
card_x=30+i*(card_width+15)
card=Card(card_x,content_y,card_width,height-content_y-80,title)
card_rect=card.draw(self.screen)

#実績ベースでソート
if stat_type=="era":
#防御率は低い順、投球回5以上で
qual if ied=[p f or p in all_pitchers if p[0].rec or d.in n in gs_pitched>=5]
s or ted_pitchers=s or ted(qual if ied,key=lambda x: x[0].rec or d.era if x[0].rec or d.era>0else99)
el if stat_type=="k":
s or ted_pitchers=s or ted(all_pitchers,key=lambda x:-x[0].rec or d.str ikeouts_pitched)
else:
s or ted_pitchers=s or ted(all_pitchers,key=lambda x:-x[0].rec or d.w in s)

y=card_rect.y+50

f or rank,(player,team_name) in enumerate(s or ted_pitchers[: 10],1):
row_rect=pygame.Rect(card_rect.x+10,y,card_rect.width-20,35)

if player_team and team_name==player_team.name:
pygame.draw.rect(self.screen,(*Col or s.PRIMARY[: 3],30),row_rect,b or der_radius=4)

rank_col or=Col or s.GOLD if rank<=3else Col or s.TEXT_MUTED
rank_surf=fonts.small.render(f"{rank}",True,rank_col or)
self.screen.blit(rank_surf,(row_rect.x+5,y+8))

name_surf=fonts.small.render(player.name[: 5],True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(row_rect.x+30,y+8))

abbr=self.get_team_abbr(team_name)
team_surf=fonts.t in y.render(abbr,True,Col or s.TEXT_MUTED)
self.screen.blit(team_surf,(row_rect.x+100,y+10))

#実績値表示
if stat_type=="era":
era=player.rec or d.era
d is play_val=f"{era:.2f}"if era>0else"0.00"
el if stat_type=="k":
d is play_val=str(player.rec or d.str ikeouts_pitched)
else:
d is play_val=str(player.rec or d.w in s)
stat_surf=fonts.body.render(d is play_val,True,Col or s.SUCCESS)
stat_rect=stat_surf.get_rect(right=row_rect.right-10,centery=y+17)
self.screen.blit(stat_surf,stat_rect)

y+=38

#========================================
#スケジュール画面
#========================================
def draw_schedule_screen(self,schedule_manager,player_team,scroll_off set: in t=0,
selected_game_idx: in t=-1)->Dict[str,Button]:
"""スケジュール画面を描画（NPB完全版）"""
draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()

team_col or=self.get_team_col or(player_team.name) if player_team else Col or s.PRIMARY
header_h=draw_header(self.screen,"SCHEDULE",player_team.name if player_team else"",team_col or)

buttons={}

if schedule_manager and player_team:
games=schedule_manager.get_team_schedule(player_team.name)

#統計情報を計算
completed_games=[g f or g in games if g.is _completed]
w in s=sum(1f or g in completed_games if g.get_w in ner()==player_team.name)
losses=sum(1f or g in completed_games if g.get_w in ner() and g.get_w in ner()!=player_team.name)
draws=sum(1f or g in completed_games if g.is _draw())

#左パネル: シーズン概要
summary_card=Card(30,header_h+20,280,200,"シーズン概要")
summary_rect=summary_card.draw(self.screen)

y=summary_rect.y+55
summary_items=[
("総試合数",f"{len(games)}試合"),
("消化試合",f"{len(completed_games)}試合"),
("残り試合",f"{len(games)-len(completed_games)}試合"),
("",""),
("成績",f"{w in s}勝{losses}敗{draws}分"),
]

f or label,value in summary_items:
if label=="":
y+=10
cont in ue
label_surf=fonts.small.render(label,True,Col or s.TEXT_SECONDARY)
value_surf=fonts.small.render(value,True,Col or s.TEXT_PRIMARY)
self.screen.blit(label_surf,(summary_rect.x+20,y))
self.screen.blit(value_surf,(summary_rect.x+130,y))
y+=28

#左パネル: 直近の成績
recent_card=Card(30,header_h+235,280,200,"直近5試合")
recent_rect=recent_card.draw(self.screen)

recent_games=completed_games[-5:]if len(completed_games)>=5else completed_games
y=recent_rect.y+55

if recent_games:
f or game in reversed(recent_games):
is _home=game.home_team_name==player_team.name
opponent=game.away_team_name if is _home else game.home_team_name
opponent_abbr=self.get_team_abbr(opponent)

my_sc or e=game.home_sc or e if is _home else game.away_sc or e
opp_sc or e=game.away_sc or e if is _home else game.home_sc or e

#勝敗マーク
if my_sc or e>opp_sc or e:
result_mark="○"
result_col or=Col or s.SUCCESS
el if my_sc or e<opp_sc or e:
result_mark="●"
result_col or=Col or s.DANGER
else:
result_mark="△"
result_col or=Col or s.WARNING

mark_surf=fonts.body.render(result_mark,True,result_col or)
self.screen.blit(mark_surf,(recent_rect.x+20,y))

vs_text=f"vs{opponent_abbr}"
vs_surf=fonts.small.render(vs_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(vs_surf,(recent_rect.x+50,y))

sc or e_text=f"{my_sc or e}-{opp_sc or e}"
sc or e_surf=fonts.small.render(sc or e_text,True,Col or s.TEXT_PRIMARY)
self.screen.blit(sc or e_surf,(recent_rect.x+180,y))

y+=28
else:
no_game_surf=fonts.small.render("まだ試合がありません",True,Col or s.TEXT_MUTED)
self.screen.blit(no_game_surf,(recent_rect.x+20,y))

#右パネル: 全試合日程
schedule_card=Card(330,header_h+20,width-360,height-header_h-100,"試合日程一覧")
schedule_rect=schedule_card.draw(self.screen)

#ヘッダー
headers=[("#",40),("日付",90),("対戦相手",160),("場所",80),("スコア",100),("結果",60)]
x=schedule_rect.x+20
y=schedule_rect.y+50

f or header_text,w in headers:
h_surf=fonts.t in y.render(header_text,True,Col or s.TEXT_MUTED)
self.screen.blit(h_surf,(x,y))
x+=w

y+=25
pygame.draw.l in e(self.screen,Col or s.BORDER,
(schedule_rect.x+15,y),(schedule_rect.right-15,y),1)
y+=8

#試合一覧
row_height=32
v is ible_count=(schedule_rect.height-100)//row_height

#次の試合を探す
next_game_idx=next((i f or i,g in enumerate(games) if not g.is _completed),len(games))

f or i in range(scroll_off set,m in(len(games),scroll_off set+v is ible_count)):
game=games[i]

row_rect=pygame.Rect(schedule_rect.x+10,y-3,schedule_rect.width-20,row_height-2)

#選択された日程をハイライト
if i==selected_game_idx and not game.is _completed:
pygame.draw.rect(self.screen,(*Col or s.GOLD[: 3],60),row_rect,b or der_radius=4)
pygame.draw.rect(self.screen,Col or s.GOLD,row_rect,2,b or der_radius=4)
#次の試合をハイライト
el if i==next_game_idx:
pygame.draw.rect(self.screen,(*team_col or[: 3],40),row_rect,b or der_radius=4)
pygame.draw.rect(self.screen,team_col or,row_rect,2,b or der_radius=4)
el if i%2==0:
pygame.draw.rect(self.screen,Col or s.BG_INPUT,row_rect,b or der_radius=2)

#未完了の試合はクリック可能なボタンとして登録
if not game.is _completed:
row_btn=Button(row_rect.x,row_rect.y,row_rect.width,row_rect.height,"","ghost")
row_btn.col or _n or mal=(0,0,0,0)#透明
row_btn.col or _hover=(*team_col or[: 3],30)
buttons[f"select_game_{i}"]=row_btn

x=schedule_rect.x+20

#試合番号
num_col or=Col or s.TEXT_PRIMARY if not game.is _completed else Col or s.TEXT_MUTED
num_surf=fonts.small.render(str(i+1),True,num_col or)
self.screen.blit(num_surf,(x,y))
x+=40

#日付
date_ str=f"{game.month}/{game.day}"
date_col or=Col or s.TEXT_PRIMARY if not game.is _completed else Col or s.TEXT_MUTED
date_surf=fonts.small.render(date_ str,True,date_col or)
self.screen.blit(date_surf,(x,y))
x+=90

#対戦相手
is _home=game.home_team_name==player_team.name
opponent=game.away_team_name if is _home else game.home_team_name
opp_col or=self.get_team_col or(opponent)
opp_abbr=self.get_team_abbr(opponent)
opp_surf=fonts.small.render(opp_abbr,True,opp_col or if not game.is _completed else Col or s.TEXT_MUTED)
self.screen.blit(opp_surf,(x,y))
x+=160

#場所
if is _home:
loc_text="HOME"
loc_col or=Col or s.SUCCESS
else:
loc_text="AWAY"
loc_col or=Col or s.WARNING
if game.is _completed:
loc_col or=Col or s.TEXT_MUTED
loc_surf=fonts.t in y.render(loc_text,True,loc_col or)
self.screen.blit(loc_surf,(x,y+2))
x+=80

#スコア
if game.is _completed:
my_sc or e=game.home_sc or e if is _home else game.away_sc or e
opp_sc or e=game.away_sc or e if is _home else game.home_sc or e
sc or e_text=f"{my_sc or e}-{opp_sc or e}"
sc or e_surf=fonts.small.render(sc or e_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(sc or e_surf,(x,y))
else:
if i==next_game_idx:
next_surf=fonts.t in y.render("NEXT",True,team_col or)
self.screen.blit(next_surf,(x+10,y+2))
else:
pend in g_surf=fonts.small.render("---",True,Col or s.TEXT_MUTED)
self.screen.blit(pend in g_surf,(x,y))
x+=100

#結果
if game.is _completed:
w in ner=game.get_w in ner()
if w in ner==player_team.name:
result_text="勝ち"
result_col or=Col or s.SUCCESS
el if w in ner is None:
result_text="引分"
result_col or=Col or s.WARNING
else:
result_text="負け"
result_col or=Col or s.DANGER
result_surf=fonts.small.render(result_text,True,result_col or)
self.screen.blit(result_surf,(x,y))

y+=row_height

if y>schedule_rect.bottom-20:
break

#スクロールインジケーター
if len(games)>v is ible_count:
total_pages=(len(games)+v is ible_count-1)//v is ible_count
current_page=scroll_off set//v is ible_count+1
page_text=f"{current_page}/{total_pages}ページ(スクロールで移動)"
page_surf=fonts.t in y.render(page_text,True,Col or s.TEXT_MUTED)
self.screen.blit(page_surf,(schedule_rect.x+20,schedule_rect.bottom-25))

#ボタン
buttons["BACK"]=Button(
50,height-70,150,50,
"←BACK","ghost",font=fonts.body
)
buttons["BACK"].draw(self.screen)

#次の試合へジャンプボタン
if schedule_manager and player_team:
games=schedule_manager.get_team_schedule(player_team.name)
next_idx=next((i f or i,g in enumerate(games) if not g.is _completed),-1)
if next_idx>=0:
buttons["jump_next"]=Button(
220,height-70,150,50,
"NEXTGAME","ghost",font=fonts.body
)
buttons["jump_next"].draw(self.screen)

#選択した日程までスキップボタン
buttons["skip_to_date"]=Button(
390,height-70,200,50,
"この日程まで進む","primary",font=fonts.body
)
buttons["skip_to_date"].draw(self.screen)

#ヒント
h in t _text="日程をクリックして選択→「この日程まで進む」で試合をシミュレート"
h in t _surf=fonts.t in y.render(h in t _text,True,Col or s.TEXT_MUTED)
self.screen.blit(h in t _surf,(620,height-55))

To as tManager.update_ and _draw(self.screen)

return buttons

#========================================
#ドラフト画面
#========================================
def draw_draft_screen(self,prospects: L is t,selected_idx: in t=-1,
draft_round: in t=1,draft_messages: L is t[str]=None,
scroll_off set: in t=0)->Dict[str,Button]:
"""ドラフト画面を描画（スクロール対応）"""
draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()
center_x=width//2

#ヘッダーにラウンド表示
round_text=f"第{draft_round}巡目"
header_h=draw_header(self.screen,f"DRAFT-{round_text}","有望な新人選手を獲得しよう")

buttons={}

#左側: 選手リストカード
card_width=width-350if draft_messages else width-60
card=Card(30,header_h+20,card_width-30,height-header_h-130)
card_rect=card.draw(self.screen)

#ヘッダー
headers=[("名前",150),("ポジション",100),("年齢",60),("ポテンシャル",100),("総合力",80),("",50)]
x=card_rect.x+20
y=card_rect.y+20

f or header_text,w in headers:
h_surf=fonts.small.render(header_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(h_surf,(x,y))
x+=w

y+=25
pygame.draw.l in e(self.screen,Col or s.BORDER,
(card_rect.x+15,y),(card_rect.right-15,y),1)
y+=8

#選手一覧（スクロール対応・画面サイズ適応）
row_height=38
max_v is ible=(card_rect.height-80)//row_height
v is ible_count=m in(max_v is ible,len(prospects)-scroll_off set)

f or i in range(scroll_off set,m in(scroll_off set+v is ible_count,len(prospects))):
prospect=prospects[i]
d is play_i=i-scroll_off set#表示上のインデックス

row_rect=pygame.Rect(card_rect.x+10,y-3,card_rect.width-20,34)

#選択中
if i==selected_idx:
pygame.draw.rect(self.screen,(*Col or s.PRIMARY[: 3],50),row_rect,b or der_radius=5)
pygame.draw.rect(self.screen,Col or s.PRIMARY,row_rect,2,b or der_radius=5)
el if d is play_i%2==0:
pygame.draw.rect(self.screen,Col or s.BG_INPUT,row_rect,b or der_radius=4)

x=card_rect.x+20

#名前
name_surf=fonts.body.render(prospect.name[: 10],True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(x,y+3))
x+=150

#ポジション
pos_text=prospect.position.value
if prospect.pitch_type:
pos_text+=f"({prospect.pitch_type.value[: 2]})"
pos_surf=fonts.small.render(pos_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(pos_surf,(x,y+5))
x+=100

#年齢
age_surf=fonts.body.render(f"{prospect.age}歳",True,Col or s.TEXT_PRIMARY)
self.screen.blit(age_surf,(x,y+3))
x+=60

#ポテンシャル
pot_col or=Col or s.GOLD if prospect.potential>=8else(
Col or s.SUCCESS if prospect.potential>=6else Col or s.TEXT_PRIMARY
)
pot_surf=fonts.body.render(f"{'★'*m in(prospect.potential,5)}",True,pot_col or)
self.screen.blit(pot_surf,(x,y+3))
x+=100

#総合力
overall=prospect.stats.overall_batt in g() if prospect.position.value!="投手"else prospect.stats.overall_pitch in g()
overall_surf=fonts.body.render(f"{overall:.0f}",True,Col or s.TEXT_PRIMARY)
self.screen.blit(overall_surf,(x,y+3))
x+=80

#詳細ボタン
detail_btn=Button(x,y,40,28,"詳細","outl in e",font=fonts.t in y)
detail_btn.draw(self.screen)
buttons[f"draft_detail_{i}"]=detail_btn

y+=38

#スクロールバー
if len(prospects)>max_v is ible:
scroll_track_h=card_rect.height-80
scroll_h=max(30,in t(scroll_track_h*max_v is ible/len(prospects)))
scroll_y_pos=card_rect.y+50+in t((scroll_off set/max(1,len(prospects)-max_v is ible))*(scroll_track_h-scroll_h))
pygame.draw.rect(self.screen,Col or s.BG_INPUT,
(card_rect.right-15,card_rect.y+50,8,scroll_track_h),b or der_radius=4)
pygame.draw.rect(self.screen,Col or s.PRIMARY,
(card_rect.right-15,scroll_y_pos,8,scroll_h),b or der_radius=4)

#右側: ドラフトログ（メッセージがある場合）
if draft_messages:
log_card=Card(width-310,header_h+20,280,height-header_h-130,"PICKLOG")
log_rect=log_card.draw(self.screen)

log_y=log_rect.y+45
#最新10件を表示
recent_msgs=draft_messages[-10:]if len(draft_messages)>10else draft_messages
f or msg in recent_msgs:
msg_surf=fonts.small.render(msg[: 35],True,Col or s.TEXT_SECONDARY)
self.screen.blit(msg_surf,(log_rect.x+10,log_y))
log_y+=22

#ボタン
btn_y=height-90

buttons["draft_player"]=Button(
center_x+50,btn_y,200,55,
"この選手を指名","success",font=fonts.body
)
buttons["draft_player"].enabled=selected_idx>=0
buttons["draft_player"].draw(self.screen)

buttons["BACK"]=Button(
50,btn_y,150,50,
"ドラフト終了","ghost",font=fonts.body
)
buttons["BACK"].draw(self.screen)

To as tManager.update_ and _draw(self.screen)

return buttons

#========================================
#育成ドラフト画面
#========================================
def draw_ikusei_draft_screen(self,prospects: L is t,selected_idx: in t=-1,
draft_round: in t=1,draft_messages: L is t[str]=None,
scroll_off set: in t=0)->Dict[str,Button]:
"""育成ドラフト画面を描画（スクロール対応）"""
draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()
center_x=width//2

#ヘッダー
round_text=f"第{draft_round}巡目"
header_h=draw_header(self.screen,f"DEVELOPMENTDRAFT-{round_text}","将来性のある選手を育成枠で獲得")

buttons={}

#説明カード
in fo_card=Card(30,header_h+10,350,50)
in fo_rect=in fo_card.draw(self.screen)
in fo_text=fonts.small.render("育成選手は背番号3桁で支配下登録枠外です",True,Col or s.INFO)
self.screen.blit(in fo_text,(in fo_rect.x+15,in fo_rect.y+15))

#選手リストカード
card_width=width-350if draft_messages else width-60
card=Card(30,header_h+70,card_width-30,height-header_h-180)
card_rect=card.draw(self.screen)

#ヘッダー
headers=[("名前",150),("ポジション",100),("年齢",60),("伸びしろ",100),("総合力",80),("",50)]
x=card_rect.x+20
y=card_rect.y+20

f or header_text,w in headers:
h_surf=fonts.small.render(header_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(h_surf,(x,y))
x+=w

y+=25
pygame.draw.l in e(self.screen,Col or s.BORDER,
(card_rect.x+15,y),(card_rect.right-15,y),1)
y+=8

#選手一覧（育成選手は少し能力が低め、スクロール対応・画面サイズ適応）
row_height=38
max_v is ible=(card_rect.height-80)//row_height
v is ible_count=m in(max_v is ible,len(prospects)-scroll_off set)

f or i in range(scroll_off set,m in(scroll_off set+v is ible_count,len(prospects))):
prospect=prospects[i]
d is play_i=i-scroll_off set

row_rect=pygame.Rect(card_rect.x+10,y-3,card_rect.width-20,34)

#選択中
if i==selected_idx:
pygame.draw.rect(self.screen,(*Col or s.SUCCESS[: 3],50),row_rect,b or der_radius=5)
pygame.draw.rect(self.screen,Col or s.SUCCESS,row_rect,2,b or der_radius=5)
el if d is play_i%2==0:
pygame.draw.rect(self.screen,Col or s.BG_INPUT,row_rect,b or der_radius=4)

x=card_rect.x+20

#名前（育成マーク）
name_text=f"*{prospect.name[: 9]}"
name_surf=fonts.body.render(name_text,True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(x,y+3))
x+=150

#ポジション
pos_text=prospect.position.value
if h as attr(prospect,'pitch_type') and prospect.pitch_type:
pos_text+=f"({prospect.pitch_type.value[: 2]})"
pos_surf=fonts.small.render(pos_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(pos_surf,(x,y+5))
x+=100

#年齢
age_surf=fonts.body.render(f"{prospect.age}歳",True,Col or s.TEXT_PRIMARY)
self.screen.blit(age_surf,(x,y+3))
x+=60

#伸びしろ（潜在能力）
growth=getattr(prospect,'growth_potential',prospect.potential)
growth_col or=Col or s.SUCCESS if growth>=7else(
Col or s.PRIMARY if growth>=5else Col or s.TEXT_SECONDARY
)
growth_bar="▰"*growth+"▱"*(10-growth)
growth_surf=fonts.small.render(growth_bar,True,growth_col or)
self.screen.blit(growth_surf,(x,y+5))
x+=100

#総合力（育成なので低め）
if h as attr(prospect,'potential_stats'):
overall=prospect.potential_stats.overall_batt in g() if prospect.position.value!="投手"else prospect.potential_stats.overall_pitch in g()
else:
overall=30#デフォルト値
overall_surf=fonts.body.render(f"{overall:.0f}",True,Col or s.TEXT_SECONDARY)
self.screen.blit(overall_surf,(x,y+3))
x+=80

#詳細ボタン
detail_btn=Button(x,y,40,28,"詳細","outl in e",font=fonts.t in y)
detail_btn.draw(self.screen)
buttons[f"ikusei_detail_{i}"]=detail_btn

y+=38

#スクロールバー
if len(prospects)>max_v is ible:
scroll_track_h=card_rect.height-80
scroll_h=max(30,in t(scroll_track_h*max_v is ible/len(prospects)))
scroll_y_pos=card_rect.y+50+in t((scroll_off set/max(1,len(prospects)-max_v is ible))*(scroll_track_h-scroll_h))
pygame.draw.rect(self.screen,Col or s.BG_INPUT,
(card_rect.right-15,card_rect.y+50,8,scroll_track_h),b or der_radius=4)
pygame.draw.rect(self.screen,Col or s.SUCCESS,
(card_rect.right-15,scroll_y_pos,8,scroll_h),b or der_radius=4)

#右側: ドラフトログ
if draft_messages:
log_card=Card(width-310,header_h+70,280,height-header_h-180,"PICKLOG")
log_rect=log_card.draw(self.screen)

log_y=log_rect.y+45
recent_msgs=draft_messages[-10:]if len(draft_messages)>10else draft_messages
f or msg in recent_msgs:
msg_surf=fonts.small.render(msg[: 35],True,Col or s.TEXT_SECONDARY)
self.screen.blit(msg_surf,(log_rect.x+10,log_y))
log_y+=22

#ボタン
btn_y=height-90

buttons["draft_ikusei_player"]=Button(
center_x+50,btn_y,200,55,
"この選手を指名","success",font=fonts.body
)
buttons["draft_ikusei_player"].enabled=selected_idx>=0
buttons["draft_ikusei_player"].draw(self.screen)

buttons["skip_ikusei"]=Button(
center_x-180,btn_y,180,50,
"この巡はパス","outl in e",font=fonts.body
)
buttons["skip_ikusei"].draw(self.screen)

buttons["f in is h_ikusei_draft"]=Button(
50,btn_y,150,50,
"育成終了→FA","ghost",font=fonts.body
)
buttons["f in is h_ikusei_draft"].draw(self.screen)

To as tManager.update_ and _draw(self.screen)

return buttons

#========================================
#選手詳細画面（パワプロ風）
#========================================
def draw_player_detail_screen(self,player,scroll_y: in t=0)->Dict[str,Button]:
"""選手詳細画面を描画（パワプロ風の能力表示）"""
draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()
center_x=width//2

#ヘッダー
header_h=draw_header(self.screen,f"{player.name}",f"{player.position.value}/{player.age}歳")

buttons={}

#スクロール対応の描画領域を設定
content_y=header_h+20-scroll_y

#==========基本情報カード==========
in fo_card=Card(30,content_y,400,200,"基本情報")
in fo_rect=in fo_card.draw(self.screen)

in fo_items=[
("背番号",f"#{player.uni f or m_number}"),
("ポジション",player.position.value),
("年齢",f"{player.age}歳"),
("投打",f"{getattr(player.stats,'throw in g_h and','右')}投{getattr(player.stats,'batt in g_h and','右')}打"),
]

y=in fo_rect.y+45
f or label,value in info_items:
label_surf=fonts.small.render(f"{label}:",True,Col or s.TEXT_SECONDARY)
value_surf=fonts.body.render(str(value),True,Col or s.TEXT_PRIMARY)
self.screen.blit(label_surf,(in fo_rect.x+20,y))
self.screen.blit(value_surf,(in fo_rect.x+120,y))
y+=32

#==========打撃能力カード==========
if player.position.value!="投手":
batt in g_card=Card(450,content_y,400,250,"BATTING")
batt in g_rect=batt in g_card.draw(self.screen)

batt in g_stats=[
("ミート",player.stats.contact,Col or s.INFO),
("パワー",player.stats.power,Col or s.DANGER),
("走力",player.stats.speed,Col or s.SUCCESS),
("肩力",player.stats.throw in g if h as attr(player.stats,'throw in g') else player.stats.arm,Col or s.WARNING),
("守備",player.stats.field in g,Col or s.PRIMARY),
("捕球",getattr(player.stats,'catch in g',player.stats.field in g),Col or s.GOLD),
]

y=batt in g_rect.y+45
f or stat_name,value,col or in batt in g_stats:
#ラベル
label_surf=fonts.small.render(stat_name,True,Col or s.TEXT_SECONDARY)
self.screen.blit(label_surf,(batt in g_rect.x+20,y+3))

#バー
bar_x=batt in g_rect.x+80
bar_width=200
bar_height=18

#背景バー
pygame.draw.rect(self.screen,Col or s.BG_INPUT,
(bar_x,y,bar_width,bar_height),b or der_radius=3)

#値バー
filled_width=in t(bar_width*value/100)
if filled_width>0:
pygame.draw.rect(self.screen,col or,
(bar_x,y,filled_width,bar_height),b or der_radius=3)

#数値
value_surf=fonts.body.render(f"{value}",True,Col or s.TEXT_PRIMARY)
self.screen.blit(value_surf,(bar_x+bar_width+10,y))

#ランク表示
rank=self._get_ability_rank(value)
rank_col or=self._get_rank_col or(rank)
rank_surf=fonts.body.render(rank,True,rank_col or)
self.screen.blit(rank_surf,(batt in g_rect.right-40,y))

y+=30

#==========投球能力カード（投手の場合）==========
if player.position.value=="投手":
pitch in g_card=Card(450,content_y,400,250,"PITCHING")
pitch in g_rect=pitch in g_card.draw(self.screen)

pitch in g_stats=[
("球速",player.stats.velocity,Col or s.DANGER),
("コントロール",player.stats.control,Col or s.INFO),
("スタミナ",player.stats.stam in a,Col or s.SUCCESS),
("変化球",player.stats.break in g_ball,Col or s.PRIMARY),
("キレ",getattr(player.stats,'pitch_movement',50),Col or s.WARNING),
]

y=pitch in g_rect.y+45
f or stat_name,value,col or in pitch in g_stats:
label_surf=fonts.small.render(stat_name,True,Col or s.TEXT_SECONDARY)
self.screen.blit(label_surf,(pitch in g_rect.x+20,y+3))

bar_x=pitch in g_rect.x+100
bar_width=180
bar_height=18

pygame.draw.rect(self.screen,Col or s.BG_INPUT,
(bar_x,y,bar_width,bar_height),b or der_radius=3)

filled_width=in t(bar_width*value/100)
if filled_width>0:
pygame.draw.rect(self.screen,col or,
(bar_x,y,filled_width,bar_height),b or der_radius=3)

value_surf=fonts.body.render(f"{value}",True,Col or s.TEXT_PRIMARY)
self.screen.blit(value_surf,(bar_x+bar_width+10,y))

rank=self._get_ability_rank(value)
rank_col or=self._get_rank_col or(rank)
rank_surf=fonts.body.render(rank,True,rank_col or)
self.screen.blit(rank_surf,(pitch in g_rect.right-40,y))

y+=35

#==========特殊能力カード==========
abilities_y=content_y+260
special_card=Card(30,abilities_y,width-60,150,"✨特殊能力")
special_rect=special_card.draw(self.screen)

special_abilities=[]

#パワプロ風特殊能力
traject or y=getattr(player.stats,'traject or y',2)
if traject or y==4:
special_abilities.append(("弾道4",Col or s.GOLD))
el if traject or y==1:
special_abilities.append(("弾道1",Col or s.TEXT_SECONDARY))

clutch=getattr(player.stats,'clutch',10)
if clutch>=15:
special_abilities.append(("チャンス◎",Col or s.SUCCESS))
el if clutch>=12:
special_abilities.append(("チャンス○",Col or s.INFO))
el if clutch<=5:
special_abilities.append(("チャンス×",Col or s.DANGER))

eye=getattr(player.stats,'eye',10)
if eye>=15:
special_abilities.append(("選球眼◎",Col or s.SUCCESS))
el if eye>=12:
special_abilities.append(("選球眼○",Col or s.INFO))

vs_left=getattr(player.stats,'vs_left_pitch in g',10)
if vs_left>=15:
special_abilities.append(("対左投手◎",Col or s.SUCCESS))
el if vs_left<=5:
special_abilities.append(("対左投手×",Col or s.DANGER))

#投手特殊能力
if player.position.value=="投手":
vs_p in ch=getattr(player.stats,'vs_p in ch',10)
if vs_p in ch>=15:
special_abilities.append(("対ピンチ◎",Col or s.SUCCESS))
el if vs_p in ch<=5:
special_abilities.append(("対ピンチ×",Col or s.DANGER))

fatigue=getattr(player.stats,'fatigue_res is tance',10)
if fatigue>=15:
special_abilities.append(("回復◎",Col or s.SUCCESS))

#特殊能力表示
x=special_rect.x+20
y=special_rect.y+45
f or ability_name,col or in special_abilities:
#タグ風の表示
text_surf=fonts.small.render(ability_name,True,Col or s.WHITE)
text_w=text_surf.get_width()
tag_rect=pygame.Rect(x,y,text_w+16,28)
pygame.draw.rect(self.screen,col or,tag_rect,b or der_radius=14)
self.screen.blit(text_surf,(x+8,y+6))
x+=text_w+24

#折り返し
if x>special_rect.right-100:
x=special_rect.x+20
y+=35

#特殊能力がない場合
if not special_abilities:
no_ability=fonts.small.render("特殊能力なし",True,Col or s.TEXT_SECONDARY)
self.screen.blit(no_ability,(special_rect.x+20,special_rect.y+55))

#BACKボタン
buttons["BACK"]=Button(
50,height-80,150,50,
"←BACK","ghost",font=fonts.body
)
buttons["BACK"].draw(self.screen)

To as tManager.update_ and _draw(self.screen)

return buttons

def _get_ability_rank(self,value: in t)->str:
"""能力値をランクに変換"""
if value>=90:
return"S"
el if value>=80:
return"A"
el if value>=70:
return"B"
el if value>=60:
return"C"
el if value>=50:
return"D"
el if value>=40:
return"E"
el if value>=30:
return"F"
else:
return"G"

def _get_rank_col or(self,rank: str):
"""ランクに応じた色を返す"""
col or s={
"S": Col or s.GOLD,
"A": Col or s.DANGER,
"B": Col or s.WARNING,
"C": Col or s.SUCCESS,
"D": Col or s.INFO,
"E": Col or s.TEXT_SECONDARY,
"F": Col or s.TEXT_SECONDARY,
"G": Col or s.TEXT_SECONDARY,
}
return col or s.get(rank,Col or s.TEXT_PRIMARY)

#========================================
#外国人FA画面
#========================================
def draw_free_agent_screen(self,player_team,free_agents: L is t,selected_idx: in t=-1)->Dict[str,Button]:
"""外国人FA画面を描画"""
draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()
center_x=width//2

team_col or=self.get_team_col or(player_team.name) if player_team else Col or s.PRIMARY
header_h=draw_header(self.screen,"外国人選手市場",
f"予算:{player_team.budget if player_teamelse0}億円",team_col or)

buttons={}

#選手リストカード
card=Card(30,header_h+20,width-60,height-header_h-130)
card_rect=card.draw(self.screen)

#ヘッダー
headers=[("名前",180),("ポジション",120),("年俸",100),("総合力",100)]
x=card_rect.x+25
y=card_rect.y+25

f or header_text,w in headers:
h_surf=fonts.small.render(header_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(h_surf,(x,y))
x+=w

y+=30
pygame.draw.l in e(self.screen,Col or s.BORDER,
(card_rect.x+20,y),(card_rect.right-20,y),1)
y+=10

#選手一覧（行をクリック可能にするためrect情報を保存）
self.fa_row_rects=[]
f or i,player in enumerate(free_agents[: 10]):
row_rect=pygame.Rect(card_rect.x+15,y-5,card_rect.width-30,38)
self.fa_row_rects.append(row_rect)

#選択中の行はハイライト
if i==selected_idx:
pygame.draw.rect(self.screen,(*Col or s.PRIMARY[: 3],60),row_rect,b or der_radius=4)
pygame.draw.rect(self.screen,Col or s.PRIMARY,row_rect,2,b or der_radius=4)
el if i%2==0:
pygame.draw.rect(self.screen,Col or s.BG_INPUT,row_rect,b or der_radius=4)

x=card_rect.x+25

#名前
name_surf=fonts.body.render(player.name[: 12],True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(x,y+5))
x+=180

#ポジション
pos_text=player.position.value
if player.pitch_type:
pos_text+=f"({player.pitch_type.value[: 2]})"
pos_surf=fonts.body.render(pos_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(pos_surf,(x,y+5))
x+=120

#年俸
salary_surf=fonts.body.render(f"{player.salary}億",True,Col or s.WARNING)
self.screen.blit(salary_surf,(x,y+5))
x+=100

#総合力
overall=player.stats.overall_batt in g() if player.position.value!="投手"else player.stats.overall_pitch in g()
overall_surf=fonts.body.render(f"{overall:.0f}",True,Col or s.TEXT_PRIMARY)
self.screen.blit(overall_surf,(x,y+5))

y+=42

#ボタン行
btn_y=height-90

#獲得ボタン
sign_style="primary"if selected_idx>=0else"ghost"
buttons["sign_fa"]=Button(
center_x-200,btn_y,180,50,
"SIGN",sign_style,font=fonts.body
)
buttons["sign_fa"].draw(self.screen)

#次へボタン（新シーズン開始）
buttons["next_se as on"]=Button(
center_x+20,btn_y,180,50,
"NEWSEASON","success",font=fonts.body
)
buttons["next_se as on"].draw(self.screen)

To as tManager.update_ and _draw(self.screen)

return buttons

#========================================
#設定画面
#========================================
def draw_ set t in gs_screen(self,set t in gs_obj,set t in gs_tab: str="d is play",scroll_off set: in t=0)->Dict[str,Button]:
"""設定画面を描画

Args:
set t in gs_obj: 設定オブジェクト
set t in gs_tab: 表示するタブ("d is play","game_rules")
scroll_off set: スクロールオフセット
"""
draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()
center_x=width//2

header_h=draw_header(self.screen,"SETTINGS")

buttons={}

#タブボタン
tab_y=header_h+20
tab_width=200
tabs=[
("d is play","表示設定"),
("game_rules","ゲームルール"),
]

f or i,(tab_key,tab_label) in enumerate(tabs):
style="primary"if set t in gs_tab==tab_key else"ghost"
btn=Button(center_x-210+i*220,tab_y,tab_width,45,tab_label,style,font=fonts.body)
btn.draw(self.screen)
buttons[f"set t in gs_tab_{tab_key}"]=btn

card_top=tab_y+65
content_height=height-card_top-100#利用可能な高さ

if set t in gs_tab=="d is play":
#表示設定カード
card=Card(center_x-350,card_top,700,400,"表示設定")
card_rect=card.draw(self.screen)

y=card_rect.y+55

#解像度設定
res_label=fonts.h3.render("解像度",True,Col or s.TEXT_PRIMARY)
self.screen.blit(res_label,(card_rect.x+30,y))
y+=45

resolutions=[(1280,720),(1600,900),(1920,1080)]
f or i,(w,h) in enumerate(resolutions):
btn_x=card_rect.x+30+i*200
is _current=(set t in gs_obj.screen_width,set t in gs_obj.screen_height)==(w,h)
style="primary"if is _current else"ghost"

btn=Button(btn_x,y,180,45,f"{w}x{h}",style,font=fonts.body)
btn.draw(self.screen)
buttons[f"resolution_{w}x{h}"]=btn

y+=75

#フルスクリーン
fullscreen_label=fonts.h3.render("フルスクリーン",True,Col or s.TEXT_PRIMARY)
self.screen.blit(fullscreen_label,(card_rect.x+30,y))

fullscreen_status="ON"if set t in gs_obj.fullscreen else"OFF"
fullscreen_style="success"if set t in gs_obj.fullscreen else"ghost"
buttons["toggle_fullscreen"]=Button(
card_rect.x+350,y-5,120,45,
fullscreen_status,fullscreen_style,font=fonts.body
)
buttons["toggle_fullscreen"].draw(self.screen)

y+=70

#サウンド
sound_label=fonts.h3.render("サウンド",True,Col or s.TEXT_PRIMARY)
self.screen.blit(sound_label,(card_rect.x+30,y))

sound_status="ON"if set t in gs_obj.sound_enabled else"OFF"
sound_style="success"if set t in gs_obj.sound_enabled else"ghost"
buttons["toggle_sound"]=Button(
card_rect.x+350,y-5,120,45,
sound_status,sound_style,font=fonts.body
)
buttons["toggle_sound"].draw(self.screen)

else:#game_rulesタブ
#ゲームルール設定（スクロール対応）
rules=set t in gs_obj.game_rules

#スクロール可能エリアの設定
scroll_area_top=card_top
scroll_area_height=height-card_top-100
max_scroll=max(0,650-scroll_area_height)#コンテンツ高さ-表示高さ
scroll_off set=m in(scroll_off set,max_scroll)

#クリッピング領域を設定
clip_rect=pygame.Rect(30,scroll_area_top,width-60,scroll_area_height)
self.screen.set _clip(clip_rect)

#単一カードに全設定を配置
card=Card(50,card_top-scroll_off set,width-100,700,"ゲームルール設定")
card_rect=card.draw(self.screen)

y=card_rect.y+55
col1_x=card_rect.x+30
col2_x=card_rect.x+card_rect.width//2+20

#===左列: DH・リーグ設定===
section_label=fonts.h3.render("DH制ルール",True,Col or s.PRIMARY)
self.screen.blit(section_label,(col1_x,y))
y+=40

dh_ set t in gs=[
("セリーグDH制","central_dh",rules.central_dh),
("パリーグDH制","pac if ic_dh",rules.pac if ic_dh),
("交流戦DH（ホームルール）","in t erleague_dh",rules.in t erleague_dh),
]

f or label,key,value in dh_ set t in gs:
label_surf=fonts.small.render(label,True,Col or s.TEXT_PRIMARY)
self.screen.blit(label_surf,(col1_x,y+6))

status="ON"if value else"OFF"
style="success"if value else"ghost"
btn=Button(col1_x+250,y,80,32,status,style,font=fonts.t in y)
btn.draw(self.screen)
buttons[f"toggle_{key}"]=btn
y+=40

y+=15
pygame.draw.l in e(self.screen,Col or s.BORDER,(col1_x,y),(col1_x+330,y),1)
y+=15

#シーズン構成
section_label=fonts.h3.render("シーズン構成",True,Col or s.PRIMARY)
self.screen.blit(section_label,(col1_x,y))
y+=40

se as on_ set t in gs=[
("春季キャンプ","enable_spr in g_camp",rules.enable_spr in g_camp),
("交流戦","enable_ in t erleague",rules.enable_ in t erleague),
("オールスター","enable_allstar",rules.enable_allstar),
("クライマックスシリーズ","enable_climax_series",rules.enable_climax_series),
("タイブレーク制度","enable_tie break er",rules.enable_tie break er),
]

f or label,key,value in se as on_ set t in gs:
label_surf=fonts.small.render(label,True,Col or s.TEXT_PRIMARY)
self.screen.blit(label_surf,(col1_x,y+6))

status="ON"if value else"OFF"
style="success"if value else"ghost"
btn=Button(col1_x+250,y,80,32,status,style,font=fonts.t in y)
btn.draw(self.screen)
buttons[f"toggle_{key}"]=btn
y+=40

#===右列: 数値設定===
y2=card_rect.y+55

section_label=fonts.h3.render("外国人枠",True,Col or s.PRIMARY)
self.screen.blit(section_label,(col2_x,y2))
y2+=40

#外国人枠無制限
label_surf=fonts.small.render("外国人枠無制限",True,Col or s.TEXT_PRIMARY)
self.screen.blit(label_surf,(col2_x,y2+6))
status="ON"if rules.unlimited_ f or eign else"OFF"
style="success"if rules.unlimited_ f or eign else"ghost"
btn=Button(col2_x+250,y2,80,32,status,style,font=fonts.t in y)
btn.draw(self.screen)
buttons["toggle_unlimited_ f or eign"]=btn
y2+=40

#外国人支配下枠
label_surf=fonts.small.render("外国人支配下枠",True,Col or s.TEXT_PRIMARY)
self.screen.blit(label_surf,(col2_x,y2+6))
y2+=28
btn_x=col2_x
f or opt in[0,3,4,5]:
d is play="無制限"if opt==0else str(opt)
is _selected=rules.f or eign_player_limit==opt
style="primary"if is _selected else"outl in e"
btn=Button(btn_x,y2,70,28,d is play,style,font=fonts.t in y)
btn.draw(self.screen)
buttons[f"set _ f or eign_player_limit_{opt}"]=btn
btn_x+=78
y2+=45

pygame.draw.l in e(self.screen,Col or s.BORDER,(col2_x,y2),(col2_x+330,y2),1)
y2+=15

section_label=fonts.h3.render("試合・登録設定",True,Col or s.PRIMARY)
self.screen.blit(section_label,(col2_x,y2))
y2+=40

#数値設定（コンパクト版）
number_ set t in gs=[
("シーズン試合数","regular_se as on_games",rules.regular_se as on_games,[120,130,143]),
("一軍登録枠","roster_limit",rules.roster_limit,[25,26,28]),
("延長上限","extra_ in n in gs_limit",rules.extra_ in n in gs_limit,[9,12,0]),
("キャンプ日数","spr in g_camp_days",rules.spr in g_camp_days,[14,21,28]),
]

f or label,key,current_value,options in number_ set t in gs:
label_surf=fonts.small.render(label,True,Col or s.TEXT_PRIMARY)
self.screen.blit(label_surf,(col2_x,y2+6))
y2+=28

btn_x=col2_x
f or opt in options:
if opt==0and"in n in gs"in key:
d is play="無制限"
else:
d is play=str(opt)

is _selected=current_value==opt
style="primary"if is _selected else"outl in e"
btn=Button(btn_x,y2,70,28,d is play,style,font=fonts.t in y)
btn.draw(self.screen)
buttons[f"set _{key}_{opt}"]=btn
btn_x+=78
y2+=42

#クリッピング解除
self.screen.set _clip(None)

#スクロールバー
if max_scroll>0:
scrollbar_height=scroll_area_height*scroll_area_height/650
scrollbar_y=scroll_area_top+(scroll_off set/max_scroll)*(scroll_area_height-scrollbar_height)
pygame.draw.rect(self.screen,Col or s.BG_CARD_HOVER,
(width-25,scroll_area_top,8,scroll_area_height),b or der_radius=4)
pygame.draw.rect(self.screen,Col or s.PRIMARY,
(width-25,scrollbar_y,8,scrollbar_height),b or der_radius=4)

#BACKボタン
buttons["BACK"]=Button(
50,height-70,150,50,
"←BACK","ghost",font=fonts.body
)
buttons["BACK"].draw(self.screen)

To as tManager.update_ and _draw(self.screen)

return buttons

#========================================
#チーム成績画面
#========================================
def draw_team_stats_screen(self,player_team,current_year: in t)->Dict[str,Button]:
"""チーム成績詳細画面を描画"""
draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()

team_col or=self.get_team_col or(player_team.name) if player_team else Col or s.PRIMARY

header_h=draw_header(self.screen,f"{player_team.name}成績",
f"{current_year}年シーズン",team_col or)

buttons={}

if player_team:
#左パネル: チーム基本情報
b as ic_card=Card(30,header_h+20,350,450,"シーズン成績")
b as ic_rect=b as ic_card.draw(self.screen)

y=b as ic_rect.y+55

#本拠地球場
stadium=NPB_STADIUMS.get(player_team.name,{})
stadium_name=stadium.get("name","不明")
stadium_capacity=stadium.get("capacity",0)

#チーム基本情報
in fo_items=[
("本拠地",stadium_name),
("収容人数",f"{stadium_capacity:,}人"if stadium_capacity>0else"不明"),
("",""),#空行
("勝利",f"{player_team.w in s}"),
("敗北",f"{player_team.losses}"),
("引分",f"{player_team.draws}"),
("",""),#空行
("勝率",f".{in t(player_team.w in _rate*1000): 03d}"if player_team.games_played>0else".000"),
("消化試合",f"{player_team.games_played}/143"),
("残り試合",f"{143-player_team.games_played}"),
]

f or label,value in info_items:
if label=="":
y+=15
cont in ue
label_surf=fonts.body.render(label,True,Col or s.TEXT_SECONDARY)
value_surf=fonts.body.render(value,True,Col or s.TEXT_PRIMARY)
self.screen.blit(label_surf,(b as ic_rect.x+25,y))
self.screen.blit(value_surf,(b as ic_rect.x+160,y))
y+=32

#シーズン進行バー
y+=10
progress=player_team.games_played/143if player_team.games_played>0else0
bar=ProgressBar(b as ic_rect.x+25,y,300,18,progress,team_col or)
bar.draw(self.screen)

#中央パネル: 打撃成績上位
batt in g_card=Card(400,header_h+20,360,320,"🏏打撃成績上位")
bat_rect=batt in g_card.draw(self.screen)

#打者をフィルタ
batters=[p f or p in player_team.players if p.position.value!="投手"]
#打率でソート（仮の計算）
s or ted_batters=s or ted(batters,
key=lambda p: p.stats.contact+p.stats.power+p.stats.speed,
reverse=True)[: 6]

y=bat_rect.y+55
headers=["選手","打率","本","打点"]
header_x=[25,150,230,280]

f or i,h in enumerate(headers):
h_surf=fonts.t in y.render(h,True,Col or s.TEXT_MUTED)
self.screen.blit(h_surf,(bat_rect.x+header_x[i],y))

y+=28

f or player in s or ted_batters:
#選手名
name_surf=fonts.small.render(player.name[: 10],True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(bat_rect.x+header_x[0],y))

#仮のシーズン成績（実際のゲームでは累積する）
avg=0.220+(player.stats.contact/1000)
hr=in t(player.stats.power/5)
rbi=in t((player.stats.power+player.stats.contact)/4)

avg_surf=fonts.small.render(f".{in t(avg*1000): 03d}",True,Col or s.TEXT_SECONDARY)
self.screen.blit(avg_surf,(bat_rect.x+header_x[1],y))

hr_surf=fonts.small.render(str(hr),True,Col or s.TEXT_SECONDARY)
self.screen.blit(hr_surf,(bat_rect.x+header_x[2],y))

rbi_surf=fonts.small.render(str(rbi),True,Col or s.TEXT_SECONDARY)
self.screen.blit(rbi_surf,(bat_rect.x+header_x[3],y))

y+=32

#投手成績
pitch in g_card=Card(400,header_h+360,360,180,"PITCHINGTOP")
pitch_rect=pitch in g_card.draw(self.screen)

pitchers=[p f or p in player_team.players if p.position.value=="投手"]
s or ted_pitchers=s or ted(pitchers,
key=lambda p: p.stats.overall_pitch in g(),
reverse=True)[: 3]

y=pitch_rect.y+55
p_headers=["選手","防御率","勝","負","S"]
p_header_x=[25,130,205,245,285]

f or i,h in enumerate(p_headers):
h_surf=fonts.t in y.render(h,True,Col or s.TEXT_MUTED)
self.screen.blit(h_surf,(pitch_rect.x+p_header_x[i],y))

y+=28

f or player in s or ted_pitchers:
name_surf=fonts.small.render(player.name[: 8],True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(pitch_rect.x+p_header_x[0],y))

#仮のシーズン成績
era=5.00-(player.stats.control/50)-(player.stats.stam in a/100)
era=max(1.50,m in(6.00,era))
w in s=in t(player.stats.control/10)
losses=max(0,10-w in s)
saves=0if player.pitch_type and player.pitch_type.value!="クローザー"else in t(player.stats.control/5)

era_surf=fonts.small.render(f"{era:.2f}",True,Col or s.TEXT_SECONDARY)
self.screen.blit(era_surf,(pitch_rect.x+p_header_x[1],y))

w_surf=fonts.small.render(str(w in s),True,Col or s.TEXT_SECONDARY)
self.screen.blit(w_surf,(pitch_rect.x+p_header_x[2],y))

l_surf=fonts.small.render(str(losses),True,Col or s.TEXT_SECONDARY)
self.screen.blit(l_surf,(pitch_rect.x+p_header_x[3],y))

s_surf=fonts.small.render(str(saves),True,Col or s.TEXT_SECONDARY)
self.screen.blit(s_surf,(pitch_rect.x+p_header_x[4],y))

y+=28

#右パネル: タイトル候補
title_card=Card(780,header_h+20,330,520,"TITLERACE")
title_rect=title_card.draw(self.screen)

y=title_rect.y+55

#打撃タイトル
bat_title_label=fonts.small.render("【打撃部門】",True,Col or s.GOLD)
self.screen.blit(bat_title_label,(title_rect.x+20,y))
y+=30

f or title_key,title_name in l is t(NPB_BATTING_TITLES.items())[: 4]:
title_surf=fonts.t in y.render(f"・{title_name}",True,Col or s.TEXT_SECONDARY)
self.screen.blit(title_surf,(title_rect.x+30,y))

#最有力候補（チーム内）
if s or ted_batters:
c and idate=s or ted_batters[0]
c and _surf=fonts.t in y.render(f"→{c and idate.name[: 6]}",True,Col or s.TEXT_MUTED)
self.screen.blit(c and _surf,(title_rect.x+170,y))
y+=25

y+=20

#投手タイトル
pitch_title_label=fonts.small.render("【投手部門】",True,Col or s.SECONDARY)
self.screen.blit(pitch_title_label,(title_rect.x+20,y))
y+=30

f or title_key,title_name in l is t(NPB_PITCHING_TITLES.items())[: 4]:
title_surf=fonts.t in y.render(f"・{title_name}",True,Col or s.TEXT_SECONDARY)
self.screen.blit(title_surf,(title_rect.x+30,y))

if s or ted_pitchers:
c and idate=s or ted_pitchers[0]
c and _surf=fonts.t in y.render(f"→{c and idate.name[: 6]}",True,Col or s.TEXT_MUTED)
self.screen.blit(c and _surf,(title_rect.x+170,y))
y+=25

#BACKボタン
buttons["BACK"]=Button(
50,height-70,150,50,
"←BACK","ghost",font=fonts.body
)
buttons["BACK"].draw(self.screen)

To as tManager.update_ and _draw(self.screen)

return buttons

#========================================
#チーム編集画面
#========================================
def draw_team_edit_screen(self,all_teams: L is t,edit in g_team_idx: in t=-1,
in put_text: str="",custom_names: Dict=None)->Dict[str,Button]:
"""チーム名編集画面を描画"""
draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()

header_h=draw_header(self.screen,"チーム名編集",
"各チームの名前をカスタマイズできます")

buttons={}
custom_names=custom_names or{}

#メインカード
card_width=m in(900,width-60)
card_x=(width-card_width)//2
ma in _card=Card(card_x,header_h+20,card_width,height-header_h-100,"チーム一覧")
card_rect=ma in _card.draw(self.screen)

#ヘッダー行
y=card_rect.y+55
headers=[("リーグ",80),("デフォルト名",220),("カスタム名",250),("操作",120)]
x=card_rect.x+25

f or header_text,col_width in headers:
header_surf=fonts.small.render(header_text,True,Col or s.TEXT_MUTED)
self.screen.blit(header_surf,(x,y))
x+=col_width

y+=35
pygame.draw.l in e(self.screen,Col or s.BORDER,
(card_rect.x+20,y-5),
(card_rect.x+card_width-40,y-5),1)

#チーム一覧
f or idx,team in enumerate(all_teams):
row_y=y+idx*45
if row_y>card_rect.y+card_rect.height-50:
break

#編集中のチームをハイライト
if idx==edit in g_team_idx:
highlight_rect=pygame.Rect(card_rect.x+15,row_y-5,card_width-50,40)
pygame.draw.rect(self.screen,(*Col or s.PRIMARY[: 3],30),highlight_rect,b or der_radius=4)

x=card_rect.x+25

#リーグ
league_text="セ"if idx<6else"パ"
league_col or=Col or s.PRIMARY if idx<6else Col or s.DANGER
league_surf=fonts.body.render(league_text,True,league_col or)
self.screen.blit(league_surf,(x+20,row_y))
x+=80

#デフォルト名
team_col or=self.get_team_col or(team.name)
def ault_name_surf=fonts.body.render(team.name[: 12],True,team_col or)
self.screen.blit(def ault_name_surf,(x,row_y))
x+=220

#カスタム名（入力中or設定済み）
if idx==edit in g_team_idx:
#入力ボックス
in put_rect=pygame.Rect(x,row_y-3,200,32)
pygame.draw.rect(self.screen,Col or s.BG_INPUT,in put_rect,b or der_radius=4)
pygame.draw.rect(self.screen,Col or s.PRIMARY,in put_rect,2,b or der_radius=4)

d is play_text=in put_text if in put_text else"入力してください..."
text_col or=Col or s.TEXT_PRIMARY if in put_text else Col or s.TEXT_MUTED
in put_surf=fonts.body.render(d is play_text[: 14],True,text_col or)
self.screen.blit(in put_surf,(x+8,row_y+2))

#カーソル（点滅）
if in t(time.time()*2)%2==0:
curs or _x=x+8+fonts.body.size(in put_text[: 14])[0]
pygame.draw.l in e(self.screen,Col or s.TEXT_PRIMARY,
(curs or _x,row_y),(curs or _x,row_y+24),2)
else:
custom_name=custom_names.get(team.name,"")
if custom_name:
custom_surf=fonts.body.render(custom_name[: 14],True,Col or s.SUCCESS)
self.screen.blit(custom_surf,(x,row_y))
else:
no_custom_surf=fonts.body.render("---",True,Col or s.TEXT_MUTED)
self.screen.blit(no_custom_surf,(x,row_y))

x+=250

#編集ボタン
if idx==edit in g_team_idx:
#確定・キャンセルボタン
confirm_btn=Button(x,row_y-5,50,32,"OK","success",font=fonts.small)
confirm_btn.draw(self.screen)
buttons[f"confirm_edit_{idx}"]=confirm_btn

cancel_btn=Button(x+55,row_y-5,50,32,"✗","danger",font=fonts.small)
cancel_btn.draw(self.screen)
buttons[f"cancel_edit_{idx}"]=cancel_btn
else:
edit_btn=Button(x,row_y-5,70,32,"編集","ghost",font=fonts.small)
edit_btn.draw(self.screen)
buttons[f"edit_team_{idx}"]=edit_btn

#リセットボタン（カスタム名がある場合）
if team.name in custom_names:
re set _btn=Button(x+75,row_y-5,45,32,"×","ghost",font=fonts.small)
re set _btn.draw(self.screen)
buttons[f"re set _team_{idx}"]=re set _btn

#下部ボタン
buttons["BACK_to_select"]=Button(
50,height-70,150,50,
"←BACK","ghost",font=fonts.body
)
buttons["BACK_to_select"].draw(self.screen)

buttons["apply_names"]=Button(
width-200,height-70,150,50,
"適用して選択へ","primary",font=fonts.body
)
buttons["apply_names"].draw(self.screen)

#ヒント
h in t _text="チーム名を変更すると、ゲーム内のすべての表示に反映されます"
h in t _surf=fonts.t in y.render(h in t _text,True,Col or s.TEXT_MUTED)
self.screen.blit(h in t _surf,((width-h in t _surf.get_width())//2,height-25))

To as tManager.update_ and _draw(self.screen)

return buttons

#========================================
#育成画面
#========================================
def draw_tra in ing_screen(self,player_team,selected_player_idx: in t=-1,
tra in ing_po in t s: in t=0)->Dict[str,Button]:
"""育成画面を描画"""
draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()

team_col or=self.get_team_col or(player_team.name) if player_team else Col or s.PRIMARY
header_h=draw_header(self.screen,"💪育成","選手を鍛えて能力アップ！",team_col or)

buttons={}

if not player_team:
return buttons

#左パネル: 選手一覧
roster_card=Card(30,header_h+20,400,height-header_h-100,"選手一覧")
roster_rect=roster_card.draw(self.screen)

#育成ポイント表示
po in t s_text=f"育成ポイント:{tra in ing_po in t s}pt"
po in t s_surf=fonts.h3.render(po in t s_text,True,Col or s.GOLD)
self.screen.blit(po in t s_surf,(roster_rect.x+20,roster_rect.y+50))

#ヘッダー行
y=roster_rect.y+90
headers=[("名前",150),("Pos",60),("年齢",50),("総合",70)]
x=roster_rect.x+20

f or header_text,col_width in headers:
h_surf=fonts.t in y.render(header_text,True,Col or s.TEXT_MUTED)
self.screen.blit(h_surf,(x,y))
x+=col_width

y+=25
pygame.draw.l in e(self.screen,Col or s.BORDER,
(roster_rect.x+15,y),(roster_rect.right-15,y),1)
y+=8

#選手リスト
players=player_team.players[: 20]#最大20人表示
f or idx,player in enumerate(players):
row_rect=pygame.Rect(roster_rect.x+10,y-3,roster_rect.width-20,28)

#選択中の選手をハイライト
if idx==selected_player_idx:
pygame.draw.rect(self.screen,(*team_col or[: 3],50),row_rect,b or der_radius=4)
pygame.draw.rect(self.screen,team_col or,row_rect,2,b or der_radius=4)
el if idx%2==0:
pygame.draw.rect(self.screen,Col or s.BG_INPUT,row_rect,b or der_radius=2)

#クリック可能なボタンとして登録
row_btn=Button(row_rect.x,row_rect.y,row_rect.width,row_rect.height,"","ghost")
row_btn.col or _n or mal=(0,0,0,0)
row_btn.col or _hover=(*team_col or[: 3],30)
buttons[f"select_player_{idx}"]=row_btn

x=roster_rect.x+20

#名前
name_surf=fonts.small.render(player.name[: 8],True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(x,y))
x+=150

#ポジション
pos_surf=fonts.t in y.render(player.position.value[: 3],True,Col or s.TEXT_SECONDARY)
self.screen.blit(pos_surf,(x,y+2))
x+=60

#年齢
age_surf=fonts.small.render(str(player.age),True,Col or s.TEXT_SECONDARY)
self.screen.blit(age_surf,(x,y))
x+=50

#総合力
if player.position.value=="投手":
overall=player.stats.overall_pitch in g()
else:
overall=player.stats.overall_batt in g()
overall_surf=fonts.small.render(f"{overall:.0f}",True,Col or s.PRIMARY)
self.screen.blit(overall_surf,(x,y))

y+=30

if y>roster_rect.bottom-30:
break

#右パネル: 選手詳細&育成メニュー
if selected_player_idx>=0and selected_player_idx<len(players):
player=players[selected_player_idx]

#選手詳細カード
detail_card=Card(450,header_h+20,width-480,280,f"{player.name}")
detail_rect=detail_card.draw(self.screen)

y=detail_rect.y+55

#基本情報
potential=player.growth.potential if player.growthelse5
in fo_items=[
("ポジション",player.position.value),
("年齢",f"{player.age}歳"),
("ポテンシャル",f"{'★'*(potential//2)}{'☆'*(5-potential//2)}"),
]

f or label,value in info_items:
label_surf=fonts.small.render(label,True,Col or s.TEXT_SECONDARY)
value_surf=fonts.small.render(value,True,Col or s.TEXT_PRIMARY)
self.screen.blit(label_surf,(detail_rect.x+20,y))
self.screen.blit(value_surf,(detail_rect.x+130,y))
y+=28

y+=10

#能力値表示
if player.position.value=="投手":
stats_items=[
("球速",player.stats.speed,Col or s.DANGER),
("制球",player.stats.control,Col or s.PRIMARY),
("変化",player.stats.break in g,Col or s.SUCCESS),
("スタミナ",player.stats.stam in a,Col or s.WARNING),
]
else:
stats_items=[
("ミート",player.stats.contact,Col or s.PRIMARY),
("パワー",player.stats.power,Col or s.DANGER),
("走力",player.stats.run,Col or s.SUCCESS),
("守備",player.stats.field in g,Col or s.WARNING),
]

f or label,value,col or in stats_items:
label_surf=fonts.small.render(label,True,Col or s.TEXT_SECONDARY)
self.screen.blit(label_surf,(detail_rect.x+20,y))

#能力バー
bar_width=200
bar_rect=pygame.Rect(detail_rect.x+100,y+3,bar_width,14)
pygame.draw.rect(self.screen,Col or s.BG_INPUT,bar_rect,b or der_radius=7)

fill_width=in t(bar_width*m in(value,20)/20)
fill_rect=pygame.Rect(bar_rect.x,bar_rect.y,fill_width,14)
pygame.draw.rect(self.screen,col or,fill_rect,b or der_radius=7)

value_surf=fonts.t in y.render(f"{value}",True,Col or s.TEXT_PRIMARY)
self.screen.blit(value_surf,(bar_rect.right+10,y+1))

y+=28

#育成メニューカード
tra in ing_card=Card(450,header_h+320,width-480,height-header_h-420,"TRAININGMENU")
tra in ing_rect=tra in ing_card.draw(self.screen)

y=tra in ing_rect.y+55

#育成オプション
if player.position.value=="投手":
tra in ing_options=[
("tra in _velocity","球速強化","球速+1",50),
("tra in _control","制球強化","制球+1",40),
("tra in _ break in g","変化球強化","変化+1",45),
("tra in _stam in a","スタミナ強化","スタミナ+1",35),
]
else:
tra in ing_options=[
("tra in _contact","ミート強化","ミート+1",40),
("tra in _power","パワー強化","パワー+1",50),
("tra in _speed","走力強化","走力+1",35),
("tra in _ def ense","守備強化","守備+1",40),
]

f or btn_name,btn_text,effect,cost in t ra in ing_options:
btn=Button(
tra in ing_rect.x+20,y,200,40,
btn_text,"ghost"if tra in ing_po in t s>=cost else"outl in e",
font=fonts.small
)
btn.draw(self.screen)
buttons[btn_name]=btn

#効果とコスト
effect_surf=fonts.t in y.render(effect,True,Col or s.SUCCESS)
cost_col or=Col or s.TEXT_PRIMARY if tra in ing_po in t s>=cost else Col or s.DANGER
cost_surf=fonts.t in y.render(f"{cost}pt",True,cost_col or)
self.screen.blit(effect_surf,(tra in ing_rect.x+240,y+5))
self.screen.blit(cost_surf,(tra in ing_rect.x+240,y+22))

y+=50
else:
#選手未選択時
h in t _card=Card(450,header_h+20,width-480,200,"ヒント")
h in t _rect=h in t _card.draw(self.screen)

h in t _text="左の一覧から選手を選択してください"
h in t _surf=fonts.body.render(h in t _text,True,Col or s.TEXT_MUTED)
self.screen.blit(h in t _surf,(h in t _rect.x+30,h in t _rect.y+80))

#BACKボタン
buttons["BACK"]=Button(
50,height-70,150,50,
"←BACK","ghost",font=fonts.body
)
buttons["BACK"].draw(self.screen)

To as tManager.update_ and _draw(self.screen)

return buttons

#========================================
#経営画面
#========================================
def draw_management_screen(self,player_team: Team,f in ances,tab: str="overview")->Dict[str,Button]:
"""経営画面を描画"""
draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()
buttons={}

#ヘッダー
header_h=80
team_ in fo=player_team.name if player_team else None
draw_header(self.screen,"MANAGEMENT",team_ in fo)

#タブ
tabs=[
("overview","概要"),
("f in ances","財務"),
("facilities","施設"),
("spons or s","スポンサー"),
("staff","スタッフ"),
]

tab_y=header_h+15
tab_x=30

f or tab_id,tab_name in t abs:
style="primary"if tab==tab_id else"ghost"
btn=Button(tab_x,tab_y,130,40,tab_name,style,font=fonts.small)
btn.draw(self.screen)
buttons[f"mgmt_tab_{tab_id}"]=btn
tab_x+=140

#財務データの取得（デフォルト値）
if f in ances:
budget=f in ances.budget if h as attr(f in ances,'budget') else50.0
payroll=f in ances.payroll if h as attr(f in ances,'payroll') else30.0
revenue=f in ances.revenue if h as attr(f in ances,'revenue') else25.0
spons or ship=f in ances.spons or ship if h as attr(f in ances,'spons or ship') else10.0
ticket_sales=f in ances.ticket_sales if h as attr(f in ances,'ticket_sales') else5.0
merch and is e=f in ances.merch and is e if h as attr(f in ances,'merch and is e') else3.0
else:
budget=50.0
payroll=30.0
revenue=25.0
spons or ship=10.0
ticket_sales=5.0
merch and is e=3.0

available=budget-payroll

content_y=header_h+70

if tab=="overview":
#概要タブ
#左カード: 収支サマリー
summary_card=Card(30,content_y,380,250,"SUMMARY")
summary_rect=summary_card.draw(self.screen)

y=summary_rect.y+55
summary_items=[
("総予算",f"{budget:.1f}億円",Col or s.PRIMARY),
("年俸総額",f"{payroll:.1f}億円",Col or s.DANGER),
("利用可能",f"{available:.1f}億円",Col or s.SUCCESS if available>0else Col or s.DANGER),
("年間収入",f"{revenue:.1f}億円",Col or s.TEXT_PRIMARY),
]

f or label,value,col or in summary_items:
label_surf=fonts.body.render(label,True,Col or s.TEXT_SECONDARY)
value_surf=fonts.h3.render(value,True,col or)
self.screen.blit(label_surf,(summary_rect.x+25,y))
self.screen.blit(value_surf,(summary_rect.x+200,y))
y+=45

#右カード: 収入内訳
in come_card=Card(430,content_y,350,250,"INCOME")
in come_rect=in come_card.draw(self.screen)

y=in come_rect.y+55
in come_items=[
("スポンサー",spons or ship),
("チケット売上",ticket_sales),
("グッズ売上",merch and is e),
]

total_ in come=spons or ship+ticket_sales+merch and is e

f or label,value in income_items:
label_surf=fonts.body.render(label,True,Col or s.TEXT_SECONDARY)
self.screen.blit(label_surf,(in come_rect.x+20,y))

#棒グラフ
bar_width=150
bar_rect=pygame.Rect(in come_rect.x+120,y+3,bar_width,20)
pygame.draw.rect(self.screen,Col or s.BG_INPUT,bar_rect,b or der_radius=10)

if total_ in come>0:
fill_ratio=value/total_ in come
fill_rect=pygame.Rect(bar_rect.x,bar_rect.y,in t(bar_width*fill_ratio),20)
pygame.draw.rect(self.screen,Col or s.SUCCESS,fill_rect,b or der_radius=10)

value_surf=fonts.small.render(f"{value:.1f}億",True,Col or s.TEXT_PRIMARY)
self.screen.blit(value_surf,(bar_rect.right+10,y+2))

y+=40

#下カード: 今後の予定
schedule_card=Card(30,content_y+270,750,180,"SCHEDULE")
schedule_rect=schedule_card.draw(self.screen)

y=schedule_rect.y+55
schedule_items=[
("ドラフト契約金","約5.0億円","10月"),
("FA補強","予算10.0億円","11-12月"),
("施設維持費","年間3.0億円","通年"),
]

f or i,(item,amount,period) in enumerate(schedule_items):
x_off set=schedule_rect.x+25+i*240
item_surf=fonts.body.render(item,True,Col or s.TEXT_PRIMARY)
amount_surf=fonts.small.render(amount,True,Col or s.WARNING)
period_surf=fonts.t in y.render(period,True,Col or s.TEXT_MUTED)
self.screen.blit(item_surf,(x_off set,y))
self.screen.blit(amount_surf,(x_off set,y+28))
self.screen.blit(period_surf,(x_off set,y+50))

el if tab=="f in ances":
#財務タブ
#年俸一覧
payroll_card=Card(30,content_y,500,height-content_y-100,"💵選手年俸一覧")
payroll_rect=payroll_card.draw(self.screen)

y=payroll_rect.y+55

if player_team:
#年俸順にソート
s or ted_players=s or ted(player_team.players,
key=lambda p: p.salary if h as attr(p,'salary') else1000,reverse=True)

f or i,player in enumerate(s or ted_players[: 12]):
salary=player.salary if h as attr(player,'salary') else1000
salary_oku=salary/10000#万円→億円

#行背景
row_rect=pygame.Rect(payroll_rect.x+15,y,payroll_rect.width-30,35)
if i%2==0:
pygame.draw.rect(self.screen,(*Col or s.BG_CARD[: 3],100),row_rect,b or der_radius=4)

name_surf=fonts.body.render(player.name[: 8],True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(row_rect.x+10,y+7))

pos_surf=fonts.t in y.render(player.position.value,True,Col or s.TEXT_MUTED)
self.screen.blit(pos_surf,(row_rect.x+150,y+10))

salary_col or=Col or s.DANGER if salary_oku>3else Col or s.TEXT_PRIMARY
salary_surf=fonts.body.render(f"{salary_oku:.2f}億円",True,salary_col or)
self.screen.blit(salary_surf,(row_rect.x+250,y+7))

y+=38

#年俸ランキング（リーグ）
rank_card=Card(550,content_y,250,200,"SALARYRANK")
rank_rect=rank_card.draw(self.screen)

rank_text=fonts.h2.render("3位",True,Col or s.PRIMARY)
rank_ in fo=fonts.small.render("セ・リーグ",True,Col or s.TEXT_MUTED)
self.screen.blit(rank_text,(rank_rect.x+90,rank_rect.y+80))
self.screen.blit(rank_ in fo,(rank_rect.x+85,rank_rect.y+120))

el if tab=="facilities":
#施設タブ
facility_card=Card(30,content_y,750,height-content_y-100,"FACILITIES")
facility_rect=facility_card.draw(self.screen)

y=facility_rect.y+55

facilities=[
("本拠地球場","レベル5","収容: 40,000人","良好",95),
("室内練習場","レベル3","バッティング・ブルペン","普通",70),
("トレーニング施設","レベル4","筋力・走力強化","良好",85),
("リハビリ施設","レベル2","怪我からの復帰支援","普通",60),
("寮","レベル3","若手選手向け","普通",75),
("スカウティング設備","レベル3","ドラフト・FAの情報収集","普通",70),
]

f or name,level,desc,condition,rat in g in facilities:
#施設行
row_rect=pygame.Rect(facility_rect.x+20,y,facility_rect.width-40,60)
pygame.draw.rect(self.screen,Col or s.BG_INPUT,row_rect,b or der_radius=8)

name_surf=fonts.body.render(name,True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(row_rect.x+15,y+8))

level_surf=fonts.small.render(level,True,Col or s.PRIMARY)
self.screen.blit(level_surf,(row_rect.x+180,y+10))

desc_surf=fonts.t in y.render(desc,True,Col or s.TEXT_MUTED)
self.screen.blit(desc_surf,(row_rect.x+15,y+35))

#レーティングバー
bar_x=row_rect.x+400
bar_rect=pygame.Rect(bar_x,y+20,150,16)
pygame.draw.rect(self.screen,Col or s.BORDER,bar_rect,b or der_radius=8)

fill_width=in t(150*rat in g/100)
if rat in g>=80:
fill_col or=Col or s.SUCCESS
el if rat in g>=50:
fill_col or=Col or s.WARNING
else:
fill_col or=Col or s.DANGER
fill_rect=pygame.Rect(bar_x,y+20,fill_width,16)
pygame.draw.rect(self.screen,fill_col or,fill_rect,b or der_radius=8)

#投資ボタン
buttons[f"upgrade_{name}"]=Button(
row_rect.right-100,y+15,80,35,
"投資","ghost",font=fonts.t in y
)
buttons[f"upgrade_{name}"].draw(self.screen)

y+=68

el if tab=="spons or s":
#スポンサータブ
spons or _card=Card(30,content_y,500,height-content_y-100,"🤝スポンサー契約")
spons or _rect=spons or _card.draw(self.screen)

y=spons or _rect.y+55

spons or s=[
("メインスポンサー","○○自動車","10.0億円/年",3,"契約中"),
("ユニフォームスポンサー","△△銀行","5.0億円/年",2,"契約中"),
("球場看板","□□飲料","2.0億円/年",1,"更新可"),
("公式パートナー","◎◎電機","1.5億円/年",5,"契約中"),
]

f or name,company,amount,years,status in spons or s:
row_rect=pygame.Rect(spons or _rect.x+15,y,spons or _rect.width-30,55)
pygame.draw.rect(self.screen,Col or s.BG_INPUT,row_rect,b or der_radius=8)

name_surf=fonts.body.render(name,True,Col or s.TEXT_SECONDARY)
self.screen.blit(name_surf,(row_rect.x+10,y+5))

company_surf=fonts.body.render(company,True,Col or s.TEXT_PRIMARY)
self.screen.blit(company_surf,(row_rect.x+10,y+28))

amount_surf=fonts.small.render(amount,True,Col or s.SUCCESS)
self.screen.blit(amount_surf,(row_rect.x+200,y+15))

years_surf=fonts.t in y.render(f"残{years}年",True,Col or s.TEXT_MUTED)
self.screen.blit(years_surf,(row_rect.x+320,y+18))

status_col or=Col or s.SUCCESS if status=="契約中"else Col or s.WARNING
status_surf=fonts.small.render(status,True,status_col or)
self.screen.blit(status_surf,(row_rect.x+400,y+15))

y+=62

#新規スポンサー獲得
new_card=Card(550,content_y,250,150,"📢新規獲得")
new_rect=new_card.draw(self.screen)

buttons["f in d_spons or s"]=Button(
new_rect.x+40,new_rect.y+70,170,45,
"🔍営業活動","secondary",font=fonts.body
)
buttons["f in d_spons or s"].draw(self.screen)

el if tab=="staff":
#スタッフタブ
staff_card=Card(30,content_y,750,height-content_y-100,"👔コーチングスタッフ")
staff_rect=staff_card.draw(self.screen)

y=staff_rect.y+55

staff_ l is t=[
("監督","山田一郎","A","チーム士気向上"),
("ヘッドコーチ","佐藤二郎","B","総合指導"),
("打撃コーチ","鈴木三郎","A","打撃能力向上"),
("投手コーチ","高橋四郎","B","投球能力向上"),
("守備・走塁コーチ","田中五郎","C","守備・走塁向上"),
("バッテリーコーチ","伊藤六郎","B","捕手育成"),
("育成コーチ","渡辺七郎","A","若手成長支援"),
]

f or role,name,rank,effect in staff_ l is t:
row_rect=pygame.Rect(staff_rect.x+15,y,staff_rect.width-30,45)
pygame.draw.rect(self.screen,Col or s.BG_INPUT,row_rect,b or der_radius=6)

role_surf=fonts.small.render(role,True,Col or s.TEXT_MUTED)
self.screen.blit(role_surf,(row_rect.x+10,y+13))

name_surf=fonts.body.render(name,True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(row_rect.x+160,y+10))

#ランク
rank_col or s={"S": Col or s.WARNING,"A": Col or s.SUCCESS,"B": Col or s.PRIMARY,"C": Col or s.TEXT_MUTED}
rank_col or=rank_col or s.get(rank,Col or s.TEXT_MUTED)
rank_surf=fonts.h3.render(rank,True,rank_col or)
self.screen.blit(rank_surf,(row_rect.x+340,y+8))

effect_surf=fonts.t in y.render(effect,True,Col or s.TEXT_SECONDARY)
self.screen.blit(effect_surf,(row_rect.x+400,y+15))

#変更ボタン
buttons[f"change_staff_{role}"]=Button(
row_rect.right-90,y+5,70,35,
"変更","ghost",font=fonts.t in y
)
buttons[f"change_staff_{role}"].draw(self.screen)

y+=52

#BACKボタン
buttons["BACK"]=Button(
50,height-70,150,50,
"←BACK","ghost",font=fonts.body
)
buttons["BACK"].draw(self.screen)

To as tManager.update_ and _draw(self.screen)

return buttons

def draw_roster_management_screen(self,player_team:'Team',selected_tab: str="roster",
selected_player_idx: in t=-1,scroll_off set: in t=0)->dict:
"""選手登録管理画面（支配下・育成管理）-改良版"""
buttons={}
width,height=self.screen.get_size()
header_h=70

#背景
draw_BACKground(self.screen,"gradient")

#ヘッダー
header_rect=pygame.Rect(0,0,width,header_h)
pygame.draw.rect(self.screen,Col or s.BG_CARD,header_rect)

title_surf=fonts.h2.render("ROSTERMANAGEMENT",True,Col or s.TEXT_PRIMARY)
self.screen.blit(title_surf,(30,20))

#登録状況サマリー
roster_count=player_team.get_roster_count()
dev_count=player_team.get_developmental_count()

summary_text=f"支配下:{roster_count}/70育成:{dev_count}/30"
summary_surf=fonts.body.render(summary_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(summary_surf,(width-summary_surf.get_width()-30,25))

#タブ
tab_y=header_h+8
tabs=[
("or der","オーダー"),
("players","選手一覧"),
("promote","支配下昇格"),
("rele as e","自由契約"),
("f or eign","外国人補強"),
("trade","トレード"),
]

tab_x=30
tab_width=110
f or tab_id,tab_name in t abs:
is _active=tab_id==selected_tab
btn=Button(
tab_x,tab_y,tab_width,36,
tab_name,"primary"if is _active else"ghost",font=fonts.small
)
btn.draw(self.screen)
buttons[f"tab_{tab_id}"]=btn
tab_x+=tab_width+10

content_y=tab_y+48
content_height=height-content_y-70

if selected_tab=="or der":
self._draw_ or der_tab(player_team,content_y,content_height,scroll_off set,selected_player_idx,buttons)
el if selected_tab=="players":
self._draw_players_tab(player_team,content_y,content_height,scroll_off set,selected_player_idx,buttons)
el if selected_tab=="promote":
self._draw_promote_tab(player_team,content_y,content_height,scroll_off set,buttons,roster_count)
el if selected_tab=="rele as e":
self._draw_rele as e_tab(player_team,content_y,content_height,scroll_off set,buttons)
el if selected_tab=="f or eign":
self._draw_ f or eign_tab(player_team,content_y,content_height,scroll_off set,buttons)
el if selected_tab=="trade":
self._draw_trade_tab(player_team,content_y,content_height,scroll_off set,buttons)

#BACKボタン
buttons["BACK"]=Button(
30,height-60,130,45,
"←BACK","ghost",font=fonts.body
)
buttons["BACK"].draw(self.screen)

To as tManager.update_ and _draw(self.screen)

return buttons

def _draw_roster_tab(self,player_team,content_y,content_height,scroll_off set,selected_player_idx,buttons):
"""支配下選手タブを描画（改良版：コンパクトで一覧性向上）"""
width=self.screen.get_width()

#選手を投手/野手で分類
pitchers=[(i,p) f or i,p in enumerate(player_team.players)
if not p.is _developmental and p.position.value=="投手"]
batters=[(i,p) f or i,p in enumerate(player_team.players)
if not p.is _developmental and p.position.value!="投手"]

#左パネル: 投手一覧
left_width=(width-80)//2
left_card=Card(30,content_y,left_width,content_height,f"投手({len(pitchers)}人)")
left_rect=left_card.draw(self.screen)

#右パネル: 野手一覧
right_card=Card(50+left_width,content_y,left_width,content_height,f"野手({len(batters)}人)")
right_rect=right_card.draw(self.screen)

row_height=32
header_height=22

#投手リスト
self._draw_player_ l is t _compact(
left_rect,pitchers,scroll_off set,selected_player_idx,
row_height,header_height,buttons,"pitcher",
["#","名前","タイプ","球速","制球","スタミナ"]
)

#野手リスト
self._draw_player_ l is t _compact(
right_rect,batters,scroll_off set,selected_player_idx,
row_height,header_height,buttons,"batter",
["#","名前","守備","ミート","パワー","走力"]
)

def _draw_player_ l is t _compact(self,card_rect,players,scroll_off set,selected_idx,
row_height,header_height,buttons,player_type,headers):
"""コンパクトな選手リストを描画"""
y=card_rect.y+45
max_v is ible=(card_rect.height-60)//row_height

#ヘッダー
col_widths=[35,75,55,45,45,45]if player_type=="pitcher"else[35,75,55,45,45,45]
x=card_rect.x+10
f or i,hdr in enumerate(headers):
hdr_surf=fonts.t in y.render(hdr,True,Col or s.TEXT_MUTED)
self.screen.blit(hdr_surf,(x,y))
x+=col_widths[i]
y+=header_height

#選手行
f or i in range(scroll_off set,m in(scroll_off set+max_v is ible,len(players))):
idx,player=players[i]
row_rect=pygame.Rect(card_rect.x+5,y,card_rect.width-25,row_height-2)

is _selected=idx==selected_idx
bg_col or=(*Col or s.PRIMARY[: 3],60) if is _selected else Col or s.BG_INPUT
pygame.draw.rect(self.screen,bg_col or,row_rect,b or der_radius=3)

x=card_rect.x+10

#背番号
num_surf=fonts.t in y.render(str(player.uni f or m_number),True,Col or s.TEXT_PRIMARY)
self.screen.blit(num_surf,(x,y+7))
x+=col_widths[0]

#名前
name_surf=fonts.t in y.render(player.name[: 5],True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(x,y+7))
x+=col_widths[1]

if player_type=="pitcher":
#タイプ
type_text=player.pitch_type.value[: 2]if player.pitch_type else"-"
type_surf=fonts.t in y.render(type_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(type_surf,(x,y+7))
x+=col_widths[2]

#球速
speed_col or=self._get_stat_col or(player.stats.speed)
speed_surf=fonts.t in y.render(str(player.stats.speed),True,speed_col or)
self.screen.blit(speed_surf,(x,y+7))
x+=col_widths[3]

#制球
ctrl_col or=self._get_stat_col or(player.stats.control)
ctrl_surf=fonts.t in y.render(str(player.stats.control),True,ctrl_col or)
self.screen.blit(ctrl_surf,(x,y+7))
x+=col_widths[4]

#スタミナ
stam_col or=self._get_stat_col or(player.stats.stam in a)
stam_surf=fonts.t in y.render(str(player.stats.stam in a),True,stam_col or)
self.screen.blit(stam_surf,(x,y+7))
else:
#守備
pos_text=player.position.value[: 2]
pos_surf=fonts.t in y.render(pos_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(pos_surf,(x,y+7))
x+=col_widths[2]

#ミート
contact_col or=self._get_stat_col or(player.stats.contact)
contact_surf=fonts.t in y.render(str(player.stats.contact),True,contact_col or)
self.screen.blit(contact_surf,(x,y+7))
x+=col_widths[3]

#パワー
power_col or=self._get_stat_col or(player.stats.power)
power_surf=fonts.t in y.render(str(player.stats.power),True,power_col or)
self.screen.blit(power_surf,(x,y+7))
x+=col_widths[4]

#走力
run_col or=self._get_stat_col or(player.stats.run)
run_surf=fonts.t in y.render(str(player.stats.run),True,run_col or)
self.screen.blit(run_surf,(x,y+7))

#詳細ボタン
detail_btn=Button(row_rect.right-40,y+3,35,row_height-8,"詳","outl in e",font=fonts.t in y)
detail_btn.draw(self.screen)
buttons[f"roster_detail_{idx}"]=detail_btn

buttons[f"player_{idx}"]=row_rect
y+=row_height

#スクロールバー
if len(players)>max_v is ible:
self._draw_scrollbar(card_rect,scroll_off set,len(players),max_v is ible)

def _get_stat_col or(self,value):
"""能力値に応じた色を返す"""
if value>=80:
return Col or s.WARNING#金
el if value>=70:
return Col or s.SUCCESS#緑
el if value>=50:
return Col or s.TEXT_PRIMARY#白
else:
return Col or s.TEXT_MUTED#グレー

def _draw_scrollbar(self,card_rect,scroll_off set,total_items,v is ible_items):
"""スクロールバーを描画"""
scroll_track_h=card_rect.height-60
scroll_h=max(20,in t(scroll_track_h*v is ible_items/total_items))
max_scroll=total_items-v is ible_items
scroll_y=card_rect.y+45+in t((scroll_off set/max(1,max_scroll))*(scroll_track_h-scroll_h))
pygame.draw.rect(self.screen,Col or s.BG_INPUT,
(card_rect.right-12,card_rect.y+45,6,scroll_track_h),b or der_radius=3)
pygame.draw.rect(self.screen,Col or s.PRIMARY,
(card_rect.right-12,scroll_y,6,scroll_h),b or der_radius=3)

def _draw_developmental_tab(self,player_team,content_y,content_height,scroll_off set,selected_player_idx,buttons):
"""育成選手タブを描画"""
width=self.screen.get_width()

card=Card(30,content_y,width-60,content_height,"育成選手一覧")
card_rect=card.draw(self.screen)

dev_players=[(i,p) f or i,p in enumerate(player_team.players) if p.is _developmental]

row_height=32
y=card_rect.y+45
max_v is ible=(card_rect.height-60)//row_height

#ヘッダー
headers=["#","名前","位置","年齢","★","能力"]
col_widths=[35,65,50,40,60,120]
hx=card_rect.x+15
f or i,hdr in enumerate(headers):
hdr_surf=fonts.t in y.render(hdr,True,Col or s.TEXT_MUTED)
self.screen.blit(hdr_surf,(hx,y))
hx+=col_widths[i]
y+=22

f or i in range(scroll_off set,m in(scroll_off set+max_v is ible,len(dev_players))):
idx,player=dev_players[i]
row_rect=pygame.Rect(card_rect.x+10,y,card_rect.width-60,row_height-2)

is _selected=idx==selected_player_idx
bg_col or=(*Col or s.PRIMARY[: 3],60) if is _selected else Col or s.BG_INPUT
pygame.draw.rect(self.screen,bg_col or,row_rect,b or der_radius=4)

x=card_rect.x+15

#背番号
num_surf=fonts.t in y.render(str(player.uni f or m_number),True,Col or s.TEXT_PRIMARY)
self.screen.blit(num_surf,(x,y+7))
x+=col_widths[0]

#名前
name_surf=fonts.t in y.render(player.name[: 5],True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(x,y+7))
x+=col_widths[1]

#ポジション
pos_text=player.position.value[: 2]
pos_surf=fonts.t in y.render(pos_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(pos_surf,(x,y+7))
x+=col_widths[2]

#年齢
age_surf=fonts.t in y.render(f"{player.age}",True,Col or s.TEXT_SECONDARY)
self.screen.blit(age_surf,(x,y+7))
x+=col_widths[3]

#ポテンシャル
if h as attr(player,'growth') and player.growth:
pot=player.growth.potential
pot_col or=Col or s.WARNING if pot>=7else Col or s.SUCCESS if pot>=5else Col or s.TEXT_MUTED
pot_surf=fonts.t in y.render("★"*m in(pot,5),True,pot_col or)
self.screen.blit(pot_surf,(x,y+7))
x+=col_widths[4]

#主要能力
if player.position.value=="投手":
stat_text=f"球{player.stats.speed}制{player.stats.control}"
else:
stat_text=f"ミ{player.stats.contact}パ{player.stats.power}"
stat_surf=fonts.t in y.render(stat_text,True,Col or s.TEXT_MUTED)
self.screen.blit(stat_surf,(x,y+7))

#詳細ボタン
detail_btn=Button(row_rect.right-40,y+3,35,row_height-8,"詳","outl in e",font=fonts.t in y)
detail_btn.draw(self.screen)
buttons[f"roster_detail_{idx}"]=detail_btn

buttons[f"player_{idx}"]=row_rect
y+=row_height

#スクロールバー
if len(dev_players)>max_v is ible:
self._draw_scrollbar(card_rect,scroll_off set,len(dev_players),max_v is ible)

def _draw_promote_tab(self,player_team,content_y,content_height,scroll_off set,buttons,roster_count):
"""支配下昇格タブを描画"""
width=self.screen.get_width()

card=Card(30,content_y,width-60,content_height,"育成→支配下昇格")
card_rect=card.draw(self.screen)

#説明と枠状況
can_promote=player_team.can_add_roster_player()
status_col or=Col or s.SUCCESS if can_promote else Col or s.DANGER

desc_surf=fonts.small.render("育成選手を支配下登録に昇格させます",True,Col or s.TEXT_SECONDARY)
self.screen.blit(desc_surf,(card_rect.x+20,card_rect.y+45))

status_text=f"支配下枠:{roster_count}/70{'(空きあり)'if can_promote else'(満員)'}"
status_surf=fonts.body.render(status_text,True,status_col or)
self.screen.blit(status_surf,(card_rect.x+20,card_rect.y+70))

dev_players=[(i,p) f or i,p in enumerate(player_team.players) if p.is _developmental]

row_height=60#少し高くして詳細ボタンを収める
y=card_rect.y+110
max_v is ible=(card_rect.height-130)//row_height

f or i in range(scroll_off set,m in(scroll_off set+max_v is ible,len(dev_players))):
idx,player=dev_players[i]
row_rect=pygame.Rect(card_rect.x+15,y,card_rect.width-180,row_height-5)
pygame.draw.rect(self.screen,Col or s.BG_INPUT,row_rect,b or der_radius=6)

#選手情報（詳細表示）
in fo_l in e1=f"#{player.uni f or m_number}{player.name}({player.position.value}){player.age}歳"
in fo_surf1=fonts.small.render(in fo_l in e1,True,Col or s.TEXT_PRIMARY)
self.screen.blit(in fo_surf1,(row_rect.x+15,y+6))

#能力値
if player.position.value=="投手":
stat_text=f"球速:{player.stats.speed}制球:{player.stats.control}スタミナ:{player.stats.stam in a}"
else:
stat_text=f"ミート:{player.stats.contact}パワー:{player.stats.power}走力:{player.stats.run}"

#ポテンシャル
pot_text=""
if h as attr(player,'growth') and player.growth:
pot_text=f"★{'★'*m in(player.growth.potential-1,4)}"

in fo_surf2=fonts.t in y.render(stat_text+pot_text,True,Col or s.TEXT_MUTED)
self.screen.blit(in fo_surf2,(row_rect.x+15,y+28))

#詳細ボタン（能力詳細を見るため）
detail_btn=Button(row_rect.x+row_rect.width-50,y+35,45,20,"詳細","outl in e",font=fonts.t in y)
detail_btn.draw(self.screen)
buttons[f"roster_detail_{idx}"]=detail_btn

#昇格ボタン
if can_promote:
promote_btn=Button(row_rect.right+15,y+8,100,34,"昇格","primary",font=fonts.small)
promote_btn.draw(self.screen)
buttons[f"promote_{idx}"]=promote_btn
else:
#枠なしの場合はグレーアウト
d is abled_surf=fonts.small.render("枠なし",True,Col or s.TEXT_MUTED)
self.screen.blit(d is abled_surf,(row_rect.right+35,y+15))

y+=row_height

#スクロールバー
if len(dev_players)>max_v is ible:
self._draw_scrollbar(card_rect,scroll_off set,len(dev_players),max_v is ible)

def _draw_ or der_tab(self,player_team,content_y,content_height,scroll_off set,selected_player_idx,buttons):
"""オーダー編成タブを描画（自由な打順・守備位置設定）"""
width=self.screen.get_width()
from set t in gs_manager imp or t set t in gs
from mo del s imp or t Position

#DH制の判定
is _pac if ic=h as attr(player_team,'league') and player_team.league.value=="パシフィック"
use_dh=(is _pac if ic and set t in gs.game_rules.pac if ic_dh) or(not is _pac if ic and set t in gs.game_rules.central_dh)

#========================================
#左パネル: スタメン（打順と守備位置を自由に設定）
#========================================
left_width=430
or der_card=Card(30,content_y+5,left_width,content_height-70,"スタメン")
or der_rect=or der_card.draw(self.screen)

row_height=34
y=or der_rect.y+40

#ヘッダー行
headers=[("打順",40),("守備",55),("選手",145),("適性",110),("入替",50)]
hx=or der_rect.x+8
f or hdr,w in headers:
hdr_surf=fonts.t in y.render(hdr,True,Col or s.TEXT_MUTED)
self.screen.blit(hdr_surf,(hx,y-14))
hx+=w

#守備位置選択肢（DH対応）
all_positions=["捕","一","二","三","遊","左","中","右"]
if use_dh:
all_positions.append("DH")

#l in eup_positionsがない場合は初期化（打順に対するポジションを保持）
if not h as attr(player_team,'l in eup_positions') or player_team.l in eup_positions is None:
player_team.l in eup_positions=["捕","一","二","三","遊","左","中","右","DH"if use_dh else"投"]

f or i in range(9):
#行の背景
row_rect=pygame.Rect(or der_rect.x+6,y,left_width-16,row_height-2)

#選択中のスロットかどうか
is _selected_slot=(i==selected_player_idx)

#選手がいる場合の処理
if i<len(player_team.current_l in eup) and player_team.current_l in eup[i]is not None:
player_idx=player_team.current_l in eup[i]
if0<=player_idx<len(player_team.players):
player=player_team.players[player_idx]

#行の背景（選択中は強調表示）
if is _selected_slot:
pygame.draw.rect(self.screen,(50,60,80),row_rect,b or der_radius=4)
pygame.draw.rect(self.screen,Col or s.PRIMARY,row_rect,2,b or der_radius=4)
else:
pygame.draw.rect(self.screen,Col or s.BG_INPUT,row_rect,b or der_radius=4)

x=or der_rect.x+10

#打順番号（円形バッジ）
badge_col or=Col or s.WARNING if is _selected_slot else Col or s.PRIMARY
pygame.draw.circle(self.screen,badge_col or,(x+12,y+row_height//2),12)
num_surf=fonts.small.render(str(i+1),True,Col or s.TEXT_PRIMARY)
num_rect=num_surf.get_rect(center=(x+12,y+row_height//2))
self.screen.blit(num_surf,num_rect)
x+=40

#守備位置（クリックで変更可能なボタン）
current_pos=player_team.l in eup_positions[i]if i<len(player_team.l in eup_positions) else"DH"
pos_btn_rect=pygame.Rect(x,y+3,45,row_height-8)
pos_hovered=pos_btn_rect.collidepo in t(pygame.mouse.get_pos())
pos_bg=Col or s.BG_HOVER if pos_hovered else Col or s.BG_CARD
pygame.draw.rect(self.screen,pos_bg,pos_btn_rect,b or der_radius=4)

is _dh=current_pos=="DH"
pos_b or der_col or=Col or s.WARNING if is _dh else Col or s.SUCCESS
pygame.draw.rect(self.screen,pos_b or der_col or,pos_btn_rect,1,b or der_radius=4)

pos_col or=Col or s.WARNING if is _dh else Col or s.SUCCESS
pos_surf=fonts.small.render(current_pos,True,pos_col or)
pos_rect=pos_surf.get_rect(center=pos_btn_rect.center)
self.screen.blit(pos_surf,pos_rect)

#ポジション変更ボタンとして登録
pos_btn=Button(pos_btn_rect.x,pos_btn_rect.y,pos_btn_rect.width,pos_btn_rect.height,"","ghost")
buttons[f"change_pos_{i}"]=pos_btn
x+=55

#選手名（背番号付き）
name_text=f"#{player.uni f or m_number}{player.name}"
name_surf=fonts.small.render(name_text[: 10],True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(x,y+7))
x+=145

#守備適性表示
ma in _pos=player.position.value[: 1]if player.position.value!="外野手"else"外"
sub_positions=getattr(player,'sub_positions',[]) or[]

apt_text=f"◎{ma in _pos}"
f or sp in sub_positions[: 2]:
sp_ str=sp.value if h as attr(sp,'value') else str(sp)
sp_sh or t=sp_ str[: 1]if sp_ str!="外野手"else"外"
apt_text+=f"○{sp_sh or t}"

apt_surf=fonts.t in y.render(apt_text,True,Col or s.TEXT_MUTED)
self.screen.blit(apt_surf,(x,y+9))
x+=110

#入替ボタン（上下）
if i>0:
up_btn=Button(x,y+2,22,14,"▲","ghost",font=fonts.t in y)
up_btn.draw(self.screen)
buttons[f"swap_up_{i}"]=up_btn
if i<8:
down_btn=Button(x,y+17,22,14,"▼","ghost",font=fonts.t in y)
down_btn.draw(self.screen)
buttons[f"swap_down_{i}"]=down_btn
x+=25

#削除ボタン
remove_btn=Button(x,y+5,22,row_height-12,"×","danger",font=fonts.t in y)
remove_btn.draw(self.screen)
buttons[f"remove_l in eup_{i}"]=remove_btn
else:
#空きスロット
pygame.draw.rect(self.screen,Col or s.BG_CARD,row_rect,b or der_radius=4)
pygame.draw.rect(self.screen,Col or s.BORDER,row_rect,1,b or der_radius=4)

x=or der_rect.x+10
#打順番号
pygame.draw.circle(self.screen,Col or s.BG_INPUT,(x+12,y+row_height//2),12)
pygame.draw.circle(self.screen,Col or s.BORDER,(x+12,y+row_height//2),12,1)
num_surf=fonts.small.render(str(i+1),True,Col or s.TEXT_MUTED)
num_rect=num_surf.get_rect(center=(x+12,y+row_height//2))
self.screen.blit(num_surf,num_rect)

#守備位置を選べるボタン
x+=40
current_pos=player_team.l in eup_positions[i]if i<len(player_team.l in eup_positions) else"?"
pos_btn_rect=pygame.Rect(x,y+3,45,row_height-8)
pos_hovered=pos_btn_rect.collidepo in t(pygame.mouse.get_pos())
pos_bg=Col or s.BG_HOVER if pos_hovered else Col or s.BG_INPUT
pygame.draw.rect(self.screen,pos_bg,pos_btn_rect,b or der_radius=4)
pygame.draw.rect(self.screen,Col or s.BORDER,pos_btn_rect,1,b or der_radius=4)
pos_surf=fonts.small.render(current_pos,True,Col or s.TEXT_MUTED)
pos_rect=pos_surf.get_rect(center=pos_btn_rect.center)
self.screen.blit(pos_surf,pos_rect)

pos_btn=Button(pos_btn_rect.x,pos_btn_rect.y,pos_btn_rect.width,pos_btn_rect.height,"","ghost")
buttons[f"change_pos_{i}"]=pos_btn

#空き表示
empty_surf=fonts.small.render("--選手を選択--",True,Col or s.TEXT_MUTED)
self.screen.blit(empty_surf,(x+55,y+7))

y+=row_height

#先発投手セクション
y+=6
pygame.draw.l in e(self.screen,Col or s.BORDER,(or der_rect.x+8,y),(or der_rect.x+left_width-20,y),1)
y+=6

sp_row=pygame.Rect(or der_rect.x+6,y,left_width-16,row_height)
pygame.draw.rect(self.screen,Col or s.BG_INPUT,sp_row,b or der_radius=4)

sp_label=fonts.body.render("先発",True,Col or s.INFO)
self.screen.blit(sp_label,(or der_rect.x+18,y+7))

if player_team.start in g_pitcher_idx>=0and player_team.start in g_pitcher_idx<len(player_team.players):
sp=player_team.players[player_team.start in g_pitcher_idx]
sp_text=f"#{sp.uni f or m_number}{sp.name}"
sp_surf=fonts.small.render(sp_text,True,Col or s.TEXT_PRIMARY)
self.screen.blit(sp_surf,(or der_rect.x+68,y+7))

#投手能力
sp_stat=f"球速{sp.stats.speed}制球{sp.stats.control}"
sp_stat_surf=fonts.t in y.render(sp_stat,True,Col or s.TEXT_MUTED)
self.screen.blit(sp_stat_surf,(or der_rect.x+220,y+9))
else:
no_sp=fonts.small.render("--未設定--",True,Col or s.TEXT_MUTED)
self.screen.blit(no_sp,(or der_rect.x+68,y+7))

#========================================
#右パネル: 選手一覧（野手のみ・クリックで追加）
#========================================
right_x=30+left_width+15
right_width=width-right_x-30
right_card=Card(right_x,content_y,right_width,content_height-60,"野手一覧（クリックで追加）")
right_rect=right_card.draw(self.screen)

#現在のラインアップに含まれない野手
l in eup_ set=set(player_team.current_l in eup) if player_team.current_l in eup else set()
available_batters=[(i,p) f or i,p in enumerate(player_team.players)
if not p.is _developmental and p.position!=Position.PITCHER and i not in l in eup_ set]

#ヘッダー
row_height=34
l is t _y=right_rect.y+45
hdr_x=right_rect.x+10
f or hdr,w in[("守備",45),("選手名",115),("ミ",35),("パ",35),("走",35),("適性",80)]:
hdr_surf=fonts.t in y.render(hdr,True,Col or s.TEXT_MUTED)
self.screen.blit(hdr_surf,(hdr_x,l is t _y))
hdr_x+=w
l is t _y+=20

max_v is ible=(right_rect.height-80)//row_height

f or i in range(scroll_off set,m in(scroll_off set+max_v is ible,len(available_batters))):
idx,player=available_batters[i]
row_rect=pygame.Rect(right_rect.x+8,l is t _y,right_rect.width-20,row_height-2)

is _hovered=row_rect.collidepo in t(pygame.mouse.get_pos())
bg_col or=Col or s.BG_HOVER if is _hovered else Col or s.BG_INPUT
pygame.draw.rect(self.screen,bg_col or,row_rect,b or der_radius=4)

x=right_rect.x+12

#守備
pos_text=player.position.value[: 2]if player.position.value!="外野手"else"外"
pos_surf=fonts.small.render(pos_text,True,Col or s.SUCCESS)
self.screen.blit(pos_surf,(x,l is t _y+7))
x+=45

#選手名
name_text=f"#{player.uni f or m_number}{player.name}"
name_surf=fonts.small.render(name_text[: 8],True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(x,l is t _y+7))
x+=115

#ミート
contact_col or=self._get_stat_col or(player.stats.contact)
contact_surf=fonts.t in y.render(str(player.stats.contact),True,contact_col or)
self.screen.blit(contact_surf,(x+5,l is t _y+9))
x+=35

#パワー
power_col or=self._get_stat_col or(player.stats.power)
power_surf=fonts.t in y.render(str(player.stats.power),True,power_col or)
self.screen.blit(power_surf,(x+5,l is t _y+9))
x+=35

#走力
run_col or=self._get_stat_col or(player.stats.run)
run_surf=fonts.t in y.render(str(player.stats.run),True,run_col or)
self.screen.blit(run_surf,(x+5,l is t _y+9))
x+=35

#守備適性
ma in _pos=player.position.value[: 1]if player.position.value!="外野手"else"外"
apt_text=f"◎{ma in _pos}"
if h as attr(player,'sub_positions') and player.sub_positions:
f or sp in player.sub_positions[: 1]:
#Positionオブジェクトの場合は.valueを取得
sp_ str=sp.value if h as attr(sp,'value') else str(sp)
sp_sh or t=sp_ str[: 1]if sp_ str!="外野手"else"外"
apt_text+=f"○{sp_sh or t}"
apt_surf=fonts.t in y.render(apt_text,True,Col or s.TEXT_MUTED)
self.screen.blit(apt_surf,(x,l is t _y+9))

#クリック可能エリア
btn=Button(row_rect.x,row_rect.y,row_rect.width,row_rect.height,"","ghost")
btn.is _hovered=is _hovered
buttons[f"add_l in eup_{idx}"]=btn

l is t _y+=row_height

#スクロールバー
if len(available_batters)>max_v is ible:
self._draw_scrollbar(right_rect,scroll_off set,len(available_batters),max_v is ible)

#下部ボタン
btn_y=content_y+content_height-50
auto_btn=Button(30,btn_y,130,38,"自動編成","primary",font=fonts.small)
auto_btn.draw(self.screen)
buttons["auto_l in eup"]=auto_btn

clear_btn=Button(170,btn_y,100,38,"クリア","danger",font=fonts.small)
clear_btn.draw(self.screen)
buttons["clear_l in eup"]=clear_btn

#ポジションクイック選択バー（右側）
pos_bar_x=290
pos_bar_label=fonts.t in y.render("位置:",True,Col or s.TEXT_MUTED)
self.screen.blit(pos_bar_label,(pos_bar_x,btn_y+12))
pos_bar_x+=35

quick_positions=["捕","一","二","三","遊","左","中","右"]
if use_dh:
quick_positions.append("DH")

f or pos in quick_positions:
pos_btn_w=28
pos_btn=Button(pos_bar_x,btn_y+3,pos_btn_w,32,pos,"outl in e",font=fonts.t in y)
pos_btn.draw(self.screen)
buttons[f"quick_pos_{pos}"]=pos_btn
pos_bar_x+=pos_btn_w+4

def _draw_rele as e_tab(self,player_team,content_y,content_height,scroll_off set,buttons):
"""自由契約タブを描画"""
width=self.screen.get_width()

card=Card(30,content_y,width-60,content_height,"自由契約（選手解雇）")
card_rect=card.draw(self.screen)

desc_surf=fonts.small.render("選手を自由契約にして登録枠を空けます。解雇した選手は戻ってきません。",True,Col or s.TEXT_SECONDARY)
self.screen.blit(desc_surf,(card_rect.x+20,card_rect.y+45))

#支配下選手のみ
players=[(i,p) f or i,p in enumerate(player_team.players) if not p.is _developmental]

row_height=36
y=card_rect.y+80
max_v is ible=(card_rect.height-100)//row_height

f or i in range(scroll_off set,m in(scroll_off set+max_v is ible,len(players))):
idx,player=players[i]
row_rect=pygame.Rect(card_rect.x+15,y,card_rect.width-150,row_height-4)
pygame.draw.rect(self.screen,Col or s.BG_INPUT,row_rect,b or der_radius=4)

in fo_text=f"#{player.uni f or m_number}{player.name}({player.position.value}){player.age}歳"
in fo_surf=fonts.small.render(in fo_text,True,Col or s.TEXT_PRIMARY)
self.screen.blit(in fo_surf,(row_rect.x+10,y+8))

#年俸
if player.salary>=100000000:
salary_text=f"{player.salary//100000000}億"
else:
salary_text=f"{player.salary//10000}万"
salary_surf=fonts.t in y.render(salary_text,True,Col or s.WARNING)
self.screen.blit(salary_surf,(row_rect.right-80,y+10))

#解雇ボタン
rele as e_btn=Button(row_rect.right+15,y+2,80,28,"解雇","danger",font=fonts.small)
rele as e_btn.draw(self.screen)
buttons[f"rele as e_{idx}"]=rele as e_btn

y+=row_height

if len(players)>max_v is ible:
self._draw_scrollbar(card_rect,scroll_off set,len(players),max_v is ible)

def _draw_ f or eign_tab(self,player_team,content_y,content_height,scroll_off set,buttons):
"""新外国人補強タブを描画"""
width=self.screen.get_width()

card=Card(30,content_y,width-60,content_height,"外国人選手補強")
card_rect=card.draw(self.screen)

desc_surf=fonts.small.render("外国人選手を獲得します。外国人枠は5名までです。",True,Col or s.TEXT_SECONDARY)
self.screen.blit(desc_surf,(card_rect.x+20,card_rect.y+45))

#現在の外国人数を計算
f or eign_count=sum(1f or p in player_team.players if h as attr(p,'is _ f or eign') and p.is _ f or eign)
status_text=f"現在の外国人選手:{f or eign_count}/5"
status_col or=Col or s.SUCCESS if f or eign_count<5else Col or s.DANGER
status_surf=fonts.body.render(status_text,True,status_col or)
self.screen.blit(status_surf,(card_rect.x+20,card_rect.y+70))

#外国人FA市場へのリンク
fa_btn=Button(card_rect.x+20,card_rect.y+110,200,45,"外国人FA市場を開く","primary",font=fonts.body)
fa_btn.draw(self.screen)
buttons["open_ f or eign_fa"]=fa_btn

in fo_text="※外国人FA市場では世界各国のフリーエージェント選手と契約できます"
in fo_surf=fonts.t in y.render(in fo_text,True,Col or s.TEXT_MUTED)
self.screen.blit(in fo_surf,(card_rect.x+20,card_rect.y+170))

def _draw_trade_tab(self,player_team,content_y,content_height,scroll_off set,buttons):
"""トレードタブを描画"""
width=self.screen.get_width()

card=Card(30,content_y,width-60,content_height,"トレード")
card_rect=card.draw(self.screen)

desc_surf=fonts.small.render("他球団と選手をトレードします。",True,Col or s.TEXT_SECONDARY)
self.screen.blit(desc_surf,(card_rect.x+20,card_rect.y+45))

#トレード市場へのリンク
trade_btn=Button(card_rect.x+20,card_rect.y+90,200,45,"トレード市場を開く","primary",font=fonts.body)
trade_btn.draw(self.screen)
buttons["open_trade_market"]=trade_btn

in fo_text="※トレードでは他球団の選手と交換できます。金銭トレードも可能です。"
in fo_surf=fonts.t in y.render(in fo_text,True,Col or s.TEXT_MUTED)
self.screen.blit(in fo_surf,(card_rect.x+20,card_rect.y+150))

def _draw_players_tab(self,player_team,content_y,content_height,scroll_off set,selected_player_idx,buttons):
"""選手一覧タブを描画"""
width=self.screen.get_width()
from mo del s imp or t Position

#投手/野手のフィルタボタン
filter_y=content_y
pitcher_btn=Button(30,filter_y,100,32,"投手","outl in e",font=fonts.small)
pitcher_btn.draw(self.screen)
buttons["filter_pitcher"]=pitcher_btn

batter_btn=Button(140,filter_y,100,32,"野手","outl in e",font=fonts.small)
batter_btn.draw(self.screen)
buttons["filter_batter"]=batter_btn

all_btn=Button(250,filter_y,100,32,"全員","primary",font=fonts.small)
all_btn.draw(self.screen)
buttons["filter_all"]=all_btn

#選手リスト
l is t _y=filter_y+45
l is t _height=content_height-55

card=Card(30,l is t _y,width-60,l is t _height,"選手一覧")
card_rect=card.draw(self.screen)

#全選手（支配下・育成含む）
all_players=[(i,p) f or i,p in enumerate(player_team.players)]

row_height=34
y=card_rect.y+45
max_v is ible=(card_rect.height-60)//row_height

#ヘッダー
headers=["#","名前","ポジ","年齢","契約","能力"]
header_x=[15,50,200,280,330,400]
f or h,hx in zip(headers,header_x):
h_surf=fonts.t in y.render(h,True,Col or s.TEXT_MUTED)
self.screen.blit(h_surf,(card_rect.x+hx,card_rect.y+45))

y+=25

f or i in range(scroll_off set,m in(scroll_off set+max_v is ible,len(all_players))):
idx,player=all_players[i]
row_rect=pygame.Rect(card_rect.x+10,y,card_rect.width-20,row_height-4)

is _selected=idx==selected_player_idx
is _hovered=row_rect.collidepo in t(pygame.mouse.get_pos())

if is _selected:
bg_col or=lerp_col or(Col or s.BG_CARD,Col or s.PRIMARY,0.3)
el if is _hovered:
bg_col or=Col or s.BG_HOVER
else:
bg_col or=Col or s.BG_INPUT if i%2==0else Col or s.BG_CARD

pygame.draw.rect(self.screen,bg_col or,row_rect,b or der_radius=4)

#背番号
num_surf=fonts.small.render(str(player.uni f or m_number),True,Col or s.TEXT_SECONDARY)
self.screen.blit(num_surf,(card_rect.x+20,y+7))

#名前
name_col or=Col or s.WARNING if player.is _developmental else Col or s.TEXT_PRIMARY
name_surf=fonts.small.render(player.name[: 8],True,name_col or)
self.screen.blit(name_surf,(card_rect.x+55,y+7))

#ポジション
pos_surf=fonts.small.render(player.position.value[: 3],True,Col or s.TEXT_SECONDARY)
self.screen.blit(pos_surf,(card_rect.x+205,y+7))

#年齢
age_surf=fonts.small.render(str(player.age),True,Col or s.TEXT_SECONDARY)
self.screen.blit(age_surf,(card_rect.x+285,y+7))

#契約
contract_text="育成"if player.is _developmental else"支配下"
contract_surf=fonts.t in y.render(contract_text,True,Col or s.WARNING if player.is _developmental else Col or s.SUCCESS)
self.screen.blit(contract_surf,(card_rect.x+335,y+9))

#総合能力
overall=player.stats.overall_pitch in g() if player.position==Position.PITCHER else player.stats.overall_batt in g()
rank=player.stats.get_rank(overall)
rank_col or=player.stats.get_rank_col or(overall)
overall_surf=fonts.small.render(f"{rank}({overall})",True,rank_col or)
self.screen.blit(overall_surf,(card_rect.x+405,y+7))

#詳細ボタン
detail_btn=Button(row_rect.right-55,y+3,50,26,"詳細","outl in e",font=fonts.t in y)
detail_btn.draw(self.screen)
buttons[f"player_detail_{idx}"]=detail_btn

y+=row_height

if len(all_players)>max_v is ible:
self._draw_scrollbar(card_rect,scroll_off set,len(all_players),max_v is ible)

#========================================
#選手詳細画面（パワプロ風）
#========================================
def draw_player_detail_screen(self,player,scroll_off set: in t=0,team_col or=None)->Dict[str,Button]:
"""選手詳細画面を描画（パワプロ風能力表示・強化版）"""
from mo del s imp or t Position

draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()
center_x=width//2

if team_col or is None:
team_col or=Col or s.PRIMARY

#ヘッダー（選手情報をコンパクトに）
pos_text=player.position.value
if player.pitch_type:
pos_text+=f"({player.pitch_type.value})"

#カスタムヘッダー（より詳細な情報付き）
header_h=100
pygame.draw.rect(self.screen,Col or s.BG_CARD,(0,0,width,header_h))

#背番号を大きく表示
number_surf=fonts.h1.render(f"#{player.uni f or m_number}",True,team_col or)
self.screen.blit(number_surf,(30,20))

#名前
name_surf=fonts.h2.render(player.name,True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(120,25))

#ポジション・年齢・契約タイプを横に
contract_text="育成"if player.is _developmental else"支配下"
in fo_l in e=f"{pos_text}|{player.age}歳|{contract_text}|プロ{player.years_pro}年目"
in fo_surf=fonts.body.render(in fo_l in e,True,Col or s.TEXT_SECONDARY)
self.screen.blit(in fo_surf,(120,60))

#年俸表示（右側）
if player.salary>=100000000:
salary_text=f"{player.salary//100000000}億{(player.salary%100000000)//10000000}千万"
else:
salary_text=f"{player.salary//10000}万円"
salary_surf=fonts.body.render(salary_text,True,Col or s.WARNING)
self.screen.blit(salary_surf,(width-salary_surf.get_width()-30,35))

buttons={}
stats=player.stats

#=====能力値表示エリア=====
content_y=header_h+10

if player.position==Position.PITCHER:
#投手能力カード（左側）
ability_card=Card(20,content_y,400,260,"PITCHER")
ability_rect=ability_card.draw(self.screen)

#基本能力（2x2グリッド）
abilities=[
("球速",stats.speed,"",f"{130+stats.speed*2}km"),
("コントロール",stats.control,"",""),
("スタミナ",stats.stam in a,"",""),
("変化球",stats.break in g,"",""),
]

y=ability_rect.y+45
f or i,(name,value,icon,extra) in enumerate(abilities):
col=i%2
x=ability_rect.x+20+col*185
if i==2:
y+=55

#名前
name_surf=fonts.small.render(f"{icon}{name}",True,Col or s.TEXT_SECONDARY)
self.screen.blit(name_surf,(x,y))

#ランク（大きく）
rank=stats.get_rank(value)
rank_col or=stats.get_rank_col or(value)
rank_surf=fonts.h2.render(rank,True,rank_col or)
self.screen.blit(rank_surf,(x,y+18))

#数値とバー
value_text=f"{value}"+(f"{extra}"if extra else"")
val_surf=fonts.t in y.render(value_text,True,Col or s.TEXT_MUTED)
self.screen.blit(val_surf,(x+35,y+28))

#バー
bar_x=x+80
bar_y=y+30
pygame.draw.rect(self.screen,Col or s.BG_INPUT,(bar_x,bar_y,80,6),b or der_radius=3)
fill_w=in t(80*m in(value/20,1.0))
pygame.draw.rect(self.screen,rank_col or,(bar_x,bar_y,fill_w,6),b or der_radius=3)

#球種カード（右側）
pitch_card=Card(430,content_y,width-450,260,"🎱持ち球")
pitch_rect=pitch_card.draw(self.screen)

y=pitch_rect.y+45
if h as attr(stats,'pitch_repertoire') and stats.pitch_repertoire:
f or pitch_name,break _value in l is t(stats.pitch_repertoire.items())[: 8]:
#球種名
pitch_surf=fonts.body.render(pitch_name,True,Col or s.TEXT_PRIMARY)
self.screen.blit(pitch_surf,(pitch_rect.x+20,y))
#変化量バー
bar_x=pitch_rect.x+150
pygame.draw.rect(self.screen,Col or s.BG_INPUT,(bar_x,y+5,80,8),b or der_radius=4)
fill_w=in t(80*m in(break _value/7,1.0))
pygame.draw.rect(self.screen,Col or s.INFO,(bar_x,y+5,fill_w,8),b or der_radius=4)
#変化量
val_surf=fonts.small.render(f"{break _value}",True,Col or s.TEXT_SECONDARY)
self.screen.blit(val_surf,(bar_x+85,y+2))
y+=26
el if stats.break in g_balls:
f or pitch_name in stats.break in g_balls[: 8]:
pitch_surf=fonts.body.render(f"•{pitch_name}",True,Col or s.TEXT_PRIMARY)
self.screen.blit(pitch_surf,(pitch_rect.x+20,y))
y+=26

else:
#野手能力カード（左側）
ability_card=Card(20,content_y,400,260,"🏏野手能力")
ability_rect=ability_card.draw(self.screen)

#弾道表示（上部に大きく）
traject or y=getattr(stats,'traject or y',2)
traj_names={1:"グラウンダー",2:"ライナー",3:"普通",4:"パワー"}

traj_label=fonts.small.render("弾道",True,Col or s.TEXT_SECONDARY)
self.screen.blit(traj_label,(ability_rect.x+20,ability_rect.y+42))

#弾道アイコン（丸で表示）
f or i in range(4):
col or=Col or s.WARNING if i<traject or y else Col or s.BG_INPUT
pygame.draw.circle(self.screen,col or,(ability_rect.x+80+i*25,ability_rect.y+52),8)
traj_name_surf=fonts.small.render(traj_names.get(traject or y,'普通'),True,Col or s.TEXT_MUTED)
self.screen.blit(traj_name_surf,(ability_rect.x+190,ability_rect.y+45))

#基本能力（3列×2行）
abilities=[
("ミート",stats.contact,""),
("パワー",stats.power,""),
("走力",stats.run,""),
("肩力",stats.arm,""),
("守備",stats.field in g,""),
("捕球",getattr(stats,'catch in g',stats.field in g),""),
]

y=ability_rect.y+75
f or i,(name,value,icon) in enumerate(abilities):
col=i%3
x=ability_rect.x+15+col*125
if i==3:
y+=55

#名前
name_surf=fonts.t in y.render(f"{icon}{name}",True,Col or s.TEXT_SECONDARY)
self.screen.blit(name_surf,(x,y))

#ランク（大きく）
rank=stats.get_rank(value)
rank_col or=stats.get_rank_col or(value)
rank_surf=fonts.h3.render(rank,True,rank_col or)
self.screen.blit(rank_surf,(x,y+15))

#数値
val_surf=fonts.t in y.render(f"{value}",True,Col or s.TEXT_MUTED)
self.screen.blit(val_surf,(x+30,y+22))

#バー
bar_x=x+50
bar_y=y+25
pygame.draw.rect(self.screen,Col or s.BG_INPUT,(bar_x,bar_y,60,5),b or der_radius=2)
fill_w=in t(60*m in(value/20,1.0))
pygame.draw.rect(self.screen,rank_col or,(bar_x,bar_y,fill_w,5),b or der_radius=2)

#守備適性カード（右側）
pos_card=Card(430,content_y,width-450,260,"POSITION")
pos_rect=pos_card.draw(self.screen)

#メインポジション
ma in _pos_surf=fonts.body.render(f"メイン:{player.position.value}",True,Col or s.PRIMARY)
self.screen.blit(ma in _pos_surf,(pos_rect.x+20,pos_rect.y+45))

#サブポジション
y=pos_rect.y+75
sub_label=fonts.small.render("サブポジション:",True,Col or s.TEXT_SECONDARY)
self.screen.blit(sub_label,(pos_rect.x+20,y))
y+=25

if h as attr(player,'sub_positions') and player.sub_positions:
f or sub_pos in player.sub_positions[: 4]:
pos_surf=fonts.body.render(f"•{sub_pos.value}",True,Col or s.TEXT_PRIMARY)
self.screen.blit(pos_surf,(pos_rect.x+30,y))
y+=24
else:
none_surf=fonts.small.render("なし",True,Col or s.TEXT_MUTED)
self.screen.blit(none_surf,(pos_rect.x+30,y))

#特殊能力カード（下部左）
special_card=Card(20,content_y+270,400,155,"SKILLS")
special_rect=special_card.draw(self.screen)

if player.position==Position.PITCHER:
special_abilities=[
("対ピンチ",stats.clutch,""),
("対左打者",getattr(stats,'vs_left',10),""),
("メンタル",stats.mental,""),
("安定感",stats.cons is tency,""),
("クイック",getattr(stats,'quick',10),""),
("牽制",getattr(stats,'pickoff',10),""),
]
else:
special_abilities=[
("チャンス",stats.clutch,""),
("対左投手",getattr(stats,'vs_left',10),""),
("メンタル",stats.mental,""),
("安定感",stats.cons is tency,""),
("盗塁",getattr(stats,'steal in g',stats.run),""),
("送球",getattr(stats,'throw in g',stats.arm),""),
]

y=special_rect.y+42
f or i,(name,value,icon) in enumerate(special_abilities):
col=i%3
x=special_rect.x+15+col*125
if i==3:
y+=38

rank=stats.get_rank(value)
rank_col or=stats.get_rank_col or(value)

name_surf=fonts.t in y.render(f"{icon}{name}",True,Col or s.TEXT_SECONDARY)
rank_surf=fonts.body.render(rank,True,rank_col or)

self.screen.blit(name_surf,(x,y))
self.screen.blit(rank_surf,(x,y+16))

#ミニバー
bar_x=x+30
pygame.draw.rect(self.screen,Col or s.BG_INPUT,(bar_x,y+22,50,4),b or der_radius=2)
fill=in t(50*m in(value/20,1.0))
pygame.draw.rect(self.screen,rank_col or,(bar_x,y+22,fill,4),b or der_radius=2)

#成績カード（下部右）
rec or d=player.rec or d
rec or d_card=Card(430,content_y+270,width-450,155,"STATS")
rec or d_rect=rec or d_card.draw(self.screen)

if player.position==Position.PITCHER:
stats_items=[
("登板",f"{rec or d.games_pitched}",Col or s.TEXT_PRIMARY),
("勝",f"{rec or d.w in s}",Col or s.SUCCESS),
("敗",f"{rec or d.losses}",Col or s.DANGER),
("S",f"{rec or d.saves}",Col or s.INFO),
("防御率",f"{rec or d.era:.2f}",Col or s.WARNING if rec or d.era<3.0else Col or s.TEXT_PRIMARY),
("K",f"{rec or d.str ikeouts_pitched}",Col or s.PRIMARY),
]
else:
avg=rec or d.batt in g_average
avg_col or=Col or s.WARNING if avg>=0.300else Col or s.SUCCESS if avg>=0.280else Col or s.TEXT_PRIMARY
stats_items=[
("打率",f".{in t(avg*1000): 03d}"if avg>0else".000",avg_col or),
("安打",f"{rec or d.hits}",Col or s.TEXT_PRIMARY),
("HR",f"{rec or d.home_runs}",Col or s.DANGER if rec or d.home_runs>=20else Col or s.TEXT_PRIMARY),
("打点",f"{rec or d.rb is}",Col or s.SUCCESS),
("盗塁",f"{rec or d.sto len _b as es}",Col or s.INFO),
("OPS",f"{rec or d.ops:.3f}"if h as attr(rec or d,'ops') else"-",Col or s.WARNING),
]

x=rec or d_rect.x+15
y=rec or d_rect.y+45
item_width=(rec or d_rect.width-30)//len(stats_items)
f or label,value,col or in stats_items:
label_surf=fonts.t in y.render(label,True,Col or s.TEXT_SECONDARY)
value_surf=fonts.h3.render(value,True,col or)
self.screen.blit(label_surf,(x,y))
self.screen.blit(value_surf,(x,y+18))
x+=item_width

#BACKボタン
buttons["BACK"]=Button(
50,height-70,150,50,
"←BACK","ghost",font=fonts.body
)
buttons["BACK"].draw(self.screen)

To as tManager.update_ and _draw(self.screen)

return buttons

#========================================
#育成ドラフト画面
#========================================
def draw_developmental_draft_screen(self,prospects: L is t,selected_idx: in t=-1,
draft_round: in t=1,draft_messages: L is t[str]=None)->Dict[str,Button]:
"""育成ドラフト画面を描画"""
draw_BACKground(self.screen,"gradient")

width=self.screen.get_width()
height=self.screen.get_height()
center_x=width//2

#ヘッダー（育成は別色）
round_text=f"育成第{draft_round}巡目"
header_h=draw_header(self.screen,f"DEVDRAFT-{round_text}","将来性のある選手を発掘",Col or s.SUCCESS)

buttons={}

#左側: 候補者リスト
card_width=width-320if draft_messages else width-60
card=Card(30,header_h+15,card_width-30,height-header_h-120)
card_rect=card.draw(self.screen)

#ヘッダー行
headers=[("名前",140),("ポジション",90),("年齢",50),("ポテンシャル",90),("総合",70)]
x=card_rect.x+15
y=card_rect.y+18

f or header_text,w in headers:
h_surf=fonts.t in y.render(header_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(h_surf,(x,y))
x+=w

y+=22
pygame.draw.l in e(self.screen,Col or s.BORDER,(card_rect.x+10,y),(card_rect.right-10,y),1)
y+=8

#候補者一覧
v is ible_count=m in(12,len(prospects))

f or i in range(v is ible_count):
prospect=prospects[i]
row_rect=pygame.Rect(card_rect.x+8,y-2,card_rect.width-16,32)

#選択中
if i==selected_idx:
pygame.draw.rect(self.screen,(*Col or s.SUCCESS[: 3],50),row_rect,b or der_radius=4)
pygame.draw.rect(self.screen,Col or s.SUCCESS,row_rect,2,b or der_radius=4)
el if i%2==0:
pygame.draw.rect(self.screen,Col or s.BG_INPUT,row_rect,b or der_radius=3)

x=card_rect.x+15

#名前
name_surf=fonts.small.render(prospect.name[: 8],True,Col or s.TEXT_PRIMARY)
self.screen.blit(name_surf,(x,y+4))
x+=140

#ポジション
pos_text=prospect.position.value[: 2]
if prospect.pitch_type:
pos_text+=f"({prospect.pitch_type.value[0]})"
pos_surf=fonts.t in y.render(pos_text,True,Col or s.TEXT_SECONDARY)
self.screen.blit(pos_surf,(x,y+6))
x+=90

#年齢
age_surf=fonts.small.render(f"{prospect.age}",True,Col or s.TEXT_PRIMARY)
self.screen.blit(age_surf,(x,y+4))
x+=50

#ポテンシャル（星表示、育成は最大3つ）
pot_stars=m in(prospect.potential//3,3)
pot_col or=Col or s.SUCCESS if pot_stars>=2else Col or s.TEXT_SECONDARY
pot_surf=fonts.small.render("*"*pot_stars,True,pot_col or)
self.screen.blit(pot_surf,(x,y+4))
x+=90

#総合力
overall=prospect.stats.overall_batt in g() if prospect.position.value!="投手"else prospect.stats.overall_pitch in g()
overall_surf=fonts.small.render(f"{overall:.0f}",True,Col or s.TEXT_PRIMARY)
self.screen.blit(overall_surf,(x,y+4))

y+=35

#右側: 指名履歴
if draft_messages:
log_card=Card(width-280,header_h+15,250,height-header_h-120,"PICKLOG")
log_rect=log_card.draw(self.screen)

log_y=log_rect.y+42
recent_msgs=draft_messages[-8:]if len(draft_messages)>8else draft_messages
f or msg in recent_msgs:
msg_surf=fonts.t in y.render(msg[: 28],True,Col or s.TEXT_SECONDARY)
self.screen.blit(msg_surf,(log_rect.x+8,log_y))
log_y+=20

#ボタン
btn_y=height-85

buttons["draft_developmental"]=Button(
center_x+30,btn_y,180,50,
"この選手を指名","success",font=fonts.body
)
buttons["draft_developmental"].enabled=selected_idx>=0
buttons["draft_developmental"].draw(self.screen)

buttons["skip_developmental"]=Button(
center_x-210,btn_y,180,50,
"育成ドラフト終了","ghost",font=fonts.body
)
buttons["skip_developmental"].draw(self.screen)

To as tManager.update_ and _draw(self.screen)

return buttons
