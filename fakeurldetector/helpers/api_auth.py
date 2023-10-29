from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyQuery

from fakeurldetector import Config, LOGGER

api_key_query_auth = APIKeyQuery(name="api_key", auto_error=True)


async def verify_api_key(api_key_query: str = Security(api_key_query_auth)):
    if api_key_query != Config.API_KEY:
        LOGGER.debug("API Key Mismatch")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
