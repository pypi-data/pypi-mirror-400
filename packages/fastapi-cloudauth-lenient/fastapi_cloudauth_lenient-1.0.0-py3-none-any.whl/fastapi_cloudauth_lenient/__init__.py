"""
fastapi-cloudauth-lenient: Lenient Firebase authentication for FastAPI.

Extends fastapi-cloudauth with configurable grace periods for time-based JWT claims
(iat and auth_time) to handle tokens issued slightly in the future.
"""

from fastapi_cloudauth.firebase import FirebaseClaims

from .firebase_auth import FirebaseCurrentUserLenient

__all__ = ["FirebaseCurrentUserLenient", "FirebaseClaims"]

