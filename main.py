"""
Mintのメインソースコード
"""

# まずライブラリのインポート(Quart, asyncpg, os)
from quart import Quart, render_template, send_from_directory
import asyncpg
import os
import asyncio

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
		description = await connection.fetchval("SELECT description FROM bbs WHERE id = $1", bbs)
		raw_threads = await connection.fetch("SELECT * FROM threads WHERE bbs_id = $1", bbs)
	return await render_template("bbsPage.html", bbs_name=bbs_name, description=description, threads=raw_threads)

@app.errorhandler(404)
def page_not_found(error):
	return "404 Not Found", 404

# 実行
if __name__ == "__main__":
	app.run()
