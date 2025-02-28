import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv(dotenv_path=".env.local")

KEY = os.getenv("ENCRYPTION_KEY")
cipher = Fernet(KEY)

def encrypt(data: str) -> str:
    return cipher.encrypt(data.encode()).decode()

def decrypt(encrypted_data: str) -> str:
    return cipher.decrypt(encrypted_data.encode()).decode()