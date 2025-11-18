import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from jose import jwt, JWTError
import requests
from functools import lru_cache
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@lru_cache()
def get_jwks() -> Dict[str, Any]:
    jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
    try:
        response = requests.get(jwks_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch Auth0 configuration"
        )


def verify_auth0_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        jwks = get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
        if not rsa_key:
            logger.warning("Unable to find appropriate key")
            return None

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=[settings.AUTH0_ALGORITHMS],
            audience=settings.AUTH0_API_AUDIENCE,
            issuer=settings.AUTH0_ISSUER
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error verification Auth0 token: {str(e)}")
        return None
