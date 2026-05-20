// =====================================================
// 体験者レポート 自動Slack送信スクリプト
// 対象店舗: 碑文谷 / 溝の口
// 送信タイミング: 毎週月曜・木曜 12:00
// =====================================================

const SPREADSHEET_ID = '1JpiPUR_xfBmmDe0FGHvgSpA6KzlyiGIMDEsobdZJJRY';
const SLACK_USER_ID = 'U011C4NEGEB'; // 儀間 禎平
const TARGET_STORES = ['碑文谷', '溝の口'];

// =====================================================
// メイン関数（トリガーから呼ぶ）
// =====================================================
function sendTrialReport() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const now = new Date();
  const currentMonth = Utilities.formatDate(now, 'Asia/Tokyo', 'yyyy-MM');
  const dateLabel = Utilities.formatDate(now, 'Asia/Tokyo', 'M/d(EEE) HH:mm');

  // シートを探す
  const mainDbSheet = findSheetByHeaders(ss, ['顧客名', 'ステータス', '体験月']);
  const scheduleSheet = findSheetByHeaders(ss, ['顧客名', '予約日時', '店舗名']);

  let message = `📊 *5月 体験者レポート* (${dateLabel} 更新)\n\n`;

  for (const store of TARGET_STORES) {
    message += `━━━━━━━━━━━━━━━━\n`;
    message += `🏠 *${store}*\n\n`;

    // 入会 / 検討中 / 失注
    if (mainDbSheet) {
      const { joined, considering, lost } = extractStatusData(mainDbSheet, store, currentMonth);

      message += `✅ *入会（${joined.length}名）*\n`;
      message += joined.length ? joined.map(n => `　• ${n}`).join('\n') + '\n' : '　なし\n';

      message += `\n🔄 *検討中（${considering.length}名）*\n`;
      message += considering.length ? considering.map(n => `　• ${n}`).join('\n') + '\n' : '　なし\n';

      message += `\n❌ *失注（${lost.length}名）*\n`;
      message += lost.length ? lost.map(n => `　• ${n}`).join('\n') + '\n' : '　なし\n';
    }

    // 今後の体験予定
    message += `\n📅 *今後の体験予定*\n`;
    if (scheduleSheet) {
      const upcoming = extractUpcoming(scheduleSheet, store);
      message += upcoming.length ? upcoming.map(r => `　• ${r.name}｜${r.date}`).join('\n') + '\n' : '　なし\n';
    }

    message += '\n';
  }

  sendSlackDM(message);
}

// =====================================================
// ステータス別データ抽出（入会 / 検討中 / 失注）
// =====================================================
function extractStatusData(sheet, store, currentMonth) {
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const nameCol = headers.indexOf('顧客名');
  const storeCol = headers.indexOf('店舗');
  const statusCol = headers.indexOf('ステータス');
  const monthCol = headers.indexOf('体験月');

  const joined = [], considering = [], lost = [];

  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const storeName = String(row[storeCol] || '');
    const month = String(row[monthCol] || '');

    if (!storeName.includes(store) || month !== currentMonth) continue;

    const name = row[nameCol];
    const status = String(row[statusCol] || '');

    if (status === '入会') joined.push(name);
    else if (status === '検討中') considering.push(name);
    else if (status === '失注') lost.push(name);
  }

  return { joined, considering, lost };
}

// =====================================================
// 今後の体験予定抽出
// =====================================================
function extractUpcoming(sheet, store) {
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const nameCol = headers.indexOf('顧客名');
  const dateCol = headers.indexOf('予約日時');
  const storeCol = headers.indexOf('店舗名');

  const results = [];

  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const storeName = String(row[storeCol] || '');
    if (storeName.includes(store) && row[nameCol]) {
      results.push({ name: row[nameCol], date: row[dateCol] });
    }
  }

  return results;
}

// =====================================================
// ヘッダーでシートを検索
// =====================================================
function findSheetByHeaders(ss, requiredHeaders) {
  for (const sheet of ss.getSheets()) {
    const lastCol = sheet.getLastColumn();
    if (lastCol < 1) continue;
    const firstRow = sheet.getRange(1, 1, 1, lastCol).getValues()[0].map(String);
    if (requiredHeaders.every(h => firstRow.includes(h))) return sheet;
  }
  return null;
}

// =====================================================
// Slack DM 送信
// =====================================================
function sendSlackDM(message) {
  const token = PropertiesService.getScriptProperties().getProperty('SLACK_BOT_TOKEN');
  if (!token) throw new Error('SLACK_BOT_TOKEN がスクリプトプロパティに設定されていません');

  const response = UrlFetchApp.fetch('https://slack.com/api/chat.postMessage', {
    method: 'post',
    contentType: 'application/json',
    headers: { Authorization: `Bearer ${token}` },
    payload: JSON.stringify({ channel: SLACK_USER_ID, text: message, mrkdwn: true }),
    muteHttpExceptions: true,
  });

  const result = JSON.parse(response.getContentText());
  if (!result.ok) throw new Error('Slack送信失敗: ' + result.error);
}

// =====================================================
// 手動テスト実行用
// =====================================================
function testReport() {
  sendTrialReport();
}
