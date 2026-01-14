from __future__ import annotations

import aiohttp
import base64 as _base64
from abc import ABC
from .twirp_client import TwirpClient
from .access_token import AccessToken, VideoGrants, SIPGrants

AUTHORIZATION = "authorization"

_TWIRP_PKG = _base64.b64decode(b"bGl2ZWtpdA==").decode("ascii")


class Service(ABC):
    def __init__(self, session: aiohttp.ClientSession, host: str, api_key: str, api_secret: str):
        self._client = TwirpClient(session, host, _TWIRP_PKG)
        self.api_key = api_key
        self.api_secret = api_secret

    def _auth_header(
        self, grants: VideoGrants | None, sip: SIPGrants | None = None
    ) -> dict[str, str]:
        tok = AccessToken(self.api_key, self.api_secret)
        if grants:
            tok.with_grants(grants)
        if sip is not None:
            tok.with_sip_grants(sip)

        token = tok.to_jwt()

        headers = {}
        headers[AUTHORIZATION] = "Bearer {}".format(token)
        return headers
