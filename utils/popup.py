import sys
import os
# PySide6のQtWidgets：ボタンやメッセージ箱などの部品を呼び出す
from PySide6.QtWidgets import QApplication, QMessageBox
# PySide6.QtCore:窓の属性で最前面に出したり、タイマーを制御する
from PySide6.QtCore import Qt, QTimer

# Mac専用のOS操作ライブラリの読み込み準備
# Windowsで動かしたときにエラーにならないようにtryにする
try:
    #もし実行しているOSがMac(darwin)だったときに専用のAppkitを取り出す
    if sys.platform == 'darwin':
        #NSApp:Macのときにこのアプリ自信を操作するためのオブジェクト
        #NSApplicationActivateIgnoringOtherApps：強制的に割り込みを許可する
        from AppKit import NSApp, NSApplicationActivateIgnoringOtherApps
except ImportError:
    #ライブラリにない環境でもプログラミングが止まらないようにする
    pass

############################################

# PySide6を使用して、リサーチ完了を知らせるポップアップを表示する
def show_completion_popup(count: int):
    # ①アプリを動かすためのエンジンを起動
    app = QApplication.instance() or QApplication(sys.argv)
    
    # ②メッセージボックスを作成
    msg_box = QMessageBox()
    
    # ③メッセージボックスのタイトルと内容をセットする
    msg_box.setWindowTitle("リサーチ完了")
    msg_box.setText("スプレッドシートの書き込みが完了しました！")
    #メインのメッセージの下に補足の内容を表示
    msg_box.setInformativeText(f"今回の処理件数は{count}件です。\n確認したらOKを押してください。")
    
    # ④アイコンを「お知らせ(!マーク)」にする
    msg_box.setIcon(QMessageBox.Information)
    # ⑤OKボタンを表示させる ※OKはダメ!Okと書くと決まっている
    msg_box.setStandardButtons(QMessageBox.Ok)
    
    # ⑥窓の属性をセットする
    #Qt.WindowStaysOnTopHint：他の窓より上に居続ける(Windowsで特に強力)
    #Qt.Tool：OSに「これはツールパネルだ」と伝え、重ね順の優先度を上げる
    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint | Qt.Tool)

    # ⑦【Mac専用：最強の試行錯誤】OSレベルで「他のアプリを無視して」自分を前に出す
    def force_activate():
        if sys.platform == 'darwin':
            try:
                # Mac：OS本体に対して「このアプリを強制的に最前面にして!」と命じる
                NSApp.activateIgnoringOtherApps_(True)
            except NameError:
                # pyobjcがインストールされていない場合の予備
                pass
        #⑧OS問わずに一番最前面にもってくる
        msg_box.activateWindow()      #WindowsやMacのシステム全体で一番手前に持ってくる
        msg_box.raise_()              #自分のアプリの中で一番上に持ってくる
        app.setActiveWindow(msg_box)  #アプリ全体で窓が一番主役としてOSに教える

    #窓が表示されるタイミングに合わせて、0.1秒後に強制的にアクティブにする
    #窓が作られる前に命令すると無視されるから、同時にすると負けちゃうから0.1秒後に主役にする
    #QTimerは時間の単位がミリ秒の扱いになる
    QTimer.singleShot(100, force_activate)
    
    # ⑦ 実行（表示して待機）
    msg_box.exec()

# -------------テスト用---------------
#if __name__ == "__main__":
#    show_completion_popup(10)