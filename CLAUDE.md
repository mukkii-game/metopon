# metopon — 作業メモ（短く保つ。詳しいことは docs/ へ）

いまの本線は **「ナスの地上絵」パイロット版**（`xemetous/index.html`、URL のフォルダ名は xemetous のまま）。
8ビット風の縦スクロールシューティング×文字そろえ（パズドラ式）。ビルド無しの単一 HTML（素の JS、`'use strict'`）。
仕様は `docs/xemetous.md`、素材の出どころとクレジットは `docs/assets.md`。ユーザーへの返事と文書は日本語。
ほかのフォルダ（root, blast/, push/, blaster/, versions/）は前の試作で、触らない。

## 公開
- `main` に push すると GitHub Pages に出る（https://mukkii-game.github.io/metopon/xemetous/）。
- 作業ブランチ `claude/zebius-match3-game-r1ozjp` で commit → push → `main` に fast-forward で取り込んで push。

## 確かめ方
- `python3 -m http.server 8765` で配信し、Playwright（Python）で見る（クラウドでは Chromium を
  `executable_path='/opt/pw-browsers/chromium'` で指定。ローカルなら普通に `playwright install chromium`）。
- ゲームの関数は `page.evaluate` から直接呼べる（`reset()`, `update(1/60)`, `makePuzzle()`, `startBoss()` など）。
  自機を無敵（`ship.inv=1e9`）にして1面を通し、エラーが出ないか・板が重ならないかを見る。
- 大きく書き換えたら、`<script>` の中身を取り出して `node --check` で文法を確かめる（壊すと画面が出ない）。
- 台本 `areaScript()` は時刻順に並べ替えてから実行する（書いた順は自由）。

## 素材を作り直す
- 声：VOICEVOX エンジンを動かしてから `python3 tools/gen_voice.py`（assets/voice/*.wav を全部書き出す）
  ```
  docker run -d --rm --name vv -p 50021:50021 voicevox/voicevox_engine:cpu-ubuntu20.04-latest
  ```
  （クラウドでは先に `dockerd &`。ローカルなら VOICEVOX アプリを起動しておくだけでもよい。ポート 50021）
  - 女の子＝春日部つむぎ（speaker 8）。ボスの名乗り＝青山龍星（speaker 13）。
  - 言葉を足したら `tools/gen_voice.py` の LIST（言葉・アクセント位置・ファイル名）と `xemetous/index.html` の `VOICE_FILE` の両方に。
  - アクセントはエンジン任せにせず、東京式の決まりで高さを付け直している（0＝平板、1＝頭高、n＝n拍目の後で下がる）。
    確認済み：うんこ・うんち・ちんちん・ちんこ＝頭高、おちんちん・おちんこ＝2、おにぎり＝2、ごりら＝1、
    こいぬ・こねこ・すいか・りんご・さかな・きりん・いるか・おうち＝0。ユーザーは耳で確かめて直してくる。
- 出てくる物の絵：Twemoji（npm の @twemoji/svg）を `assets/img/items.png` に並べたもの。
- 効果音・BGM：魔王魂（https://maou.audio/）。ファイルは各曲のページを Referer にしないと 403
  （`curl -A Mozilla/5.0 -H "Referer: https://maou.audio/se_8bit21/" https://maou.audio/sound/se/maou_se_8bit21.wav`）。
  名前に説明が無いので、スペクトログラムや和音を調べて選んだ（docs/assets.md に対応表）。
- ロゴ：`tools/logo_nasu.html` をブラウザで描いて `assets/img/logo_nasu.png` に。
- 古い合成の絵と音は `tools/gen_art.py`・`tools/gen_sfx.py`（前の試作用）。

## 決まりごと
- 言葉は3文字から。最初から読めてしまう板は作らない。うんちモードでも性的な言葉（まんこ・おっぱい系）は作れないようにする。
- 素材は使い方の条件を確かめてから使う。クレジットが要るものは画面（`CREDIT` とタイトルの credit）と `docs/assets.md` に書く。
- ユーザーは音声入力でひらがな混じりの短い指示を出す。分かりにくい時は直前の流れから読み取り、勝手に大きく変えない。

## まだ決まっていないこと
- 生まれたキャラごとの役割（今はどれも同じ働きで、威力と HP だけ違う）。ユーザーと相談して決める。
- 地面（砂）とピラミッドの絵はまだ前の自作のまま。自機・空の敵・砲台・Pの塔・ボスは Kenney「Pixel Shmup」（CC0）に差し替えた
  （`python tools/gen_kenney.py <展開したzip>` で assets/img/kenney_*.png を作り直す。読めない時は前の自作の絵で描く）。
- 女の子の絵はコードで描いたちびキャラ（画像生成AIの絵は不評で戻した）。
