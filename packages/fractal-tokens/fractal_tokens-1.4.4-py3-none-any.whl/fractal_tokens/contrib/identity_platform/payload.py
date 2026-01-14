from dataclasses import dataclass

from fractal_tokens.services.generic import TokenPayload as BaseTokenPayload


@dataclass
class TokenPayload(BaseTokenPayload):
    uid: str = ""
    email: str = ""
    email_verified: bool = False
