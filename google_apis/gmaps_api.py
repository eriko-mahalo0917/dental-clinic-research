#=========================================================
#インポート
import os
import sys
#APIでエラーが出たときのために
import time

#型ヒント用：戻り値が分かりやすくなるように
from typing import Optional, Dict

#APIをリクエストするため
import requests

#自作分のお呼び出し
#ログ
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.logger import SimpleLogger
#=========================================================

class GoogleMapsAPI:
    def __init__(self):
        #logger
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()
        
        #APIキーの取得（.envにある）
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    def receive_clinic_name(self,clinic_name: str) ->Optional[str]: #結果があるときは文字で返すけど、ないときはNoneって返すかもって意味
        #-----------------------------------------------
        # １つ目のフロー
        # クリニック名を受け取る　←for文を使うから１つだけでOKな認識！
        # 空文字ならNoneを返す　※これはステータス行が空白のものだけが入ってくる
        #-----------------------------------------------
            
        if not clinic_name:
            self.logger.info("クリニック名が空白です")
            return None
            
        self.logger.info(f"クリニック名を受け取りました:{clinic_name}")
        return clinic_name
        

#-----------------------------------------------
# ２つ目のフロー
# GoogleMapsのAPIでクリニックを検索する！
#-----------------------------------------------

#-----------------------------------------------
# ３つ目のフロー
# 検索結果からplace_idを取得する
# 見つからない場合はNoneを返す
#-----------------------------------------------

#-----------------------------------------------
# ４つ目のフロー
# place_id を使って基本情報を取得する
# ・住所
# ・電話番号
# ・ホームページURL
# ・評価
# ・レビュー総数
#-----------------------------------------------

#-----------------------------------------------
# ５つ目のフロー
# place_id を使って口コミを取得する
# コメントが空の口コミも含める
#-----------------------------------------------

#-----------------------------------------------
# ６つ目のフロー
# 取得した基本情報と口コミを1つのデータにまとめる
#-----------------------------------------------

#-----------------------------------------------
# ７つ目のフロー
# place_id が取得できなかった場合
# ・すべて空で返す
#-----------------------------------------------



#〜〜〜〜〜実行〜〜〜〜〜〜
if __name__ == "__main__":
    #インスタンス
    api = GoogleMapsAPI()
    
    #テスト①正常なクリニック名　※ここではただ単にクリニック名を入れたときのテスト
    result = api.receive_clinic_name("テストクリニック")
    print("テスト①：",result)
    
    #テスト②　※空っぽだったらNoneのテスト
    result = api.receive_clinic_name("")
    print("テスト②：",result)

    #sheet_reader.pyからちゃんと受け取れているかチェック
    from sheets_reader import SheetReader
        
    reader = SheetReader()
        
    TEST_URL = TEST_URL = "https://docs.google.com/spreadsheets/d/1PrESjDHuqNpsZfo-fvd6hb8tOuAXl63aDio7hdjt6hg/edit?gid=1025571184#gid=1025571184"
    TEST_SHEET = "テスト一覧"
    CLINIC_KEY = "クリニック名"
    STATUS_KEY = "ステータス"
        
    df_all = reader.get_clinic_name_df( sheet_url=TEST_URL, worksheet_name=TEST_SHEET )
    
    clinic_list = reader.get_status_none_clinic_name_list( df=df_all, status_key=STATUS_KEY, clinic_key=CLINIC_KEY )


    #リストにしてみる
    for clinic_name in clinic_list:
        result = api.receive_clinic_name(clinic_name)
        #
        print("受け取った名前:", result)