
#=========================================================
#インポート
import gspread
import os, sys
import pandas as pd
from typing import Dict

# このPathを読み込むための定義
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

#JSONファイルを読み込みするためのモジュール
from google.oauth2.service_account import Credentials
#logger
from utils.logger import Logger
#Pathを使うため
from pathlib import Path

#=========================================================

class SheetReader:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()
        
        #Noneで初期化
        self.client = None           #これはapiの接続窓口で接続前的な！よく分からない！まとめ案件！
        self.spreadsheet_id = None   #スプシも空っぽ
        
    #１つ目のフロー
    #WSとのAPI連携
    ##.envの場所を特定　Path(__file__)はファイル自身の住所！
    def gspread_api(self):
        #認証に必要なものも初期化
        creds = None
        
        
        self.spreadsheet_id = os.getenv("SPREADSHEET_ID")
        
        #ここでID取得のときにエラーがでないかを確認する！
        #【条件分岐】 空っぽではない場合
        # if json_path_from_env and self.spreadsheet_id:
        #     try:
        #         self.logger.info("IDを取得しました。Googleへの接続を試みます。")

#=========================================================
# jsonファイルのパスを取得

    def _get_json_path(self):
        json_name = os.getenv("SECRET_KEY_JSON")
        self.logger.warning(f"JSONファイル名: {json_name}")
        
        parents_dir = Path(__file__).parents[1]
        self.logger.info(f"親ディレクトリ: {parents_dir}")
        
        json_path = parents_dir / json_name
        self.logger.critical(f"JSONファイルのフルパス: {json_path}")
        
        return json_path
        
#=========================================================
    def _get_gss_df_to_gui(self, gui_info: Dict, sheet_url: str, worksheet_name: str):
        client = self.client(json_key_name=gui_info["JSON_KEY_NAME"])

        # 対象のスプシを開く
        worksheet = client.open_by_url(url=sheet_url).worksheet(worksheet_name)

        # デバッグ用
        all_values = worksheet.get_all_values()
        # self.logger.debug(f"ワークシート全データ: {all_values}")

        # シートのデータを取得→ここでのデータは辞書型
        # columnの行に空白があると読込ができない→入力されてる部分以外を選択して消去
        dictData = worksheet.get_all_records()

        # DataFrameに変換
        df = pd.DataFrame(dictData)
        self.logger.info(f"スプシ読み込み完了 :\n{df.head()}")

        return df    
    
    # ----------------------------------------------------------------------------------
    # スプシの認証プロパティ

    def creds(self, json_key_name: str):
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        jsonKeyPath = self.path._get_secret_key_path(file_name=json_key_name)
        creds = Credentials.from_service_account_file(jsonKeyPath, scopes=SCOPES)
        return creds

    # ----------------------------------------------------------------------------------
    # スプシアクセスのプロパティ

    def client(self, json_key_name: str):
        creds = self.creds(json_key_name=json_key_name)
        client = gspread.authorize(creds)
        return client

    # ----------------------------------------------------------------------------------
        
    #２つ目のフロー
    #スプレッドシートのクリニック一覧シートのデータを取得
    #取得した歯医者さんの名前を全てDataFrameとして読み込む
    
    
    
    
    #３つ目のフロー
    #取得したDataFrameを受け取る
    #DataFrameをチェックし、入力済みのステータスがない行だけを抽出
    #抽出したデータから、クリニック名のリストを返す

if __name__ == "__main__":

    instance_sheet_reader = SheetReader()
    # JSONファイルのパスを取得
    json_path_from_env = instance_sheet_reader._get_json_path()
    print(f"JSON Path from .env: {json_path_from_env}")    
