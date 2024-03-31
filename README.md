# Mint
pythonで作った2ch専ブラ互換の掲示板です。
## テスト環境
- Python 3.11
- supabase
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
py main.py
```
(↑のコマンドが実行できない場合は、以下のコマンドを実行してください。)  
```
python3 main.py
```
データベースの設定については[database.md](database.md)をお読みください。
