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
#configを呼び出す
import config
#=========================================================

class MainFlow:
    def __init__(self):
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()
        

    def dental_clinic_research_run(self):
        #-----------------------------------------------
        #１つ目のフロー：スプシからクリニック名を取得する
        #----------------------------------------------- 
        self.logger.info("クリニック一覧のリサーチを開始します！")  
        
        #インタンス作成
        sheet_reader = SheetReader()
        
        #①対象のスプシを開く
        df_all = sheet_reader.get_gsheet_df(sheet_url=config.TEST_URL,worksheet_name=config.TEST_SHEET)
        
        #②ステータスが空白のクリニックを取得する
        clinic_name_list = sheet_reader.get_status_none_clinic_name_list(df=df_all, status_key=config.STATUS_KEY, clinic_key= config.CLINIC_KEY)
        
        self.logger.info(f"対象のクリニック数：{len(clinic_name_list)}件")
        
        #-----------------------------------------------
        #2つ目のフロー：GoogleMapAPIからデータを取得する
        #-----------------------------------------------    
        #インスタンス作成
        google_maps_api = GoogleMapsAPI()
        
        #３つ目のインスタンス作成　※forの中に入ってしまって、何回を生成してしまっているのでここに
        clinic_data_flow = ClinicDataFlow()
        
        #取得したデータをリストにまとめる
        clinic_sheet_data_list = []
        
        #クリニックを１件ずつ検索をする
        for clinic_name in clinic_name_list:
            
            #①クリニック名で検索（Text Search）
            search_clinic_data = google_maps_api.search_clinic(clinic_name)
            if not search_clinic_data:
                continue
            
            #②検索結果からplace_idを取得
            place_id = google_maps_api.get_place_id(search_clinic_data)
            if not place_id:
                continue
            
            #③place_idを使って詳細情報を取得
            place_detail = google_maps_api.get_place_id_detail(place_id)
            
            #④レビューを取得　デフォルトで待10秒
            reviews = google_maps_api.get_place_reviews(place_id)
        
        
            #-----------------------------------------------
            #3つ目のフロー：データを渡せる形に整える
            #----------------------------------------------- 
            
            #１店舗を１行にして渡せるように
            clinic_sheet_data = clinic_data_flow.make_sheet_data(clinic_name = clinic_name,place_detail = place_detail,reviews = reviews)
            
            #取得したデータを入れるリストに追加
            clinic_sheet_data_list.append(clinic_sheet_data)
            
        if not clinic_sheet_data_list:
            self.logger.info("処理対処のクリニックがありませんでした")
            return
            
            
        #-----------------------------------------------
        #4つ目のフロー：スプシにシート作成　＋　ステータス更新
        #----------------------------------------------- 
        sheet_writer = SheetWriter()
        
        #①Google Sheet APIに接続
        sheet_writer.connect_spreadsheet()
        
        #②WS作成のリクエストを作る
        add_sheet_requests = sheet_writer.make_add_sheet_request(clinic_sheet_data_list = clinic_sheet_data_list)
        
        #③WS作成を実行　＋　sheet_id_mapを取得　_,はadd_sheet_batch_responseで今回は不要だからこれ！タプル！
        _,sheet_id_map = sheet_writer.create_worksheets_batch(spreadsheet_id = config.SPREADSHEET_ID, add_sheet_requests= add_sheet_requests)
        
        #④クリニックのデータをセルに書き込むリクエストを作成
        cell_write_requests = sheet_writer.make_cell_write_requests(clinic_sheet_data_list = clinic_sheet_data_list, sheet_id_map= sheet_id_map)
        
        #⑤セルにデータの書き込みを実行
        sheet_writer.write_cells_batch(spreadsheet_id = config.SPREADSHEET_ID, sheets_api_batch_requests = cell_write_requests)
        
        #⑥クリニック一覧のsheet_idを取得する
        clinic_list_sheet_id = sheet_writer.get_sheet_id_by_title(spreadsheet_id = config.SPREADSHEET_ID,sheet_title =config.TEST_SHEET)
        
        #⑦ステータスを更新するリクエストを作成
        #③で作成した中から
        created_ws_names = list(sheet_id_map.keys())
        status_up_data_requests = sheet_writer.make_status_update_requests(clinic_list_sheet_id = clinic_list_sheet_id,created_ws_names = created_ws_names,clinic_list_rows = df_all.values,status_column_index = 1)
        
        #⑧ステータスの更新を実行
        sheet_writer.clinic_list_status_update(spreadsheet_id = config.SPREADSHEET_ID, status_update_requests = status_up_data_requests)
        
        self.logger.info("クリニック一覧のリサーチが完了しました！")