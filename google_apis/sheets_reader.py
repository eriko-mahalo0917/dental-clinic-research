#==========================================================
#path_helper.pyを使うからここでは不要
#スプレッドシートを操作できるように
import gspread

#表（DataFrame）に変換するため
import pandas as pd
#型ヒントで辞書と教えるため
#from typing import Dict

#JSONファイルを読み込むため
from google.oauth2.service_account import Credentials

#logger
from utils.logger import SimpleLogger
from utils.path_helper import get_creds_path

#==========================================================

class SheetReader:
    def __init__(self):
        #logger
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()
        
    #-----------------------------------------------
    # １つ目のフロー：API連携
    #-----------------------------------------------         
    def creds(self):
        #この秘密ファイルで認証してねでscopeをする
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        
        #ファイルの住所を特定する　
        #同じクラス内のget_json_path() メソッドを呼び出し
        json_key_path = get_creds_path()
        self.logger.info(f"JSONパス:{json_key_path}")
        
        #鍵の生成
        creds = Credentials.from_service_account_file(json_key_path, scopes=SCOPES)
        
        #戻り値
        return creds

    #-----------------------------------------------
    # スプシ接続
    #-----------------------------------------------
    #スプシアクセスのプロパティ
    #さっき作った『鍵（creds）』を使って、Googleスプレッドシートの世界に『接続（ログイン）』する」 メソッド
    def get_client(self):
        self.logger.info("APIクライアントに接続します")
        #同じクラス内の creds()メソッドを呼び出し
        creds = self.creds()
        #その関数の処理を使ってgspreadログインし、Clientを作成！
        client = gspread.authorize(creds)
        self.logger.info("APIクライアントの作成が完了しました")
        return client
    
    # ------------------------------------------------------------    
    #対象のスプシを開く
    def get_gsheet_df( self, sheet_url: str, worksheet_name: str ):
        
        """
        指定したGoogleスプレッドシートのURLとワークシートのデータを取得して
        PandasでDataFrameにして返すメソッド
        def get_clientで取得されたJSONを使って接続する
        """
        #同じクラス内のget_clientメソッドを呼び出して鍵をゲット
        client = self.get_client()
        
        #対象のスプレッドシートをURLで開き、対象のワークシートを取得する
        #どっちもgspreadのメソッド
        worksheet = client.open_by_url(url = sheet_url).worksheet(worksheet_name)
        
        self.logger.info("ワークシート全データを取得します")
        
        #シートの全データを辞書リストとして取得
        #１行目をヘッダーとして使った辞書　{名：値}にする
        #空白が列名の１列目に空白があると失敗するので注意
        dict_data = worksheet.get_all_records()
        
        df = pd.DataFrame(dict_data)
        #ヘッダー行＋最初の5行だけ表示する
        self.logger.info(f"スプレッドシート読み込み完了！：\n{df.head()}")
        return df
    
    #-----------------------------------------------
    #２つ目のフロー　全データをdfで取得する
    #-----------------------------------------------
    def get_clinic_name_df(self, sheet_url: str, worksheet_name: str)-> pd.DataFrame:
        """
        取得した歯医者さんの名前を全てDataFrameとして読み込む
        ①１つ目もフローの全データを再利用
        """
        #①１つ目にフローを呼び出して利用して全データを取得したものをdf_allに代入する
        df_all = self.get_gsheet_df( sheet_url=sheet_url, worksheet_name=worksheet_name )
        
        self.logger.info("一覧のシートの全データを取得しました")
        return df_all        
        
        
    #-----------------------------------------------
    #３つ目のフロー　今のWS名をすべて取得する ※今は使わないため、コメントアウト
    #-----------------------------------------------
    #def get_all_ws_name(self,sheet_url: str):
        #"""
        #①鍵をゲット
        #②スプシをURLで開く
        #③全てのワークシートを取得
        #④WS名をリストにする
        #"""
        
        #①同じクラス内のget_clientメソッドを呼び出して鍵をゲット
        #client = self.get_client()
        
        #②対象のスプレッドシートをURLで開く
        #どっちもgspreadのメソッド
        #spreadsheet = client.open_by_url(sheet_url)
        
        #self.logger.info(f"WS名を一覧で取得します")
        
        #③すべてのワークシート（タブ）を取得するメソッド
        #worksheets = spreadsheet.worksheets()
        
        #④ws名だけを取り出してリストにする
        #これはリスト内包表記！おまとめ式！wsの属性でタイトルだけを取得
        #ws_name_list = [ws.title for ws in worksheets] #ws.titleってすることでタイトルだけ取れる！大事！
        
        #self.logger.info(f"取得したWS名一覧：{ws_name_list}")
        #return ws_name_list
        
    
    #-----------------------------------------------
    #４つ目のフロー　スタータスが空白のクリニック名を取得する
    #-----------------------------------------------
    def get_status_none_clinic_name_list(self,df: pd.DataFrame, status_key: str, clinic_key: str) -> list:
        """
        ステータスが空白のクリニックを取得
        
        """
        self.logger.info("スタータス空白のクリニック名を取得します")
        
        #②ステータス空白を抽出
        #df["ステータス"]列だけ取り出す　
        status_none_df = df[df[status_key].astype(str).str.strip() == ""] #文字列にして、前後の空白を strip() で除去、空文字かどうかをTrue / False で判定
        clinic_name_list = status_none_df[clinic_key].tolist() #.tolist()でリストにしている
        return clinic_name_list

    


"""
#〜〜〜〜実行〜〜〜〜
if __name__ == "__main__":

    instance_sheet_reader = SheetReader()

    # ---------------------------------
    # ① JSONファイルのパス確認
    # ---------------------------------
    json_path = instance_sheet_reader.get_json_path()
    print(f"JSON Path: {json_path}")

    # ---------------------------------
    # テスト用定数
    # ---------------------------------
    TEST_URL = "https://docs.google.com/spreadsheets/d/1PrESjDHuqNpsZfo-fvd6hb8tOuAXl63aDio7hdjt6hg/edit?gid=1025571184#gid=1025571184"
    TEST_SHEET = "テスト一覧"
    CLINIC_KEY = "クリニック名"
    STATUS_KEY = "ステータス"

    # ---------------------------------
    # ② 全データ取得
    # ---------------------------------
    df_all = instance_sheet_reader.get_gsheet_df(sheet_url=TEST_URL,worksheet_name=TEST_SHEET)

    print("\n--- df_all 取得成功 ---")
    print(df_all.head())

    # ---------------------------------
    # ④ 空白のステータスのクリニック名を取得
    #  ---------------------------------
    no_status_clinic_list = instance_sheet_reader.get_status_none_clinic_name_list( df=df_all, status_key=STATUS_KEY, clinic_key=CLINIC_KEY )

    print("\n--- ステータス空白のクリニック名一覧 ---")
    print(no_status_clinic_list)
    
"""
