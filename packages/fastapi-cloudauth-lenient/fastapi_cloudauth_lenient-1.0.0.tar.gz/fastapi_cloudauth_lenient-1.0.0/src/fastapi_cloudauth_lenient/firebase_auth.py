from calendar import timegm
from datetime import datetime, timezone
from typing import Dict
from fastapi import HTTPException, status
from fastapi_cloudauth.firebase import FirebaseCurrentUser, FirebaseClaims
from fastapi_cloudauth.messages import (
    NOT_AUTHENTICATED,
    NOT_VERIFIED,
)
from fastapi_cloudauth.verification import JWKsVerifier
from fastapi_cloudauth.firebase import FirebaseExtraVerifier
from jose import JWTError, jwt
from loguru import logger


class _JWKsVerifierWithIatGracePeriod(JWKsVerifier):
    """
    Extends the default JWT claim verification functionality with a configurable grace period for
    iat (issued at) claims. It was observed that Firebase, Cognito, and other JWT providers may
    issue tokens with iat claim values one second in the future, and as a result, unexpectedly fail token
    verification. This class maintains all existing functionality in `JWKsVerifier` and only
    modifies the relevant iat verification section of `_verify_claims()`.

    NOTE: Developers should intermittently monitor activity on the corresponding fastapi-cloudauth
    issue: https://github.com/tokusumi/fastapi-cloudauth/issues/65
    """

    def __init__(
        self,
        jwks,
        iat_grace_period_seconds,
        audience=None,
        issuer=None,
        auto_error=True,
        *args,
        extra=None,
        **kwargs,
    ):
        super().__init__(
            jwks, audience, issuer, auto_error, *args, extra=extra, **kwargs
        )
        self._iat_grace_period_seconds = iat_grace_period_seconds

    def _verify_claims(self, http_auth):
        """
        Adds a grace period to iat claim verification. All other logic from `JWKsVerifier` is maintained as-is.
        """
        is_verified = False
        try:
            # check the expiration, issuer
            is_verified = jwt.decode(
                http_auth.credentials,
                "",
                audience=self._aud,
                issuer=self._iss,
                options={
                    "verify_signature": False,
                    "verify_sub": False,
                    "verify_at_hash": False,
                },  # done
            )
        except jwt.ExpiredSignatureError as e:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=NOT_VERIFIED
                ) from e
            return False
        except jwt.JWTClaimsError as e:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=NOT_VERIFIED
                ) from e
            return False
        except JWTError as e:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=NOT_AUTHENTICATED
                ) from e
            else:
                return False

        claims = jwt.get_unverified_claims(http_auth.credentials)

        # iat validation with grace period
        if claims.get("iat"):
            iat = int(claims["iat"])
            now = timegm(datetime.now(timezone.utc).utctimetuple())
            if now < iat - self._iat_grace_period_seconds:
                logger.warning(
                    f"iat token [{iat}] was issued before current time [{now}]"
                )
                if self.auto_error:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED, detail=NOT_VERIFIED
                    )
                return False

        if self._extra_verifier:
            # check extra claims validation
            is_verified = self._extra_verifier(
                claims=claims, auto_error=self.auto_error
            )

        return is_verified


class _FirebaseExtraVerifierWithAuthTimeGracePeriod(FirebaseExtraVerifier):
    """
    Extends the default Firebase-specific extra JWT verification functionality with a
    configurable grace period for auth_time claims. It was observed that Firebase may issue
    tokens with auth_time claim values one second in the future, and as a result, unexpectedly
    fail token verification. This class maintains all existing functionality in `FirebaseExtraVerifier`
    and only modifies the relevant auth_time verification logic.
    """

    def __init__(self, project_id, auth_time_grace_period_seconds):
        super().__init__(project_id)
        self._auth_time_grace_period_seconds = auth_time_grace_period_seconds

    def __call__(self, claims: Dict[str, str], auto_error: bool = True) -> bool:
        if claims.get("auth_time"):
            auth_time = int(claims["auth_time"])
            now = timegm(datetime.now(timezone.utc).utctimetuple())
            if now < auth_time - self._auth_time_grace_period_seconds:
                logger.warning(
                    f"auth_time token [{auth_time}] was issued before current time [{now}]"
                )
                if auto_error:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED, detail=NOT_VERIFIED
                    )
                return False
        return True


class FirebaseCurrentUserLenient(FirebaseCurrentUser):
    """
    Firebase authentication handler with lenient time-based claim verification.
    
    Extends `FirebaseCurrentUser` from fastapi-cloudauth with configurable grace periods
    for `iat` (issued at) and `auth_time` claims. This addresses issues where Firebase
    may issue tokens with timestamps slightly in the future, causing unexpected verification
    failures.
    
    Args:
        project_id: Firebase project ID
        iat_grace_period_seconds: Grace period for `iat` claim validation (default: 5 seconds)
        auth_time_grace_period_seconds: Grace period for `auth_time` claim validation (default: 5 seconds)
        
    Example:
        ```python
        from fastapi import FastAPI, Depends
        from fastapi_cloudauth_lenient import FirebaseCurrentUserLenient, FirebaseClaims
        
        app = FastAPI()
        
        get_current_user = FirebaseCurrentUserLenient(
            project_id="your-project-id"
        )
        
        @app.get("/user/")
        def secure_user(current_user: FirebaseClaims = Depends(get_current_user)):
            return f"Hello, {current_user.user_id}"
        ```
    """
    
    def __init__(
        self,
        project_id: str,
        iat_grace_period_seconds: int = 5,
        auth_time_grace_period_seconds: int = 5,
    ):
        super().__init__(project_id=project_id)
        
        # Override the verifier with lenient versions
        _default_verifier = self.verifier
        self.verifier = _JWKsVerifierWithIatGracePeriod(
            _default_verifier._jwks,
            iat_grace_period_seconds=iat_grace_period_seconds,
            audience=_default_verifier._aud,
            issuer=_default_verifier._iss,
            auto_error=_default_verifier._auto_error,
            extra=_FirebaseExtraVerifierWithAuthTimeGracePeriod(
                project_id=_default_verifier._aud,
                auth_time_grace_period_seconds=auth_time_grace_period_seconds,
            ),
        )
