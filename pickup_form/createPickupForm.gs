/**
 * 8月マンスリー ピックアップ「かかりつけられた」エピソード 事前ヒアリング
 * Googleフォームを自動生成し、回答用スプレッドシートを連携するスクリプト。
 *
 * 使い方：
 *   1. https://script.google.com で新規プロジェクトを作成
 *   2. このコードを貼り付けて保存
 *   3. 関数「createPickupForm」を実行 → 初回は承認（許可）が必要
 *   4. 実行ログに出る3つのURL（回答用フォーム / 編集用 / スプレッドシート）を確認
 *   5. 「回答用フォームURL」を飯田さん・小林 愛さんに共有
 *
 * 以降、送信された回答は連携スプレッドシートに自動で1行ずつ溜まります。
 */

function createPickupForm() {

  // --- フォーム本体 ---
  var form = FormApp.create('8月マンスリー ピックアップ｜「かかりつけられた」エピソード 事前ヒアリング');

  form.setDescription(
    'お疲れ様です！\n' +
    'これは当日の登壇（各3分）をスムーズにするための事前ヒアリングです。\n' +
    'お客様に「かかりつけられている（＝この人にお願いしたい、と頼られている）」と感じた ' +
    '具体的なエピソードを1つ 思い浮かべながら記入してください。\n' +
    'きれいな文章でなくてOK。重要なワード・パワーフレーズだけ書ければ大丈夫です。深掘りは当日一緒に行います。'
  );

  form.setProgressBar(true);
  form.setAllowResponseEdits(true);
  form.setCollectEmail(false); // メール収集が必要ならtrueに

  // --- 記入者情報（1ページ目） ---
  form.addTextItem().setTitle('氏名').setRequired(true);
  form.addTextItem().setTitle('所属店舗').setRequired(true);
  form.addTextItem().setTitle('トレーナー歴');

  // --- セクション1 ---
  form.addPageBreakItem()
    .setTitle('セクション1｜あなたにとっての「かかりつけ」')
    .setHelpText('まずは肩慣らしです。言葉を短く置いておければOK。');
  form.addParagraphTextItem()
    .setTitle('Q1. 「かかりつけられている」とは、どんな状態だと思いますか？')
    .setHelpText('一言＋その理由');
  form.addParagraphTextItem()
    .setTitle('Q2. お客様と関わるうえで、心掛けていること・モットーは？');

  // --- セクション2 ---
  form.addPageBreakItem()
    .setTitle('セクション2｜エピソードの主役を決める')
    .setHelpText('今回話す「かかりつけられたエピソード」を1つに絞ります。');
  form.addParagraphTextItem()
    .setTitle('Q3. 今回話したいエピソードの主役は、どんなお客様ですか？')
    .setHelpText('差し支えない範囲で／年代・きっかけ・関係の長さ など');
  form.addParagraphTextItem()
    .setTitle('Q4. その方が「この人に頼りたい」と感じてくれたと思う瞬間・出来事は？');
  form.addParagraphTextItem()
    .setTitle('Q5. なぜ自分が選ばれた・頼られたと思いますか？');

  // --- セクション3 ---
  form.addPageBreakItem()
    .setTitle('セクション3｜あなたの関わり方')
    .setHelpText('そのお客様に、どう向き合ってきたか。');
  form.addParagraphTextItem()
    .setTitle('Q6. 特に意識して・工夫して関わったことは？')
    .setHelpText('トレーニング以外の関わりも含めて');
  form.addParagraphTextItem()
    .setTitle('Q7. 一番印象に残っているやり取り・かけられた言葉は？');
  form.addParagraphTextItem()
    .setTitle('Q8. 迷ったこと・大変だったことは？ どう乗り越えましたか？');

  // --- セクション4 ---
  form.addPageBreakItem()
    .setTitle('セクション4｜変化と、エピソードの核')
    .setHelpText('ここが当日のいちばんの聞かせどころになります。');
  form.addParagraphTextItem()
    .setTitle('Q9. あなたの関わりを通じて、お客様にどんな変化がありましたか？');
  form.addParagraphTextItem()
    .setTitle('Q10. お客様からの言葉・反応で、忘れられないものは？');
  form.addParagraphTextItem()
    .setTitle('Q11. このエピソードは、自分にとってどんな意味がありましたか？「かかりつけられる」ことの価値をどう感じましたか？');

  // --- セクション5 ---
  form.addPageBreakItem()
    .setTitle('セクション5｜3分トークの組み立て（当日の型）')
    .setHelpText(
      'セクション1〜4の回答を、そのまま3分に流し込む設計です（18:50–19:00の枠）。\n' +
      '　〜0:30｜つかみ：主役のお客様との出会い（どんな方か）\n' +
      '　〜1:30｜転機：頼られた瞬間／あなたが向き合ったこと\n' +
      '　〜2:30｜変化：お客様の変化・忘れられない言葉\n' +
      '　〜3:00｜締め：伝えたい「かかりつけられる」価値・想い'
    );
  form.addParagraphTextItem()
    .setTitle('Q12. 当日、司会（聞き手）に特に拾ってほしいポイントは？');

  // --- 回答用スプレッドシートを作成して連携 ---
  var ss = SpreadsheetApp.create('【回答】8月マンスリー ピックアップ 事前ヒアリング');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  // --- 実行ログにURLを出力 ---
  Logger.log('■ 回答用フォームURL（発表者に共有）: %s', form.getPublishedUrl());
  Logger.log('■ 編集用URL（設問の修正）      : %s', form.getEditUrl());
  Logger.log('■ 回答スプレッドシートURL      : %s', ss.getUrl());
}
