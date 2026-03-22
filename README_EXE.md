# Windows用 EXE作成手順書（最終版）

## 🎯 目的

`dental-clinic-research` フォルダから
`Dental-Clinic-Research.exe` を作成します。

---

## ✅ 事前準備

* Python がインストールされていること
* 受け取ったZIPファイルがあること

※すべて「コマンドプロンプト」で操作します

---

# ① ZIPファイルを解凍する

1. ZIPファイルを **デスクトップ** に保存
2. 右クリック
3. 「すべて展開」をクリック
4. `dental-clinic-research` フォルダができていることを確認

---

# ② コマンドプロンプトを開く

### 方法①（ショートカット）

```id="6n6c64"
Windowsキー + R
```

Macの場合：

```id="h2xw0u"
⌘ + R
```

↓

```id="7iv9p5"
cmd
```

↓

Enter

---

### 方法②（確実）

Windowsの検索バーに

```id="mcz7yt"
cmd
```

と入力 → Enter

---

# ③ プロジェクトフォルダへ移動（重要）

## ✅ まず必ず実行（必須）

```id="9d2u7p"
cd %USERPROFILE%\Desktop
```

※現在の場所に関係なく、確実にデスクトップへ移動します

---

## ✅ 王道パターン（推奨）

1. `dental-clinic-research` フォルダを右クリック
2. 「パスのコピー」
3. 以下を入力

```id="b4bpx1"
cd "ここに貼り付け"
```

例：

```id="qkz6qg"
cd "C:\Users\user\Desktop\dental-clinic-research"
```

---

## ⚠ 注意

* フォルダ名にスペースがある場合は
  **"（ダブルクォーテーション）必須**
* ない場合でも付けてOK（安全）

---

## 確認

```id="6l0x5g"
dir
```

以下が表示されればOK

```id="tnf0ma"
main.py
requirements.txt
```

---

# ④ 仮想環境（venv）を作成

```id="f0n9nj"
python -m venv venv
```

エラー時：

```id="m8n9g2"
py -m venv venv
```

---

# ⑤ 仮想環境を有効化

```id="k91pzt"
venv\Scripts\activate
```

成功すると：

```id="5rru4m"
(venv)
```

と表示される

---

# ⑥ ライブラリをインストール

```id="d4pl5d"
python -m pip install -r requirements.txt
```

---

## ✅ インストール完了の確認（追加）

以下のどちらかになればOK：

### パターン①

```id="v7o2tr"
Successfully installed ○○○
```

---

### パターン②

エラーが出ずに、再び入力できる状態になる

---

## ✅ インストール内容を確認（推奨）

```id="m3b9zq"
pip list
```

インストールされたライブラリ一覧が表示される

---

## ❗ エラーが出た場合（バージョン問題）

```id="m8j1xy"
python -m pip install --upgrade pip
```

↓

```id="kg6p2l"
python -m pip install -r requirements.txt
```

---

# ⑦ PyInstallerをインストール

```id="4c4t1l"
python -m pip install pyinstaller
```

---

# ⑧ EXEファイルを作成

```id="l3r4w2"
pyinstaller main.py --onefile --name Dental-Clinic-Research
```

※1〜2分ほどかかります

---

# ⑨ EXE確認

```id="n7qz5u"
cd dist
dir
```

```id="d5xmb8"
Dental-Clinic-Research.exe
```

があれば成功

---

# ⑩ Windows Defender の警告

表示された場合：

```id="brrh7n"
Windows によって PC が保護されました
```

対応：

1. 「詳細情報」クリック
2. 「実行」クリック

---

# 🔄 EXEを作り直す方法

```id="lqhj6b"
rmdir /s /q dist
rmdir /s /q build
del Dental-Clinic-Research.spec
```

↓

```id="ibz9fz"
pyinstaller main.py --onefile --name Dental-Clinic-Research
```

---

# ⚠ エラー対処

## pythonが認識されない

```id="w3kbbm"
py -m venv venv
```

---

## pipが認識されない

```id="h2a7wh"
python -m pip install -r requirements.txt
```

---

## exeがすぐ閉じる

```id="w8pyjz"
cd dist
Dental-Clinic-Research.exe
```

---

# 🎉 完成

```id="6jv68q"
dist\Dental-Clinic-Research.exe
```

---

# 💡今回の強化ポイント

✔ `cd %USERPROFILE%\Desktop` を必須化
✔ パスコピー方式（王道）
✔ ダブルクォーテーション明記
✔ pip install後の確認追加
✔ pip listで可視化