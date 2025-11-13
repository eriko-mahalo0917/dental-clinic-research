#=========================================================
#インポート
import gspread

#JSONファイルを読み込みするためのモジュール
from google.oauth2.service_account import Credentials
#=========================================================

#1つ目のフロー
#JSONファイルの指定
JSON_FILE = "creds.json"

#スプレッドシートのID
SPREADSHEET_ID ="1PrESjDHuqNpsZfo-fvd6hb8tOuAXl63aDio7hdjt6hg"


#２つ目のフロー
#承認&実行
#リスト：実行していいよの定型文みいなもの
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]