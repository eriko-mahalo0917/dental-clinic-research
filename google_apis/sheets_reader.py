#=========================================================
#インポート
import gspread
import os
from dotenv import load_dotenv #直接呼び出す

#JSONファイルを読み込みするためのモジュール
from google.oauth2.service_account import Credentials
#logger
from utils import logger
#Pathを使うため
from pathlib import Path

#.envから設定を読み込むための
#from utils.env_loader import config　#直接呼ぶからコメントアウト
#=========================================================

class SheetReader:
    def __init__(self):
        #utils/logger.py のロガー（SimpleLogger）をセットアップする
        self.logger_setup = logger.SimpleLogger()
        self.logger = self.logger_setup.get_logger()
        
        #１つ目のフロー
        #.envの場所を特定　Path(__file__)はファイル自身の住所！
        self.env_path = Path(__file__).parents[1]
        dotenv_path = self.env_path/".env"
        load_dotenv(dotenv_path)
        
        #承認&実行
        #リスト：実行していいよの定型文みたいなもの
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        #２つ目のフロー
        #開きたいスプレッドシートのIDを取得する
        try:
            self.logger.info("SPREADSHEET_IDを取得します")
            #jsonファイルは一時的に保存？ちょっとよく分からない
            json_path_from_env = os.getenv("SERVICE_ACCOUNT_FILE_PATH")
            self.spreadsheet_id = os.getenv("SPREADSHEET_ID")
            
            
        
        
        
        
        #３つ目のフロー
        #スプレッドシートを読み取る
        
        
        