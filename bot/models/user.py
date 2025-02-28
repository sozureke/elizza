from sqlite3 import Connection
from bot.utils.encryption import encrypt, decrypt

class User:
	def __init__(self, user_id: int, login: str, password: str):
		self.user_id = user_id
		self.login = login
		self.password = password

		@staticmethod
		def create_table(conn: Connection):
			conn.execute("""
				CREATE TABLE IF NOT EXISTS users (
					user_id INTEGER PRIMARY KEY,
					login TEXT NOT NULL,
					password TEXT NOT NULL
				)
			""")

		@staticmethod
		def save_user(conn: Connection, user_id: int, login: str, password: str):
			encrypted_password = encrypt(password)
			conn.execute("""
			INSERT INTO users (user_id, login, password)
			VALUES (?, ?, ?)
			ON CONFLICT(user_id) DO UPDATE SET
					login = excluded.login,
					password = excluded.password
			""", (user_id, login, encrypted_password))
			conn.commit()

		@staticmethod
		def get_user(conn: Connection, user_id: int) -> "User":
			cursor = conn.execute("SELECT login, password FROM users WHERE user_id = ?", (user_id,))
			row = cursor.fetchone()
			if row:
				login, encrypted_password = row
				password = decrypt(encrypted_password)
				return User(user_id, login, password)
			return None

			
	