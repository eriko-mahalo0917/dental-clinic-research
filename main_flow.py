#=========================================================
#インポート
import os

#logger
from utils.logger import SimpleLogger

#スプシからデータを読み取る
from google_apis.sheets_reader import SheetReader
#Google Maps APiからデータを取得する
from google_apis.gmaps_api import GoogleMapsAPI
#基本情報と口コミを1つのデータにまとめる
from models.clinic_data_flow import ClinicDataFlow
#スプシへデータを書き込みする
from google_apis.sheets_writer import SheetWriter
#=========================================================

class MainFlow:
    def __init__(self):
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()
        

    def run(self):
        #-----------------------------------------------
        #１つ目のフロー：スプシからクリニック名を取得する
        #-----------------------------------------------    
        
        
        #-----------------------------------------------
        #2つ目のフロー：GoogleMapAPIからデータを取得する
        #-----------------------------------------------    
        
        
        #-----------------------------------------------
        #3つ目のフロー：データを渡せる形に整える
        #----------------------------------------------- 
        
        
    
        #-----------------------------------------------
        #4つ目のフロー：スプシにシート作成　＋　ステータス更新
        #----------------------------------------------- 