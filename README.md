# DENTAL-CLINIC-RESEARCH
このプロジェクトは、スプレッドシートに記載されたクリニック名をもとにGoogle Maps APIを利用して基本情報を取得するリサーチツールです。

## 🟡概要
このツールは、スプレッドシートの**クリニック一覧**シートからデータを取得し、
クリニックごとにワークシートを作成します。

ワークシート作成時には、Google Maps APIより取得した基本情報を書き込みます。
作成後は、クリニック一覧のステータスを「WS作成済み」に更新をします。

## 🟡処理フロー
1. スプレッドシートからクリニック一覧を取得
2. ステータスが未処理のクリニック名を抽出
3. Google Maps APIでクリニック情報・口コミを取得
4. スプレッドシートへ書き込める形式にデータを整形
5. クリニックごとのワークシートを作成
6. 基本情報・口コミを書き込み
7. 一覧シートのステータスを「WS作成済み」に更新

## 🟡ファイル構成と役割
### sheets_reader.py
Googleスプレッドシートからデータを取得する役割を担います。

- サービスアカウント（creds.json）を用いた認証
- 指定したワークシートを DataFrame として取得
- ステータスが空白のクリニック名を抽出

### gmaps_api.py
GoogleMaps API を利用してクリニック情報を取得します。

- クリニック名による検索
- place_idの取得
- 基本情報の取得（住所・TEL・URL・評価・総合レビュー（総合評価））
- 口コミを最大５件取得

### clinic_data_flow.py
取得した情報をスプレッドシートに書き込める形式にします。

- １店舗分：基本情報 + 口コミを１行のDictniまとめる
- データが存在しない項目は空白

### sheets_writer.py
Google Sheet APIを利用してワークシート作成 ＋ データ書き込み + ステータス更新を行います。

- クリニック名をシート名としてワークシートを一括処理
- ヘッダー行とデータを書き込み
- ヘッダーの背景色を設定
- クリニック一覧シートのステータスを「WS作成済み」に更新

### main_flow.py
各処理を組み合わせて、処理全体の流れとなります。

- クリニック一覧取得
- Google Maps API 呼び出し
- データ整形
- スプレッドシート書き込み処理の実行

### main.py
このファイルを実行することで、処理が実行されます。


## 🟡事前準備
### 1.GoogleスプレッドシートID
- 処理対象となるスプレッドシートのIDを取得してください。
- スプレッドシートIDは、URL内の以下の部分です。

https://docs.google.com/spreadsheets/d/【この部分】/edit


### 2.環境変数（.envファイル）の準備
- Google API 認証情報
- スプレッドシートID

※リポジトリには含めません。

### 3.Google API 認証ファイル（creds.json）
- Google Sheets API / Google Maps API を利用するための認証ファイルです。
- Google Cloud Console にて発行した認証情報（JSON形式）を使用します。
- ファイル名は `creds.json` とし、指定のディレクトリに配置してください。

※リポジトリには含めません。

## 🟡ファイル階層
```
DENTAL-CLINIC-RESEARCH/
├ google_apis/
│   ├ gmaps_api.py
│   ├ sheets_reader.py
│   └ sheets_writer.py
├ models/
│   └ clinic_data_flow.py
├ utils/
│   └ logger.py
├ config.py
├ main_flow.py
├ main.py
├ requirements.txt
├ .env
├ creds.json
└ README.md
```


## ⚠️注意点

- 本ツールは、スプレッドシートの構成（シート名・列構成）が
  想定された形式であることを前提としています。
  構成を変更した場合、正常に動作しない可能性があります。

- `creds.json` や `.env` ファイルには機密情報が含まれるため、
  GitHubなどのリポジトリには絶対に含めないでください。