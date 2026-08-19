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

## web/ — ブラウザ内でエンジンと対局できるデモ

`web/` に、やねうら王のWebAssembly版をブラウザ内で動かし、実際に駒を動かして対局できるデモがあります。

- 盤面UI: [shogiground](https://github.com/WandererXII/shogiground)（lishogi.orgで使われている標準的な将棋盤UI）
- ルール処理（合法手生成・成り・詰み判定など）: [shogiops](https://github.com/WandererXII/shogiops)
- 思考エンジン: やねうら王 WebAssembly版（Web Worker上で動作）

```bash
cd web
npm install   # postinstallでエンジンファイルを public/engine/ にコピー
npm run dev
```

- サーバー不要（ブラウザ内で探索・対局が完結）
- COOP/COEPヘッダーが必須（マルチスレッド実行のため）
- 同梱の評価関数は軽量版のため、本番投入時はより強い評価関数への差し替えを検討してください
- 盤・駒の画像は `public/theme/`（shogigroundの標準テーマ）を使用。詳細は `public/theme/NOTICE.md` を参照
- ライセンス: やねうら王・shogiground・shogiopsはいずれもGPL-3.0系です。公開サービスにする場合はソースコード公開義務に注意してください

### 公開先について（Claude Artifact / GitHub Pages）

このデモはマルチスレッド実行のため`SharedArrayBuffer`が必須で、それには`Cross-Origin-Opener-Policy`/`Cross-Origin-Embedder-Policy`ヘッダーが必要です。

- **Claude Artifact**: ヘッダーを外部から設定できないため**動作しません**（実機検証済み）。
- **GitHub Pages（素）**: 同様にヘッダーを設定できないため動きません。
- **GitHub Pages + coi-serviceworker**: 採用している方式です。[coi-serviceworker](https://github.com/gzuidhof/coi-serviceworker)（MIT License）というService Workerが、ページ読み込み時にクライアント側でCOOP/COEPヘッダーを擬似的に付与し、`crossOriginIsolated`を有効化します。初回アクセス時のみ有効化のための自動リロードが1回入ります。`index.html` から読み込んでいます（`public/coi-serviceworker.js`）。
- **Netlify/Vercel/Cloudflare Pages**: レスポンスヘッダーを設定できるホスティング先なら、coi-serviceworkerなしでも素直に動きます。

### GitHub Pagesへのデプロイ

`.github/workflows/deploy-web.yml` により、`main`ブランチへの`web/`配下の変更をトリガーにGitHub Pagesへ自動デプロイされます。利用するには、リポジトリの Settings → Pages → Source を「GitHub Actions」に設定してください。デプロイ先は `https://<owner>.github.io/shogi/` です（`vite.config.ts` の `base` をリポジトリ名に合わせています）。
