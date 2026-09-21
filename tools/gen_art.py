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
    if kind == 4:      # 輪
        return [[(11.5 + math.cos(a * math.pi / 18) * 8.5,
                  11.5 + math.sin(a * math.pi / 18) * 8.5) for a in range(37)]]
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
        'shot.png': shot_sprite(),
        'boom.png': boom_sheet(),
        'glyphs.png': glyph_sheet(),
        'slab.png': slab(False),
        'slab_lit.png': slab(True),
        'sand.png': sand_tile(),
    }
    for name, img in made.items():
        save(img, name)
    return made


if __name__ == '__main__':
    made = build()
    # 目視確認用の一覧を一時ディレクトリへ（リポジトリには入れない）
    tmp = tempfile.gettempdir()
    contact_sheet([made['ship.png'], made['enemy1.png'], made['enemy2.png'],
                   made['enemy4.png'], made['shot.png']]).save(os.path.join(tmp, 'metopon_sprites.png'))
    contact_sheet([made['glyphs.png'], made['slab.png'], made['slab_lit.png'],
                   made['sand.png'], made['boom.png']], scale=3).save(os.path.join(tmp, 'metopon_tiles.png'))
    print('プレビュー:', tmp)
