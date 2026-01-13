from datetime import datetime, timedelta, timezone

import jwt
from connector_sdk_types.generated import ErrorCode, JWTCredential

from connector.oai.errors import ConnectorError


def sign_jwt(credentials: JWTCredential, expiration_minutes: int = 20) -> str:
    # modify the claims to include the current `iat` and `exp` expiration time in UNIX time (seconds since the Unix epoch)
    now = datetime.now(timezone.utc)
    expiration_time = now + timedelta(minutes=expiration_minutes)
    credentials.claims.iat = int(now.timestamp())
    credentials.claims.exp = int(expiration_time.timestamp())
    try:
        token = jwt.encode(
            payload=credentials.claims.to_dict(),
            key=credentials.secret,
            headers=credentials.headers.to_dict(),
        )
    except Exception as e:
        raise ConnectorError(
            message=f"Failed to sign JWT: {e}",
            error_code=ErrorCode.BAD_REQUEST,
        ) from e
    return token
