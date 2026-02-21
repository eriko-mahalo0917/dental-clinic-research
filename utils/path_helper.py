######exeファイルからjsonファイルとconfig.pyを呼び出すよ用#########

from pathlib import Path
import sys

##########################

def get_base_dir():
    
    #getattr(オブジェクト,属性名,デフォルト値　→　あるか分からない属性を、安全に取り出す係
    #sys frozenはこれってexeですか？　→　Falseではい！
    if getattr(sys, 'frozen', False):
        
        #sys._MEIPASS（PyInstallerが実行時に sys に追加した属性）
        #exeの中身が今使われているフォルダの場所パスだけ返す
        return Path(sys._MEIPASS)
    
    #Pythonで実行したときはこのファイルを見てね
    return Path(__file__).parents[1]

def get_config_dir():
    #config.pyのディレクトリのパスを返す
    return get_base_dir()/"config"

def get_creds_path():
    #cread.jsonのパスを返す
    return get_base_dir()/"cread.json"

def get_env_path():
    #.envのパスを返す
    return get_base_dir()/".env"