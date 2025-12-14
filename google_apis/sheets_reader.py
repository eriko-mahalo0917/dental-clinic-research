#=========================================================
#インポート
#スプレッドシートを操作できるように
import gspread
import os
import sys
#表（DataFrame）に変換するため
import pandas as pd
#型ヒントで辞書と教えるため
from typing import Dict

#JSONファイルを読み込むため
from google.oauth2.service_account import Credentials
#ファイルやフォルダの住所を扱うためのモジュール
from pathlib import Path

#お隣のutilsのPathを指定するために必要　アブソルートパス
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../")))
#logger
from utils.logger import SimpleLogger

#==========================================================

class SheetReader:
    def __init__(self):
        #logger
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()
        
        #Noneで初期化 空っぽだから、まだ接続していないと分かる
        #１〜３のフローで毎回接続が必要になるから、最初に__init__に入れる
        self.client = None
        self.spreadsheet_id = None
    
    #-----------------------------------------------
    # １つ目のフロー：API連携
    #----------------------------------------------- 
    #jsonファイルのパスを取得
    def _get_json_path(self):
        #.envファイルから"creds.json"を名前を見つけて取り出す
        json_name = "creds.json"
        self.logger.info(f"JSONファイル名: {json_name}")
        
        #ここから.envがあるフォルダのパスを教える！親の親
        parents_dir = Path(__file__).parents[1]
        self.logger.info(f"親ディレクトリ: {parents_dir}")
        
        #Pathlibでフォルダとファイル名を結合して、ここだよ〜！って教える！
        json_path = parents_dir / json_name
        self.logger.info(f"JSONファイルのフルパス: {json_path}")
        
        #creds.jsonまでのパスを返す！
        return json_path
    
# ------------------------------------------------------------    
    #スプシの認証プロパティ
    #json_key_nameは"creds.json"の秘密ファイル
    #型ヒント：文字列　※これはオーオース・ツー
    def creds(self):
        #この秘密ファイルで認証してねでscopeをする
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        
        #ファイルの住所を特定する　
        #同じクラス内の_get_json_path() メソッドを呼び出し
        json_key_path = self._get_json_path()
        
        #鍵の生成
        creds = Credentials.from_service_account_file(json_key_path, scopes=SCOPES)
        
        #戻り値
        return creds

# ------------------------------------------------------------ 
    #スプシアクセスのプロパティ
    #さっき作った『鍵（creds）』を使って、Googleスプレッドシートの世界に『接続（ログイン）』する」 メソッド
    def get_client(self):
        #同じクラス内の creds()メソッドを呼び出し
        creds = self.creds()
        #その関数の処理を使ってgspreadログインし、Clientを作成！
        client = gspread.authorize(creds)
        return client
    
# ------------------------------------------------------------    
    #対象のスプシを開く
    def _get_gsheet_df_to_gui(
        self,
        gui_info: Dict, 
        sheet_url: str, 
        worksheet_name: str
        ):
        
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
        
        #ワークシートの全テータをゲットせよの関数！これはgspreadのメソッド
        all_values = worksheet.get_all_values()
        self.logger.debug(f"ワークシート全データ：\n{all_values}")
        
        #シートのデータを辞書リストとして取得
        #１行目をヘッダーとして使って、{名：値}にする
        #空白が列名の１列目に空白があると失敗するので注意
        dict_data = worksheet.get_all_records()
        
        df = pd.DataFrame(dict_data)
        #ヘッダー行＋最初の5行だけ表示する
        self.logger.info(f"スプレッドシート読み込み完了！：\n{df.head()}")
        return df
    
    #-----------------------------------------------
    #２つ目のフロー
    #-----------------------------------------------
        """
        取得した歯医者さんの名前を全てDataFrameとして読み込む
        ①１つ目もフローの全データを再利用
        ②クリニック名の列を取り出す
        """
    def get_clinic_name_df(
        self,
        gui_info: Dict, 
        sheet_url: str, 
        worksheet_name: str,
        clinic_column: str
        )-> pd.DataFrame:
        
        #①１つ目にフローを呼び出して利用して全データを取得したものをdf_allに代入する
        df_all = self._get_gsheet_df_to_gui(
            gui_info=gui_info,
            sheet_url=sheet_url,
            worksheet_name=worksheet_name
            )
        
        #②クリニックの列を指定する
        try:
            #[[]]は二次元らしい！そしてこれは縦だけをdfとして取り出す！
            clinic_df = df_all[[clinic_column]]
            self.logger.info(f"{clinic_column}の取得に成功しました！")
            return clinic_df
        except Exception as e:
            #指定した列が存在しない場合＋何が指定できるのかを１行目を表示してリストで出す
            self.logger.error(f"{clinic_column}の列が存在しません！\n利用可能な列は{list(df_all.columns)}")
            #処理停止
            raise
        
        
        
    #-----------------------------------------------
    #３つ目のフロー
    #-----------------------------------------------
    #２つ目で取得したDataFrameを受け取る
    #DataFrameをチェックし、入力済みのステータスがない行だけを抽出
    #抽出したデータから、クリニック名のリストを返す


#〜〜〜〜実行〜〜〜〜
if __name__ == "__main__":

    instance_sheet_reader = SheetReader()
    # JSONファイルのパスを取得
    json_path_from_env = instance_sheet_reader._get_json_path()
    print(f"JSON Path from .env: {json_path_from_env}")   
    
   
    TEST_URL = "https://docs.google.com/spreadsheets/d/1PrESjDHuqNpsZfo-fvd6hb8tOuAXl63aDio7hdjt6hg/edit?gid=1025571184"
    TEST_SHEET = "クリニック一覧"  
    CLINIC_COLUMN = "クリニック名" 
    
    # df_all を取得
    df_all = instance_sheet_reader._get_gsheet_df_to_gui(
        gui_info={},
        sheet_url=TEST_URL,
        worksheet_name=TEST_SHEET
    )

    print("--- df_all 取得成功 ---")
    print(df_all.head())

    try:
        clinic_df = df_all[[CLINIC_COLUMN]]
        print(f"--- {CLINIC_COLUMN} 列抽出成功 ---")
        print(clinic_df.head())
    except Exception as e:
        print(f"列 {CLINIC_COLUMN} が存在しません！")
        print(f"利用可能な列: {list(df_all.columns)}")
        raise

    print("--- クリニック名 DataFrame 取得完了 ---")
