import base64
import logging
import time

from aiohttp import web
from cryptography.fernet import Fernet, InvalidToken

_LOGGER = logging.getLogger(__name__)
_FERNET = Fernet(Fernet.generate_key())


def generate() -> str:
    ciphertext = _FERNET.encrypt(b"")
    return base64.urlsafe_b64encode(ciphertext).decode()


def verify(challenge: str):
    try:
        ciphertext = base64.urlsafe_b64decode(challenge)
        plaintext = _FERNET.decrypt(ciphertext)
    except (ValueError, InvalidToken):
        _LOGGER.warning("challenge base64 decode error: %s", challenge, exc_info=True)
        raise web.HTTPBadRequest()
    if plaintext != b"":
        _LOGGER.warning("challenge plaintext token is invalid")
        raise web.HTTPBadRequest()
    if (challenge_time := _FERNET.extract_timestamp(ciphertext)) + 3600 < time.time():
        _LOGGER.warning("challenge is too old: challenge=%s now=%s", challenge_time, int(time.time()))
        raise web.HTTPBadRequest()
