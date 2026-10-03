# metopon — 作業メモ（短く保つ。詳しいことは docs/ へ）

8ビット風の縦スクロールシューティング×文字そろえ。ビルド無しの単一 HTML（素の JS、`'use strict'`）。
本線は `xemetous/index.html`。仕様と段取りは `docs/xemetous.md`、素材の出どころは `docs/assets.md`。
ユーザーへの返事と文書は日本語。

## 公開
- `main` に push すると GitHub Pages に出る（https://mukkii-game.github.io/metopon/xemetous/）。
- 作業ブランチで commit → push → `main` に fast-forward で取り込んで push、の順。

## 確かめ方
- `python3 -m http.server 8765` で配信し、Playwright（Python）で見る。
  Chromium は `executable_path='/opt/pw-browsers/chromium'` を指定（playwright install はしない）。
- ゲームの関数は `page.evaluate` から直接呼べる（`reset()`, `update(1/60)`, `makePuzzle()` など）。
  自機を無敵（`ship.inv=1e9`）にして1面を通し、エラーが出ないか・板が重ならないかを見る。

## 素材を作り直す
- 絵：`python3 tools/gen_art.py`、効果音：`python3 tools/gen_sfx.py`
- 声（VOICEVOX:春日部つむぎ）：Docker でエンジンを動かしてから `python3 tools/gen_voice.py`
  ```
  dockerd &   # 動いていなければ
  docker run -d --rm --name vv -p 50021:50021 voicevox/voicevox_engine:cpu-ubuntu20.04-latest
  ```
  言葉を足したら `tools/gen_voice.py` の LIST（言葉・アクセント位置・ファイル名）と、
  `xemetous/index.html` の `VOICE_FILE` の両方に足す。アクセントは東京式で付け直している。

## 決まりごと
- 言葉は3文字から。最初から読めてしまう板は作らない。うんちモードでも性的な言葉（まんこ・おっぱい系）は作れないようにする。
- 素材は使い方の条件を確かめてから使う。クレジットが要るものは画面と `docs/assets.md` に書く。
