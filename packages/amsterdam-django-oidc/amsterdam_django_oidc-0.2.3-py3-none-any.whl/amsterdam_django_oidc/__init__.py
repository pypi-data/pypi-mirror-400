import time
from typing import Any, TypedDict

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from mozilla_django_oidc.auth import (
    OIDCAuthenticationBackend as MozillaOIDCAuthenticationBackend,
)


class Payload(TypedDict):
    iss: str
    aud: str | list[str]
    exp: int


class OIDCAuthenticationBackend(MozillaOIDCAuthenticationBackend):
    def validate_issuer(self, payload: Payload) -> None:
        """https://www.rfc-editor.org/rfc/rfc7519#section-4.1.1 states that the claim
        will contain a single string.
        https://learn.microsoft.com/en-us/entra/identity-platform/access-token-claims-reference#payload-claims
        also states it will contain a single string.
        https://datatracker.ietf.org/doc/html/rfc9068#section-4-5.3 states that it must
        match exactly.
        """
        issuer = self.get_settings("OIDC_OP_ISSUER")
        iss = payload.get("iss")

        if issuer != iss:
            msg = (f'"iss": {iss} does not match configured value for OIDC_OP_ISSUER:'
                   f' {issuer}')
            raise PermissionDenied(msg)

    def validate_audience(self, payload: Payload) -> None:
        """https://learn.microsoft.com/en-us/entra/identity-platform/access-token-claims-reference#payload-claims
        states that the aud claim will only be a string.
        However, https://openid.net/specs/openid-connect-core-1_0.html#IDToken states
        that the aud claim can be either an array of strings or a single string.
        https://www.rfc-editor.org/rfc/rfc7519#section-4.1.3 also states that the aud
        claim can contain an array of strings or a single string.
        https://datatracker.ietf.org/doc/html/rfc9068#section-4-5.4 states:
            The resource server MUST validate that the "aud" claim contains a resource
            indicator value corresponding to an identifier the resource server expects
            for itself. The JWT access token MUST be rejected if "aud" does not contain
            a resource indicator of the current resource server as a valid audience.
        Therefor we need to handle both cases.
        """
        if self.get_settings("OIDC_VERIFY_AUDIENCE", True):  # noqa: FBT003
            trusted_audiences = self.get_settings("OIDC_TRUSTED_AUDIENCES", [])
            if trusted_audiences is None:
                msg = "OIDC_TRUSTED_AUDIENCES must not be None!"
                raise TypeError(msg)

            audiences = payload.get("aud")
            if audiences is None:
                msg = "Aud claim missing"
                raise SuspiciousOperation(msg)

            if isinstance(audiences, str):
                audiences = [audiences]

            trusted_audience_found = False
            for audience in audiences:
                if audience in trusted_audiences:
                    trusted_audience_found = True
                    break

            if not trusted_audience_found:
                msg = "No trusted audience found"
                raise PermissionDenied(msg)

    def validate_expiry(self, payload: Payload) -> None:
        """https://learn.microsoft.com/en-us/entra/identity-platform/access-token-claims-reference#payload-claims
        states that this claim will contain an integer representing a Unix time stamp.
        https://www.rfc-editor.org/rfc/rfc7519#section-4.1.4 states that the claim will
        be a number containing a NumericDate value. NumericDate is defined as:
            A JSON numeric value representing the number of seconds from
            1970-01-01T00:00:00Z UTC until the specified UTC date/time,
            ignoring leap seconds. This is equivalent to the IEEE Std 1003.1,
            2013 Edition [POSIX.1] definition "Seconds Since the Epoch", in
            which each day is accounted for by exactly 86400 seconds, other
            than that non-integer values can be represented. See RFC 3339
            [RFC3339] for details regarding date/times in general and UTC in
            particular.
        https://datatracker.ietf.org/doc/html/rfc9068#section-4-5.6 states:
            The current time MUST be before the time represented by the "exp" claim.
            Implementers MAY provide for some small leeway, usually no more than a few
            minutes, to account for clock skew.
        """
        expire_time = payload.get("exp")
        if expire_time is None:
            msg = "Exp claim missing"
            raise SuspiciousOperation(msg)

        now = time.time()
        if now > expire_time:
            msg = f"Access-token is expired {now} > {expire_time}"
            raise PermissionDenied(msg)

    def validate_access_token(self, payload: Payload) -> None:
        self.validate_issuer(payload)
        self.validate_audience(payload)
        self.validate_expiry(payload)

    def get_userinfo(
        self,
        access_token: str,
        id_token: str | None = None,  # noqa: ARG002
        payload: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> Payload:
        access_token_payload = (
            self._decode_access_token_and_validate_signature(access_token))
        self.validate_access_token(access_token_payload)

        return access_token_payload

    def _decode_access_token_and_validate_signature(self, access_token: str) -> Payload:
        """Based on https://github.com/mozilla/mozilla-django-oidc/blob/2c2334fdc9b2fc72a492b5f0e990b4c30de68363/mozilla_django_oidc/auth.py#L204"""
        if self.OIDC_RP_SIGN_ALGO.startswith("RS") or self.OIDC_RP_SIGN_ALGO.startswith(
            "ES",
        ):
            if self.OIDC_RP_IDP_SIGN_KEY is not None:
                key = self.OIDC_RP_IDP_SIGN_KEY
            else:
                key = self.retrieve_matching_jwk(access_token)
        else:
            key = self.OIDC_RP_CLIENT_SECRET

        return self.get_payload_data(access_token, key)
