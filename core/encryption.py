# core/encryption.py

from cryptography.fernet import Fernet
import os

# 암호화 키 저장 위치
KEY_FILE = os.path.join(os.path.dirname(__file__), '../data/key.bin')

def generate_key():
    """
    새로운 암호화 키를 생성하고 저장
    """
    key = Fernet.generate_key()
    os.makedirs(os.path.dirname(KEY_FILE), exist_ok=True)
    with open(KEY_FILE, 'wb') as f:
        f.write(key)

def load_key():
    """
    암호화 키를 불러오거나 없으면 새로 생성
    """
    if not os.path.exists(KEY_FILE):
        generate_key()
    with open(KEY_FILE, 'rb') as f:
        return f.read()

# Fernet 인스턴스 준비
fernet = Fernet(load_key())

def encrypt_password(password: str) -> str:
    """
    비밀번호를 암호화하여 문자열로 반환
    """
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(token: str) -> str:
    """
    암호화된 문자열을 복호화하여 원래 비밀번호로 복원
    """
    return fernet.decrypt(token.encode()).decode()
