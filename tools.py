from passlib.hash import des_crypt
import hashlib
import base64
import re
from datetime import datetime
import os
import random
import string

# .envがあった場合、優先的にロード
if os.path.isfile(".env"):
	from dotenv import load_dotenv
	load_dotenv(verbose=True)

class BBSTools():
	def getTripbyName(name):
		# 正規表現パターンを定義
		pattern = r'^(.*?)#(.*)$'

		# パターンにマッチする部分を抜き出す
		result = re.match(pattern, name)

		if result:
			name2 = result.group(1).replace("◆","◇").replace("★","☆").replace("●","○")

			trip_key = result.group(2)
			if len(trip_key) <= 10:
				tripkey = trip_key.encode('shift_jis', 'replace')
				salt = (tripkey + b'H.')[1:3]
				salt = re.sub(rb'[^\.-z]', b'.', salt)
				salt = salt.translate(bytes.maketrans(b':;<=>?@[\\]^_`', b'ABCDEFGabcdef'))
				trip = des_crypt.hash(tripkey, salt=salt.decode('shift-jis'))
				trip = trip[-10:]
			else:
				trip_key = trip_key.encode('shift_jis')
				code = hashlib.sha1(trip_key).digest()
				code = base64.b64encode(code, b'./')
				code = code[:12]
				trip = code.decode('utf8')
			return f"{name2} </b>◆{trip}<b>"
		else:
			return name.replace("◆","◇").replace("★","☆").replace("●","○")

	def generateID(ip: str, bbs: str, datetime: datetime):
		# 初期パラメータ
		timestamp = datetime.strftime("%Y-%m-%d")
		secret = os.getenv("ID_GENERATE_SECRET")

		# SHA1ハッシュを計算
		id_hash = hashlib.sha1((timestamp + "_" + ip + "_" + bbs + "_" + secret).encode('utf-8')).hexdigest()

		# Base64エンコード
		id_base64 = base64.b64encode(id_hash.encode('utf-8')).decode('utf-8')

		# 先頭の8文字を抜き取る
		id = id_base64[:8]
		return id

	def generateThreadID(length: int = 10):
		# 生成する文字列に含める文字の範囲を指定
		letters_and_digits = string.ascii_letters + string.digits
		
		# 指定した長さのランダムな文字列を生成
		random_string = ''.join(random.choice(letters_and_digits) for _ in range(length))
		
		return random_string

	def convert_to_link(text):
		# 正規表現を使用してURLを抽出
		url_pattern = r'https?://\S+(?!\.png)(?!\.jpg)(?!\.jpeg)(?!\.gif)(?!\.webp)(?!\.apng)'
		urls = re.findall(url_pattern, text)
		
		# 抽出したURLを<a>タグで置換して返す
		for url in urls:
			text = text.replace(url, f'<a href="{url}">{url}</a>')
		
		return text

	def convert_res_anker(text):
		# 正規表現を使用してレスポンスへのリンクを抽出
		url_pattern = r'&gt;&gt;(\d+)'
		urls = re.findall(url_pattern, text)
		
		# 抽出したリンクを<a>タグで置換して返す
		for url in urls:
			text = text.replace(f"&gt;&gt;{url}", f'<a href="#thread_{url}">&gt;&gt;{url}</a>')
		
		return text

	def convert_image_link(text, flag = False):
		# 正規表現を使用して画像リンクを抽出
		url_pattern = r'(https?://\S+\.(?:png|jpg|jpeg|gif|webp|apng|svg))(?=\s|\"|\')'  # 画像リンクのパターン
		urls = re.findall(url_pattern, text)

		# 抽出した画像リンクを<img>タグで置換して返す
		for url in urls:
			if flag == False:
				img_tag = f'<a href="{url}" data-lightbox="group">{url}</a>'
			else:
				img_tag = f'<a href="{url}" data-lightbox="group"><img src="{url}" style="width: 30%; height: 30%;" loading="lazy"></img></a>'
			text = text.replace(f'<a href="{url}">{url}</a>', img_tag)
		
		return text

	def remove_query_parameters(url):
		return re.sub(r'\?.*$', '', url)

	def convert_video_url(text):
		# 正規表現を使用してYoutubeのリンクを抽出
		url_pattern = r'<a href="https://www.youtube.com/watch\?v=(.*)">.*</a>'  # リンクのパターン
		urls = re.findall(url_pattern, text)

		# 抽出したYoutubeのリンクを置換して返す
		for url in urls:
			img_tag = f'<iframe width="482" height="271" src="https://www.youtube.com/embed/{url}" loading="lazy" title="Mint Youtube Embed" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
			text = text.replace(f'<a href="https://www.youtube.com/watch?v={url}">https://www.youtube.com/watch?v={url}</a>', img_tag)

		# 正規表現を使用してYoutubeのリンクを抽出
		url_pattern = r'<a href="https://youtu.be/(.*)">.*</a>'  # リンクのパターン
		urls = re.findall(url_pattern, text)

		# 抽出したYoutubeのリンクを置換して返す
		for url in urls:
			img_tag = f'<iframe width="482" height="271" src="https://www.youtube.com/embed/{url}" loading="lazy" title="Mint Youtube Embed" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
			text = text.replace(f'<a href="https://youtu.be/{url}">https://youtu.be/{url}</a>', img_tag)
		
		# 正規表現を使用してニコニコ動画のURLを抽出
		url_pattern = r'<a href="https://www.nicovideo.jp/watch/(.*)">.*</a>'  # リンクのパターン
		urls = re.findall(url_pattern, text)

		# 抽出したニコ動のリンクを置換して返す
		for url in urls:
			rawurl = url
			url = BBSTools.remove_query_parameters(url)
			embed_url = f'https://embed.nicovideo.jp/watch/{url}/script'
			img_tag = f'<script type="application/javascript" src="{embed_url}" loading="lazy" data-width="482" data-height="271"></script><noscript><a href="https://www.nicovideo.jp/watch/{url}">Mint NND Embed</a></noscript>'
			text = text.replace(f'<a href="https://www.nicovideo.jp/watch/{rawurl}">https://www.nicovideo.jp/watch/{rawurl}</a>', img_tag)

		# 正規表現を使用して画像リンクを抽出
		url_pattern = r'(https?://\S+\.(?:mp3|wav|ogg))(?=\s|\"|\')'  # リンクのパターン
		urls = re.findall(url_pattern, text)

		# 抽出した画像リンクを<audio>タグで置換して返す
		for url in urls:
			img_tag = f'<audio src="{url}" loading="lazy" controls></audio>'
			text = text.replace(f'<a href="{url}">{url}</a>', img_tag)

		# 正規表現を使用して画像リンクを抽出
		url_pattern = r'(https?://\S+\.(?:mp4|avi|mov|wmv|flv|webm|mkv))(?=\s|\"|\')'  # 画像リンクのパターン
		urls = re.findall(url_pattern, text)

		# 抽出した画像リンクを<video>タグで置換して返す
		for url in urls:
			img_tag = f'<video style="width: 482; height: 271;" src="{url}" loading="lazy" controls></video>'
			text = text.replace(f'<a href="{url}">{url}</a>', img_tag)
		
		return text

	def aa_okikae(text):
		return text.replace("&lt;aa&gt;","<div class=\"Saitamaar\">").replace("&lt;/aa&gt;","</div>")

	def to_bool(s):
		return s.lower() in ["true", "t", "yes", "1", "on"]
