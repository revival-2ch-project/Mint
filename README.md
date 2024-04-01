# Mint
pythonで作った2ch専ブラ互換の掲示板です。
## テスト環境
- Python 3.11
- supabase
## 現在のバグ情報
- 専ブラに対するサポートが正しくありません。
Quartでsjisって使えるんですかね...?
## How to install
まず、以下のコマンドを使用し、Mintで使用されるライブラリをインストールします。  
```
pip install -r requirements.txt
```
(パスが通っていない場合は、以下のコマンドを使用してください。)  
```
python3 -m pip install -r requirements.txt
```
(オプション).envファイルをmain.pyと同じパスに作成し、以下のように設定します。  
```
database=<データベースのURL>
ID_GENERATE_SECRET=<ID生成のために使うシークレット>
debug=FALSE
```
(.envファイルを使用しない場合は、自分で環境変数を設定してください。)
最後に、main.pyを実行します。
```
hypercorn main:app -b 0.0.0.0:10000
```
このコマンドではデフォルトではポート**10000**でリッスンします。
データベースの設定については[database.md](database.md)をお読みください。
