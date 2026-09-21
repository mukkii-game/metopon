# metopon
メテオスとパネポン、そしてゼビウス。

砂漠の上を飛びながら空の敵を撃ち、撃ち落とした素材で地上の模様をそろえて消す、
8ビット風のシューティング×マッチ3の試作です。

- 遊ぶ: `index.html`（単一ファイル）
- ルールと設計メモ: [docs/concept.md](docs/concept.md)
- 絵と音の出どころ・作り方: [docs/assets.md](docs/assets.md)

## 動かす
音は WAV を `fetch` で読むため、HTTP で配信してください。

```
python3 -m http.server 8000     # → http://localhost:8000/
```

`file://` で直接開いても遊べますが、効果音は合成音のフォールバックになります。

## 素材を作り直す
```
pip install numpy pillow
python3 tools/gen_art.py        # assets/img/*.png
python3 tools/gen_sfx.py        # assets/sfx/*.wav
```
