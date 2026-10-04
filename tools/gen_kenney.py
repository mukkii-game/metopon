"""Kenney「Pixel Shmup」(CC0) から、ナスの地上絵で使う絵だけを切り出して assets/img/ に並べる。

使い方:
  1. https://kenney.nl/assets/pixel-shmup から kenney_pixel-shmup.zip を落として展開する
  2. python tools/gen_kenney.py <展開したフォルダ>

書き出すもの（どれも 1ドット＝1px。表示側で整数倍に近い大きさへ拡大する）:
  kenney_ships.png  32×32 を横に5コマ：自機 / リング / 円盤 / 箱 / 翼（敵は下向きに180°回した）
  kenney_tiles.png  16×16 を横に4コマ：要塞の砲台 / 壊れた跡 / Pの塔 / 地上の砲台
  kenney_boss.png   120×63：要塞インドアジェネシスの船体（八角形の台に灰色の大型機を載せた合成。
                    中央のコアと四隅の砲台はゲーム側で上に重ねて描く）
  kenney_plate.png  16×16 を横に2コマ：回る板（バキュラ）の表＝Tiles/tile_0016 ／ 裏＝同じ絵を Kenney の灰色で一段暗くしたもの
  kenney_pyramid.png 20×20：ピラミッド。Kenney の茶色の地面（tile_0116/0117）の色で、真上から見た四角すいを描いた合成（18×18＋右下の影2px）
  kenney_ground.png 160×256：砂地。茶色の地面タイル（tile_0116）を 10×16 に敷き、向きを変えて変化を付け、
                    ときどき tile_0117（丸い跡）を混ぜたもの。上下左右につながる（ゲーム側で3倍にして流す）
"""
import os
import random
import sys

from PIL import Image, ImageDraw

SRC = sys.argv[1] if len(sys.argv) > 1 else 'kenney_pixel-shmup'
OUT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'img')

SHIPS = [(0, False), (10, True), (9, True), (11, True), (5, True)]   # (番号, 下向きにするか)
TILES = [16, 8, 25, 17]

# Kenney の灰色の色（ship_0014 から拾った）
OUTLINE = (67, 74, 95, 255)
G1 = (117, 123, 154, 255)
G2 = (149, 154, 177, 255)
G3 = (175, 179, 197, 255)
G4 = (220, 225, 231, 255)


def ship(n):
    return Image.open(os.path.join(SRC, 'Ships', f'ship_{n:04d}.png')).convert('RGBA')


def tile(n):
    return Image.open(os.path.join(SRC, 'Tiles', f'tile_{n:04d}.png')).convert('RGBA')


def octagon(d, cx, cy, w, h, k, fill):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2 - 1, cy + h / 2 - 1
    d.polygon([(x0 + k, y0), (x1 - k, y0), (x1, y0 + k), (x1, y1 - k), (x1 - k, y1), (x0 + k, y1), (x0, y1 - k), (x0, y0 + k)], fill=fill)


# 灰色を一段ずつ暗くする対応（回る板の裏側）
DARKER = {G4[:3]: G2[:3], G2[:3]: G1[:3], OUTLINE[:3]: (40, 44, 60)}


def plate():
    front = tile(16)
    back = front.copy()
    px = back.load()
    for y in range(16):
        for x in range(16):
            r, g, b_, a = px[x, y]
            if a == 0:
                continue
            if (r, g, b_) == (0, 0, 0):                    # 真ん中の黒い溝も少しだけ持ち上げる
                px[x, y] = (24, 26, 36, a)
            elif (r, g, b_) in DARKER:
                px[x, y] = DARKER[(r, g, b_)] + (a,)
    sheet = Image.new('RGBA', (32, 16))
    sheet.paste(front, (0, 0))
    sheet.paste(back, (16, 0))
    sheet.save(os.path.join(OUT, 'kenney_plate.png'))


# Kenney の茶色の地面の色（tile_0116/0117/0115 から拾った）
B_DARK = (180, 114, 83, 255)
B_MID = (203, 129, 94, 255)
B_LIGHT = (224, 142, 103, 255)
B_HI = (244, 172, 102, 255)
B_SHADE = (150, 92, 68, 255)        # 影の面だけ、茶色をもう一段暗くした色
INK = (52, 45, 50, 255)             # 輪郭（Kenney の家の輪郭 52,85,81 より暗めの焦げ茶寄り）
GOLD = (255, 189, 32, 255)          # てっぺん（tile_0000 の金色）


def pyramid():
    N = 18
    im = Image.new('RGBA', (N + 2, N + 2))
    d = ImageDraw.Draw(im)
    d.rectangle([2, 2, N + 1, N + 1], fill=(40, 24, 16, 110))   # 右下に落ちる影（砂地から浮かせる）
    c, lo, hi = (N - 1) / 2, 1, N - 2
    d.rectangle([0, 0, N - 1, N - 1], fill=INK)
    d.polygon([(lo, lo), (hi, lo), (c, c)], fill=B_HI)       # 北：光が当たる
    d.polygon([(lo, lo), (lo, hi), (c, c)], fill=B_LIGHT)    # 西
    d.polygon([(hi, lo), (hi, hi), (c, c)], fill=B_DARK)     # 東
    d.polygon([(lo, hi), (hi, hi), (c, c)], fill=B_SHADE)    # 南：影
    d.line([(lo, lo), (hi, hi)], fill=INK)                   # 稜線
    d.line([(hi, lo), (lo, hi)], fill=INK)
    for k in (4, 7):                                          # 石を積んだ段
        d.line([(lo + k, lo + k), (hi - k, lo + k)], fill=B_LIGHT)
        d.line([(lo + k, hi - k), (hi - k, hi - k)], fill=B_DARK)
    d.rectangle([c - 1, c - 1, c + 1, c + 1], fill=GOLD)    # てっぺんの金
    im.save(os.path.join(OUT, 'kenney_pyramid.png'))


def ground():
    rnd = random.Random(7)                                   # 毎回同じ並びになるように
    base, mark = tile(116), tile(117)
    variants = [base, base.transpose(Image.FLIP_LEFT_RIGHT), base.transpose(Image.FLIP_TOP_BOTTOM), base.rotate(90), base.rotate(180)]
    cols, rows = 10, 16
    g = Image.new('RGBA', (16 * cols, 16 * rows))
    for r in range(rows):
        for c in range(cols):
            t = mark if rnd.random() < .035 else rnd.choice(variants)
            g.paste(t, (c * 16, r * 16))
    g.save(os.path.join(OUT, 'kenney_ground.png'))


def main():
    sheet = Image.new('RGBA', (32 * len(SHIPS), 32))
    for i, (n, flip) in enumerate(SHIPS):
        im = ship(n)
        sheet.paste(im.rotate(180) if flip else im, (i * 32, 0))
    sheet.save(os.path.join(OUT, 'kenney_ships.png'))

    ts = Image.new('RGBA', (16 * len(TILES), 16))
    for i, n in enumerate(TILES):
        ts.paste(tile(n), (i * 16, 0))
    ts.save(os.path.join(OUT, 'kenney_tiles.png'))

    W, H = 120, 63
    b = Image.new('RGBA', (W, H))
    d = ImageDraw.Draw(b)
    cx, cy = W / 2, H / 2
    octagon(d, cx, cy, W, H, 17, OUTLINE)
    octagon(d, cx, cy, W - 4, H - 4, 16, G2)
    octagon(d, cx, cy, W - 22, H - 16, 12, G1)
    octagon(d, cx, cy, W - 36, H - 28, 8, G3)
    for x in (10, W - 11):                                  # 側面の溝
        d.line([(x, 15), (x, H - 16)], fill=OUTLINE)
        d.line([(x + 1, 15), (x + 1, H - 16)], fill=G4)
    for x in range(30, W - 29, 10):                          # 鋲
        d.point([(x, 3), (x, H - 4)], fill=G4)
    core = ship(14).rotate(180)                              # 中央に載せる灰色の大型機（下向き）
    b.alpha_composite(core, (int(cx) - 16, int(cy) - 16))
    b.save(os.path.join(OUT, 'kenney_boss.png'))

    plate()
    pyramid()
    ground()
    print('ok')


if __name__ == '__main__':
    main()
