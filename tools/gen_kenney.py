"""Kenney「Pixel Shmup」(CC0) から、ナスの地上絵で使う絵だけを切り出して assets/img/ に並べる。

使い方:
  1. https://kenney.nl/assets/pixel-shmup から kenney_pixel-shmup.zip を落として展開する
  2. python tools/gen_kenney.py <展開したフォルダ>

書き出すもの（どれも 1ドット＝1px。表示側で整数倍に近い大きさへ拡大する）:
  kenney_ships.png  32×32 を横に5コマ：自機 / リング / 円盤 / 箱 / 翼（敵は下向きに180°回した）
  kenney_tiles.png  16×16 を横に4コマ：要塞の砲台 / 壊れた跡 / Pの塔 / 地上の砲台
  kenney_boss.png   120×63：要塞インドアジェネシスの船体（八角形の台に灰色の大型機を載せた合成。
                    中央のコアと四隅の砲台はゲーム側で上に重ねて描く）
"""
import os
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
    print('ok')


if __name__ == '__main__':
    main()
