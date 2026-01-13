import json
import jwt
import time
import requests
from ..config.config import config
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from ..utils.logger import get_logger
from ..utils.token_utils import set_internal_token, is_token_expired
from urllib.parse import urlparse

logger = get_logger()

class AGClient:
    """
    Low-level HTTP client for AG Server requests.
    Handles token refresh and request routing.
    """
    def __init__(
        self,
        URL,
        PORT,
        headers=None,
    ):
        """Initialize low-level AG HTTP client.

        Args:
            URL (str): Base host (scheme+host) e.g. http://localhost
            PORT (str): Port as string
            headers (dict|None): Initial headers (may contain external Authorization token)
        """
        self.url = URL
        self.port = PORT
        url = urlparse(URL)
        self.base_url = url._replace(netloc=f"{url.hostname}:{PORT}").geturl()
        self.session = requests.Session()

        if headers:
            self.session.headers.update(headers)

    def update_headers(self, headers):
        self.session.headers.update(headers)

    def get(self, endpoint, data=None, json=None, params=None, headers=None):
        return self._make_request(
            "GET", endpoint, data=data, json=json, params=params, headers=headers
        )

    def post(self, endpoint, data=None, json=None, params=None, headers=None, files=None):
        return self._make_request(
            "POST", endpoint, data=data, json=json, params=params, headers=headers, files=files
        )

    def put(self, endpoint, data=None, json=None, params=None, headers=None):
        return self._make_request(
            "PUT", endpoint, data=data, json=json, params=params, headers=headers
        )

    def delete(self, endpoint, data=None, json=None, params=None, headers=None):
        return self._make_request(
            "DELETE", endpoint, data=data, json=json, params=params, headers=headers
        )
    
    def __is_token_expired(self) -> bool:
        """Check if the internal access token is expired."""
        return is_token_expired(dict(self.session.headers))

    def __get_refresh_token(self) -> None:
        """Refresh the internal access token if expired.
        
        Note: Only the internal token (from API key login or token exchange) is refreshed.
        The proxy token provided by the user for token exchange is never refreshed by us.
        """
        try:
            if not self.session.headers.get('refresh_token'):
                return
            if not self.__is_token_expired():
                return
            res = requests.post(
                config.AGENT_CONSOLE_URL + "/jupyter/token/refresh",
                json={"refresh_token": self.session.headers.get('refresh_token')},
                headers=dict(self.session.headers),
            )
            res.raise_for_status()
            data = res.json()
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            if access_token:
                # Determine header based on X-Authorization presence (indicates proxy mode)
                proxy_auth = bool(self.session.headers.get('X-Authorization'))
                set_internal_token(self.session.headers, access_token, refresh_token or '', proxy_auth)
            logger.debug("Token refreshed successfully")
        except Exception as e:
            logger.error(f"Error while refreshing token: {str(e)}")
            raise ConnectionError("Error while refreshing token")

    def _make_request(
        self, method, endpoint, data=None, json=None, params=None, headers=None, files=None
    ):
        # Refresh token if we have internal auth (either in Authorization or X-Authorization)
        if self.session.headers.get('Authorization') or self.session.headers.get('X-Authorization'):
            self.__get_refresh_token()
        url = endpoint
        
        # Log request details
        logger.info(f"Making {method} request to: {url}")
        request_headers = headers if headers else self.session.headers
        logger.debug(f"Request headers: {dict(request_headers)}")
        if json:
            logger.debug(f"Request JSON body: {json}")
        if data:
            logger.debug(f"Request data: {data}")
        if params:
            logger.debug(f"Request params: {params}")
        
        verify = True
        if hasattr(config, 'TLS_ENABLED'):
            verify = config.TLS_ENABLED.lower() == "true"
            if not verify:
                urllib3.disable_warnings(InsecureRequestWarning)
                logger.debug("TLS verification disabled")
        if headers:
            with self.session as s:
                s.headers.update(headers)
                response = s.request(method, url, data=data, json=json, params=params, files=files, verify=verify)
                s.headers.update(self.session.headers)
        else:
            response = self.session.request(
                method, url, data=data, json=json, params=params, verify=verify
            )
        logger.debug(f"{method} request to {endpoint} completed with status {response.status_code}")
        return response


def get_ag_client():
    """
    Connect to AG server Server and initialize the Oblv client, AG server Server URL and port from config.
    """
    logger.debug(f"Creating AG client for url: {config.AGENT_JUPYTER_URL} port: {config.AGENT_JUPYTER_PORT}")
    return AGClient(
        config.AGENT_JUPYTER_URL,
        config.AGENT_JUPYTER_PORT,
    )
