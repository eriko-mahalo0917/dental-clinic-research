#=================================================
"""
configファイルにAPIキーとURLとIDの一つの窓口として
load_dotenv()で呼び出してあげる
"""
import os
from dotenv import load_dotenv
from utils.path_helper import get_env_path

#.envファイルを読み込む
load_dotenv(get_env_path())

#=================================================
#スプレッドシート設定 (.envから取得)
#=================================================
SPREADSHEET_URL = os.getenv("SPREADSHEET_URL")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")


#=================================================
#シート内の設定(固定値)
#=================================================
CLINIC_SHEET = "クリニック一覧"
CLINIC_KEY = "クリニック名"
STATUS_KEY = "ステータス"