import base64
import os

from cryptography.fernet import Fernet

from .settings import fernet_key


class Crypto:
    def __init__(self, key: str):
        self.fernet = Fernet(key.encode("utf-8"))

    @staticmethod
    def generate_key() -> str:
        return base64.urlsafe_b64encode(os.urandom(24)).decode("utf-8")

    def encrypt(self, data: str) -> bytes:
        return self.fernet.encrypt(data.encode("utf-8"))

    def decrypt(self, data: bytes) -> str:
        return self.fernet.decrypt(data).decode("utf-8")


async def init_crypto(app):
    app["crypto"] = Crypto(fernet_key)
