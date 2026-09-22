#!/usr/bin/env python3
"""METOPON 8bit ドット絵ジェネレータ。

無料素材サイトへ到達できない環境のため、ゼビウス風の 8bit スプライトを
自前で生成する。出力は assets/img/*.png（1ドット=1px、表示時に整数倍拡大）。
再生成: python3 tools/gen_art.py
"""
import math, os, tempfile
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'img')

# --- 砂漠パレット（8bit機の色数に寄せて絞る） ---
PAL = {
    '.': (0, 0, 0, 0),
    'o': (26, 20, 14, 255),      # 輪郭／彫り込みの影
    'O': (58, 42, 26, 255),      # 砂の深い影
    'D': (143, 109, 56, 255),    # 砂・暗
    'S': (200, 160, 98, 255),    # 砂・基本
    'H': (236, 209, 150, 255),   # 砂・明
    'W': (250, 238, 205, 255),   # 砂・ハイライト
    'b': (228, 238, 238, 255),   # 機体・明
    'm': (137, 163, 176, 255),   # 機体・中
    'a': (214, 82, 54, 255),     # 赤ライン
    'c': (95, 214, 230, 255),    # 排気
    'R': (206, 62, 52, 255),     # 敵・赤
    'r': (122, 32, 28, 255),
    'L': (255, 176, 150, 255),
    'G': (92, 178, 74, 255),     # 敵・緑
    'g': (40, 96, 38, 255),
    'l': (186, 232, 150, 255),
    'P': (148, 162, 190, 255),   # 敵・鋼
    'p': (72, 84, 110, 255),
    'y': (246, 226, 122, 255),   # 発光
    'n': (72, 36, 102, 255),     # ナス・最暗
    'v': (108, 58, 150, 255),    # ナス・暗
    'V': (152, 94, 198, 255),    # ナス・中
    'U': (198, 152, 232, 255),   # ナス・明
    'K': (232, 186, 74, 255),    # 黄金
    'k': (166, 118, 34, 255),    # 黄金・影
    'B': (58, 106, 192, 255),    # エジプト青
    'b2': (30, 58, 118, 255),    # エジプト青・影
    'N': (26, 24, 30, 255),      # 黒（アヌビス）
    'n2': (58, 54, 66, 255),     # 黒・明
    'F': (238, 236, 228, 255),   # 白布（メジェド）
    'f': (186, 184, 176, 255),   # 白布・影
    'T': (214, 162, 104, 255),   # 砂岩の肌
    't': (168, 118, 68, 255),
    'X': (240, 205, 148, 255),   # スフィンクスの砂色（線画の塗り）
    'x': (214, 176, 122, 255),   # その影
    'M': (166, 102, 46, 255),    # アヌビスの肌
    'Y': (247, 196, 44, 255),    # 黄（腰布・装飾）
    'A': (232, 124, 44, 255),    # 橙（襟）
    'e': (250, 232, 206, 255),   # 白目
}


def from_rows(rows, mirror_x=False, mirror_y=False):
    """文字グリッドから画像を作る。mirror 指定で左右／上下対称に展開。"""
    w = len(rows[0])
    for r in rows:
        assert len(r) == w, f'行の長さが揃っていない: {len(r)} != {w} ({r!r})'
    grid = [list(r) for r in rows]
    if mirror_x:
        grid = [r + r[::-1] for r in grid]
    if mirror_y:
        grid = grid + grid[::-1]
    img = Image.new('RGBA', (len(grid[0]), len(grid)), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            px[x, y] = PAL[ch]
    return img


def save(img, name):
    path = os.path.join(OUT, name)
    img.save(path)
    print(f'{name:14s} {img.width:3d}x{img.height:<3d} {os.path.getsize(path)/1024:5.1f} KB')
    return img


# ---------------------------------------------------------------- 自機
# ゼビウスのソルバルウ風。左半分だけ書いて左右対称に展開する。
SHIP = [
    '.......o',
    '.......o',
    '......ob',
    '......ob',
    '.....oab',
    '.....oab',
    '....ombb',
    '...ommab',
    '..ommmab',
    '.oammmab',
    'oammmmab',
    'oammmmab',
    'oaammmab',
    '.oommmab',
    '...ocmab',
    '....occb',
]

# ---------------------------------------------------------------- 敵 1x1
# トーロイド風の回転リング。四分円を書いて上下左右に展開。
E1 = [
    '.....ooo',
    '...ooRRR',
    '..oRRLLR',
    '.oRRLLRR',
    '.oRLLRro',
    'oRRLRro.',
    'oRRLRo..',
    'oRRLRo..',
]

# ---------------------------------------------------------------- 敵 2x1
# 横長の高速機。左半分を左右対称に展開して 32x16。
E2 = [
    '...............o',
    '..............oG',
    '............oogG',
    '.........ooogGGG',
    '......ooogGGGGll',
    '...oogGGGGGGGlll',
    '.oogGGGGooGGGlll',
    'ogGGGGGoRRoGllll',
    'ogGGGGGoRRoGllll',
    '.oogGGGGooGGGlll',
    '...oogGGGGGGGlll',
    '......ooogGGGGll',
    '.........ooogGGG',
    '............oogG',
    '..............oG',
    '...............o',
]

# ---------------------------------------------------------------- 敵 2x2
def enemy4(n=32):
    """大型母艦。鋼の外殻に赤い環と発光コアを同心に重ねる。"""
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = (n - 1) / 2
    rings = [(15.5, 'o'), (14.5, 'P'), (12.0, 'p'), (11.0, 'P'),
             (8.5, 'o'), (7.5, 'R'), (4.5, 'r'), (3.5, 'L'), (1.5, 'y')]
    for r, col in rings:
        d.ellipse([c - r, c - r, c + r, c + r], fill=PAL[col])
    for a in range(0, 360, 45):          # 外殻のスポーク
        rad = math.radians(a + 22.5)
        d.line([(c + math.cos(rad) * 9, c + math.sin(rad) * 9),
                (c + math.cos(rad) * 14, c + math.sin(rad) * 14)], fill=PAL['p'], width=2)
    for a in range(0, 360, 90):          # 砲座
        rad = math.radians(a)
        x, y = c + math.cos(rad) * 12.5, c + math.sin(rad) * 12.5
        d.rectangle([x - 1.5, y - 1.5, x + 1.5, y + 1.5], fill=PAL['o'])
        d.point((x, y), fill=PAL['R'])
    return img


def zako22(n=32):
    """2x2 の雑魚。ボス（大型母艦）と取り違えないよう、四つ足の角ばった機体にする。"""
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([3, 3, n - 4, n - 4], fill=PAL['o'])
    d.rectangle([4, 4, n - 5, n - 5], fill=PAL['g'])
    d.rectangle([6, 6, n - 7, n - 7], fill=PAL['G'])
    for (x, y) in ((1, 1), (n - 7, 1), (1, n - 7), (n - 7, n - 7)):   # 四隅の推進ポッド
        d.rectangle([x, y, x + 5, y + 5], fill=PAL['o'])
        d.rectangle([x + 1, y + 1, x + 4, y + 4], fill=PAL['l'])
        d.point((x + 2, y + 2), fill=PAL['G'])
    c = (n - 1) / 2
    d.ellipse([c - 4, c - 4, c + 4, c + 4], fill=PAL['o'])            # 目
    d.ellipse([c - 3, c - 3, c + 3, c + 3], fill=PAL['R'])
    d.ellipse([c - 1, c - 1, c + 1, c + 1], fill=PAL['y'])
    return img


def nasu_big(n=64):
    """強力攻撃の「でっかいナス」。地上絵ではなく実体として描く。"""
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = n / 2
    top, bot = 15, n - 2
    for y in range(top, bot):
        f = (y - top) / float(bot - top - 1)
        # 上は細く、下2/3でふくらんで、底で少しすぼまる：ナスの輪郭
        w = 4.0 + 12.5 * math.sin(min(1.0, f * 1.12) * math.pi * 0.78 + 0.30)
        if f > 0.93:
            w *= 1 - (f - 0.93) * 7
        w = max(1.5, w)
        d.line([(cx - w, y), (cx + w, y)], fill=PAL['o'])
        d.line([(cx - w + 2, y), (cx + w - 2, y)], fill=PAL['v'])
        d.line([(cx - w + 3, y), (cx + w - 5, y)], fill=PAL['V'])
    d.line([(cx - 6, 28), (cx - 7, 44)], fill=PAL['U'], width=3)      # 縦のつや
    d.line([(cx - 6, 30), (cx - 7, 41)], fill=PAL['W'], width=1)
    for y in range(bot - 7, bot):                                     # 底の影
        f = (y - (bot - 7)) / 7.0
        w = 15 - f * 12
        d.line([(cx - w, y), (cx + w, y)], fill=PAL['n'])
    for a in (-1, 1):                                                 # へた
        d.polygon([(cx, 11), (cx + a * 13, 12), (cx + a * 7, 21), (cx + a * 2, 18)],
                  fill=PAL['G'], outline=PAL['g'])
    d.polygon([(cx - 5, 10), (cx + 5, 10), (cx + 3, 20), (cx - 3, 20)], fill=PAL['G'], outline=PAL['g'])
    d.rectangle([cx - 2, 2, cx + 1, 12], fill=PAL['g'])               # 軸
    d.line([(cx - 1, 3), (cx - 1, 11)], fill=PAL['l'])
    return img


# --- ボス4体 ---------------------------------------------------------------
# 参考にした絵の雰囲気（太い輪郭＋べた塗り、目が大きくてとぼけた顔）に寄せて
# ドットで描き起こしたもの。素材そのものは使っていない。
# ボスの帯は暗いので、シルエットのまわりに淡いふちを足して浮かせる。
INK = (26, 20, 14, 255)
RIM = (250, 238, 205, 255)


def add_rim(img, col=RIM, w=2):
    """不透明な部分のまわりに淡いふちを足す。暗い体でも形が見えるように。"""
    from PIL import ImageChops, ImageFilter
    a = img.split()[3].point(lambda v: 255 if v > 128 else 0)
    ring = ImageChops.subtract(a.filter(ImageFilter.MaxFilter(2 * w + 1)), a)
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    out.paste(col, (0, 0), ring)
    out.alpha_composite(img)
    return out


def boss_sphinx(n=64):
    """1面：スフィンクス。丸い頭巾に大きな目、寝そべったライオンの体。"""
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 63), (0, 46), (6, 39), (18, 36), (34, 38), (44, 46), (47, 63)],
              fill=PAL['X'])                                        # 尻から胸へ続く胴
    d.polygon([(26, 63), (26, 53), (44, 51), (63, 55), (63, 63)], fill=PAL['X'])  # 前脚
    d.polygon([(13, 24), (15, 9), (23, 1), (41, 1), (49, 9), (51, 24),
               (50, 36), (43, 44), (21, 44), (14, 36)], fill=PAL['X'])  # 頭巾
    d.ellipse([21, 7, 47, 43], fill=PAL['X'], outline=INK, width=2)  # 顔
    d.arc([14, 15, 23, 31], 65, 295, fill=INK, width=2)             # 耳
    for x in (28, 41):                                              # 丸い目（白目・虹彩・瞳）
        d.ellipse([x - 6, 15, x + 6, 27], fill=PAL['e'], outline=INK, width=2)
        d.ellipse([x - 3, 18, x + 3, 24], fill=INK)
        d.point((x - 1, 20), fill=PAL['e'])
    d.arc([30, 1, 38, 11], 195, 345, fill=INK, width=3)             # 額のウラエウス
    d.line([(34, 6), (34, 12)], fill=INK, width=3)
    d.line([(33, 30), (36, 30)], fill=INK, width=2)                 # 鼻
    d.arc([29, 30, 40, 39], 25, 155, fill=INK, width=2)             # 口
    d.line([(26, 53), (26, 63)], fill=INK, width=2)                 # 前脚の割れ目
    d.line([(44, 52), (44, 63)], fill=INK, width=2)
    for x in (52, 57):
        d.line([(x, 56), (x, 63)], fill=PAL['x'], width=1)          # 爪
    d.arc([2, 38, 24, 60], 200, 320, fill=INK, width=2)             # 後ろ脚のふくらみ
    return add_rim(img)


def boss_medjed(n=64):
    """2面：メジェド。白い布からのぞく目と、二本の足だけ。"""
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for a in (-1, 1):                                               # 足
        d.polygon([(32 + a * 14, 46), (32 + a * 5, 46), (32 + a * 7, 60),
                   (32 + a * 19, 60), (32 + a * 16, 53)], fill=PAL['T'], outline=INK, width=2)
    d.polygon([(32, 2), (42, 6), (48, 17), (53, 34), (56, 50), (8, 50),
               (11, 34), (16, 17), (22, 6)], fill=PAL['F'], outline=INK, width=3)  # 白い布
    for a, x in ((-1, 24), (1, 40)):                                # 目
        d.arc([x - 10, 17, x + 10, 31], 190, 350, fill=INK, width=2)   # まぶた
        d.ellipse([x - 7, 22, x + 7, 34], fill=PAL['e'], outline=INK, width=2)
        d.ellipse([x - 4, 24, x + 4, 32], fill=INK)
        d.line([(x + a * 9, 23), (x + a * 13, 20)], fill=INK, width=2)  # まつげ
    return add_rim(img)


def boss_bastet(n=64):
    """3面：バステト。黒猫の頭に黄金の輪と耳飾り、縞の衣。"""
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(19, 46), (45, 46), (51, 63), (13, 63)], fill=PAL['T'])   # 肩
    for a in (-1, 1):                                                    # 耳
        d.polygon([(32 + a * 7, 18), (32 + a * 13, 1), (32 + a * 20, 20)], fill=PAL['n2'])
        d.polygon([(32 + a * 11, 16), (32 + a * 14, 7), (32 + a * 17, 17)], fill=PAL['Y'])
    d.ellipse([13, 11, 51, 47], fill=PAL['n2'])                          # 顔
    d.polygon([(23, 52), (41, 52), (46, 63), (18, 63)], fill=PAL['n2'])  # 縞の衣
    for i in range(-2, 3):
        d.line([(32 + i * 5, 53), (32 + i * 6, 62)], fill=PAL['Y'], width=2)
    d.rectangle([21, 45, 43, 48], fill=PAL['A'])                         # 襟
    d.line([(21, 46), (43, 46)], fill=PAL['e'], width=1)
    d.line([(21, 48), (43, 48)], fill=PAL['B'], width=2)
    d.arc([24, 6, 40, 20], 195, 345, fill=PAL['K'], width=3)             # 額の輪
    d.ellipse([44, 14, 55, 26], outline=PAL['K'], width=3)               # 耳飾り
    for x in (25, 39):                                                   # 目
        d.polygon([(x - 6, 27), (x + 6, 24), (x + 5, 30), (x - 5, 31)], fill=PAL['K'])
        d.ellipse([x - 3, 25, x + 2, 30], fill=INK)
    d.polygon([(29, 32), (35, 32), (32, 36)], fill=PAL['Y'])             # 鼻
    d.arc([25, 34, 32, 41], 0, 140, fill=PAL['Y'], width=2)              # 口
    d.arc([32, 34, 39, 41], 40, 180, fill=PAL['Y'], width=2)
    for a in (-1, 1):                                                    # ひげ
        d.line([(32 + a * 9, 35), (32 + a * 19, 33)], fill=PAL['n2'], width=1)
    return add_rim(img)


def boss_anubis(n=64):
    """4面：アヌビス。黒いジャッカルの頭、青い頭巾と橙の襟。"""
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.line([(6, 18), (6, 63)], fill=INK, width=3)                        # 杖
    d.arc([2, 10, 14, 22], 100, 310, fill=INK, width=3)
    for a in (-1, 1):                                                    # 青い頭巾
        d.polygon([(32 + a * 12, 26), (32 + a * 23, 34), (32 + a * 21, 52),
                   (32 + a * 10, 48)], fill=PAL['B'])
    d.polygon([(18, 52), (46, 52), (52, 63), (12, 63)], fill=PAL['M'])   # 肩
    d.polygon([(21, 57), (43, 57), (48, 63), (16, 63)], fill=PAL['Y'])   # 腰布
    for a in (-1, 1):                                                    # 立った耳
        d.polygon([(32 + a * 5, 22), (32 + a * 8, 1), (32 + a * 16, 21)], fill=PAL['n2'])
        d.polygon([(32 + a * 8, 19), (32 + a * 10, 8), (32 + a * 13, 19)], fill=PAL['B'])
    d.ellipse([17, 12, 47, 40], fill=PAL['n2'])                          # 頭
    d.polygon([(26, 30), (38, 30), (40, 50), (24, 50)], fill=PAL['n2'])  # 鼻面
    d.ellipse([25, 44, 39, 53], fill=PAL['n2'])
    d.ellipse([28, 46, 36, 52], fill=PAL['N'])                           # 鼻先
    d.rectangle([20, 50, 44, 54], fill=PAL['A'])                         # 襟
    d.line([(20, 51), (44, 51)], fill=PAL['Y'], width=2)
    d.line([(20, 54), (44, 54)], fill=PAL['B'], width=2)
    for x in (25, 39):                                                   # 目
        d.polygon([(x - 5, 24), (x + 5, 21), (x + 4, 27), (x - 4, 28)], fill=PAL['e'])
        d.ellipse([x - 2, 22, x + 3, 27], fill=INK)
    return add_rim(img)


def spiral_points(cx, cy, turns, r0, r1, steps=120):
    pts = []
    for i in range(steps + 1):
        f = i / steps
        a = f * turns * 2 * math.pi
        r = r0 + (r1 - r0) * f
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def glyph_paths(kind, n=24):
    """地上ピースの模様。色ではなく『線のバリエーション』で区別する。"""
    if kind == 0:      # 二条線
        return [[(8, 3), (8, 20)], [(15, 3), (15, 20)]]
    if kind == 1:      # 十字
        return [[(3, 11.5), (20, 11.5)], [(11.5, 3), (11.5, 20)]]
    if kind == 2:      # 稲妻（折れ線）
        return [[(4, 4), (17, 9), (6, 14), (19, 19)]]
    if kind == 3:      # 渦
        return [spiral_points(11.5, 11.5, 1.75, 1.5, 9.5)]
    if kind == 4:      # ナスの地上絵（下がふくらんだ実＋へた）
        body = []
        for i in range(41):
            a = i / 40 * 2 * math.pi - math.pi / 2
            rx = 4.3 + 1.7 * math.sin(a)      # 上は細く、下はふくらむ
            body.append((11.5 + math.cos(a) * rx, 14.6 + math.sin(a) * 7.0))
        return [body,
                [(11.5, 7.8), (11.5, 4.2)],                    # へたの軸
                [(11.5, 5.6), (7.6, 3.4)], [(11.5, 5.6), (15.4, 3.4)]]   # へたの葉
    raise ValueError(kind)


def draw_glyph(kind, n=24, groove=True):
    """砂に彫り込まれた線に見えるよう、影の線と明の線を1pxずらして重ねる。"""
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    paths = glyph_paths(kind, n)
    if groove:
        for p in paths:                     # 溝の下側＝反射光
            d.line([(x + 1, y + 1) for x, y in p], fill=PAL['W'], width=3, joint='curve')
    for p in paths:                         # 溝そのもの＝影
        d.line(p, fill=PAL['O'], width=3, joint='curve')
    for p in paths:                         # 芯を一段暗く
        d.line(p, fill=PAL['o'], width=1, joint='curve')
    return img


def glyph_sheet():
    n, count = 24, 5
    sheet = Image.new('RGBA', (n * count, n), (0, 0, 0, 0))
    for k in range(count):
        sheet.paste(draw_glyph(k, n), (k * n, 0))
    return sheet


def slab(lit=False):
    """地上ピースの土台。砂を削り出した石板のような面取り。"""
    n = 24
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    base, top, bot = ('H', 'W', 'D') if lit else ('S', 'H', 'O')
    d.rectangle([0, 0, n - 1, n - 1], fill=PAL[base])
    d.line([(0, 0), (n - 2, 0)], fill=PAL[top])
    d.line([(0, 0), (0, n - 2)], fill=PAL[top])
    d.line([(1, n - 1), (n - 1, n - 1)], fill=PAL[bot])
    d.line([(n - 1, 1), (n - 1, n - 1)], fill=PAL[bot])
    # 砂のざらつき（決め打ちのディザで模様が毎回同じになるように）
    for y in range(2, n - 2):
        for x in range(2, n - 2):
            if (x * 7 + y * 13) % 23 == 0:
                d.point((x, y), fill=PAL[top])
            elif (x * 5 + y * 3) % 29 == 0:
                d.point((x, y), fill=PAL[bot])
    return img


def sand_tile(n=64):
    """縦横につながる砂漠の地面。強い模様ではなく、浅い風紋と小石だけ。"""
    img = Image.new('RGBA', (n, n), PAL['D'])
    d = ImageDraw.Draw(img)
    tone = [(118, 90, 48, 255), (132, 101, 54, 255), PAL['D'], (158, 122, 64, 255)]
    for y in range(n):
        for x in range(n):
            # 横に流れる浅いうねり＋細かい粒
            v = math.sin((x / n) * 2 * math.pi * 2 + math.sin((y / n) * 2 * math.pi) * 2.2)
            v = v * 0.5 + 0.5
            i = int(v * 3.99)
            if (x * 5 + y * 11) % 17 == 0:
                i = min(3, i + 1)
            elif (x * 3 + y * 7) % 19 == 0:
                i = max(0, i - 1)
            d.point((x, y), fill=tone[i])
    for (x, y) in ((11, 9), (40, 21), (25, 47), (55, 56), (6, 35)):   # 小石
        d.rectangle([x, y, x + 2, y + 1], fill=PAL['O'])
        d.point((x, y), fill=PAL['S'])
    return img


def boom_sheet(frames=5, n=24):
    """爆発。外へ広がるドットのリングと、縮んでいく芯。"""
    sheet = Image.new('RGBA', (n * frames, n), (0, 0, 0, 0))
    ring = ['W', 'y', 'a', 'R', 'r']
    core = ['W', 'W', 'y', 'a', 'r']
    for f in range(frames):
        img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        r = 3 + f * 2.1
        for a in range(0, 360, 9):
            rad = math.radians(a + f * 13)
            jitter = 1.6 if (a // 9) % 2 else 0
            x = round((n / 2 + math.cos(rad) * (r + jitter)) / 2) * 2
            y = round((n / 2 + math.sin(rad) * (r + jitter)) / 2) * 2
            d.rectangle([x - 1, y - 1, x, y], fill=PAL[ring[f]])
        cr = 5 - f
        if cr > 0:
            d.rectangle([n / 2 - cr, n / 2 - cr, n / 2 + cr - 1, n / 2 + cr - 1], fill=PAL[core[f]])
        sheet.paste(img, (f * n, 0))
    return sheet


def shot_sprite():
    img = Image.new('RGBA', (4, 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([1, 0, 2, 11], fill=PAL['y'])
    d.rectangle([0, 2, 3, 8], fill=PAL['a'])
    d.rectangle([1, 3, 2, 7], fill=PAL['W'])
    return img


def app_icon(kind=3, blast=False, push=False, n=64):
    """ホーム画面に追加した時のアイコン。64pxのドット絵を整数倍に拡大して使う。"""
    img = sand_tile(n)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, n - 1, n - 1], outline=PAL['o'], width=3)
    d.rectangle([3, 3, n - 4, n - 4], outline=PAL['S'], width=1)
    if push:
        # レーンを押し上げる、という図
        for (x, y) in ((14, 34), (32, 34), (14, 50), (32, 50)):
            d.rectangle([x, y, x + 16, y + 14], fill=PAL['S'], outline=PAL['O'], width=2)
        d.polygon([(32, 8), (46, 24), (37, 24), (37, 30), (27, 30), (27, 24), (18, 24)],
                  fill=PAL['W'], outline=PAL['o'])
        d.rectangle([12, 26, 52, 28], fill=PAL['O'])
    elif blast:
        # 四角を上へ撃ち返す、という図
        for (x, y) in ((16, 30), (34, 30), (16, 48), (34, 48)):
            d.rectangle([x, y, x + 14, y + 14], fill=PAL['S'], outline=PAL['O'], width=2)
        d.polygon([(32, 8), (48, 26), (38, 26), (38, 30), (26, 30), (26, 26), (16, 26)],
                  fill=PAL['W'], outline=PAL['o'])
    else:
        g = draw_glyph(kind, 24).resize((48, 48), Image.NEAREST)
        img.paste(g, (8, 8), g)
    return img


def contact_sheet(images, scale=4):
    """目視確認用の一覧（リポジトリには入れない）。"""
    pad = 6
    w = sum(i.width * scale + pad for i in images) + pad
    h = max(i.height * scale for i in images) + pad * 2
    out = Image.new('RGBA', (w, h), (18, 14, 10, 255))
    x = pad
    for i in images:
        big = i.resize((i.width * scale, i.height * scale), Image.NEAREST)
        out.paste(big, (x, pad), big)
        x += big.width + pad
    return out


def build():
    os.makedirs(OUT, exist_ok=True)
    made = {
        'ship.png': from_rows(SHIP, mirror_x=True),
        'enemy1.png': from_rows(E1, mirror_x=True, mirror_y=True),
        'enemy2.png': from_rows(E2, mirror_x=True),
        'enemy4.png': enemy4(),
        'zako22.png': zako22(),
        'nasu.png': nasu_big(),
        'boss1.png': boss_sphinx(),
        'boss2.png': boss_medjed(),
        'boss3.png': boss_bastet(),
        'boss4.png': boss_anubis(),
        'shot.png': shot_sprite(),
        'boom.png': boom_sheet(),
        'glyphs.png': glyph_sheet(),
        'slab.png': slab(False),
        'slab_lit.png': slab(True),
        'sand.png': sand_tile(),
        'icon-192.png': app_icon().resize((192, 192), Image.NEAREST),
        'icon-512.png': app_icon().resize((512, 512), Image.NEAREST),
        'icon-blast-192.png': app_icon(blast=True).resize((192, 192), Image.NEAREST),
        'icon-blast-512.png': app_icon(blast=True).resize((512, 512), Image.NEAREST),
        'icon-push-192.png': app_icon(push=True).resize((192, 192), Image.NEAREST),
        'icon-push-512.png': app_icon(push=True).resize((512, 512), Image.NEAREST),
    }
    for name, img in made.items():
        save(img, name)
    return made


if __name__ == '__main__':
    made = build()
    # 目視確認用の一覧を一時ディレクトリへ（リポジトリには入れない）
    tmp = tempfile.gettempdir()
    contact_sheet([made['ship.png'], made['enemy1.png'], made['enemy2.png'],
                   made['boss1.png'], made['boss2.png'], made['boss3.png'], made['boss4.png'],
                   made['nasu.png']]).save(os.path.join(tmp, 'metopon_sprites.png'))
    contact_sheet([made['glyphs.png'], made['slab.png'], made['slab_lit.png'],
                   made['sand.png'], made['boom.png']], scale=3).save(os.path.join(tmp, 'metopon_tiles.png'))
    print('プレビュー:', tmp)
