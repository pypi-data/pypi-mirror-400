"""
Firebase Authentication Module
"""

from fastapi import Header, HTTPException
from firebase_admin import auth

from commons.utils.constants import constants


async def get_authenticated_user_uuid(authorization: str = Header(None)):
    """Retrieve the authenticated user's UUID from the provided token."""

    if constants.EXECUTION_ENVIRONMENT == "local":
        return constants.LOCAL_USER_UUID

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid authentication token"
        )

    # Extract the token from the header
    token = authorization.split(" ")[1]
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token.get("uid")
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
