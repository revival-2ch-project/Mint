from passlib.hash import des_crypt
import re

class TripTools():
	def getTripbyName(name):
		# 正規表現パターンを定義
		pattern = r'^(.*?)#(.*)$'

		# パターンにマッチする部分を抜き出す
		result = re.match(pattern, name)

		if result:
			name2 = result.group(1).replace("◆","◇").replace("★","☆")

			trip_key = result.group(2)
			tripkey = trip_key[1:].encode('shift_jis')
			# treat as Shift-JIS bytes
			tripkey = bytes(tripkey, encoding='shift-jis')
			salt = (tripkey + b'H.')[1:3]
			salt = re.sub(rb'[^\.-z]', b'.', salt)
			salt = salt.translate(bytes.maketrans(b':;<=>?@[\\]^_`', b'ABCDEFGabcdef'))
			trip = des_crypt.hash(tripkey, salt=salt.decode('shift-jis'))
			trip = trip[-10:]
			return f"{name2}◆{trip}"
		else:
			return name.replace("◆","◇").replace("★","☆")
