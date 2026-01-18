#=========================================================
#インポート
import os
import sys
from googleapiclient.discovery import build
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
        # １つ目のフロー：認証情報（creds）を取得
        # ・SheetReaderの認証処理を再利用
        # ・gspreadとaddBatchUpdateで利用するためのAPIの認証を取得
        #-----------------------------------------------
        self.logger.info("【SheetWriter】Google認証情報を取得します")
        
        #sheet_reader.pyのAPI接続を再利用
        reader = SheetReader()
        #SheetReaderにある接続処理を利用
        self.creds = reader.creds()
        
        self.logger.info("【SheetWriter】認証情報の取得が完了しました")
        return self.creds
    
    
        
    #※勘違いポイント！1行分 → Dict　複数行分 → List[Dict]だからList[Dict]
    def make_add_sheet_request(self, clinic_sheet_data_list: List[Dict]) -> List[Dict]:

        #-----------------------------------------------
        # 2つ目のフロー：WS作成リクエスト作成
        # ・クリニック名をWS名としてaddSheet用（新しいシート）のリクエストを作る
        # ・複数クリニック分のaddSheet命令をfor文で作成する
        # ・batchUpdateで一気に実行できるrequests配列にまとめて返す
        #※batchUpdate = addSheet を一気にまとめて実行するための箱
        #-----------------------------------------------
        self.logger.info("WS作成リクエスト作成を開始します")
        
        #変数名: 型 = 値 requests: は 変数の型ヒント
        add_sheet_requests: List[Dict] = []
        
        for clinic_sheet_data in clinic_sheet_data_list:
            #1店舗分からクリニック名だけを取る
            clinic_name = clinic_sheet_data["クリニック名"]
            
            #addSheet: = 新しいシートを追加する
            #properties:新しく作るシートの設定（プロパティ）
            single_add_sheet_request = {"addSheet": {"properties":{"title":clinic_name}}}
            
            #リクエストのリストに追加をして、次々とリクエストを作成していく
            add_sheet_requests.append(single_add_sheet_request)
            
            self.logger.info("addSheetをリクエスト作成しました")
        
        self.logger.info(f"WS作成リクエスト数：{len(add_sheet_requests)} 件")
        
        return add_sheet_requests
        
    
    def create_worksheets_batch(self, spreadsheet_id: str, add_sheet_requests: List[Dict]) ->Dict:
        #-----------------------------------------------
        # ３つ目のフロー：WS作成を一括実行
        # batchUpdateを使って複数のaddSheetを1回のAPIで実行
        #-----------------------------------------------
        self.logger.info("WS一括作成（batchUpdate）を開始します")
        
        #build()は操作したい値を入れてAPIするためのもの！v4は現在のGoogle Sheets APIのバージョン
        #credentials=認証情報　serviceという名前はAPIを利用していると分かるように
        service = build("sheets", "v4", credentials = self.creds)
        
        #batchUpdateに渡すリクエストボディ（ボディだから2つ目のフローの成果物を詰めてる感じ）
        batch_update_body = {"requests":add_sheet_requests}
        
        #新しいたくさんWS作成を一括で実行
        # #service.spreadsheets().batchUpdate(...).execute()は決まり文句
        add_sheet_batch_response = (
            service.spreadsheets()
            .batchUpdate(spreadsheetId=spreadsheet_id,body=batch_update_body)
            .execute()
        )
        
        self.logger.info("WS一括作成（batchUpdate）が完了しました")
        
        return add_sheet_batch_response
        
    #sheet_id_mapはセルの住所
    def make_cell_write_requests(self,clinic_sheet_data_list:List[Dict], sheet_id_map: Dict[str,int]) ->List[Dict]
        #-----------------------------------------------
        # 4つ目のフロー：データを書き込む　※ここは命令だけでAPIはまだしない！
        # clinic_data_flow.py から受け取ったDictを使用する
        # ヘッダー行 + データ行をupdateCells リクエストとして配列にまとめる
        #-----------------------------------------------
        self.logger.info("セル書き込みのリクエスト作成を開始します")
        
        #Sheet APIに渡すリクエストの配列でList[Dict]と決まっている！これを準備
        sheets_api_batch_requests: List[Dict] = []
        
        #for文でクリニックごと二処理をする
        for clinic_sheet_data in clinic_sheet_data_list:
            clinic_name = clinic_sheet_data["クリニック名"]
            
            #このクリニックシートのIDを取得して、どこに書き込めばいいかを確認させる
            sheet_id = sheet_id_map[clinic_name]
        
        
        
        
        
        
        #-----------------------------------------------
        # ５つ目のフロー：データ書き込みを一括実行
        # 複数WSへの書き込みをbatchUpdateで1回のAPIで実行
        #-----------------------------------------------
        
        #-----------------------------------------------
        # ６つ目のフロー：ステータス更新
        # WS作成・書き込みが成功した件数と取得件数に差異がないか確認する
        # 問題なければ一覧シートのステータス列を「WS作成済み」に更新
        #-----------------------------------------------



#=========================================================
# 実行してみる（1〜3つ目のフロー）
#=========================================================
if __name__ == "__main__":

    print("=== 実行テスト開始 ===")

    # SheetWriter インスタンス作成
    writer = SheetWriter()
    
    #-----------------------------------------------
    #１つ目のフローのcredsを取得
    #-----------------------------------------------
    creds = writer.connect_spreadsheet()
    print("creds取得しました")
    
    #対象のシートのIDを教えてる
    spreadsheet_id = "1PrESjDHuqNpsZfo-fvd6hb8tOuAXl63aDio7hdjt6hg"

    #-----------------------------------------------
    # ２つ目のフロー：clinic_data_flow.pyのデータをゲット
    #-----------------------------------------------
    # clinic_data_flow.py はまだ使わず、とりあえず仮のデータで！
    sheet_data_list = [{"クリニック名": "リベ大デンタルクリニック"},{"クリニック名": "ハニーチュロ歯科"}]
    
    print("取得したクリニック件数：", len(sheet_data_list))
    
    add_sheet_requests = writer.make_add_sheet_request(sheet_data_list)
    
    
    #-----------------------------------------------
    # 3つ目のフロー：WS作成を一括実行（batchUpdate）
    #-----------------------------------------------
    batch_update_result = writer.create_worksheets_batch(spreadsheet_id=spreadsheet_id,add_sheet_requests=add_sheet_requests)

    print(batch_update_result)
    print("🦷🦷🦷ばっちり🦷🦷🦷")


