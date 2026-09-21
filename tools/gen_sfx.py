#!/usr/bin/env python3
"""METOPON 8bit SE generator.

効果音ラボ等の配布サイトへ到達できない環境のため、同種の効果音を
矩形波／ノイズで自作する。出力は assets/sfx/*.wav（22050Hz 8bit mono）。
再生成: python3 tools/gen_sfx.py
"""
import math, os, wave
import numpy as np

SR = 22050
OUT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'sfx')

def n(sec):
    return max(1, int(SR * sec))

def t(sec):
    return np.arange(n(sec)) / SR

def env(sec, attack=0.004, curve=4.0):
    x = np.linspace(0, 1, n(sec))
    a = np.clip(x / max(attack / sec, 1e-6), 0, 1)
    return a * (1 - x) ** curve

def square(freq, sec, duty=0.5):
    """freq: float or (start, end) glide."""
    if isinstance(freq, tuple):
        f = np.linspace(freq[0], freq[1], n(sec))
    else:
        f = np.full(n(sec), float(freq))
    phase = np.cumsum(f) / SR
    return np.where((phase % 1.0) < duty, 1.0, -1.0)

def triangle(freq, sec):
    f = np.linspace(*freq, n(sec)) if isinstance(freq, tuple) else np.full(n(sec), float(freq))
    phase = np.cumsum(f) / SR % 1.0
    return 4 * np.abs(phase - 0.5) - 1

def noise(sec, seed=0, step=1):
    """step>1 で粗い（低いサンプルレートの）ノイズ = ファミコンのノイズch風。"""
    rng = np.random.default_rng(seed)
    raw = rng.uniform(-1, 1, size=n(sec) // step + 1)
    return np.repeat(raw, step)[:n(sec)]

def blip(freq, sec, duty=0.5, curve=3.0, gain=1.0):
    return square(freq, sec, duty) * env(sec, curve=curve) * gain

def seq(notes, sec, duty=0.5, gain=1.0):
    """notes を等分割して並べたアルペジオ。"""
    each = sec / len(notes)
    return np.concatenate([blip(f, each, duty, curve=1.6, gain=gain) for f in notes])

def cat(*parts):
    return np.concatenate([p for p in parts])

def save(name, sig, peak=0.85):
    sig = np.asarray(sig, dtype=np.float64)
    m = np.max(np.abs(sig))
    if m > 0:
        sig = sig / m * peak
    # 8bit 量子化でわざとザラつかせる
    data = np.clip(np.round(sig * 127) + 128, 0, 255).astype(np.uint8)
    path = os.path.join(OUT, name)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    return path, len(data)


def build():
    os.makedirs(OUT, exist_ok=True)
    out = {}

    # 自機ショット（ザッパー）: 高音から一気に落ちる矩形波
    out['shot.wav'] = square((1500, 420), 0.055, 0.25) * env(0.055, curve=2.5)

    # 弾が当たった（撃破前のヒット）: 短いノイズ
    out['hit.wav'] = noise(0.045, seed=1, step=2) * env(0.045, curve=3.0)

    # 小型機の爆発
    out['boom_s.wav'] = (noise(0.22, seed=2, step=3) * env(0.22, curve=2.2)
                         + square((180, 60), 0.22, 0.5) * env(0.22, curve=3.0) * 0.35)

    # 大型機の爆発
    out['boom_l.wav'] = (noise(0.46, seed=3, step=5) * env(0.46, curve=1.8)
                         + square((120, 38), 0.46, 0.5) * env(0.46, curve=2.2) * 0.5)

    # ピース獲得（NEXT にストック）
    out['pickup.wav'] = seq([784, 1047, 1319], 0.16, duty=0.25)

    # 地上：入れ替え
    out['swap.wav'] = cat(blip(660, 0.035, 0.125, curve=2.0), blip(880, 0.045, 0.125, curve=2.0))

    # 地上：配置（ずしっと置く）
    out['place.wav'] = (square((320, 150), 0.1, 0.5) * env(0.1, curve=2.5)
                        + noise(0.1, seed=4, step=4) * env(0.1, curve=4.0) * 0.5)

    # 成立（消去待ちに入った合図）
    out['match.wav'] = seq([523, 659, 784], 0.18, duty=0.5)

    # 消去 = 3直線
    out['clear.wav'] = seq([784, 988, 1175, 1568], 0.26, duty=0.25)

    # 消去 = 2x2
    out['sq2.wav'] = cat(seq([659, 831, 988], 0.18, duty=0.5),
                         blip(1319, 0.16, 0.25, curve=1.2))

    # 消去 = 3x3（大物）
    out['sq3.wav'] = cat(seq([523, 659, 784, 1047], 0.28, duty=0.5),
                         seq([1319, 1568], 0.16, duty=0.25),
                         triangle((1568, 1568), 0.22) * env(0.22, curve=1.0))

    # 連鎖（再生時に playbackRate で音程を上げる）
    out['chain.wav'] = square((880, 1320), 0.1, 0.25) * env(0.1, curve=1.5)

    # 置けない／素材なし
    out['deny.wav'] = square((160, 120), 0.14, 0.5) * env(0.14, curve=1.5)

    # カーソル移動（自機のマス移動）
    out['move.wav'] = blip(1046, 0.022, 0.125, curve=4.0, gain=0.5)

    # ボス接近の警報
    out['warn.wav'] = cat(*[blip(f, 0.12, 0.5, curve=0.9) for f in (740, 494, 740, 494)])

    # ボス撃破
    out['bossdown.wav'] = cat(noise(0.5, seed=5, step=6) * env(0.5, curve=1.4),
                              seq([392, 523, 659, 784], 0.32, duty=0.5),
                              blip(1047, 0.4, 0.25, curve=0.8))

    # スタートのジングル
    out['start.wav'] = cat(seq([392, 523, 659], 0.21, duty=0.5),
                           blip(784, 0.12, 0.25, curve=1.4),
                           blip(1047, 0.26, 0.25, curve=1.0))

    total = 0
    for name, sig in sorted(out.items()):
        path, size = save(name, sig)
        total += size
        print(f'{name:12s} {size/1024:6.1f} KB  {size/SR:4.2f}s')
    print(f'{"合計":12s} {total/1024:6.1f} KB')


if __name__ == '__main__':
    build()
