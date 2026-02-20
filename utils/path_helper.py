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
    return Path(__file__).resolve().parent.parent