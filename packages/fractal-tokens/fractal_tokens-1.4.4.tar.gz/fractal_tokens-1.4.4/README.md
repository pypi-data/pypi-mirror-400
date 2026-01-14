# Fractal Tokens

> Fractal Tokens provides a flexible way to generate and verify JWT tokens for your Python applications.

[![PyPI Version][pypi-image]][pypi-url]
[![Build Status][build-image]][build-url]
[![Code Coverage][coverage-image]][coverage-url]
[![Code Quality][quality-image]][quality-url]

<!-- Badges -->

[pypi-image]: https://img.shields.io/pypi/v/fractal-tokens
[pypi-url]: https://pypi.org/project/fractal-tokens/
[build-image]: https://github.com/douwevandermeij/fractal-tokens/actions/workflows/build.yml/badge.svg
[build-url]: https://github.com/douwevandermeij/fractal-tokens/actions/workflows/build.yml
[coverage-image]: https://codecov.io/gh/douwevandermeij/fractal-tokens/branch/main/graph/badge.svg
[coverage-url]: https://codecov.io/gh/douwevandermeij/fractal-tokens
[quality-image]: https://api.codeclimate.com/v1/badges/9242f796b5edee2c327d/maintainability
[quality-url]: https://codeclimate.com/github/douwevandermeij/fractal-tokens

## Installation

```sh
pip install fractal-tokens
```

## Development

Setup the development environment by running:

```sh
make deps
pre-commit install
```

Happy coding.

Occasionally you can run:

```sh
make lint
```

This is not explicitly necessary because the git hook does the same thing.

**Do not disable the git hooks upon commit!**

## Usage

A token is a digital key that gives (temporary) access to a certain (online) resource.
This can be anything, it can give a user access to a backend system (login/authentication), or allow a certain file to be downloaded, etc.

In any case, the token is stand-alone, contains its own permissions, is signed and can (thus) be validated and used in a stateless way.
Only to be able to validate the signature, a key related to the key that has been used to sign the token, is necessary to the validating service (the validator).

In case of a symmetric encryption key, the exact same "secret key" needs to be available to the validator.\
In case of an asymmetric encryption key (public/private key pair), the public key needs to be available to the validator (assuming the token has been signed with the private key).

### Dummy TokenService

To illustrate how the token service works we'll be using a dummy TokenService. This dummy TokenService doesn't use encryption.
In our case, it uses JSON to generate and verify tokens (json.dumps and json.loads respectively).

Consider the following TokenService:

```python
class DummyJsonTokenService(TokenService):
    def __init__(self, token_payload_cls: Type[TokenPayload] = TokenPayload):
        self.token_payload_cls = token_payload_cls

    def generate(
        self,
        payload: dict,
        token_type: str = "access",
        seconds_valid: int = ACCESS_TOKEN_EXPIRATION_SECONDS,
    ) -> str:
        return json.dumps(self._prepare(payload, token_type, seconds_valid, "dummy"))

    def verify(self, token: str, *, typ: str = "access") -> TokenPayload:
        try:
            return self.token_payload_cls(**self.decode(token))
        except Exception:
            raise TokenInvalidException()

    def decode(self, token: str) -> dict:
        return json.loads(token)

    def get_unverified_claims(self, token: str) -> dict:
        return self.decode(token)
```

Note the `generate` function calls `json.dumps` and the `decode` function, which is also called from `verify`, will call `json.loads`.

The generated tokens from this TokenService are in a JSON format. The JSON formatted tokens can be verified and a TokenPayload object will be returned.

This TokenService can be used during testing. The generated tokens are human-readable, so easy to debug.

Notice the `verify` function returns a TokenPayload object.

### TokenPayload

The `verify` function of a TokenService returns a TokenPayload object, or a subclass. To use a subclass, that class needs to be registered upon initialization of the TokenService.

The TokenPayload is a contract about the payload of the token.

While generating and verifying tokens is stateless, it can be handy to make agreements about the payload structure of the tokens.
Stateless token authentication can be particularly handy in a microservice architecture, where one microservice generated the token
and another consuming (validating) it to be able to process something on behalf of the token's subject.
Since both microservices have their own application context, they don't share the same code (directly).
This means that the payload that is used to generate the token, may be of a different structure than the payload that is expected in the consuming service.
This may happen when one of the two microservices gets a change regarding the payload structure and the other doesn't.

It is a good habit to make at least some constraints around the token payload structure and the TokenPayload object may be of help here.
By default, the TokenPayload just contains default JWT claims and a custom claim `typ` (type of token).
A JWT is a JSON Web Token (https://www.rfc-editor.org/rfc/rfc7519) that holds certain claims to be transferred between different applications/services.

```python
@dataclass
class TokenPayload:
    iss: str  # Issuer
    aud: str  # Audience
    sub: str  # Subject
    exp: int  # Expiration Time
    nbf: int  # Not Before
    iat: int  # Issued At
    jti: str  # JWT ID
    typ: str  # Type of token (custom)
```

#### Additional custom claims

While the TokenPayload object is already quite usefull, it can be extended with more custom claims.
For example, when using role-based permissions, the role(s) can be added to the token as well.

Consider the following TokenPayloadRoles object:

```python
@dataclass
class TokenPayloadRoles(TokenPayload):
    roles: List[str]
```

This new TokenPayloadRoles can be used as follows in both the generating service as the consuming service (the validator):

```python
token_service = DummyJsonTokenService(TokenPayloadRoles)
```

The TokenPayloadRoles object needs to be available in all application's contexts.
This means it needs to be either copied over to all applications or injected via a dependency (shared module).

The generating service now needs to provide `roles` when generating the token:

```python
token_service = DummyJsonTokenService(TokenPayloadRoles)
token = token_service.generate(
    {
        "roles": ["admin", "user"],
    }
)
```

Failing to provide a `roles` claim will result in an `InvalidPayloadException` error.

The consuming service can now verify the token and get a TokenPayloadRoles object.

```python
token_service = DummyJsonTokenService(TokenPayloadRoles)
payload = token_service.verify(token)
```

The roles themselves can also be verified, but that's out of scope for the TokenService.
For more information on how to validate roles, please check out the [**Fractal Roles**](https://github.com/douwevandermeij/fractal-roles) package.

### Symmetric JWT TokenService

Symmetric encryption means that the key that is used to encrypt/generate a token, should be the same key that should be used to decrypt/validate the token.
This key should be secret because when someone gets hold of the key, he can not only decrypt/validate tokens, but also encrypt/generate new ones.
Any consumer needs to know the secret key to be able to validate tokens. This could be a security risk.

However, if security of the secret key is covered, symmetric encryption is a viable solution for JWT tokens and can be used as follows:

```python
token_service = SymmetricJwtTokenService(issuer="example", secret_key="**SECRET**")

token = token_service.generate(
    {
        "sub": str(uuid.uuid4()),  # any subject
    }
)

payload = token_service.verify(token)
```

Similar to the dummy TokenService, also the symmetric TokenService supports custom claims:

```python
token_service = SymmetricJwtTokenService(issuer="example", secret_key="**SECRET**", token_payload_cls=TokenPayloadRoles)
```

### Asymmetric JWT TokenService

Asymmetric encryption means that there are two keys, a private one and a public one, that can be used to respectively encrypt/generate and decrypt/validate tokens.
The private key should be kept secret, but the public key doesn't have to be kept secret because it cannot be used to encrypt/generate new tokens, it can only be used to decrypt/validate.
This is useful, because this way any consumer can validate a token without knowing the secret/private key. This is different from symmetric encryption.

To be able to use asymmetric encryption, you need to have or generate a public/private key pair using the [RSA algorithm](https://en.wikipedia.org/wiki/RSA_(cryptosystem)).
In Python this can be accomplished as follows:

```python
def rsa_key_pair():
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(
        backend=default_backend(),
        public_exponent=65537,
        key_size=4096,  # use at least 4096 in production
    )

    private_key = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode("utf-8")

    return private_key, key.public_key()
```

Having the public/private key pair, the asymmetric TokenService can be used as follows:

```python
private_key, public_key = rsa_key_pair()
token_service = AsymmetricJwtTokenService(
    issuer="example", private_key=private_key, public_key=public_key
)

token = token_service.generate(
    {
        "sub": str(uuid.uuid4()),  # any subject
    }
)

payload = token_service.verify(token)
```

Similar to the dummy TokenService, also the asymmetric TokenService supports custom claims:

```python
token_service = AsymmetricJwtTokenService(
    issuer="example", private_key=private_key, public_key=public_key, token_payload_cls=TokenPayloadRoles
)
```

#### Extended Asymmetric JWT TokenService

When using asymmetric encryption, where the public key can be shared with other applications, this enables a lot of possibilities.
For example, a consuming applications can have a list of public keys from several different token generating services, using different private keys.
Also, a token generating service may change to a different private key, for any reason.
When multiple public/private key pairs are in play, it is useful to know which private key has been used to generate the token,
to be able to pick the correct/corresponding public key to validate the token.
To do this, the public/private key pair can be annotated with a **key ID** and can be included in the header of the JWT token.

The `ExtendedAsymmetricJwtTokenService` is similar to the regular `AsymmetricJwtTokenService`, but adds a `kid` (key ID) to the header of the JWT token.
This `kid` refers to a generated key pair (public/private key).

```python
private_key, public_key = rsa_key_pair()
kid = str(uuid.uuid4())
token_service = ExtendedAsymmetricJwtTokenService(
    issuer="example",
    private_key=private_key,
    public_key=public_key,
    kid=kid,
)
```

In the code above an example is shown for generating asymmetric tokens having a `kid` in the header.
While this code can also be used to validate these tokens, this isn't common since the consuming application most probably doesn't know the private key.

A consuming application would use the following code to validate tokens with a `kid`:

```python
headers = jwt.get_unverified_headers(token)
kid = headers.get("kid", None)
public_key_str = find_public_key(kid)  # find public key from a registry using `kid`

public_key = serialization.load_pem_public_key(
    public_key_str.encode("utf-8"), backend=default_backend()
)
token_service = AsymmetricJwtTokenService(
    issuer="example",
    private_key="",  # unknown
    public_key=public_key,
)

token_service.verify(token)
```

Note that we first need to fetch the `kid` from the header and then do a lookup in a registry to find the public key corresponding to the `kid`.
Once we have the public key, we can just use a regular `AsymmetricJwtTokenService` to validate the token, providing the public key.
However, the function `find_public_key(kid)` is not implemented in this example. For this, Fractal Tokens comes with a JWK service.

Also note that this TokenService cannot be used to generate new tokens, as the private key is unknown (or just an empty string).
If you still try to do so, the TokenService will raise an exception.

#### JWK Service

A JWK is a JSON Web Key (https://www.rfc-editor.org/rfc/rfc7517) that refers to a specific encryption key (pair).
The JWK service holds, or interfaces with, a registry with public keys and their respective key IDs.
For a local registry the `LocalJwkService` can be used. The `LocalJwkService` contains an in-memory list of `Jwk` objects.

```python
@dataclass
class Jwk:
    id: str
    public_key: str
```

Creating a `LocalJwkService` would go as follows:

```python
private_key, public_key = rsa_key_pair()

jwk_service = LocalJwkService(
    [
        Jwk(
            id=kid,
            public_key=public_key.public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode("utf-8"),
        )
    ]
)
```

Using it in the `ExtendedAsymmetricJwtTokenService` would go as follows:

```python
token_service = ExtendedAsymmetricJwtTokenService(
    issuer="",
    private_key="",
    kid="",
    jwk_service=jwk_service,
)
```

This TokenService is intended to be used _only_ to validate tokens. It cannot generate new tokens since it doesn't know any private key,
nor kid and therefore the issuer is also not relevant. Hence, these three parameters are empty strings.

When verifying a token with this TokenService, it will look up the `kid` from the token header and find a public key corresponding to the `kid`.

So just call:

```python
token_service.verify(token)
```

When all is fine a payload will be returned. When no public key can be found by `kid`, or `kid` is not present in the token header,
a `NotAllowedException` will be raised.

It might well be that the public key is invalidated/deleted in order to block all access from certain private key.
For example in the case of a security breach.

This might not be happening a lot in case of a `LocalJwkService`, but with a `RemoteJwkService` this makes more sense,
as the public keys are managed in a separate remote service or application.

The `RemoteJwkService` opens an HTTP GET request on a certain endpoint upon calling `get_jwks(...)` on the JWK service.
By default, the `RemoteJwkService` assumes the endpoint will be `/public/keys` on a certain host, and the host is assumed to be in the `iss` (issuer) claim of the token.
The `iss` claim in the token to validate, should then start with (at least) `http`.

Because you can't know beforehand if a token to validate contains a host in the `iss` claim, you can also use the `AutomaticJwkService`
which will check for the issuer to be a host or not and select the `RemoteJwkService` or `LocalJwkService` respectively.

```python
private_key, public_key = rsa_key_pair()

jwk_service = AutomaticJwkService(
    [
        Jwk(
            id=kid,
            public_key=public_key.public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode("utf-8"),
        )
    ]
)
```

### Automatic JWT TokenService

To be fully resilient for multiple types of tokens coming at your consuming application, you can use the `AutomaticJwtTokenService`.

```python
token_service = AutomaticJwtTokenService(
    issuer="example",
    secret_key=secret_key,
    jwk_service=jwk_service,
    auto_load_jwks_from_issuer=False,
)
```

You can supply it with a symmetric secret key and a JWK service.

The parameter `auto_load_jwks_from_issuer` can be used to preload any JWKs from the issuer.
This is only possible when the `issuer` parameter is a url and it provides JWK public keys.
By default `auto_load_jwks_from_issuer` is `False`.

An `AutomaticJwtTokenService` cannot be used for generating tokens. Token generation requires an explicit chosen TokenService to do so.

#### How does it work?

First, based on the algorithm used, which can be found in the `alg` claim of the token, either the `SymmetricJwtTokenService` or an `AsymmetricJwtTokenService` will be used.
Based on the `kid` claim to be available in the token header the regular `AsymmetricJwtTokenService` will be used (in case of no `kid` claim) or the `ExtendedAsymmetricJwtTokenService` will be used.
The `ExtendedAsymmetricJwtTokenService` can be using an `AutomaticJwkService`, so even if the token contains a `kid` claim, it can still contain an `iss` claim which not represents a host.

This doesn't guarantee all tokens can be validated of course, it still depends on the right public key(s) and/or secret key to be available upon validating a token.
But of course this is the whole essence of security.

### FastAPI implementation

Since Fractal Tokens is designed in a generic way, it can be easily integrated in your FastAPI applications.
You can find the full example on a FastAPI demo in the examples in this repository.

We will make use of FastAPI's dependency injection system to verify tokens.

A protected view may look like this:

```python
@app.get("/protected")
def protected(
    payload: TokenPayload = Depends(get_token_payload(token_service=token_service)),
):
    return {"Protected": "Data", "TokenPayload": payload}
```

A more complete example:

```python
from fastapi import Depends, FastAPI
from fractal_tokens.services.generic import TokenPayload
from fractal_tokens.services.jwt.asymmetric import AsymmetricJwtTokenService

from fastapi_demo.utils import get_token_payload, rsa_key_pair

app = FastAPI()

# key pair will renew everytime you restart the app, store externally to reuse
private_key, public_key = rsa_key_pair()

token_service = AsymmetricJwtTokenService(
    issuer="example", private_key=private_key, public_key=public_key
)


@app.get("/protected")
def protected(
    payload: TokenPayload = Depends(get_token_payload(token_service=token_service)),
):
    return {"Protected": "Data", "TokenPayload": payload}
```

The most important function here is `get_token_payload`. This dependency will be injected by FastAPI upon calling this function/endpoint.

The `get_token_payload` could be implemented as follows:

```python
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from fractal_tokens.services.generic import TokenPayload, TokenService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_token_payload(
    *,
    token_service: TokenService,
    typ: str = "access",
):
    def _get_payload(token: str = Depends(oauth2_scheme)) -> TokenPayload:
        return token_service.verify(token, typ=typ)

    return _get_payload
```

The trick is of course calling `verify` on the `token_service`.

```python
return token_service.verify(token, typ=typ)
```

#### Including Roles Verification

I mentioned `get_token_payload` _could_ be implemented like this, because variations or extensions are also possible.
Consider validating roles, as provided in the [**Fractal Roles**](https://github.com/douwevandermeij/fractal-roles) package.

Using Fractal Tokens together with Fractal Roles could result in a function like this:

```python
def get_token_payload_roles(
    *,
    token_service: TokenService,
    roles_service: BaseRolesService,
    endpoint: str = "",
    method: str = "get",
    typ: str = "access",
):
    def _get_payload(token: str = Depends(oauth2_scheme)) -> TokenPayloadRoles:
        payload = token_service.verify(token, typ=typ)
        payload = roles_service.verify(payload, endpoint, method)
        return payload

    return _get_payload
```

Notice the `roles_service` next to the `token_service` and the roles verification `roles_service.verify(payload, endpoint, method)`.

The protected view in this case may look like this:

```python
@app.get("/protected")
def protected(
    payload: TokenPayloadRoles = Depends(
        get_token_payload_roles(
            token_service=token_service,
            roles_service=roles_service,
            endpoint="protected",
            method="get",
        )
    ),
):
    return {"Protected": "Data", "TokenPayload": payload}
```
Checkout the examples for a more complete overview of using FastAPI with Fractal Tokens and Fractal Roles.

For more information on how to validate roles, please check out the [**Fractal Roles**](https://github.com/douwevandermeij/fractal-roles) package.
