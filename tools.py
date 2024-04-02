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
				tripkey = trip_key.encode('shift_jis')
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
			return f"{name2}</b>◆{trip}<b>"
		else:
			return name.replace("◆","◇").replace("★","☆").replace("●","○")

	def generateID(ip: str, bbs: str, datetime: datetime):
		# 日にち (03/01/26 22:13 -> 26)
		day = datetime.day

		# /dev/randomを開き、先頭から16バイト読み出したランダムな値。
		# /dev/randomを使わない設定の場合は、ランダムな数字(16桁)。
		# 日付が変わると更新される。日付が同じなら再利用される。
		# サーバをクラックしない限り、値は分かりません。
		# 日付を取得してシード値として使用する
		today = datetime.strftime("%Y%m%d")

		# 日付に基づいて乱数生成器を初期化
		random.seed(today)

		# 16桁のランダムな数字を生成する
		rand = ''.join([str(random.randint(0, 9)) for _ in range(16)])

		# IPアドレスからMD5を算出する。(16進数形式)
		# 返ってきた文字列の"後ろから4バイト"を求める
		ipmd5 = hashlib.md5(ip.encode()).hexdigest()[-4:]

		# メッセージを作成する
		md5 = hashlib.md5()
		md5.update(ipmd5.encode())
		md5.update(bbs.encode())
		md5.update(str(day).encode())
		md5.update(str(rand).encode())

		# メッセージからMD5を算出する。(base64enc形式)
		# 返ってきた文字列の先頭から8文字がIDになります。
		id = md5.digest()[:8].decode('latin-1')
		return id

	def generateThreadID(length: int = 10):
		# 生成する文字列に含める文字の範囲を指定
		letters_and_digits = string.ascii_letters + string.digits
		
		# 指定した長さのランダムな文字列を生成
		random_string = ''.join(random.choice(letters_and_digits) for _ in range(length))
		
		return random_string

	def convert_to_link(text):
		# 正規表現を使用してURLを抽出
		url_pattern = r'https?://\S+'
		urls = re.findall(url_pattern, text)
		
		# 抽出したURLを<a>タグで置換して返す
		for url in urls:
			text = text.replace(url, f'<a href="{url}">{url}</a>')
		
		return text
