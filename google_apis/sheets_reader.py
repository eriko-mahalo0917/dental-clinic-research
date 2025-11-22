#=========================================================
#インポート
import gspread
import os
from dotenv import load_dotenv #直接呼び出す

#JSONファイルを読み込みするためのモジュール
from google.oauth2.service_account import Credentials
#logger
from utils import logger
#Pathを使うため
from pathlib import Path

#=========================================================

class SheetReader:
    def __init__(self):
        #utils/logger.py のロガー（SimpleLogger）をセットアップする
        self.logger_setup = logger.SimpleLogger()
        self.logger = self.logger_setup.get_logger()
        
        #Noneで初期化
        self.client = None           #これはapiの接続窓口で接続前的な！よく分からない！まとめ案件！
        self.spreadsheet_id = None   #スプシも空っぽ
        
    #１つ目のフロー
    #WSとのAPI連携
    ##.envの場所を特定　Path(__file__)はファイル自身の住所！
    def gspread_api(self):
        #認証に必要なものも初期化
        creds = None
        
        self.env_path = Path(__file__).parents[1]
        dotenv_path = self.env_path/".env"
        load_dotenv(dotenv_path)
        
        json_path_from_env = os.getenv("SERVICE_ACCOUNT_FILE_PATH")
        self.spreadsheet_id = os.getenv("SPREADSHEET_ID")
        
        #ここでID取得のときにエラーがでないかを確認する！
        #【条件分岐】 空っぽではない場合
        if json_path_from_env and self.spreadsheet_id:
            try:
                self.logger.info("IDを取得しました。Googleへの接続を試みます。")
            
        
    #２つ目のフロー
    #スプレッドシートのクリニック一覧シートのデータを取得
    #取得した歯医者さんの名前を全てDataFrameとして読み込む
    
    
    
    
    #３つ目のフロー
    #取得したDataFrameを受け取る
    #DataFrameをチェックし、入力済みのステータスがない行だけを抽出
    #抽出したデータから、クリニック名のリストを返す
        