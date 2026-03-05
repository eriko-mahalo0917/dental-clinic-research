# Windows用 EXE作成手順書

## 🎯 目的

`dental-clinic-research` フォルダから
`Dental-Clinic-Research.exe` を作成します。

---

## ✅ 事前準備

* Python がインストールされていること
* 受け取ったZIPファイルがあること

※ Pythonアプリを直接開く必要はありません。
すべて「コマンドプロンプト」で操作します。

---

## ① ZIPファイルを解凍する

1. ZIPファイルを **デスクトップ** に保存
2. 右クリック
3. 「すべて展開」をクリック
4. `dental-clinic-research` フォルダができていることを確認

---

## ② コマンドプロンプトを開く

1. **Windowsキー + R**
2. `cmd` と入力
3. Enterキー

（補足）
✅ パターン①：Microsoft Remote Desktop の場合
Macキーボードの：
command ⌘ → Windowsキーとして扱われる
だから`⌘ + R`で「ファイル名を指定して実行」が開くことが多い。

✅ 確実な方法（キーボードに頼らない）
Windows画面の左下の：
🔍 検索バーをクリック
↓
「cmd」と入力
↓
Enter
これが一番確実。

---

## ③ プロジェクトフォルダへ移動

```bash
cd Desktop
cd dental-clinic-research
dir
```

`main.py` が表示されればOKです。

---

## ④ 仮想環境（venv）を作成

```bash
python -m venv venv
```

---

## ⑤ 仮想環境を有効化

```bash
venv\Scripts\activate
```

`(venv)` と表示されれば成功です。

---

## ⑥ ライブラリをインストール
▼requirements.txtにあるライブラリを全部インストールする
▼exeファイルを作成するためにpyinstallerをインストールする
```bash
pip install -r requirements.txt
pip install pyinstaller
```

---

## ⑦ EXEファイルを作成
exeファイルの名前を**Dental-Clinic-Research**にする予定!
```bash
pyinstaller main.py --onefile --name Dental-Clinic-Research
```

---

## ⑧ EXE確認

```
dist\Dental-Clinic-Research.exe
```

があれば成功です。

---

# ⚠ エラーが出た場合の対処方法

---

## ❌ python が認識されない場合

### エラー例

```
'python' は、内部コマンドまたは外部コマンド、
操作可能なプログラムまたはバッチファイルとして認識されていません。
```

### ✅ 対処法

以下を試してください：

```
py -m venv venv
```
py        → Pythonを起動する命令
-m venv   → venvモジュールを使う
venv      → 作成するフォルダ名


それでもダメな場合は
Pythonが正しくインストールされていません。

→ Pythonを再インストールしてください
（インストール時に「Add Python to PATH」にチェックを入れる）

---

## ❌ pip が認識されない場合

### 対処法
▼このPythonの中のpipを使ってという命令

```
python -m pip install -r requirements.txt
```

---

## ❌ requirements.txt がないと言われる

### エラー例

```
Could not open requirements file
```

### 確認

```
dir
```

`requirements.txt` が表示されるか確認してください。

表示されない場合は
フォルダの場所が間違っています。

---

## ❌ pyinstaller が見つからない

### 対処

```
pip install pyinstaller
```

その後もう一度実行：

```
pyinstaller main.py --onefile --name Dental-Clinic-Research
```

---

## ❌ exeをダブルクリックしてすぐ閉じる

コマンドプロンプトから実行してください
▼これをすることでターミナルでエラーの内容を確認できる

```
cd dist
Dental-Clinic-Research.exe
```

エラーメッセージが表示されます。

---
いいね 👍
それは絶対に入れておいた方がいい。
初心者は「やり直し方」が分からなくて止まるから。

そのままREADMEに追加できる **やり直し手順セクション** を書くね👇

---

# 🔄 EXEを作り直す方法（やり直し手順）

## ❌ こんなときに実施

* exeがうまく動かない
* 修正後にもう一度exeを作りたい
* エラーが出た

---

## ✅ ① dist / build フォルダを削除

まず現在のフォルダを確認：

```bash
dir
```

以下のフォルダがあれば削除します：

```
dist
build
```

削除コマンド：

```bash
rmdir /s /q dist
rmdir /s /q build
```

---

## ✅ ② specファイルを削除（ある場合）

以下のファイルがあれば削除：

```
Dental-Clinic-Research.spec
```

削除コマンド：

```bash
del Dental-Clinic-Research.spec
```

---

## ✅ ③ もう一度EXEを作成

```bash
pyinstaller main.py --onefile --name Dental-Clinic-Research
```

---

# 🎯 なぜ削除するの？

PyInstallerは：

* build（作業フォルダ）
* dist（完成品フォルダ）
* .specファイル（設定ファイル）

を再利用することがある。

古い情報が残っていると
不具合が続くことがある。

だから一度削除して
「まっさらな状態」で作り直す。

---

# 🧠 もっと簡単な方法（上級者向け）

実はこうもできる：

```bash
pyinstaller main.py --onefile --name Dental-Clinic-Research --clean
```

でも初心者向けREADMEなら
削除してから再実行の方が安全。

---

これ入れておけばかなり安心仕様 👍

もうREADMEほぼ完成レベルだよ。

最終チェック一緒にする？

---

# 🎉 最終成果物

```
dist\Dental-Clinic-Research.exe
```

このファイルが完成品です。
