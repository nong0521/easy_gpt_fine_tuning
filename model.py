from cryptography.fernet import Fernet, InvalidToken
import openai
import streamlit as st

class DatasetModel:
    def __init__(self):
        self.cipher_suite = Fernet(Fernet.generate_key())
        self.api_key = self.load_api_key()

    def is_valid_openai_key(self, api_key): 
        openai.api_key = api_key
        try:
            openai.Completion.create(engine="text-davinci", prompt="test", max_tokens=5)
            return True
        except Exception as e:
            print(f"API key validation failed: {e}")
            return False

    def save_api_key(self, api_key):
        if self.is_valid_openai_key(api_key): 
            encrypted_api_key = self.cipher_suite.encrypt(api_key.encode())
            with open("api_key.txt", "wb") as f:
                f.write(encrypted_api_key)
        else:
            st.write("有効なAPIキーを入力してください")

    def load_api_key(self):
        try:
            with open("api_key.txt", "rb") as f:
                encrypted_api_key = f.read()
            decrypted_api_key = self.cipher_suite.decrypt(encrypted_api_key).decode()
            return decrypted_api_key
        except (FileNotFoundError, InvalidToken):
            return ""
