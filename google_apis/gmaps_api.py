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

from dotenv import load_dotenv
load_dotenv()
#=========================================================

class GoogleMapsAPI:
    def __init__(self):
        #logger
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()
        
        #APIキーの取得（.envにある）
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        
    #レシーブ！受け取るだけど、ちょっとしっくり来ないから検討中！
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
        
    
    def search_clinic(self, clinic_name: str) ->Optional[Dict]:
        #-----------------------------------------------
        # ２つ目のフロー　※検索して結果を丸ごと取得しただけのフロー
        # GoogleMapsのAPIでクリニックを検索する！
        #見つからなかったらNoneを返す　
        #-----------------------------------------------
        #みんな共通のもの！GoogleMapsAPI（Text Search）のエンドポイント
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        
        #APIにパラメーターを渡す　これはよく使う基本のパラメーター！
        #検索ワード、日本語、APIキー
        params = {"query": clinic_name,"language": "ja" ,"key":self.api_key}
        
        try:
            self.logger.info(f"検索を開始します")
            
            #GoogleMapのAPIにリクエストする
            #最大10秒待機！それ以上はタイムアウトでエラー
            response = requests.get(url, params=params, timeout=10)
            
            #HTTPのエラーが分かるメソッド！（認証エラーや見つからないや回数制限とか）
            response.raise_for_status()
            #レスポンスのJSONを辞書にしたもの
            return response.json()
        
        #通信系エラーのために用意されているもの
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Google Maps APIの検索エラー:clinic_name={clinic_name}\n {e}")
            
            #処理停止になったら、止まってしまうため、エラー時はNoneを返して処理を続ける！
            return None     
        
    #２つ目のフローからゲットした結果を引数に入れていて辞書型！Optional[str]は戻り値が文字列かもしれないし、Noneかもしれない！
    def get_place_id(self,search_result_json: Dict) -> Optional[str]:
        #-----------------------------------------------
        # ３つ目のフロー
        # 検索結果からplace_idを取得する
        # 見つからない場合はNoneを返す
        #-----------------------------------------------
        
        if search_result_json is None:
            self.logger.info("検索結果がNoneです")
            return None
        
        #検索結果のリストを取得する。存在しなければ空のリストを返す
        """
        .get("results", []) は 辞書の標準メソッド
        ①辞書に"results"というキーがあればその値を返す
        ②キーが存在しないときは第２引数の値の空っぽリストを返す
        """
        results = search_result_json.get("results",[])
        
        
        if not results:
            self.logger.info("検索結果にplace_idが存在しません")
            return None
        
        #最初の候補の place_id を取得
        place_id = results[0].get("place_id")
        if not place_id:
            self.logger.info("place_idが取得できませんでした") 
            return None
        
        self.logger.info("place_idが取得しました！：成功")
        return place_id
        
        
        
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
    
    #-----------------------------
    #テスト①：１つ目のフロー単体
    #-----------------------------
    #正常なクリニック名　※ここではただ単にクリニック名を入れたときのテスト
    result = api.receive_clinic_name("テストクリニック")
    print("テスト①：",result)
    
    #空っぽだったらNoneのテスト　レシーブは受け取る！
    result = api.receive_clinic_name("")
    print("テスト②：",result)
    
    #-----------------------------
    #テスト②：１つ目のフロー sheets_reader.pyでのクリニック名を受け取る
    #-----------------------------

    #sheet_reader.pyからちゃんと受け取れているかチェック
    from sheets_reader import SheetReader
        
    reader = SheetReader()
        
    TEST_URL =  "https://docs.google.com/spreadsheets/d/1PrESjDHuqNpsZfo-fvd6hb8tOuAXl63aDio7hdjt6hg/edit?gid=1025571184#gid=1025571184"
    TEST_SHEET = "テスト一覧"
    CLINIC_KEY = "クリニック名"
    STATUS_KEY = "ステータス"
        
    df_all = reader.get_clinic_name_df( sheet_url=TEST_URL, worksheet_name=TEST_SHEET )
    clinic_list = reader.get_status_none_clinic_name_list(df=df_all, status_key=STATUS_KEY,clinic_key=CLINIC_KEY)
    
    #-----------------------------
    #テスト③：１つ目のフロー →　２つ目のフロー
    #-----------------------------
    for clinic_name in clinic_list:
        clinic_name_for_search = api.receive_clinic_name(clinic_name)
        
        response_json = api.search_clinic(clinic_name_for_search)
        
        #もし空っぽだったら！==でもいいけど、１つしか尊意しないからisの方が良い
        if response_json is None:
            print("→ 検索エラー")
            continue
        
        print("→ 検索成功")
        #これはAPIのステータスを見ているという意味
        print("status:", response_json.get("status"))
        #どんなの取得しているか全部見てみたいから出力してみる！
        print(response_json)
    
    
    #-----------------------------
    #テスト④：１つ目のフロー →　２つ目のフロー　→　３つ目のフロー
    #-----------------------------
