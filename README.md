# metopon
メテオスとパネポン、そしてゼビウス。

砂漠の上を滑らかに飛び、上空の雑魚を撃って素材を集め、
地上に降りてくる大型ボスの装甲パネルを入れ替えてそろえ、剥がしていく、
8ビット風のシューティング×マッチ3の試作です。

自機も敵もマス単位ではなく実時間で連続的に動きますが、
「今どこを狙っているか」のガイドを出すことで、
アナログ移動のままマス単位で狙った場所を指定できます。

## 四つの試作

| | 遊ぶ | 中身 |
| --- | --- | --- |
| **本編** | https://mukkii-game.github.io/metopon/ | 滑らかに飛んで上空の雑魚を撃ち、地上のボスの装甲パネルをそろえて剥がす |
| **別案 BLAST** | https://mukkii-game.github.io/metopon/blast/ | 下から撃ち込んで四角を作り、その四角をそのまま天井のボスへ撃ち返す |
| **第三案 XEMETOUS** | https://mukkii-game.github.io/metopon/push/ | 盤面の下の広場を動いて弾でレーンを押し、編隊を全滅させてもらった枠で組み替え、そろえた塊をボスへ撃ち上げる。全4面・1面あたり2分のタイムアタック |
| **第四案 XEMETOUS BLASTER** | https://mukkii-game.github.io/metopon/blaster/ | ゼビウス風に自由に飛ぶ。通常弾は自動、地上攻撃の照準で地上の並びをひっくり返してそろえる。カプセルで照準が5マスまで伸びる。全4面 |

- ルールと設計メモ: [docs/concept.md](docs/concept.md)
- 別案のルールと設計メモ: [docs/blast.md](docs/blast.md)
- 第三案のルールと設計メモ: [docs/push.md](docs/push.md)
- 第四案のルールと設計メモ: [docs/blaster.md](docs/blaster.md)
- 絵と音の出どころ・作り方: [docs/assets.md](docs/assets.md)

操作: 移動＝アナログパッド／矢印・WASD、A＝Space・Z（連射）、B＝X（地上操作）、C＝Bモード切替

## スマホで遊ぶ
全画面で起動し、画面端のシステムジェスチャー・引っぱって更新・長押しメニュー・
ダブルタップ拡大を抑止している。遊んでいる間は画面が消えない。

- **Android / PC** … 「あそぶ」を押した時点で自動的に全画面になる。上部の「全画面」でも切替。
- **iPhone** … Safari に全画面APIが無いので、**共有 →「ホーム画面に追加」**で全画面になる
  （manifest と apple-touch-icon を置いてある）。画面にも案内を出す。

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
