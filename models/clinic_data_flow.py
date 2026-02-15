#=========================================================
#インポート
import os
import sys
#型ヒント用：戻り値が分かりやすくなるように
from typing import Dict, Optional, List

#自作分のお呼び出し
#ログ
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.logger import SimpleLogger
#=========================================================

class ClinicDataFlow:
    def __init__(self):
        #logger
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()

    #完成形はDictだから->Dict
    def make_sheet_data(self, clinic_name: str, place_detail: Optional[Dict], reviews: Optional[List[Dict]]) ->Dict:
        #-----------------------------------------------
        # １つ目のフロー
        # 取得した基本情報と口コミを1つのデータにまとめる
        #-----------------------------------------------
        
        #１行分のデータを準備（テンプレートを準備している状態）
        clinic_sheet_data = {
            "クリニック名": clinic_name, 
            "住所": "", 
            "電話番号": "", 
            "ホームページURL": "", 
            "評価": "", 
            "総合レビュー（総合評価）": "", 
            "口コミ_1": "",
            "口コミ_2": "",
            "口コミ_3": "",
            "口コミ_4": "",
            "口コミ_5": ""
        }
        
        #基本情報がある場合だけ上書き,なければ空白のままにして
        if place_detail:
            clinic_sheet_data["住所"] = place_detail.get("address", "")
            clinic_sheet_data["電話番号"] = place_detail.get("phone", "")
            clinic_sheet_data["ホームページURL"] = place_detail.get("website", "")
            clinic_sheet_data["評価"] = place_detail.get("rating", "")
            clinic_sheet_data["総合レビュー（総合評価）"] = place_detail.get("review_count", "")
            
        #口コミは最大５件まで
        if reviews:
            """
            口コミ３件 → len(reviews) = 3
            min(5, len(reviews)) は５回までループ ※APIは5件までした取得しないけど、変更されたとき用
            range(...) len(reviews)の回数をforで回す
            """
            for i in range(min(5, len(reviews))):
                """
                f"口コミ_{i+1}" = "口コミ_1" →forで回すたびに増えていく
                reviews[i] は口コミのリストで１件目を辞書に入れていく
                .get("text", "")はあればテキストで返して、なければ空白で返す
                """
                clinic_sheet_data[f"口コミ_{i+1}"] = reviews[i].get("text", "")
                
        self.logger.info("スプレッドシート1行分のデータを作成しました")
        return clinic_sheet_data