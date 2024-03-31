"""
Mintのメインソースコード
"""

# まずライブラリのインポート(Quart, asyncpg, os)
from quart import Quart, render_template, send_from_directory, request
import asyncpg
import os
from tools import TripTools

# .envがあった場合、優先的にロード
if os.path.isfile(".env"):
	from dotenv import load_dotenv
	load_dotenv(verbose=True)

# 環境変数の定義
DATABASE_URL = os.getenv("database")

# 次にQuartの初期化
app = Quart(__name__)

if os.getenv("debug") == "TRUE":
	app.config['TEMPLATES_AUTO_RELOAD'] = True

# データベースの準備
@app.before_serving
async def create_db_pool():
	app.db_pool = await asyncpg.create_pool(DATABASE_URL)

@app.after_serving
async def create_db_pool():
	await app.db_pool.close()

# Quartのページ類
@app.route("/")
async def hello():
	return "Mint BBS Test"

@app.route('/css/<path:filename>')
async def css(filename):
	return await send_from_directory('./static/css/', filename)

@app.route("/<string:bbs>/")
async def bbsPage(bbs: str):
	async with app.db_pool.acquire() as connection:
		bbs_name = await connection.fetchval("SELECT bbs_name FROM bbs WHERE id = $1", bbs)
		anonymous_name = await connection.fetchval("SELECT anonymous_name FROM bbs WHERE id = $1", bbs)
		description = await connection.fetchval("SELECT description FROM bbs WHERE id = $1", bbs)
		raw_threads = await connection.fetch("SELECT * FROM threads WHERE bbs_id = $1", bbs)
	return await render_template("bbsPage.html",
							  bbs_name=bbs_name,
							  description=description,
							  threads=raw_threads,
							  anonymous_name=anonymous_name,
							  bbs_id = bbs
				 )

@app.route("/test/bbs.cgi")
async def write():
	bbs = request.form.get("bbs", "")
	key = request.form.get("key", 0)
	time = request.form.get("time", 0)	# 使用する予定なし
	subject = request.form.get("subject", "")
	name = request.form.get("FROM", "")
	mail = request.form.get("mail", "")
	content = request.form.get("MESSAGE", "")

	# 板が指定されていない場合 または キーがない場合 かつ タイトルがない場合 または 本文がない場合
	if (bbs == "") or (key == 0 and subject == "") or (content == ""):
		return await render_template("kakikomi_Error.html", message="フォーム情報を正しく読み込めません！")

	async with app.db_pool.acquire() as connection:
		#BBSがあるかどうか取得
		bbs_data = await connection.fetchrow("SELECT * FROM bbs WHERE id = $1", bbs)
	if bbs_data == None:
		return await render_template("kakikomi_Error.html", message="板情報を正しく読み込めません！")

	# 規制
	if len(name) > 64:
		return await render_template("kakikomi_Error.html", message="名前欄の文字数が長すぎます！")
	if len(mail) > 32:
		return await render_template("kakikomi_Error.html", message="メール欄の文字数が長すぎます！")

	# トリップ
	lastName = TripTools.getTripbyName(name)

	# やっと書き込み処理



@app.errorhandler(404)
def page_not_found(error):
	return "404 Not Found", 404

# 実行
if __name__ == "__main__":
	app.run()
