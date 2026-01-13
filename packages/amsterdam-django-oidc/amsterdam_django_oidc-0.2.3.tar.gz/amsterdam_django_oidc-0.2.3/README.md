# amsterdam-django-oidc
This package contains an authentication backend for Django.
It is currently based on the authentication backend provided by Mozilla through the `mozilla-django-oidc` package.
The Mozilla package however does not validate the `iss`, `aud` and `exp` claims of the access token and always calls
the `userinfo` endpoint on the identity provider. Unfortunately that is not adequate for the use case within the 
landscape of applications of the city of Amsterdam. Hence, the reason for this solution.

Instead of calling the `userinfo` endpoint, it will validate the aforementioned claims.

# Install
The package can be installed using your favorite package manager for python.
For example using uv:
```shell
uv add amsterdam-django-oidc
```

Or using pip:
```shell
pip install amsterdam-django-oidc
```

# Usage
Add the backend to the setting `AUTHENTICATION_BACKENDS`:
```python
# settings.py
AUTHENTICATION_BACKENDS = [
    # ...
    "amsterdam_django_oidc.OIDCAuthenticationBackend",
]
```

There are also a few settings required in addition to those of the Mozilla package:

| Name                   | Type      | Description                                                                                                     |
|------------------------|-----------|-----------------------------------------------------------------------------------------------------------------|
| OIDC_OP_ISSUER         | str       | The allowed issuer, the value of the `iss` claim in the access token must match the value of this setting       |
| OIDC_TRUSTED_AUDIENCES | list[str] | Audiences that we trust, at least one of the values of the `aud` claim must match one the values of this setting |
| OIDC_VERIFY_AUDIENCE   | bool      | Controls wether or not to verify the `aud` claim, default: `True`                                               |

# Development
In order to facilitate further development of this package a containerized setup is provided. 

## Building the container images
```shell
docker compose build
```

## Running development tools
It's recommended to start a container and use the shell inside the container:
```shell
docker compose run --rm amsterdam-django-oidc bash
```
Once you see the shell it's possible to run commands like: 
```shell
uv run ruff check
uv run mypy .
uv run pytest
```
