# metopon
メテオスとパネポン、そしてゼビウス。

砂漠の上を滑らかに飛び、上空の雑魚を撃って素材を集め、
地上に降りてくる大型ボスの装甲パネルを入れ替えてそろえ、剥がしていく、
8ビット風のシューティング×マッチ3の試作です。

自機も敵もマス単位ではなく実時間で連続的に動きますが、
「今どこを狙っているか」のガイドを出すことで、
アナログ移動のままマス単位で狙った場所を指定できます。

**遊ぶ → https://mukkii-game.github.io/metopon/**

- ルールと設計メモ: [docs/concept.md](docs/concept.md)
- 絵と音の出どころ・作り方: [docs/assets.md](docs/assets.md)

操作: 移動＝アナログパッド／矢印・WASD、A＝Space・Z（連射）、B＝X（地上操作）、C＝Bモード切替

## 公開
`main` へプッシュすると GitHub Actions（[.github/workflows/pages.yml](.github/workflows/pages.yml)）が
GitHub Pages へ自動でデプロイする。ビルドはなく、リポジトリ直下をそのまま配信している。

## 手元で動かす
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
