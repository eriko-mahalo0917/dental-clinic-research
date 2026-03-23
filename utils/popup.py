############################################
#Pythonのインタプリタや実行環境（OS）に関する情報にアクセス・操作するための標準ライブラリ
import sys
#PySideの基本
from PySide6.QtWidgets import QApplication, QMessageBox
#窓の「最善画面固定」などの細かい設定(属性)を読み込む
from PySide6.QtCore import Qt

############################################

#PySide6を使用して、OSを問い合わすポップアップができる!
def show_completion_popup(count: int):
    #①アプリを動かすためのエンジンを起動する
    #既にエンジンが存在すれば←側を使い、存在しなければ新しいエンジンを作る
    app = QApplication.instance() or QApplication(sys.argv)
    
    #②メッセージボックスを作る
    msg_box = QMessageBox()
    
    #③メッセージボックスのタイトルと内容をセットする
    msg_box.setWindowTitle("リサーチ完了")
    msg_box.setText("スプレッドシートの書き込みが完了しました！")
    
    #メインメッセージの補足を下に出す
    msg_box.setInformativeText(f"今回の処理件数は{count}件です。\n確認したらOKを押してください。")
    
    #④アイコンを「お知らせ(!マーク)」にする
    msg_box.setIcon(QMessageBox.Information)
    
    #⑤OKボタンを表示させる ※OKはダメ!Okと書くと決まっている
    msg_box.setStandardButtons(QMessageBox.Ok)
    
    #
    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)    
    
    #⑦一番前に窓を表示させる
    msg_box.show()           # 画面に出す
    msg_box.activateWindow() # WindowsやMacのシステム全体で一番手前に持ってくる
    msg_box.raise_()         # 自分のアプリの中で一番上に持ってくる
    
    #⑧メッセージボックスを表示し、ユーザーが閉じるまでプログラムをここで待機させる
    msg_box.exec()
    
    
#-------------テスト---------------
if __name__ == "__main__":
    show_completion_popup(10)