# HANDOFF — metopon（ナスの地上絵）

## 全体に共有したい気づき
- VOICEVOX をローカル(Windows)で動かす：公式 GitHub `VOICEVOX/voicevox_engine` の Releases から `voicevox_engine-windows-cpu-0.25.2.vvpp`（中身は zip、約1.9GB）を `gh release download` で取り、`G:\マイドライブ\ai	oolsoicevox\engine\` に展開して `run.exe --host 127.0.0.1 --port 50021` で起動（`/version` が `"0.25.2"` を返せば OK。Docker もアプリも不要）。
