#=========================================================
#インポート
import os
import sys
from googleapiclient.discovery import build
#型ヒント用：戻り値が分かりやすくなるように　辞書かも！Noneかも！
from typing import Dict, Optional, List, Tuple

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
        
    
    def create_worksheets_batch(self, spreadsheet_id: str, add_sheet_requests: List[Dict]) -> Tuple[Dict, Dict[str, int]]:
        #-----------------------------------------------
        # ３つ目のフロー：WS作成を一括実行
        # batchUpdateを使って複数のaddSheetを1回のAPIで実行
        # ４つ目のフローで必要なsheet_id_mapを取得
        #-----------------------------------------------
        self.logger.info("WS一括作成（batchUpdate）を開始します")
        
        #build()は操作したい値を入れてAPIするためのもの！v4は現在のGoogle Sheets APIのバージョン
        #credentials=認証情報　serviceという名前はAPIを利用していると分かるように
        service = build("sheets", "v4", credentials = self.creds)
        
        #batchUpdateに渡すリクエストボディ（ボディだから2つ目のフローの成果物を詰めてる感じ）
        batch_update_body = {"requests":add_sheet_requests}
        
        #新しいたくさんWS作成を一括で実行
        # #service.spreadsheets().batchUpdate(...).execute()は決まり文句（レスポンス全体）
        add_sheet_batch_response = (
            service.spreadsheets()
            .batchUpdate(spreadsheetId=spreadsheet_id,body=batch_update_body)
            .execute()
        )
        
        self.logger.info("WS一括作成（batchUpdate）が完了しました")
        
        #====
        #sheet_id_mapを取得
        #====
        
        sheet_id_map: Dict[str, int] = {}
        #reply（リプライ）は1つのレスポンスの塊（辞書）のこと！！
        #repliesのキーがあれば取得、なかったら空リスト
        for reply in add_sheet_batch_response.get("replies", []):
            #replyの中に”addSheet”というキーがあれば…（これを入れることでなかった場合のエラーを回避）
            if "addSheet" in reply:
                #"addSheet"の辞書の更に中にある"properties"というキーを取り出す
                sheet_properties = reply["addSheet"]["properties"]
                #シートのタイトルを取得
                title = sheet_properties["title"]
                #sheetId取得を取得
                sheet_id = sheet_properties["sheetId"]
                #最初に準備した辞書へ追加
                #sheet_id_map = {"〇〇クリニック": 123456789}　※イメージ
                sheet_id_map[title] = sheet_id
                self.logger.info(f"シートID取得件数:{len(sheet_id_map)}")
        return  add_sheet_batch_response, sheet_id_map
    
    
        
    #sheet_id_mapはセルの住所
    def make_cell_write_requests(self,clinic_sheet_data_list:List[Dict], sheet_id_map: Dict[str,int]) ->List[Dict]:
        #-----------------------------------------------
        # 4つ目のフロー：データを書き込む　※ここは命令だけでAPIはまだしない！
        # clinic_data_flow.py から受け取ったDictを使用する
        # 3つ目のフローで取得した sheet_id_mapを使い
        # ヘッダー行 + データ行をupdateCells リクエストとして配列にまとめる
        #-----------------------------------------------
        self.logger.info("セル書き込みのリクエスト作成を開始します")
        
        #Sheet APIに渡すリクエストの配列でList[Dict]と決まっている！これを準備
        sheets_api_batch_requests: List[Dict] = []
        
        #for文で１つのクリニックごとに処理をする
        for clinic_sheet_data in clinic_sheet_data_list:
            clinic_name = clinic_sheet_data["クリニック名"]
            
            ## クリニック名をキーにして、対応するsheetIdを取得する　※イメージ　
            sheet_id = sheet_id_map[clinic_name]
            
            #====
            #ヘッダー行(1行目)
            #====
            """
            .keys()は辞書のキーだけを取り出す！
            ここでは1店舗分のクリニックデータの辞書のキー部分のクリニック名・住所・電話番号などの
            部分だけを取り出して、list(キー)をリストにしている →こうすることでSheetAPIで扱いやすくする
            →つまり！１行目に書きたい文字たちの集合体
            """
            headers = list(clinic_sheet_data.keys())
            #API用のセル形式に変換　for文を１行で書いた内包表記　セル１個＝辞書１個がAPIの決まり
            """
            【内包表記】
            headersからheader（キーだけのリスト）を1つずつ取り出して
            {"userEnteredValue":{"stringValue": 文字列}の文字列部分にキーを入れてねの処理
            この書き方はAPIのお決まり{"userEnteredValue": {"numberValue": 123}}
            """
            header_cells = [{"userEnteredValue":{"stringValue": header}} for header in headers]
            
            #{"updateCells":}ここは命令の内容を組み立てている
            header_request = {
                "updateCells":{
                    #ヘッダー1行分のセル内容だけを作成（どこに書くかはまだ決めていない）
                    "rows":[{"values": header_cells}],
                    #userEnteredValueは入力した値のことで、セルの文字列のみを書き換える
                    "fields":"userEnteredValue",
                    #書き込み開始位置の指定
                    "start":{
                        #どのシートかを指定
                        "sheetId": sheet_id,
                        #行の番号を指定
                        "rowIndex":0,
                        #列の番号を指定
                        "columnIndex":0
                        }
                    }
                }
            
            #命令のリストにこの指示を追加する　※あとでvalue分も追加予定
            sheets_api_batch_requests.append(header_request)
            
            #====
            #2行目
            #====
            #リストのvalueの部分のみ取り出してリストにする
            values = list(clinic_sheet_data.values())
            
            value_cells = [{"userEnteredValue":{"stringValue": value}} for value in values]
            
            value_request = {
                #{"updateCells":}ここは命令の内容を組み立てている
                "updateCells":{
                    #１行分のセルの内容だけを作成している（どこに書くかはまだ決めていない）
                    "rows":[{"values": value_cells}],
                    #文字列のみ書き換える　※空のセル想定でも書いておくのが決まり
                    "fields": "userEnteredValue",
                    #書き込み位置の指定
                    "start": {
                        #どのシートかを指定
                        "sheetId": sheet_id,
                        #２行目を指定
                        "rowIndex": 1,
                        #列の指定
                        "columnIndex":0
                    }
                }
            }
            
            #命令のリストに追加する
            sheets_api_batch_requests.append(value_request)
            
            self.logger.info("書き込みリクエストを作成しました")
            
        return sheets_api_batch_requests
        
        
        
        
        
        
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
    sheet_data_list = [
        {"クリニック名": "リベ大デンタルクリニック",
        "住所": "福岡市中央区1-2-3",
        "電話番号": "092-123-4567",
        "URL": "https://libe-dental.example.com"
        },
        {
        "クリニック名": "ハニーチュロ歯科",
        "住所": "福岡市博多区4-5-6",
        "電話番号": "092-987-6543",
        "URL": "https://honey-churro.example.com"
        }
        ]

    
    print("取得したクリニック件数：", len(sheet_data_list))
    
    add_sheet_requests = writer.make_add_sheet_request(sheet_data_list)
    
    
    #-----------------------------------------------
    # 3つ目のフロー：WS作成を一括実行（batchUpdate）
    #-----------------------------------------------
    batch_update_result , sheet_id_map = writer.create_worksheets_batch(spreadsheet_id=spreadsheet_id,add_sheet_requests=add_sheet_requests)

    print(batch_update_result)
    print(sheet_id_map)
    print("🦷🦷🦷ばっちり🦷🦷🦷")

    #-----------------------------------------------
    # ４つ目のフロー：セルに書き込みのリクエストを作成
    #-----------------------------------------------
    cell_write_requests = writer.make_cell_write_requests(clinic_sheet_data_list=sheet_data_list,sheet_id_map=sheet_id_map)
    
    print("4つ目のフローを実行。セルへ書き込み命令をします！")
    
    #中身を分かりやすく出色してくれるpprintをやってみた(プリティプリント)
    from pprint import pprint
    pprint(cell_write_requests)
    
    print("４つ目フロー確認完了！🦷")