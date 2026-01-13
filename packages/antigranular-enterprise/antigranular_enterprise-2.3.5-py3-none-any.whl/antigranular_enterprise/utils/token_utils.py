"""
Shared token utilities for header management across clients.

Note: These utilities manage the INTERNAL token (obtained via API key login or token exchange).
The proxy/external token (provided by user for token exchange) is never refreshed by us.
"""
import jwt
import time
from .logger import get_logger

logger = get_logger()


def get_internal_token_header(proxy_auth_provided: bool) -> str:
    """Return the header name where internal token should be stored."""
    return 'X-Authorization' if proxy_auth_provided else 'Authorization'


def format_bearer_token(token: str) -> str:
    """Ensure token has Bearer prefix."""
    if not token:
        return token
    return token if token.lower().startswith('bearer ') else f"Bearer {token}"


def set_internal_token(headers: dict, access_token: str, refresh_token: str, proxy_auth_provided: bool) -> None:
    """
    Set internal token in the appropriate header.
    
    Args:
        headers: Headers dict to update (mutated in place)
        access_token: The access token to set
        refresh_token: The refresh token to set (optional)
        proxy_auth_provided: Whether user provided proxy Authorization header
    """
    token_value = format_bearer_token(access_token)
    header_name = get_internal_token_header(proxy_auth_provided)
    
    headers[header_name] = token_value
    if refresh_token:
        headers['refresh_token'] = refresh_token
    
    logger.debug(f"Internal token set in {header_name}")


def is_token_expired(headers: dict, proxy_auth_provided: bool = None) -> bool:
    """
    Check if the internal token is expired.
    
    Args:
        headers: Headers dict containing the token
        proxy_auth_provided: If known, check specific header. If None, check both.
    
    Returns:
        True if token is missing or expired
    """
    try:
        # Determine which header to check
        if proxy_auth_provided is not None:
            token = headers.get(get_internal_token_header(proxy_auth_provided), '')
        else:
            # Check X-Authorization first, fall back to Authorization
            token = headers.get('X-Authorization', '') or headers.get('Authorization', '')
        
        if not token:
            return True
        
        # Strip Bearer prefix
        if token.lower().startswith('bearer '):
            token = token[7:]
        
        payload = jwt.decode(token, options={"verify_signature": False})
        current_time = time.time() + 10  # 10 seconds buffer
        return payload.get('exp', 0) < current_time
    except Exception:
        logger.exception("Failed to determine token expiration; treating token as expired.")
        return True
