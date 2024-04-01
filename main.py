"""
Mintのメインソースコード
"""

# まずライブラリのインポート(Quart, asyncpg, os)
from quart import Quart, render_template, send_from_directory, request, Response, make_response
import asyncpg
import os
from tools import BBSTools
from setting import settings, mintverinfo
from datetime import datetime, timedelta
import json
import locale
import html
from collections import defaultdict
import random
import codecs
import chardet
import sys

rentoukisei = defaultdict(lambda: int((datetime.now() + settings.get("timezone", timedelta(hours=0))).timestamp()) - 10)

# .envがあった場合、優先的にロード
if os.path.isfile(".env"):
	from dotenv import load_dotenv
	load_dotenv(verbose=True)

# 環境変数の定義
DATABASE_URL = os.getenv("database")

# 次にQuartの初期化
app = Quart(__name__)

if os.getenv("debug") == "TRUE":
	app.debug = True
	app.config['TEMPLATES_AUTO_RELOAD'] = True

# データベースの準備
@app.before_serving
async def create_db_pool():
	app.db_pool = await asyncpg.create_pool(DATABASE_URL)

@app.after_serving
async def create_db_pool():
	await app.db_pool.close()

async def sjis(dat):
	response = await dat
	# response.dataを取得するためにawaitを使用しない
	data = await response.get_data()
	# 新しいContent-Typeヘッダーを追加
	response.headers.add('Content-Type', 'text/plain; charset=shift_jis')
	# データをUTF-8からShift-JISに変換し、エラーが発生した場合は無視する
	encoded_data = data.decode('utf8', errors='ignore').encode('shift_jis', errors='ignore')
	# レスポンスのデータを変更
	response.set_data(encoded_data)
	return response

# Quartのページ類
@app.route("/")
async def hello():
	return "Mint BBS Test"

@app.route('/css/<path:filename>')
async def css(filename):
	response = await send_from_directory('./static/css/', filename)
	response.content_type = "text/css"
	return response

@app.route("/<string:bbs>/")
async def bbsPage(bbs: str):
	async with app.db_pool.acquire() as connection:
		bbs_name = await connection.fetchval("SELECT bbs_name FROM bbs WHERE id = $1", bbs)
		anonymous_name = await connection.fetchval("SELECT anonymous_name FROM bbs WHERE id = $1", bbs)
		description = await connection.fetchval("SELECT description FROM bbs WHERE id = $1", bbs)
		raw_threads = await connection.fetch("SELECT * FROM threads WHERE bbs_id = $1 ORDER BY last_write_time DESC", bbs)
	return await render_template("bbsPage.html",
							  bbs_name=bbs_name,
							  description=description,
							  threads=raw_threads,
							  anonymous_name=anonymous_name,
							  bbs_id = bbs
				 )

def convert_to_utf8(data):
	# 文字コードを自動検出する
	detected_encoding = chardet.detect(data.encode())
	if detected_encoding['encoding'] == 'shift_jis':
		# Shift-JISであればUTF-8に変換する
		return codecs.decode(data.encode('shift-jis'), 'utf-8')
	else:
		# それ以外の場合はそのまま返す
		return data

@app.route("/test/bbs.cgi", methods=["POST"])
async def write():
	form = await request.form
	bbs = form.get("bbs", "")
	key = form.get("key", 0, type=int)
	time = form.get("time", 0)	# 使用する予定なし
	subject = form.get("subject", "")
	name = form.get("FROM", "")
	mail = form.get("mail", "")
	content = form.get("MESSAGE", "")

	bbs = convert_to_utf8(bbs)
	subject = convert_to_utf8(subject)
	name = convert_to_utf8(name)
	mail = convert_to_utf8(mail)
	content = convert_to_utf8(content)
	subject = convert_to_utf8(subject)

	headers = request.headers
	forwarded_for = headers.get('X-Forwarded-For')
	
	if forwarded_for:
		ipaddr = forwarded_for.split(',')[0]  # 複数のIPアドレスがカンマ区切りで送信される場合があるため、最初のものを取得
	else:
		ipaddr = request.remote_addr

	if ipaddr in settings.get("KakikomiKiseiIPs", []):
		return await render_template("kakikomi_Error.html", message=f"現在このIPアドレス[{ipaddr}]は書き込み規制中です。またの機会にどうぞ。")

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
	if len(content) > 512:
		return await render_template("kakikomi_Error.html", message="本文の文字数が長すぎます！")
	
	if content.count("\n") > 15:
		return await render_template("kakikomi_Error.html", message="改行が多すぎます！")

	# トリップ / 日時 / ID / エンコード済み本文
	name = html.escape(name)
	lastName = BBSTools.getTripbyName(name)
	date = datetime.now() + settings.get("timezone", timedelta(hours=9))
	id = BBSTools.generateIDbyHostandTimestamp(ipaddr, date)
	content = html.escape(content)
	mail = html.escape(content)

	for word in settings.get("KakikomiKiseiWords", []):
		if word in content:
			return await render_template("kakikomi_Error.html", message=f"禁止ワードが含まれています！[{word}]")

	# やっと書き込み処理
	# ...の前に連投規制
	if int(date.timestamp()) >= rentoukisei[ipaddr] + 10:
		rentoukisei[ipaddr] = date.timestamp()
		if subject != "":
			subject = html.escape(subject)
			async with app.db_pool.acquire() as connection:
				if lastName == "":
					lastName = await connection.fetchval("SELECT anonymous_name FROM bbs WHERE id = $1", bbs)
				data = {"data": [{
					"name": lastName,
					"mail": mail,
					"date": date.timestamp(),
					"content": content,
					"id": id,
					"ipaddr": ipaddr
				}]}
				data_json = json.dumps(data)
				# パラメータを指定してクエリを実行
				await connection.execute(
					"INSERT INTO threads (thread_id, id, bbs_id, created_at, title, data, count, last_write_time) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
					BBSTools.generateThreadID(10),
					int(date.timestamp()),
					bbs,
					date.now(),
					subject,
					data_json,
					1,
					int(date.timestamp())
				)
			return await render_template("kakikomi_ok.html", bbs_id=bbs, key=int(date.timestamp()))
		else:
			async with app.db_pool.acquire() as connection:
				if lastName == "":
					lastName = await connection.fetchval("SELECT anonymous_name FROM bbs WHERE id = $1", bbs)
				row = await connection.fetchrow("SELECT data, count FROM threads WHERE id = $1 AND bbs_id = $2", key, bbs)
				data, count = row[0], row[1]
				data = json.loads(data)
				if count >= 1000:
					return await render_template("kakikomi_Error.html", message="このスレッドにはもう書けません。")
				elif count == 999:
					count += 1
					data["data"].append({
						"name": lastName,
						"mail": mail,
						"date": date.timestamp(),
						"content": content,
						"id": id,
						"ipaddr": ipaddr
					})
					data["data"].append({
						"name": "Over 1000 Thread",
						"mail": "",
						"date": date.timestamp(),
						"content": "レス数が1000を超えたため、このスレッドにはもう書けません...",
						"id": "System"
					})
				else:
					count += 1
					data["data"].append({
						"name": lastName,
						"mail": mail,
						"date": date.timestamp(),
						"content": content,
						"id": id,
						"ipaddr": ipaddr
					})
				data_json = json.dumps(data)
				# パラメータを指定してクエリを実行
				await connection.execute(
					"UPDATE threads SET data = $3, count = $4, last_write_time = $5 WHERE id = $1 AND bbs_id = $2",
					key,
					bbs,
					data_json,
					count,
					int(date.timestamp())
				)
			return await render_template("kakikomi_ok.html", bbs_id=bbs, key=int(date.timestamp())if key is None else key)
	else:
		return await render_template("kakikomi_Error.html", message=f"連投規制中です！あと{(rentoukisei[ipaddr] + 10) - int(date.timestamp())}秒お待ち下さい。")

@app.route("/<string:bbs>/subject.txt")
async def subjecttxt(bbs: str):
	async with app.db_pool.acquire() as connection:
		raw_threads = await connection.fetch("SELECT * FROM threads WHERE bbs_id = $1", bbs)
	ss = []
	for thread in raw_threads:
		ss.append(f'{thread["id"]}.dat<>{thread["title"]} ({thread["count"]})')
	content = "\n".join(ss)
	response = make_response(content)
	response = await sjis(response)  # sjis関数を呼び出す

	return response

@app.route("/<string:bbs>/SETTING.TXT")
async def threadSettingTxt(bbs: str):
	async with app.db_pool.acquire() as connection:
		values = await connection.fetchrow("SELECT * FROM bbs WHERE id = $1", bbs)
		s = []
		s.append(f'BBS_TITLE={values["bbs_name"]}')
		s.append(f'BBS_NONAME_NAME={values["anonymous_name"]}')
		s.append(f'BBS_SUBJECT_COUNT=128')
		s.append(f'BBS_NAME_COUNT=128')
		s.append('BBS_MAIL_COUNT=64')
		s.append('BBS_MESSAGE_COUNT=2048')
		content = "\n".join(s)
		response = make_response(content)
		response = await sjis(response)  # sjis関数を呼び出す

		return response

@app.route("/<string:bbs>/dat/<int:key>.dat")
async def threadDat(bbs: str, key: int):
	async with app.db_pool.acquire() as connection:
		values = await connection.fetchrow("SELECT * FROM threads WHERE id = $1 AND bbs_id = $2", key, bbs)
		if values is None:
			return "Thread not found", 404  # スレッドが見つからない場合は404エラーを返すなどの処理を行う
		
		res_data = json.loads(values["data"])
		ress = []
		for i, v in enumerate(res_data.get("data", [])):
			res_data["data"][i]["date"] = datetime.fromtimestamp(v["date"]).strftime("%Y/%m/%d(%a) %H:%M:%S.%f")
			res_data["data"][i]["content"] = res_data["data"][i]["content"].replace("\n"," <br> ")
			res_data["data"][i]["content"] = BBSTools.convert_to_link(res_data["data"][i]["content"])
			if i == 0:
				ress.append(f'{res_data["data"][i]["name"]}<>{res_data["data"][i]["mail"]}<>{res_data["data"][i]["date"]} ID: {res_data["data"][i]["id"]}<>{res_data["data"][i]["content"]}<>{values["title"]}')
			else:
				ress.append(f'{res_data["data"][i]["name"]}<>{res_data["data"][i]["mail"]}<>{res_data["data"][i]["date"]} ID: {res_data["data"][i]["id"]}<>{res_data["data"][i]["content"]}<>')

		response_text = "\n".join(ress)
		response = make_response(response_text)
		response = await sjis(response)  # sjis関数を呼び出す

		return response

@app.route("/test/read.cgi/<string:bbs>/<int:key>/")
async def threadPage(bbs: str, key: int):
	async with app.db_pool.acquire() as connection:
		values = await connection.fetchrow("SELECT * FROM threads WHERE id = $1 AND bbs_id = $2", key, bbs)
		if values is None:
			return "Thread not found", 404  # スレッドが見つからない場合は404エラーを返すなどの処理を行う
		res_data = json.loads(values["data"])
		for i, v in enumerate(res_data.get("data", [])):
			res_data["data"][i]["date"] = datetime.fromtimestamp(v["date"]).strftime("%Y/%m/%d(%a) %H:%M:%S.%f")
			res_data["data"][i]["content"] = res_data["data"][i]["content"].replace("\n"," <br> ")
			res_data["data"][i]["content"] = BBSTools.convert_to_link(res_data["data"][i]["content"])
		return await render_template(
			"thread_view.html",
			data=values,
			res_data=res_data.get("data", []),
			bbs_id=bbs,
			key=key,
			anonymous_name=await connection.fetchval("SELECT anonymous_name FROM bbs WHERE id = $1", bbs),
			ver=mintverinfo
		)


@app.errorhandler(404)
def page_not_found(error):
	return "404 Not Found", 404
