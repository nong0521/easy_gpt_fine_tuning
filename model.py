from cryptography.fernet import Fernet, InvalidToken

class DatasetModel:
    def __init__(self):
        self.cipher_suite = Fernet(Fernet.generate_key())
        self.api_key = self.load_api_key()
    
    def save_api_key(self, api_key):
        encrypted_api_key = self.cipher_suite.encrypt(api_key.encode())
        with open("api_key.txt", "wb") as f:
            f.write(encrypted_api_key)

    def load_api_key(self):
        try:
            with open("api_key.txt", "rb") as f:
                encrypted_api_key = f.read()
            decrypted_api_key = self.cipher_suite.decrypt(encrypted_api_key).decode()
            return decrypted_api_key
        except (FileNotFoundError, InvalidToken):
            return ""
