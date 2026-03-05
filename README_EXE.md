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
▼このPythonの中のpipを使ってとお願いする

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

# 🎉 最終成果物

```
dist\Dental-Clinic-Research.exe
```

このファイルが完成品です。
