# -*- coding: utf-8 -*-
"""Module with helpers for cryptographic algorithms.

"""

import base64
import os

from cryptography.fernet import Fernet

from .settings import fernet_key


class Crypto:
    """Class, aggregating cryptographic helpers.

    Attributes:
        fernet: well-cooked class for symmetric encryption from
            cryptography python module.

    """

    def __init__(self, key: str):
        """Initializing crypto module for immediate using it in app.

        Args:
            key: generated string for fernet initialization and
                encryption/decryption sensitive data. Must be kept in secret.
                Must be able to be encode to 32 url-safe base64-encoded bytes.
                Safely generates via Fernet.generate_key().

        """

        self.fernet = Fernet(key.encode("utf-8"))

    @staticmethod
    def generate_key(n: int) -> str:
        """Helper for generating string of length n via os.random.

        Args:
            n: Result string length.

        Returns:
            Python string, encoded in utf-8 and contains n random url
                save characters.

        """
        return base64.urlsafe_b64encode(os.urandom(n)).decode("utf-8")[:n]

    def encrypt(self, data: str) -> bytes:
        """Encrypts python string into bytes with initialized fernet.

        Args:
            data: String to encrypt.

        Returns:
            Encrypted string as bytes.

        """

        return self.fernet.encrypt(data.encode("utf-8"))

    def decrypt(self, data: bytes) -> str:
        """Decrypts bytes array into python string with initialized fernet.

        Args:
            data: Bytes to decrypt.

        Returns:
            Decrypted python string, encoded in utf-8.

        """

        return self.fernet.decrypt(data).decode("utf-8")


async def init_crypto(app):
    """Initializes crypto module in aiohttp application

    Must be handled via on_startup signal

    Args:
        app: initializing aiohttp application

    """

    app["crypto"] = Crypto(fernet_key)
