import uuid

import pytest


@pytest.fixture
def rsa_key_pair():
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(
        backend=default_backend(),
        public_exponent=65537,
        key_size=1024,  # use at least 4096 in production, not 1024, but this is quicker in tests!
    )

    private_key = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode("utf-8")

    kid = str(uuid.uuid4())

    return kid, private_key, key.public_key()


@pytest.fixture
def asymmetric_jwt_token_service(rsa_key_pair):
    kid, private_key, public_key = rsa_key_pair

    from fractal_tokens.services.jwt.asymmetric import AsymmetricJwtTokenService

    yield AsymmetricJwtTokenService(
        issuer="test",
        private_key=private_key,
        public_key=public_key,
        options={"verify_aud": False},
    )


@pytest.fixture
def extended_asymmetric_jwt_token_service(rsa_key_pair, automatic_jwk_service):
    kid, private_key, public_key = rsa_key_pair

    from fractal_tokens.services.jwt.asymmetric import ExtendedAsymmetricJwtTokenService

    yield ExtendedAsymmetricJwtTokenService(
        issuer="test",
        private_key=private_key,
        kid=kid,
        jwk_service=automatic_jwk_service,
        options={"verify_aud": False},
    )


@pytest.fixture
def extended_asymmetric_jwt_token_service_verify_aud(
    rsa_key_pair, automatic_jwk_service
):
    kid, private_key, public_key = rsa_key_pair

    from fractal_tokens.services.jwt.asymmetric import ExtendedAsymmetricJwtTokenService

    yield ExtendedAsymmetricJwtTokenService(
        issuer="test",
        private_key=private_key,
        kid=kid,
        jwk_service=automatic_jwk_service,
        audience="audience",
        options={"verify_aud": True},
    )


@pytest.fixture
def asymmetric_jwt_token_service_no_private_key(asymmetric_jwt_token_service):
    asymmetric_jwt_token_service.private_key = ""
    yield asymmetric_jwt_token_service


@pytest.fixture
def asymmetric_jwt_token_service_no_public_key(asymmetric_jwt_token_service):
    asymmetric_jwt_token_service.public_key = ""
    yield asymmetric_jwt_token_service


@pytest.fixture
def extended_asymmetric_jwt_token_service_no_private_key(
    extended_asymmetric_jwt_token_service,
):
    extended_asymmetric_jwt_token_service.private_key = ""
    yield extended_asymmetric_jwt_token_service


@pytest.fixture
def extended_asymmetric_jwt_token_service_no_jwk_service(
    extended_asymmetric_jwt_token_service,
):
    extended_asymmetric_jwt_token_service.jwk_service = None
    yield extended_asymmetric_jwt_token_service


@pytest.fixture
def asymmetric_jwt_token_service_string_public_key(rsa_key_pair):
    kid, private_key, public_key = rsa_key_pair

    from cryptography.hazmat.primitives import serialization

    from fractal_tokens.services.jwt.asymmetric import AsymmetricJwtTokenService

    # Convert public key to string format
    public_key_str = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    yield AsymmetricJwtTokenService(
        issuer="test",
        private_key=private_key,
        public_key=public_key_str,  # Pass as string instead of object
        options={"verify_aud": False},
    )
