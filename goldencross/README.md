# ゴールデンクロス通知システム

日米株の**ゴールデンクロス／デッドクロス**を毎営業日に自動検知し、
**市場環境（日経平均・S&P500・SOX・VIX・ドル円・Fear & Greed）** と
あわせて **LINE** に通知します。GitHub Actions（cron）で無料運用できます。

---

## 仕組み

```
GitHub Actions (cron, 平日)        ← サーバー不要・無料
  └─ python -m goldencross.main
        ├─ config/watchlist.yaml の銘柄を yfinance で取得
        ├─ 短期SMA(25日) が 長期SMA(75日) を上抜け → ゴールデンクロス
        │                          下抜け → デッドクロス
        ├─ 市場環境（VIX/SOX/ドル円/日経/S&P500/Fear&Greed）を取得
        └─ LINE Messaging API で push 通知
```

---

## セットアップ手順

### 1. LINE 公式アカウント（Messaging API）を用意

> ⚠️ かつての **LINE Notify は 2025/3 末で終了**したため、**Messaging API** を使います。

1. [LINE Developers](https://developers.line.biz/) にログイン
2. **プロバイダー**を作成 → **Messaging API チャネル**を新規作成
3. チャネルの **「Messaging API設定」** タブで
   **チャネルアクセストークン（長期）** を発行 → これが `LINE_CHANNEL_ACCESS_TOKEN`
4. スマホの LINE で、その公式アカウントを **友だち追加**
5. 自分だけに送るなら **userId** が必要（`LINE_TO`）。取得方法はいずれか:
   - Messaging API設定の Webhook で受信した `userId` を確認、または
   - **`LINE_TO` を未設定**にすると **broadcast（友だち全員へ配信）** になります。
     1人運用ならこれが最も簡単です。

### 2. GitHub Secrets を登録

リポジトリの **Settings → Secrets and variables → Actions → New repository secret**

| Secret 名 | 値 | 必須 |
|---|---|---|
| `LINE_CHANNEL_ACCESS_TOKEN` | チャネルアクセストークン（長期） | ✅ |
| `LINE_TO` | 送信先 userId（未設定なら broadcast） | 任意 |

### 3. 完了

`.github/workflows/golden-cross.yml` が **平日 07:00 JST（米国クローズ後）** に
自動実行します。**Actions タブ → Golden Cross Notify → Run workflow** で手動実行も可能です。

---

## 監視銘柄の変更

`config/watchlist.yaml` を編集するだけです。

```yaml
stocks:
  jp:
    - { symbol: "7203.T", name: "トヨタ自動車", theme: "主力" }  # 日本株は コード + .T
  us:
    - { symbol: "NVDA",   name: "NVIDIA",       theme: "半導体" } # 米国株は ティッカー
```

`theme` は任意のタグで、通知に `[半導体]` のように表示されます。
初期設定では日米それぞれ **主力 / 半導体 / 宇宙 / 量子コンピュータ** の
テーマ株を登録済みです。

移動平均の日数も変えられます（例: 短期5日・長期25日にするなど）。

```yaml
sma:
  short: 25
  long: 75
```

---

## ローカルでの動作確認

```bash
pip install -r requirements.txt

# LINE 送信せず本文だけ表示
python -m goldencross.main --dry-run

# クロスが無くても市場環境を表示
python -m goldencross.main --dry-run --always

# ロジックの単体テスト（ネット不要）
python tests/test_indicators.py
```

---

## 注意事項

- 株価データは Yahoo Finance（yfinance）の無料データを利用しています。
  個人利用の範囲で使ってください。
- 本通知は**テクニカル指標の機械的な検知**であり、**投資判断・投資助言ではありません**。
  最終的な投資判断はご自身の責任で行ってください。
- Fear & Greed は CNN の非公式エンドポイントを利用しているため、
  取得できない場合は通知から省略されます（他の通知は継続します）。
