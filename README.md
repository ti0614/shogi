# shogi-kifu-analyzer

将棋の棋譜（KIF形式・CSA形式）を読み込み、対局の統計情報を分析するツールです。

## できること

- KIF形式（`.kif`）・CSA形式（`.csa`）の棋譜ファイルをパース
- 盤面をシミュレーションし、各指し手について
  - 駒を取ったか（何を取ったか）
  - 成ったかどうか
  - 打った駒かどうか
  を自動判定
- 対局全体の統計を集計
  - 先手・後手それぞれの指し手数、駒取り数、成り数、打った数
  - 消費時間の平均・最大（何手目か）
  - 最終盤面の駒得点差（簡易評価値）
  - 序盤の指し手一覧
- CLIまたはPythonライブラリとして利用可能

## 使い方（CLI）

```bash
python -m shogi_kifu_analyzer samples/sample_game.kif
python -m shogi_kifu_analyzer samples/sample_game.csa --json
```

## 使い方（ライブラリ）

```python
from shogi_kifu_analyzer import parse_kif_file, GameAnalyzer

game = parse_kif_file("samples/sample_game.kif")
stats = GameAnalyzer().analyze(game)

print(stats.sente.capture_count)   # 先手の駒取り数
print(stats.material_balance_final)  # 最終盤面の駒得点差
print(stats.to_dict())             # JSON化可能な辞書
```

## ディレクトリ構成

```
shogi_kifu_analyzer/
  models.py       # 駒種・指し手・対局データの型定義
  board.py        # 盤面シミュレーター（成り・駒取りの判定）
  kif_parser.py    # KIF形式パーサー
  csa_parser.py    # CSA形式パーサー
  analyzer.py      # 統計分析ロジック
  cli.py           # コマンドラインインターフェース
samples/           # サンプル棋譜（KIF/CSA）
tests/             # pytestによるテスト
```

## テスト

```bash
pip install pytest
pytest
```

## 制限事項

- 合法手判定（駒の動かし方のルールチェック）は行いません。棋譜に書かれた指し手をそのまま盤面に反映します。
- 駒落ち（ハンディキャップ戦）は主要なパターンのみ簡易対応しています。
- 詰み判定や形勢評価（AIによる評価値）は含まれません。より高度な評価が必要な場合は、USI対応エンジン（やねうら王など）との連携を別途検討してください。

## web/ — 将棋エンジン(WASM)デモ

`web/` に、やねうら王のWebAssembly版をブラウザ内で動かし、局面(SFEN)から最善手・評価値を求める最小デモがあります。

```bash
cd web
npm install   # postinstallでエンジンファイルを public/engine/ にコピー
npm run dev
```

- サーバー不要（ブラウザ内で探索が完結）
- COOP/COEPヘッダーが必須（マルチスレッド実行のため。`vite.config.ts` で設定済み）
- 同梱の評価関数は軽量版のため、本番投入時はより強い評価関数への差し替えを検討してください
- ライセンス: やねうら王・shogigroundともにGPL-3.0系です。公開サービスにする場合はソースコード公開義務に注意してください
