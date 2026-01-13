# fastapi-cloudauth-lenient

[![PyPI version](https://img.shields.io/pypi/v/fastapi-cloudauth-lenient)](https://pypi.org/project/fastapi-cloudauth-lenient)
[![Python Versions](https://img.shields.io/pypi/pyversions/fastapi-cloudauth-lenient)](https://pypi.org/project/fastapi-cloudauth-lenient/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Lenient Firebase authentication for FastAPI with configurable grace periods for time-based JWT claims.

## Overview

`fastapi-cloudauth-lenient` extends [fastapi-cloudauth](https://github.com/tokusumi/fastapi-cloudauth) to address issues where Firebase (and other JWT providers) may issue tokens with `iat` (issued at) or `auth_time` claims slightly in the future, causing unexpected verification failures.

This library provides a drop-in replacement for `FirebaseCurrentUser` with configurable grace periods for time-based claim validation.

**Related Issue**: [fastapi-cloudauth#65](https://github.com/tokusumi/fastapi-cloudauth/issues/65)

## Features

- Drop-in replacement for `fastapi-cloudauth.firebase.FirebaseCurrentUser`
- Configurable grace periods for `iat` and `auth_time` claims
- Maintains all standard JWT validation (signature, expiration, audience, etc.)
- Full compatibility with FastAPI dependency injection
- Support for custom claims via Pydantic models

## Requirements

- Python 3.8+
- FastAPI
- fastapi-cloudauth >= 0.4.0

## Installation

```bash
# pip
pip install fastapi-cloudauth-lenient
# uv
uv add fastapi-cloudauth-lenient
# Poetry
poetry add fastapi-cloudauth-lenient
```

## Usage

### Basic Authentication

The simplest usage mirrors `fastapi-cloudauth`:

```python
from fastapi import FastAPI, Depends
from fastapi_cloudauth_lenient import FirebaseCurrentUserLenient, FirebaseClaims

app = FastAPI()

get_current_user = FirebaseCurrentUserLenient(
    project_id="your-firebase-project-id"
)

@app.get("/protected/")
def protected_route(current_user: FirebaseClaims = Depends(get_current_user)):
    """Protected endpoint that requires valid Firebase authentication."""
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
    }
```

### Custom Grace Periods

Configure grace periods for `iat` and `auth_time` validation (defaults to 5 seconds):

```python
get_current_user = FirebaseCurrentUserLenient(
    project_id="your-firebase-project-id",
    iat_grace_period_seconds=10,  # Allow iat up to 10 seconds in the future
    auth_time_grace_period_seconds=10,  # Allow auth_time up to 10 seconds in the future
)
```

### Custom Claims

Extend `FirebaseClaims` to capture additional custom claims from your Firebase tokens:

```python
from pydantic import Field
from fastapi_cloudauth.firebase import FirebaseClaims
from fastapi_cloudauth_lenient import FirebaseCurrentUserLenient

class CustomFirebaseClaims(FirebaseClaims):
    """Extended claims model with custom fields."""
    name: str = Field(None, alias="name")
    admin: bool = Field(None, alias="admin")
    auth_time: int = Field(None, alias="auth_time")

# Initialize the authentication handler
get_current_user = FirebaseCurrentUserLenient(
    project_id="your-firebase-project-id"
)

# Override the user info model
get_current_user.user_info = CustomFirebaseClaims

@app.get("/user/profile/")
def user_profile(current_user: CustomFirebaseClaims = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "name": current_user.name,
        "is_admin": current_user.admin,
    }
```

Alternatively, use the `claim()` method:

```python
get_user_detail = get_current_user.claim(CustomFirebaseClaims)

@app.get("/detailed/")
def detailed_user(user: CustomFirebaseClaims = Depends(get_user_detail)):
    return f"Hello, {user.name}"
```

## How It Works

When Firebase issues a JWT token, the `iat` (issued at) and `auth_time` claims may occasionally be set to a timestamp slightly in the future (typically 1 second). This is due to clock skew between Firebase servers and validation servers.

Standard JWT libraries reject these tokens as invalid, causing authentication failures.

`fastapi-cloudauth-lenient` adds a configurable grace period:
- **iat grace period**: Allows the `iat` claim to be up to N seconds in the future
- **auth_time grace period**: Allows the `auth_time` claim to be up to N seconds in the future

All other JWT validations (signature, expiration, audience, issuer) remain unchanged.

## API Reference

### `FirebaseCurrentUserLenient`

```python
class FirebaseCurrentUserLenient(FirebaseCurrentUser):
    def __init__(
        self,
        project_id: str,
        iat_grace_period_seconds: int = 5,
        auth_time_grace_period_seconds: int = 5,
    ):
        ...
```

**Parameters:**
- `project_id` (str): Firebase project ID
- `iat_grace_period_seconds` (int, optional): Grace period for `iat` claim validation. Default: 5
- `auth_time_grace_period_seconds` (int, optional): Grace period for `auth_time` claim validation. Default: 5

**Inherits all methods from:** `fastapi_cloudauth.firebase.FirebaseCurrentUser`

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on top of [fastapi-cloudauth](https://github.com/tokusumi/fastapi-cloudauth)
- Inspired by the community discussion in [fastapi-cloudauth#65](https://github.com/tokusumi/fastapi-cloudauth/issues/65)
