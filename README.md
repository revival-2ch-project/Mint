# Mint
pythonで作った2ch専ブラ互換の掲示板です。  
## 特徴
- Quartにより非同期的に処理されるレスポンス。  
- PostgreSQLにより(従来のファイルで管理する掲示板より)高速な書き込み。  
(なお、速度はサーバーの性能によって変動します)
- python-socketioによりリアルタイムな閲覧人数を取得・スレッドのオートリロード
(なお、同期速度はサーバーの性能によって（ｒｙ)
## 今後追加される予定の機能
- プラグイン機能
- Turnstileによる認証
## 現在のバグ情報
- 専ブラに対するサポートが正しくありません。  
sjisに変換してるはずなんですけどね...
## テスト環境
- Python 3.11
- supabase
- render.com フリープラン
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
設定を変えたい場合、`setting.py`を編集してください。  
データベースの設定については[database.md](database.md)をお読みください。  
