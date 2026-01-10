#=========================================================
#インポート
import os
import sys
#APIでエラーが出たときのために
import time

#型ヒント用：戻り値が分かりやすくなるように　辞書かも！Noneかも！
from typing import Dict, Optional

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
        search_results = search_result_json.get("results",[])
        
        
        if not search_results:
            self.logger.info("検索結果にplace_idが存在しません")
            return None
        
        #最初の候補の place_id を取得
        place_id = search_results[0].get("place_id")
        if not place_id:
            self.logger.info("place_idが取得できませんでした") 
            return None
        
        self.logger.info("place_idが取得しました！：成功")
        return place_id
        
    #辞書かも知れないし、空かもしれない！
    def get_place_id_detail(self, place_id: str) -> Optional[Dict]:
        #-----------------------------------------------
        # ４つ目のフロー
        # place_id を使って基本情報を取得する
        # ・住所
        # ・電話番号
        # ・ホームページURL
        # ・評価
        # ・レビュー総数
        #-----------------------------------------------
        if not place_id:
            self.logger.info("place_idが空のため詳細取得をスキップします!")
            return None
        
        self.logger.info("place_idの詳細を取得します!")
        
        #APIリクエストをする
        #place_id を使って「詳細情報」を取得するためのエンドポイント
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "language": "ja",
            "fields": "formatted_address,formatted_phone_number,website,rating,user_ratings_total",
            "key": self.api_key
        }
        
        detail_response = requests.get(url, params=params)
        #200はHTTPステータスコードで成功したときのステータス!だから成功しなかったときはの話
        if detail_response.status_code != 200:
            self.logger.error("HTTPリクエストに失敗しました")
            return None
        
        #リクエストの結果をJOSN形式で受け取る
        detail_response_json = detail_response.json()
        
        #result(リクエスト結果)を取得する　※APIレスポンス：欲しい情報はすべて"result"の中に入っている
        detail_result = detail_response_json.get("result",{})
        if not detail_result:
            self.logger.info("APIレスポンスにresultが存在しません")
            return None
        
        #必要な項目をゲットして抜き出す
        place_detail = {
            "address":detail_result.get("formatted_address"),
            "phone": detail_result.get("formatted_phone_number"),
            "website": detail_result.get("website"),
            "rating": detail_result.get("rating"),
            "review_count": detail_result.get("user_ratings_total")
        }
        
        self.logger.info("詳細情報を取得しました")
        return place_detail
    
    
    def get_place_reviews(self, place_id: str, timeout: int = 10) -> Optional[list]:
        #-----------------------------------------------
        #５つ目のフロー
        #・place_id を使って口コミを取得する
        #・コメントが空の口コミも含める（最大５件までしか取得できない）
        #・10秒待機を追加
        #-----------------------------------------------
        if not place_id:
            self.logger.info("place_idが空のため、口コミ取得をスキップします")
            return None
        
        self.logger.info("口コミ情報を取得します")
        
        #place_id を使って「詳細情報」を取得するためのエンドポイント
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "reviews",
            "language": "ja",
            "key": self.api_key
        }
        
        
        try:
            self.logger.info("口コミの情報を取得します")
            reviews_response = requests.get(url, params=params, timeout=timeout)
            #リクエストにある標準モジュールでエラー判定
            reviews_response.raise_for_status()
            
            #JSON型に変換し、結果があれ第一引数として結果を受け取り、なければ空の辞書として受け取る
            review_result = reviews_response.json().get("result", {})
            #reviewがなければ空のリスト　※口コミがもともとリストだから
            reviews = review_result.get("reviews", [])
            self.logger.info(f"口コミを{len(reviews)}件取得しました")
            #reviewがあればそれを返して、なければ空リストを返してね！
            return reviews if reviews else []
        
        #通信系エラーのために用意されているもの
        except requests.exceptions.RequestException as e:
            self.logger.error(f"口コミ取得エラー：{e}")
            return None       
        
        
        """
        ##################これは10秒待機がないパターン##################
        reviews_response = requests.get(url, params=params)
        
        #HTTPのエラー判定
        if reviews_response.status_code != 200:
            self.logger.error("口コミの取得APIでHTTPエラーが発生しました")
            return None
        
        #JSONに変換！リクエストの結果を辞書で受け取る
        reviews_response_json = reviews_response.json()
        
        #resultを取得する
        review_result = reviews_response_json.get("result", {})
        if not review_result:
            self.logger.info("APIレスポンスにresultが存在しません")
            return None
        
        #reviewsを取得　※なければカラリスト
        reviews = review_result.get("reviews", [])
        
        if not reviews:
            self.logger.info("口コミは存在しません（0件）")
            #口コミがないのはエラーじゃないからNoneじゃなくてリスト
            return []
        
        self.logger.info(f"口コミを{len(reviews)}件取得しました")
        return reviews
        ###########################################################
        """



#〜〜〜〜〜実行〜〜〜〜〜〜
if __name__ == "__main__":
    #インスタンス
    api = GoogleMapsAPI()
    
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
    #テスト③：１つ目のフロー →　２つ目のフロー →３つ目のフロー
    #-----------------------------
    #①受け取り
    for clinic_name in clinic_list:
        clinic_name_for_search = api.receive_clinic_name(clinic_name)
        if clinic_name_for_search is None:
            print("クリニック名が空っぽ")
            continue
        
        #②APIで検索---------------------------------------
        response_json = api.search_clinic(clinic_name_for_search)
        #もし空っぽだったら！==でもいいけど、１つしか尊意しないからisの方が良い
        if response_json is None:
            print("→検索エラー")
            continue
        
        print("→ 検索成功")
        #これはAPIのステータスを見ているという意味
        print("status:", response_json.get("status"))
        
        #③place_idを取得----------------------------------
        results = response_json.get("results",[])
        if not results:
            print("→検索結果なし：resultsが空っぽ")
            continue
        
        place_id = results[0].get("place_id")
        if not place_id:
            print("→place_idが存在しません")
            continue
        
        print("取得したplace_id:", place_id)
        
        #-----------------------------
        #テスト④：１つ目のフロー →　２つ目のフロー →３つ目のフロー →４つ目のフロー　→５つ目のフロー
        #place_id から詳細情報を取得
        #-----------------------------
        place_detail = api.get_place_id_detail(place_id)
        if place_detail is None:
            print("詳細情報が取得できませんでした")
            continue
    
        print("取得した詳細情報")
        print(place_detail)
        
        #５つ目のフロー------------------
        reviews = api.get_place_reviews(place_id)
        #値が存在しない
        if reviews is None:
            print("口コミが取得できませんでした")
            continue
        
        #review自体が存在しない０件
        if not reviews:
            print("口コミは存在しません")
            continue
        
        for review in reviews:
            author = review.get("author_name","名無し")
            rating = review.get("rating","評価なし")
            comment = review.get("text", "")
            print(f"コメント:{comment}")
            
        #６つ目のフロー------------------ 
        sheet_data = api.make_sheet_data(clinic_name=clinic_name_for_search, place_detail=place_detail, reviews=reviews)
        for key, value in sheet_data.items():
            print(f"{key}: {value}")