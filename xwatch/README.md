# xwatch — X（旧Twitter）投稿の LINE 通知

指定した X アカウント（既定: [@fumino_official](https://x.com/fumino_official)）に
新しい投稿があったら、個人の LINE に通知する仕組みです。

X API（有料）は使わず、**投稿を RSS 化したフィードを GitHub Actions で
定期チェック**し、前回までに見た投稿との差分だけを LINE に送ります。

```
GitHub Actions（15分おき cron）
  └─ xwatch.main
       ├─ X_RSS_URL のフィードを取得（feed.py）
       ├─ 既読 ID（state/seen.json）と突き合わせて新着を抽出
       ├─ 新着を LINE に push（notify.py → LINE Messaging API）
       └─ 既読 ID を更新 → ワークフローがコミットして次回へ引き継ぎ
```

## しくみのポイント

- **RSS の URL は差し替え可能**（`X_RSS_URL` シークレット）。無料の RSS 化
  ソース（RSSHub / Nitter など）はインスタンスが止まりがちなので、止まったら
  URL を変えるだけで復旧できます。
- **初回実行は通知しません**。既存の投稿を一気に送ってしまわないよう、初回は
  「基準」として現在のフィードを記録するだけ。以降の新着から通知します。
- **重複通知を防止**。直近の投稿 ID を `state/seen.json` に保持し、送信済みは
  再送しません。まとめて多数検知した場合は 1 回あたり最大 `X_MAX_NOTIFY` 件
  （既定 5）に制限し、残りは既読扱いにします。
- **LINE 送信は goldencross と共通**。`LINE_CHANNEL_ACCESS_TOKEN` /
  `LINE_TO` をそのまま使います（LINE Notify は 2025/3 終了のため
  Messaging API を使用）。

## セットアップ

### 1. RSS フィードの URL を用意する

監視したいアカウントを RSS 化した URL を用意します。例:

- RSSHub: `https://rsshub.app/twitter/user/fumino_official`
  （公式インスタンスは Twitter ルートに認証や制限がかかることがあります。
  自前ホストの RSSHub や別インスタンスの利用も検討してください）
- Nitter インスタンス: `https://<インスタンス>/fumino_official/rss`

> ⚠️ 無料ソースは安定性が保証されません。通知が止まったら、まず URL を
> ブラウザで開いてフィードが返るか確認し、ダメなら別インスタンスの URL に
> 差し替えてください。

動作確認（ローカル）:

```bash
pip install -r requirements.txt
export X_RSS_URL="https://rsshub.app/twitter/user/fumino_official"
python -m xwatch.main --dry-run          # LINE 送信せず本文だけ表示
```

### 2. GitHub のシークレット / 変数を設定する

リポジトリの **Settings → Secrets and variables → Actions** で登録します。

| 種別    | 名前                        | 内容                                             |
| ------- | --------------------------- | ------------------------------------------------ |
| Secret  | `LINE_CHANNEL_ACCESS_TOKEN` | LINE Messaging API のチャネルアクセストークン    |
| Secret  | `LINE_TO`                   | 送信先 userId（省略時は broadcast＝友だち全員）  |
| Secret  | `X_RSS_URL`                 | 監視対象アカウントの RSS フィード URL            |
| Variable| `X_ACCOUNT`（任意）         | 通知本文の表示名（既定 `fumino_official`）       |

`LINE_CHANNEL_ACCESS_TOKEN` / `LINE_TO` は goldencross と同じものを流用できます。

### 3. 動かす

- `.github/workflows/x-notify.yml` が **15分おき**に自動実行します。
- 手動実行は Actions タブ →「X Post Notify」→ Run workflow から。
  - `dry_run`: LINE 送信せず本文を確認
  - `notify_first`: 初回でも新着を通知（基準記録をスキップ）

## 環境変数

| 変数                        | 必須 | 既定              | 説明                                       |
| --------------------------- | ---- | ----------------- | ------------------------------------------ |
| `X_RSS_URL`                 | ✅   | —                 | 監視対象の RSS フィード URL                 |
| `LINE_CHANNEL_ACCESS_TOKEN` | ✅   | —                 | LINE チャネルアクセストークン              |
| `LINE_TO`                   |      | （broadcast）     | 送信先 userId                              |
| `X_ACCOUNT`                 |      | `fumino_official` | 通知本文の表示用アカウント名               |
| `X_MAX_NOTIFY`              |      | `5`               | 1 回で送る新着の最大件数                    |
| `X_STATE_PATH`              |      | `xwatch/state/seen.json` | 既読 ID の保存先                    |

## 注意点

- GitHub Actions の cron は混雑時に遅延するため、**厳密なリアルタイム通知
  ではありません**（数分〜十数分ずれることがあります）。
- 既読状態はワークフローが `xwatch/state/seen.json` に自動コミットします
  （コミットメッセージ末尾 `[skip ci]`）。

## テスト

```bash
python tests/test_xwatch.py     # ネットワーク不要のオフラインテスト
```
