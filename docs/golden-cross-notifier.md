# 📈 Golden Cross Notifier

株探 (kabutan) からゴールデンクロス系シグナル銘柄を**テーマ別**に抽出し、
GitHub Issue として通知する仕組みです。

## 仕組み

- `.github/workflows/golden-cross.yml` … 定期実行ワークフロー
- `scripts/fetch_golden_cross.py` … kabutan をスクレイプして Issue 本文を生成

## 実行タイミング

- 毎日 **08:00 JST** と **16:00 JST**（cron）
- 手動実行も可（Actions タブ → Golden Cross Notifier → Run workflow）

> ⚠️ `schedule` トリガーは**デフォルトブランチ (main)** でのみ動作します。
> 定期実行を有効にするには、このブランチを main にマージしてください。
> マージ前でも `workflow_dispatch`（手動実行）で任意ブランチでテストできます。

## 抽出テーマ

| テーマ | データ元 |
|---|---|
| 5日×25日 ゴールデンクロス | `kabutan.jp/warning/?mode=6_1` |
| 株価が25日移動平均線を上抜き | `kabutan.jp/warning/?mode=6_3` |
| MACD 買いシグナル | `kabutan.jp/tansaku/?mode=2_0440` |

テーマの追加・削除は `scripts/fetch_golden_cross.py` の `THEMES` リストを編集するだけです。

## 通知先の変更

現在は GitHub Issue を作成します。Slack 等に変えたい場合は、ワークフロー末尾の
「Create issue」ステップを差し替えてください（Slack の場合は `SLACK_WEBHOOK_URL` を
リポジトリ Secrets に登録）。

## 注意

本情報はテクニカルシグナルの機械的な抽出であり、特定銘柄の売買を推奨するものではありません。
