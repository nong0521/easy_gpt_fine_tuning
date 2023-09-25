from cryptography.fernet import Fernet, InvalidToken
import openai
import streamlit as st

class DatasetModel:
    def __init__(self):
        try:
            with open("cipher_key.txt", "rb") as f:
                key = f.read()
            self.cipher_suite = Fernet(key)
        except FileNotFoundError:
            key = Fernet.generate_key()
            with open("cipher_key.txt", "wb") as f:
                f.write(key)
            self.cipher_suite = Fernet(key)

        if 'loaded api key' not in st.session_state:
            st.session_state['loaded api key'] = self.load_api_key()

        self.api_key = st.session_state['loaded api key']

    def is_valid_openai_key(self, api_key): 
        openai.api_key = api_key
        try:
            openai.Completion.create(model="gpt-3.5-turbo-instruct", prompt="test", max_tokens=5)
            return True
        except Exception as e:
            print(f"API key validation failed: {e}")
            return False

    def save_api_key(self, api_key):
        if self.is_valid_openai_key(api_key): 
            encrypted_api_key = self.cipher_suite.encrypt(api_key.encode())
            with open("api_key.txt", "wb") as f:
                f.write(encrypted_api_key)
            st.session_state['is valid openai key'] = True
            st.session_state['loaded api key'] = api_key
        else:
            st.write("有効なAPIキーを入力してください")

    def load_api_key(self):
        try:
            with open("api_key.txt", "rb") as f:
                encrypted_api_key = f.read()
            decrypted_api_key = self.cipher_suite.decrypt(encrypted_api_key).decode()
            return decrypted_api_key
        except FileNotFoundError:
            print("File not found.")
            return ""
        except InvalidToken:
            print("Invalid Token for decryption.")
            return ""
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return ""
