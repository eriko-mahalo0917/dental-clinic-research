#=========================================================
#インポート
import os
import sys

#型ヒント用：戻り値が分かりやすくなるように　辞書かも！Noneかも！
from typing import Dict, Optional, List

#APIをリクエストするため
import gspread

#JSONファイルを読み込むため
from google.oauth2.service_account import Credentials
#ファイルやフォルダの住所を扱うためのモジュール
from pathlib import Path

#自作分のお呼び出し
#ログ
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.logger import SimpleLogger
from sheets_reader import SheetReader
#=========================================================

class SheetWriter:
    def __init__(self):
        #logger
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()

        
        
    def connect_spreadsheet(self):
        #-----------------------------------------------
        # １つ目のフロー：スプシへ接続
        # ・sheet_reader.pyのget_client()を再利用して、APIのクライアントを取得する
        #-----------------------------------------------
        self.logger.info("【SheetWriter】Google Sheets API クライアントに接続します")
        
        #sheet_reader.pyのAPI接続を再利用
        reader = SheetReader()
        #SheetReaderにある接続処理を利用
        client = reader.get_client()
        
        self.logger.info("【SheetWriter】APIクライアントの作成が完了しました")
        return client
    
    
        
    #※勘違いポイント！1行分 → Dict　複数行分 → List[Dict]だからList[Dict]
    def make_addsheet_request(self, sheet_data_list: List[Dict]) -> List[Dict]:

        #-----------------------------------------------
        # 2つ目のフロー：WS作成リクエスト作成
        # ・クリニック名をWS名としてaddSheet用（新しいシート）のリクエストを作る
        # ・複数クリニック分のaddSheet命令をfor文で作成する
        # ・batchUpdateで一気に実行できるrequests配列にまとめて返す
        #※batchUpdate = addSheet を一気にまとめて実行するための箱
        #-----------------------------------------------
        self.logger.info("WS作成リクエスト作成を開始します")
        
        #変数名: 型 = 値 requests: は 変数の型ヒント
        requests: List[Dict] = []
        
        for sheet_data in sheet_data_list:
            #1店舗分からクリニック名だけを取る
            clinic_name = sheet_data["クリニック名"]
            
            #addSheet: = 新しいシートを追加する
            #properties:新しく作るシートの設定（プロパティ）
            add_sheet_request = {"addSheet": {"properties":{"title":clinic_name}}}
            
            #リクエストのリストに追加をして、次々とリクエストを作成していく
            requests.append(add_sheet_request)
            
            self.logger.info("addSheetをリクエスト作成しました")
        
        self.logger.info(f"WS作成リクエスト数：{len(requests)} 件")
        
        return requests
        
        
        
        
        
        


        #-----------------------------------------------
        # ３つ目のフロー：WS作成を一括実行
        # batchUpdateを使って複数のaddSheetを1回のAPIで実行
        #-----------------------------------------------
        
        #-----------------------------------------------
        # 4つ目のフロー：データを書き込む
        # clinic_data_flow.py から受け取ったDictを使用する
        # ヘッダー行 + データ行をupdateCells リクエストとして配列にまとめる
        #-----------------------------------------------
        
        #-----------------------------------------------
        # ５つ目のフロー：データ書き込みを一括実行
        # 複数WSへの書き込みをbatchUpdateで1回のAPIで実行
        #-----------------------------------------------
        
        #-----------------------------------------------
        # ６つ目のフロー：ステータス更新
        # WS作成・書き込みが成功した件数と取得件数に差異がないか確認する
        # 問題なければ一覧シートのステータス列を「WS作成済み」に更新
        #-----------------------------------------------
        


    
    

