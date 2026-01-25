#=========================================================
#インポート
import os
import sys
from googleapiclient.discovery import build
#型ヒント用：戻り値が分かりやすくなるように　辞書かも！Noneかも！
from typing import Dict, Optional, List, Tuple

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
        # １つ目のフロー：Google Sheet APIの接続準備
        # ・認証情報（creds）を取得　→　SheetReaderの認証処理を再利用
        # ・Sheets APIのserviceを生成して３つ目と５つ目のフローで使う
        #-----------------------------------------------
        self.logger.info("【SheetWriter】Google認証情報を取得します")
        
        #sheet_reader.pyのAPI接続を再利用
        reader = SheetReader()
        #SheetReaderにある接続処理を利用
        self.creds = reader.creds()
        
        #sheets APIのserviceをここで１回だけ作って以降はこれを使う
        #build()は操作したい値を入れてAPIを作成！v4は現在のGoogle Sheets APIのバージョン
        #credentials=認証情報　serviceという名前はAPIを利用していると分かるように
        #service = build("sheets", "v4", credentials=self.creds) →　self.serviceにしたので不要
        self.service = build("sheets","v4", credentials=self.creds)
        
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
        #service = build("sheets", "v4", credentials = self.creds)　→　self.serviceにしたので不要
        
        #batchUpdateに渡すリクエストボディ（ボディだから2つ目のフローの成果物を詰めてる感じ）
        add_sheet_batch_body = {"requests":add_sheet_requests}
        
        try:
            
            #新しいたくさんWS作成を一括で実行
            ##service.spreadsheets().batchUpdate(...).execute()は決まり文句（レスポンス全体）
            add_sheet_batch_response = (
                self.service.spreadsheets()
                .batchUpdate(spreadsheetId=spreadsheet_id,body=add_sheet_batch_body)
                .execute()
            )
        
            self.logger.info("WS一括作成（batchUpdate）が完了しました")
            
        except Exception as e:
            self.logger.error(f"WS作成batchUpdateでエラーが発生しました：{e}")
            #WSは失敗したためNoneでsheet_id_mapは何も作成されない状態で空辞書を返す
            #返り値を同じ形にして安全に止める
            return None, {}
        
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
        # ヘッダー行 + データ行をupdateCells リクエストとして配列にまとめる＋ヘッダー行の背景色
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
            row_values = list(clinic_sheet_data.values())
            
            cell_data = [{"userEnteredValue":{"stringValue": cell_value}} for cell_value in row_values]
            
            value_request = {
                #{"updateCells":}ここは命令の内容を組み立てている
                "updateCells":{
                    #１行分のセルの内容だけを作成している（どこに書くかはまだ決めていない）
                    "rows":[{"values": cell_data}],
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
        
            #====
            # ヘッダー装飾（背景色）
            #====
            header_format_request = {
                #指定した範囲の見た目をまとめて整える
                "repeatCell":{
                    #どこの範囲か指定
                    "range":{
                        #どのシートにするのかを指定
                        "sheetId": sheet_id,
                        #１行目から
                        "startRowIndex": 0,
                        #１行目まで（０まで！）を指定
                        "endRowIndex": 1,
                        #列の指定　A列から
                        "startColumnIndex": 0,
                        #ヘッダーの数分まで（０からスタートで最後は含まれない）
                        "endColumnIndex":len(headers)
                    },
                    #見た目の設計部分
                    "cell":{
                        #userEnteredFormatセルの見た目（背景色・文字装飾など）を指定するための定型構造
                        "userEnteredFormat":{
                            #背景色の指定
                            "backgroundColor":{
                                #この３つで薄めのグレーを指定
                                "red":0.8,
                                "green": 0.8,
                                "blue": 0.8
                            },
                        }
                    },
                    #背景色のみを変更することを指定
                    "fields": "userEnteredFormat(backgroundColor)"
                }
            }
        
            #命令リストに追加する
            sheets_api_batch_requests.append(header_format_request)
        
            self.logger.info("書き込みリクエストを作成しました")
            
        return sheets_api_batch_requests
        
        
    def write_cells_batch(self, spreadsheet_id: str, sheets_api_batch_requests: List[Dict]) ->Dict:
        #-----------------------------------------------
        # ５つ目のフロー：データ書き込みを一括実行
        # ４つ目で作成したリクエストで複数WSへの書き込みをbatchUpdateで1回のAPIで実行
        #-----------------------------------------------
        self.logger.info("セル書き込みbatchUpdateを開始します")
        
        #batchUpdateに渡すリクエストボディ（ボディだから４つ目のフローの成果物を詰めている）
        write_cells_batch_body = {"requests": sheets_api_batch_requests}
        
        try:
            #一括書き込み実行
            ##service.spreadsheets().batchUpdate(...).execute()は決まり文句（レスポンス全体）
            write_response = (self.service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=write_cells_batch_body).execute())
            self.logger.info("セルの書き込みが完了しました")
            return write_response
        
        #Google Sheets APIのエラーはHttpErrorなどで返ってくるので、通信系エラーのではなくていい
        except Exception as e:
            self.logger.error(f"セルの書き込みでエラー発生:{e}")
            return None
    
    
    def get_sheet_id_by_title(self, spreadsheet_id: str, sheet_title: str) ->Optional[int]:
        # -------------------------
        #スプシ内のシート名を指定するとそのsheet_idを種痘する
        # -------------------------
        self.logger.info(f"{sheet_title}のシートIDを取得します")
        
        try:
            all_sheets_info = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        
            #スプシ全体の情報を取得
            for one_sheet_info in all_sheets_info.get("sheets",[]):
                #そのタイトルやIDなどの情報
                sheet_details = one_sheet_info["properties"]
            
                #指定したタイトルと一致したsheetIdを返す
                if sheet_details["title"] == sheet_title:
                    self.logger.info(f'{sheet_title}のシートIDを取得しました:{sheet_details["sheetId"]}')
                    return sheet_details["sheetId"]
            
        except Exception as e:
            self.logger.error(f"シートID取得に失敗しました：{e}")
            return None
            
        
        
        
    #clinic_list_sheet_idはクリニック一覧シートのID、created_ws_namesは作成済みのWS名リスト、clinic_list_rowsは一覧シートの全行データ
    def make_status_update_requests(self, clinic_list_sheet_id:str,created_ws_names: List[str], clinic_list_rows: List[List], status_column_index: int = 1) -> List[Dict]:
        #-----------------------------------------------
        # ６つ目のフロー：クリニック一覧シートのステータス更新
        # 作成したWSが一覧シートにある場合は、ステータス列（B列）に
        # 「WS作成済み」にする命令　※ここは命令だけでAPIはまだしない！
        #-----------------------------------------------
        self.logger.info("クリニック一覧シートのステータス更新を開始します")
        
        #APIにリクスストする内容をまとめる　List[Dict]と決まっている！このセルに何を書くかを追加する
        status_update_requests: List[Dict] = []
        
        #クリニック一覧シートの各行をチェック
        #enumerate(clinic_list_rows)のインデックスと要素（各業のリスト）を同時に取り出す
        #enumerate() は「インデックス番号」と「要素」を同時に取得できる関数
        for row_index, row_data in enumerate(clinic_list_rows[1:],start=1): #ヘッダーを除外
            #リストの中のクリニック名が入っているのは最初の列
            clinic_name_in_list = row_data[0] #０列目はクリニック名
            #もし作ったシートの中にリストの中のクリニック名があったら
            if clinic_name_in_list in created_ws_names:
                
                #WS作成済みという命令をここで出す
                status_cell_request = {
                    #セルの内容を変更する命令
                    "updateCells":{
                        #１行分のセルの内容だけを作成している（どこに書くかはまだ決めていない）
                        "rows":[{"values":[{"userEnteredValue":{"stringValue":"WS作成済み"}}]}],
                        #入力値だけを更新する
                        "fields": "userEnteredValue",
                        "start":{
                            "sheetId": clinic_list_sheet_id,
                            #セルの位置を指定　※for文でとってきた行
                            "rowIndex": row_index,
                            "columnIndex": status_column_index
                        }
                    }
                }
                
                status_update_requests.append(status_cell_request)
                self.logger.info("ステータス更新のリクエストが作成されました")
                
        return status_update_requests
    
    
    

    def clinic_list_status_update(self,spreadsheet_id: str, status_update_requests: list[Dict]) -> None:  #ここでは何も返さないから
        #=========================================================
        # ７つ目のフロー：ステータス更新命令の実行
        # 作成した命令をbatchUpdateで一括実行
        #=========================================================
        self.logger.info("クリニック一覧シートのステータス更新を開始します")
        
        status_update_body = {"requests":status_update_requests}
        
        try:
            self.service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=status_update_body).execute()
            
            self.logger.info("クリニック一覧シートのステータス更新が完了しました\n"
                            f"作成WS命令数：{len(created_ws_names)}\n"
                            f"ステータス更新命令数：{len(status_update_requests)}")
            
        except Exception as e:
            self.logger.error(f"ステータス更新のエラーが発生しました：{e}")
            #処理停止
            raise








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
    
    print("書き込み命令数：",len(cell_write_requests))
    
    print("４つ目フロー確認完了！🦷")
    
    #-----------------------------------------------
    # 5つ目のフロー：データ書き込みを一括で実行！
    #-----------------------------------------------
    write_result = writer.write_cells_batch(spreadsheet_id=spreadsheet_id,sheets_api_batch_requests=cell_write_requests)
    if write_result is None:
        print("書き込みに失敗しました")
    print("5つ目のフローが実行されました")
    
    
    #-----------------------------------------------
    #クリニック一覧のシートIDを取得 
    #-----------------------------------------------
    print("クリニック一覧のIDを取得します")
    sheet_title = "テスト一覧"
    clinic_list_sheet_id = writer.get_sheet_id_by_title(spreadsheet_id=spreadsheet_id,sheet_title=sheet_title)
    
    # sheet_id_mapを確認
    print(sheet_id_map)
    
    print("クリニック一覧のID取得に成功しました")
    
    #-----------------------------------------------
    # 6つ目のフロー：ステータスの更新命令
    #-----------------------------------------------
    #仮で準備して確認
    clinic_list_rows = [
    ["クリニック名", "ステータス"],  # ヘッダー
    ["リベ大デンタルクリニック", ""],
    ["ハニーチュロ歯科", ""],
]

    
    #作成済みWSの名前のリスト　３つ目のフローから持ってきた
    created_ws_names = list(sheet_id_map.keys())
    #命令
    status_update_requests = writer.make_status_update_requests(
        clinic_list_sheet_id = clinic_list_sheet_id,
        created_ws_names= created_ws_names,
        clinic_list_rows = clinic_list_rows,
        status_column_index = 1
    )
    
    print("６つ目フロー：ステータスの更新命令を作成")
    pprint(status_update_requests)
    
    #-----------------------------------------------
    # 7つ目のフロー：ステータス更新を一括実行
    #-----------------------------------------------
    print("７つ目の【フロー：ステータス更新を実行します")
    
    writer.clinic_list_status_update(
        spreadsheet_id=spreadsheet_id,
        status_update_requests=status_update_requests
    )
    
    print("7つ目のフロー：ステータス更新が完了しました")
    