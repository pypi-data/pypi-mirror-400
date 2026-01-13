import base64
import hashlib
import json
import logging
from sqlite3 import Connection
from typing import cast

from aiohttp import web
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ec import ECDSA, EllipticCurvePublicKey
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import load_der_public_key

from raphson_mp.common import util
from raphson_mp.server import auth, challenge
from raphson_mp.server.auth import Session, User
from raphson_mp.server.features import FEATURES, Feature

_LOGGER = logging.getLogger(__name__)

if Feature.WEBAUTHN not in FEATURES:
    raise RuntimeError("webauthn module must not be imported when feature is disabled")


async def setup(request: web.Request, conn: Connection, user: User):
    received_data = await request.json()
    client_data_str = received_data["client_data"]
    public_key_str = received_data["public_key"]

    # https://developer.mozilla.org/en-US/docs/Web/API/AuthenticatorResponse/clientDataJSON
    client_data = json.loads(base64.b64decode(client_data_str))
    if client_data["type"] != "webauthn.create":
        _LOGGER.warning("invalid type: %s", client_data["type"])
        raise web.HTTPBadRequest()

    # the challenge in client_data is base64url-encoded without padding
    # we can safely add maximum padding (==), Python will ignore extra padding https://stackoverflow.com/a/49459036
    provided_challenge = base64.urlsafe_b64decode(client_data["challenge"] + "==").decode()
    challenge.verify(provided_challenge)

    # verify origin
    if (actual_origin := client_data["origin"]) != (expected_origin := util.get_expected_origin(request)):
        _LOGGER.warning("origin mismatch: expected %s got %s", expected_origin, actual_origin)
        raise web.HTTPBadRequest()

    # public key in DER format
    public_key = base64.b64decode(public_key_str)

    conn.execute("INSERT INTO user_webauthn (user, public_key) VALUES (?, ?)", (user.user_id, public_key))


async def log_in(request: web.Request, conn: Connection) -> Session:
    data = await request.json()
    authenticator_data = base64.b64decode(data["authenticator_data"])
    client_data_bytes = base64.b64decode(data["client_data"])
    client_data = json.loads(client_data_bytes)
    signature = base64.b64decode(data["signature"])
    user_id = int(base64.b64decode(data["user_handle"]).decode())

    _LOGGER.debug("authenticator_data: %s", authenticator_data)
    _LOGGER.debug("client_data: %s", client_data)
    _LOGGER.debug("signature: %s", signature)
    _LOGGER.debug("user_id: %s", user_id)

    assert client_data["type"] == "webauthn.get"

    # verify clientData origin
    if (actual_origin := client_data["origin"]) != (expected_origin := util.get_expected_origin(request)):
        _LOGGER.warning("origin mismatch: expected %s got %s", expected_origin, actual_origin)
        raise web.HTTPBadRequest(reason=f"origin mismatch")

    # the challenge is base64url-encoded without padding
    # we can safely add maximum padding (==), Python will ignore extra padding https://stackoverflow.com/a/49459036
    provided_challenge = base64.urlsafe_b64decode(client_data["challenge"] + "==").decode()
    challenge.verify(provided_challenge)

    public_keys = [row[0] for row in conn.execute("SELECT public_key FROM user_webauthn WHERE user = ?", (user_id,))]

    signed_data = authenticator_data + hashlib.sha256(client_data_bytes).digest()

    _LOGGER.debug("client_data_bytes: %s", client_data_bytes)
    _LOGGER.debug("challenge: %s", provided_challenge)
    _LOGGER.debug("signed_data: %s", signed_data)

    for public_key in public_keys:
        public_key = cast(EllipticCurvePublicKey, load_der_public_key(public_key))

        try:
            public_key.verify(signature, signed_data, ECDSA(SHA256()))
            _LOGGER.info("successful login using webauthn")
            return await auth.create_session(conn, request, user_id)
        except InvalidSignature:
            continue

    if public_keys:
        _LOGGER.warning("signature didn't match using any of the stored public keys")
    else:
        _LOGGER.warning("no public keys are stored")

    raise web.HTTPBadRequest()
