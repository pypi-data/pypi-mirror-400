from typing import Optional, Union

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from jose import jwt

from fractal_tokens.exceptions import (
    NoPrivateKeyException,
    NoPublicKeyException,
    NotAllowedException,
)
from fractal_tokens.services.jwk import JwkService
from fractal_tokens.services.jwt import JwtTokenService
from fractal_tokens.settings import ACCESS_TOKEN_EXPIRATION_SECONDS


class AsymmetricJwtTokenService(JwtTokenService):
    def __init__(
        self,
        issuer: str,
        private_key: str,
        public_key: Optional[Union[PublicKeyTypes, str]] = None,
        audience: str = "",
        options: Optional[dict] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.issuer = issuer
        self.audience = audience
        self.private_key = private_key
        if isinstance(public_key, str):
            self.public_key = public_key
        elif public_key is not None:
            self.public_key = public_key.public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode("utf-8")
        else:
            self.public_key = ""
        self.options = options if options else {}
        self.algorithm = "RS256"

    def generate(
        self,
        payload: dict,
        token_type: str = "access",
        seconds_valid: int = ACCESS_TOKEN_EXPIRATION_SECONDS,
    ) -> str:
        if not self.private_key:
            raise NoPrivateKeyException(
                "Cannot generate asymmetric token since no private key provided!"
            )
        return jwt.encode(
            self._prepare(
                payload, token_type, seconds_valid, self.issuer, self.audience
            ),
            self.private_key,
            algorithm=self.algorithm,
        )

    def decode(self, token: str) -> dict:
        if not self.public_key:
            raise NoPublicKeyException(
                "Cannot decode asymmetric token since no public key provided!"
            )
        return jwt.decode(
            token,
            self.public_key,
            algorithms=self.algorithm,
            issuer=self.issuer,
            audience=self.audience,
            options=self.options,
        )

    def get_unverified_claims(self, token: str) -> dict:
        return jwt.get_unverified_claims(token)


class ExtendedAsymmetricJwtTokenService(AsymmetricJwtTokenService):
    def __init__(
        self,
        issuer: str,
        private_key: str,
        kid: str,
        jwk_service: Optional[JwkService] = None,
        audience: str = "",
        options: Optional[dict] = None,
        *args,
        **kwargs,
    ):
        kwargs.update(
            dict(
                issuer=issuer,
                private_key=private_key,
                audience=audience,
                options=options,
            )
        )
        super(ExtendedAsymmetricJwtTokenService, self).__init__(*args, **kwargs)
        self.kid = kid
        self.jwk_service = jwk_service

    def generate(
        self,
        payload: dict,
        token_type: str = "access",
        seconds_valid: int = ACCESS_TOKEN_EXPIRATION_SECONDS,
    ) -> str:
        if not self.private_key:
            raise NoPrivateKeyException(
                "Cannot generate asymmetric token since no private key supplied!"
            )
        return jwt.encode(
            self._prepare(
                payload, token_type, seconds_valid, self.issuer, self.audience
            ),
            self.private_key,
            algorithm=self.algorithm,
            headers={"kid": self.kid},
        )

    def decode(self, token: str) -> dict:
        if not self.jwk_service:
            raise NotAllowedException("No permission!")
        headers = jwt.get_unverified_headers(token)
        kid = headers.get("kid", "")
        if not kid:
            raise NotAllowedException("No permission!")
        claims = jwt.get_unverified_claims(token)
        for key in filter(
            lambda k: k.id == kid,
            self.jwk_service.get_jwks(issuer=claims["iss"], kid=kid),
        ):
            return jwt.decode(
                token,
                key.public_key,
                algorithms=self.algorithm,
                issuer=self.issuer,
                audience=self.audience,
                options=self.options,
            )
        raise NotAllowedException("No permission!")
