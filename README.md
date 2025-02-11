# 書籍管理アプリケーション

このアプリケーションは、ISBN番号を用いて書籍情報を検索・登録・表示するStreamlitアプリケーションです。

## 主な機能とページ構成

### 書籍登録ページ

- サイドバーで"書籍登録"を選択し、ISBN番号を入力して検索をクリックします。
- 検索された書籍情報が表示されます。
- 必要に応じて情報を編集し、"データを追加"ボタンをクリックして登録してください。
- "データを保存"ボタンで登録した情報をCSVファイルに保存します。

### サムネ表示ページ

- サイドバーで"サムネ表示"を選択します。
- 表示するNDC分類をフィルタリングし、サムネイル画像を確認します。
- スライダーで1行に表示する列数を調整できます。

### データ表示ページ

- サイドバーで"データ表示"を選択します。
- 登録済みデータをデータフレーム形式で確認できます。

## 注意事項

- ISBN番号を正確に入力してください。
- 同一のISBN番号がすでに登録されている場合、エラーが表示されます。
- 書籍情報が見つからない場合は、複数のAPIを利用して情報を取得しますが、それでも情報が取得できない場合があります。
