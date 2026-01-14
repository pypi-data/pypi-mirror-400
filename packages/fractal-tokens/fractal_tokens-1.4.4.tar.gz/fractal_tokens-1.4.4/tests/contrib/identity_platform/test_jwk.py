def test_jwk():
    from fractal_tokens.contrib.identity_platform.jwk import (
        GoogleIdentityPlatformJwkService,
    )

    assert len(GoogleIdentityPlatformJwkService().get_jwks()) > 0


def test_jwk_caching():
    from unittest.mock import patch

    from fractal_tokens.contrib.identity_platform.jwk import (
        GoogleIdentityPlatformJwkService,
    )

    service = GoogleIdentityPlatformJwkService()

    # Mock urlopen to track how many times it's called
    with patch("urllib.request.urlopen") as mock_urlopen:
        # Setup mock response
        mock_response = mock_urlopen.return_value
        mock_response.read.return_value = b'{"key1": "cert1", "key2": "cert2"}'

        # First call should hit the network
        jwks1 = service.get_jwks()
        assert len(jwks1) == 2
        assert mock_urlopen.call_count == 1

        # Second call with same parameters should use cache
        jwks2 = service.get_jwks()
        assert len(jwks2) == 2
        assert mock_urlopen.call_count == 1  # Still 1, no additional network call

        # Third call with different parameters creates a new cache entry
        jwks3 = service.get_jwks(issuer="different", kid="different")
        assert len(jwks3) == 2
        assert mock_urlopen.call_count == 2  # New cache entry, so another network call

        # Fourth call with same different parameters should use that cache entry
        jwks4 = service.get_jwks(issuer="different", kid="different")
        assert len(jwks4) == 2
        assert (
            mock_urlopen.call_count == 2
        )  # Still 2, cache hit for the different params


def test_token_payload():
    from fractal_tokens.contrib.identity_platform.payload import TokenPayload

    assert TokenPayload(
        iss="",
        aud="",
        sub="",
        exp=0,
        nbf=0,
        iat=0,
        jti="",
        typ="",
    )
