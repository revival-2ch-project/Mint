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
import html
from collections import defaultdict
import codecs
import chardet
import socketio
from collections import defaultdict
import feedgen.feed
import urllib.parse

rentoukisei = defaultdict(lambda: int((datetime.now() + settings.get("timezone", timedelta(hours=0))).timestamp()) - 10)

# .envがあった場合、優先的にロード
if os.path.isfile(".env"):
	from dotenv import load_dotenv
	load_dotenv(verbose=True)

# 環境変数の定義
DATABASE_URL = os.getenv("database")

# 次にQuartの初期化
quart_app = Quart(__name__)
sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio, quart_app)

quart_app.jinja_env.filters['encode_sjis'] = lambda u: codecs.encode(str(u), 'shift_jis')

if os.getenv("debug") == "TRUE":
	quart_app.debug = True
	quart_app.config['TEMPLATES_AUTO_RELOAD'] = True

# データベースの準備
@quart_app.before_serving
async def create_db_pool():
	quart_app.db_pool = await asyncpg.create_pool(DATABASE_URL)

@quart_app.after_serving
async def create_db_pool():
	await quart_app.db_pool.close()

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
@quart_app.route("/")
async def hello():
	return "Mint BBS Test"

@quart_app.route('/css/<path:filename>')
async def css(filename):
	response = await send_from_directory('./static/css/', filename)
	response.content_type = "text/css"
	return response

@quart_app.route("/<string:bbs>/")
async def bbsPage(bbs: str):
	async with quart_app.db_pool.acquire() as connection:
		bbs_name = await connection.fetchval("SELECT bbs_name FROM bbs WHERE id = $1", bbs)
		anonymous_name = await connection.fetchval("SELECT anonymous_name FROM bbs WHERE id = $1", bbs)
		description = await connection.fetchval("SELECT description FROM bbs WHERE id = $1", bbs)
		raw_threads = await connection.fetch("SELECT * FROM threads WHERE bbs_id = $1 ORDER BY last_write_time DESC", bbs)
	host = request.host
	return await render_template("bbsPage.html",
							  bbs_name=bbs_name,
							  description=description,
							  threads=raw_threads,
							  anonymous_name=anonymous_name,
							  bbs_id = bbs,
							  settings=settings,
							  ver=mintverinfo,
							  host=host,
				 )

def convert_to_utf8(data):
	# 文字コードを自動検出する
	detected_encoding = chardet.detect(data.encode())
	print(detected_encoding['encoding'])
	if detected_encoding['encoding'] == 'SHIFT_JIS':
		# Shift-JISであればUTF-8に変換する
		return codecs.decode(data, 'cp932', 'replace').encode('utf-8', 'replace')
	else:
		# それ以外の場合はそのまま返す
		return data

async def sjis_error(message: str):
	error = f"""
		<!doctype html>
		<html lang="ja">
			<head>
				<meta charset="shift-jis">
				<meta name="viewport" content="width=device-width, initial-scale=1">
				<title>Error - Mint</title>
				<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-9ndCyUaIbzAi2FUVXJi0CjmCapSmO7SnpJef0486qhLnuZ2cdeRhO02iuK6FUUVM" crossorigin="anonymous">
				<link href="/css/style.css" rel="stylesheet">
			</head>
			<body>
				<!-- 2ch_X:error -->
				<font size="+1" color="#FF0000"><b>ERROR: {message}</b></font>
			
				<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js" integrity="sha384-geWF76RCwLtnZ8qwWowPQNguL3RmwHVBC9FhGdlKrxdiJJigb/j/68SIy3Te4Bkz" crossorigin="anonymous"></script>
			</body>
		</html>
	"""
	response = make_response(error)
	response = await sjis(response)  # sjis関数を呼び出す
	return response

async def sjis_ok(bbs, key):
	res = f"""
			<!doctype html>
			<html lang="ja">
				<head>
					<meta charset="shift-jis">
					<meta name="viewport" content="width=device-width, initial-scale=1">
					<title>書きこみました。</title>
					<meta http-equiv="refresh" content="5;URL=/test/read.cgi/{bbs}/{key}/">
					<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-9ndCyUaIbzAi2FUVXJi0CjmCapSmO7SnpJef0486qhLnuZ2cdeRhO02iuK6FUUVM" crossorigin="anonymous">
					<link href="/css/style.css" rel="stylesheet">
				</head>
				<body>
					<!-- 2ch_X:true -->
					書き込みが完了しました。<br>
					1秒後に自動で転移します。
				
					<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js" integrity="sha384-geWF76RCwLtnZ8qwWowPQNguL3RmwHVBC9FhGdlKrxdiJJigb/j/68SIy3Te4Bkz" crossorigin="anonymous"></script>
				</body>
			</html>
	"""
	response = make_response(res)
	response = await sjis(response)  # sjis関数を呼び出す
	return response

@quart_app.route("/test/bbs.cgi", methods=["POST"])
async def write():
	form = await request.form
	if_utf8 = form.get("if_utf8", None, type=bool)
	data = await request.get_data()
	decoded_data = urllib.parse.unquote(data.decode().replace("+", " "), "utf-8" if if_utf8 is not None else "cp932")
	
	# URLエンコードされたデータを辞書に変換
	post_data_dict = {}
	for pair in decoded_data.split('&'):
		key, value = pair.split('=')
		post_data_dict[key] = value

	bbs = post_data_dict.get("bbs", "")
	key = int(post_data_dict.get("key", 0))
	time = int(post_data_dict.get("time", 0))	# 使用する予定なし
	subject = post_data_dict.get("subject", "")
	name = post_data_dict.get("FROM", "")
	mail = post_data_dict.get("mail", "")
	content = post_data_dict.get("MESSAGE", "").replace("\r\n", "\n").replace("\r","\n")

	headers = request.headers
	user_agent = headers.get('User-Agent', '')
	forwarded_for = headers.get('X-Forwarded-For')

	NAME = name
	MAIL = mail

	if forwarded_for:
		ipaddr = forwarded_for.split(',')[0]  # 複数のIPアドレスがカンマ区切りで送信される場合があるため、最初のものを取得
	else:
		ipaddr = request.remote_addr

	if "Monazilla/1.00" in user_agent:
		monazilla = ""
	else:
		monazilla = "#sita"

	if ipaddr in settings.get("KakikomiKiseiIPs", []):
		if if_utf8 is None:
			return await sjis_error(f"現在このIPアドレス[{ipaddr}]は書き込み規制中です。またの機会にどうぞ。")
		else:
			return await render_template("kakikomi_Error.html", message=f"現在このIPアドレス[{ipaddr}]は書き込み規制中です。またの機会にどうぞ。")

	# 板が指定されていない場合 または キーがない場合 かつ タイトルがない場合 または 本文がない場合
	if (bbs == "") or (key == 0 and subject == "") or (content.replace("\n","").replace(" ","").replace("　","") == ""):
		if if_utf8 is None:
			return await sjis_error("フォーム情報を正しく読み込めません！")
		else:
			return await render_template("kakikomi_Error.html", message="フォーム情報を正しく読み込めません！")

	async with quart_app.db_pool.acquire() as connection:
		#BBSがあるかどうか取得
		bbs_data = await connection.fetchrow("SELECT * FROM bbs WHERE id = $1", bbs)
	if bbs_data == None:
		if if_utf8 is None:
			return await sjis_error("板情報を正しく読み込めません！")
		else:
			return await render_template("kakikomi_Error.html", message="板情報を正しく読み込めません！")

	# 規制
	if len(name) > 64:
		if if_utf8 is None:
			return await sjis_error("名前欄の文字数が長すぎます！")
		else:
			return await render_template("kakikomi_Error.html", message="名前欄の文字数が長すぎます！")
	if len(mail) > 32:
		if if_utf8 is None:
			return await sjis_error("メール欄の文字数が長すぎます！")
		else:
			return await render_template("kakikomi_Error.html", message="メール欄の文字数が長すぎます！")
	if len(content) > 512:
		if if_utf8 is None:
			return await sjis_error("本文の文字数が長すぎます！")
		else:
			return await render_template("kakikomi_Error.html", message="本文の文字数が長すぎます！")
	
	if content.count("\n") > 15:
		if if_utf8 is None:
			return await sjis_error("改行が多すぎます！")
		else:
			return await render_template("kakikomi_Error.html", message="改行が多すぎます！")

	# トリップ / 日時 / ID / エンコード済み本文
	name = html.escape(name)
	lastName = BBSTools.getTripbyName(name)
	date = datetime.now() + settings.get("timezone", timedelta(hours=9))
	id = BBSTools.generateID(ipaddr, bbs, date)
	content = html.escape(content)
	mail = html.escape(mail)

	for word in settings.get("KakikomiKiseiWords", []):
		if word in content:
			if if_utf8 is None:
				return await sjis_error(f"禁止ワードが含まれています！[{word}]")
			else:
				return await render_template("kakikomi_Error.html", message=f"禁止ワードが含まれています！[{word}]")

	# やっと書き込み処理
	# ...の前に連投規制
	if int(date.timestamp()) >= rentoukisei[ipaddr] + 10:
		rentoukisei[ipaddr] = date.timestamp()
		if subject != "":
			subject = html.escape(subject)
			async with quart_app.db_pool.acquire() as connection:
				if lastName.replace(" ","").replace("　","") == "":
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
					int(date.timestamp()) if not "sage" in mail else 0
				)
			await sio.emit('thread_writed', {
				'message': 'thread_writed',
				'name': lastName,
				'mail': mail,
				'content': BBSTools.convert_to_link(content),
				'date': date.strftime("%Y/%m/%d(%a) %H:%M:%S.%f"),
				"id": id,
				"count": 1
			}, room=f"{bbs}_{int(date.timestamp()) if key is None else key}")
			if if_utf8 is None:
				response = await sjis_ok(bbs, int(date.timestamp()) if key is None else key)
			else:
				response = await make_response(await render_template("kakikomi_ok.html", bbs_id=bbs, key=int(date.timestamp()) if key is None else key, monazilla=monazilla))
			response.set_cookie("NAME", value=NAME, expires=int(datetime.now().timestamp()) + 60*60*24*365*10)
			response.set_cookie("MAIL", value=MAIL, expires=int(datetime.now().timestamp()) + 60*60*24*365*10)
			return response
		else:
			async with quart_app.db_pool.acquire() as connection:
				if lastName.replace(" ","").replace("　","") == "":
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
					int(date.timestamp()) if not "sage" in mail else 0
				)
			await sio.emit('thread_writed', {
				'message': 'thread_writed',
				'name': lastName,
				'mail': mail,
				'content': BBSTools.convert_to_link(content),
				'date': date.strftime("%Y/%m/%d(%a) %H:%M:%S.%f"),
				"id": id,
				"count": count
			}, room=f"{bbs}_{int(date.timestamp()) if key is None else key}")
			if if_utf8 is None:
				response = await sjis_ok(bbs, int(date.timestamp()) if key is None else key)
			else:
				response = await make_response(await render_template("kakikomi_ok.html", bbs_id=bbs, key=int(date.timestamp()) if key is None else key, monazilla=monazilla))
			response.set_cookie("NAME", value=NAME, expires=int(datetime.now().timestamp()) + 60*60*24*365*10)
			response.set_cookie("MAIL", value=MAIL, expires=int(datetime.now().timestamp()) + 60*60*24*365*10)
			return response
	else:
		if if_utf8 is None:
			return await sjis_error(f"連投規制中です！あと{(rentoukisei[ipaddr] + 10) - int(date.timestamp())}秒お待ち下さい。")
		else:
			return await render_template("kakikomi_Error.html", message=f"連投規制中です！あと{(rentoukisei[ipaddr] + 10) - int(date.timestamp())}秒お待ち下さい。")

@quart_app.route("/<string:bbs>/subject.txt")
async def subjecttxt(bbs: str):
	async with quart_app.db_pool.acquire() as connection:
		raw_threads = await connection.fetch("SELECT * FROM threads WHERE bbs_id = $1", bbs)
	ss = []
	for thread in raw_threads:
		ss.append(f'{thread["id"]}.dat<>{thread["title"]} ({thread["count"]})')
	content = "\n".join(ss)
	response = make_response(content)
	response = await sjis(response)  # sjis関数を呼び出す

	return response

@quart_app.route("/<string:bbs>/SETTING.TXT")
async def threadSettingTxt(bbs: str):
	async with quart_app.db_pool.acquire() as connection:
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

@quart_app.route("/<string:bbs>/threads.rdf")
async def rss_feed(bbs: str):
	async with quart_app.db_pool.acquire() as connection:
		bbs_name = await connection.fetchval("SELECT bbs_name FROM bbs WHERE id = $1", bbs)
		description = await connection.fetchval("SELECT description FROM bbs WHERE id = $1", bbs)
		raw_threads = await connection.fetch("SELECT * FROM threads WHERE bbs_id = $1", bbs)
	ss = []
	feed = feedgen.feed.FeedGenerator()
	feed.title(f"{bbs_name} - {settings.get('name')}")
	feed.description(description)
	feed.link(href=f'{settings.get("ssloption","https")}://{request.host}/{bbs}/', rel='self')
	for thread in raw_threads:
		item = feed.add_entry()
		item.title(f"{thread['title']} ({thread['count']})")
		data = json.loads(thread["data"])
		item.description(data["data"][0]["content"])
		item.link(href=f'{settings.get("ssloption","https")}://{request.host}/test/read.cgi/{bbs}/{thread["id"]}/')
	content = feed.rss_str(pretty=True)
	response = await make_response(content)
	response.content_type = "application/rss+xml charset=utf-8"
	return content

@quart_app.route("/<string:bbs>/dat/<int:key>.dat")
async def threadDat(bbs: str, key: int):
	async with quart_app.db_pool.acquire() as connection:
		values = await connection.fetchrow("SELECT * FROM threads WHERE id = $1 AND bbs_id = $2", key, bbs)
		if values is None:
			return "Thread not found", 404  # スレッドが見つからない場合は404エラーを返すなどの処理を行う
		
		res_data = json.loads(values["data"])
		ress = []
		for i, v in enumerate(res_data.get("data", [])):
			res_data["data"][i]["date"] = datetime.fromtimestamp(v["date"]).strftime("%Y/%m/%d(%a) %H:%M:%S.%f")
			res_data["data"][i]["content"] = res_data["data"][i]["content"].replace("\r\n"," <br> ").replace("\n"," <br> ").replace("\r"," <br> ")
			res_data["data"][i]["content"] = BBSTools.convert_to_link(res_data["data"][i]["content"])
			if i == 0:
				ress.append(f'{res_data["data"][i]["name"]}<>{res_data["data"][i]["mail"]}<>{res_data["data"][i]["date"]} ID: {res_data["data"][i]["id"]}<>{res_data["data"][i]["content"]}<>{values["title"]}')
			else:
				ress.append(f'{res_data["data"][i]["name"]}<>{res_data["data"][i]["mail"]}<>{res_data["data"][i]["date"]} ID: {res_data["data"][i]["id"]}<>{res_data["data"][i]["content"]}<>')

		response_text = "\n".join(ress)
		response = make_response(response_text)
		response = await sjis(response)  # sjis関数を呼び出す

		return response

@quart_app.route("/test/read.cgi/<string:bbs>/<int:key>/")
async def threadPage(bbs: str, key: int):
	async with quart_app.db_pool.acquire() as connection:
		values = await connection.fetchrow("SELECT * FROM threads WHERE id = $1 AND bbs_id = $2", key, bbs)
		if values is None:
			return "Thread not found", 404  # スレッドが見つからない場合は404エラーを返すなどの処理を行う
		res_data = json.loads(values["data"])
		for i, v in enumerate(res_data.get("data", [])):
			res_data["data"][i]["date"] = datetime.fromtimestamp(v["date"]).strftime("%Y/%m/%d(%a) %H:%M:%S.%f")
			res_data["data"][i]["content"] = res_data["data"][i]["content"].replace("\r\n"," <br> ").replace("\n"," <br> ").replace("\r"," <br> ")
			res_data["data"][i]["content"] = BBSTools.convert_to_link(res_data["data"][i]["content"])
		host = request.host
		return await render_template(
			"thread_view.html",
			data=values,
			res_data=res_data.get("data", []),
			bbs_id=bbs,
			key=key,
			anonymous_name=await connection.fetchval("SELECT anonymous_name FROM bbs WHERE id = $1", bbs),
			settings=settings,
			ver=mintverinfo,
			host=host,
			description=res_data["data"][0]["content"],
		)

@quart_app.errorhandler(404)
def page_not_found(error):
	return "404 Not Found", 404

#socketioのイベント類
room_count = defaultdict(lambda: 0)
global_count = 0

@sio.event
async def connect(sid, environ, auth):
	global global_count
	global_count += 1
	await sio.emit('global_count_event', {'message': 'client connected', 'global_count': global_count})
	print(f'connected', sid)
	print('connected member count', global_count)

def get_sid_rooms(sid):
	"""
	Get the rooms that a given sid is subscribed to.

	Args:
		sid: The SID of the client to get the rooms for.

	Returns:
		A set of room names.
	"""

	rooms = set()
	room_ids = sio.rooms(sid)
	for room_id in room_ids:
		rooms.add(room_id)

	return rooms

@sio.event
async def disconnect(sid):
	global global_count
	global_count -= 1
	await sio.emit('global_count_event', {'message': 'client disconnected', 'global_count': global_count})
	for room in get_sid_rooms(sid):
		room_count[room] -= 1
		await sio.emit('count_event', {'message': 'client disconnected', 'clients': room_count[room]}, room=room)
	print('disconnected', sid)
	print('connected member count', global_count)

@sio.event
async def join_room(sid, room):
	await sio.enter_room(sid, room)
	room_count[room] += 1
	await sio.emit('count_event', {'message': 'client connected', 'clients': room_count[room]}, room=room)
	print('joinned', room)
	print('connected member count', room_count[room])
