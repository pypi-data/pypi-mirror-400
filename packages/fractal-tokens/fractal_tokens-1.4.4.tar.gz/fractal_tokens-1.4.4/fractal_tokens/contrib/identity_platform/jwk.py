import json
from functools import lru_cache
from typing import List

from fractal_tokens.services.jwk import Jwk, JwkService


class GoogleIdentityPlatformJwkService(JwkService):
    @lru_cache(maxsize=None)
    def get_jwks(self, issuer: str = "", kid: str = "") -> List[Jwk]:
        from urllib.request import (  # needs to be here to be able to mock in tests
            urlopen,
        )

        # https://firebase.google.com/docs/auth/admin/verify-id-tokens#verify_id_tokens_using_a_third-party_jwt_library
        jsonurl = urlopen(
            "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
        )
        return [Jwk(k, v) for k, v in json.loads(jsonurl.read()).items()]
