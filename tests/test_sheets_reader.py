#============================================================
#インポート 
import pytest
import os
import sys
#ファイルやフォルダの住所を扱うためのモジュール
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#SheetReaderのクラスを読み込む
from google_apis.sheets_reader import SheetReader

#モックをインポート
from unittest.mock import patch, MagicMock
#============================================================

def test_get_json_path():
    #SheetReaderのインスタンスを作成
    #_get_json_pathはこのクラスのメソッド！
    reader = SheetReader()
    
    #メソッドを呼び出して、代入する
    json_path = reader._get_json_path()
    
    #----------ここから下はチェックするところ-----------------
    """
    ①isinstance(x, T)
    → 「x が型 T のインスタンスかどうか」をチェックして
    → True / False を返す “関数”
    ② assert 条件式
    → 「その条件が True であることを保証する」
    → False ならその場で AssertionError が起きる
    ※_get_json_path() が「Path オブジェクト」を返しているか確認する！
    """
    assert isinstance(json_path, Path)
    
    #nameはPathオブジェクトが標準で持っているプロパティ
    assert json_path.name == "creds.json"
    
    #そのPathに実際にファイルが存在するのかをチェック
    assert json_path.exists()
    
#=============================================================
"""
pytest の fixture（フィクスチャ）
・各テストの前に自動で実行される
・テスト関数の引数に「mock_reader」と書くだけで
新しいSheetReaderインスタンスがpytestから渡される！
"""
@pytest.fixture
def mock_reader():
    return SheetReader()

#①モック化してダミーパスを返す
def test_creds(mock_reader):
    #実際のファイルパスは参照せずに外部連携をテストできる
    mock_reader._get_json_path = MagicMock(return_value = "dummy/path/creds.json")
    
#②モック化して本当のGoogleと鍵を生成しないようにする
#本物の from_service_account_file() を “モック（偽物）” に差し替える
    with patch("google.oauth2.service_account.Credentials.from_service_account_file") as mock_from_file:
    #MagicMock のインスタンス作成
        fake_creds = MagicMock()
        mock_from_file.return_value = fake_creds
    
        #----------実行--------------------
        # creds() を呼ぶと、内部で _get_json_path() と Credentials.from_service_account_file(...) が呼ばれるはず
        result = mock_reader.creds()
    
        #----------チェック-----------------
        mock_reader._get_json_path.assert_called_once()
    
        mock_from_file.assert_called_once_with(
            "dummy/path/creds.json",
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
    
        #戻り値がモックのfack_credsになっていることを確認
        assert result is fake_creds