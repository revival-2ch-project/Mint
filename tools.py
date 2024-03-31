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
			name2 = result.group(1).replace("◆","◇").replace("★","☆")

			trip_key = result.group(2)
			tripkey = trip_key.encode('shift_jis')
			salt = (tripkey + b'H.')[1:3]
			salt = re.sub(rb'[^\.-z]', b'.', salt)
			salt = salt.translate(bytes.maketrans(b':;<=>?@[\\]^_`', b'ABCDEFGabcdef'))
			trip = des_crypt.hash(tripkey, salt=salt.decode('shift-jis'))
			trip = trip[-10:]
			return f"{name2}◆{trip}"
		else:
			return name.replace("◆","◇").replace("★","☆")

	def generateIDbyHostandTimestamp(ip: str, datetime: datetime):
		# 初期パラメータ
		timestamp = datetime.strftime("%Y-%m-%d")
		secret = os.getenv("ID_GENERATE_SECRET")

		# SHA1ハッシュを計算
		id_hash = hashlib.sha1((timestamp + ip).encode('utf-8')).hexdigest()

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
