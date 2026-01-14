"""
OLO Auth API - Authentication and robot access
"""

from typing import Optional, Dict, Any, List


class OLOAuth:
    """
    Authentication API for OLO platform
    Mirrors the JavaScript OLOClient authentication methods
    
    Provides methods for:
    - User authentication (username/password login)
    - Fetching user's robots
    - Token management
    """

    def __init__(self, api_url: str, public_auth_url: Optional[str] = None):
        """
        Initialize OLO Auth

        Args:
            api_url: Base API URL (e.g., https://app.olo-robotics.com)
            public_auth_url: Optional dedicated public auth URL
        """
        self._api_url = api_url.rstrip('/')
        self._public_auth_url = public_auth_url.rstrip('/') if public_auth_url else None
        self._auth_token: Optional[str] = None

    def _get_auth_endpoint(self, path: str) -> str:
        """Get the full URL for an auth endpoint"""
        if self._public_auth_url:
            return f"{self._public_auth_url}/{path}"
        return f"{self._api_url}/public-auth/{path}"

    async def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with username and password

        Args:
            username: Username or email
            password: Password

        Returns:
            Dict with 'success' and 'token' keys

        Raises:
            Exception: If authentication fails
        """
        try:
            import aiohttp
        except ImportError:
            # Fall back to synchronous requests if aiohttp not available
            return self._authenticate_sync(username, password)

        auth_url = self._get_auth_endpoint('login')

        async with aiohttp.ClientSession() as session:
            async with session.post(
                auth_url,
                json={'username': username, 'password': password},
                headers={'Content-Type': 'application/json'}
            ) as response:
                data = await response.json()

                if response.status != 200:
                    raise Exception(data.get('error', 'Authentication failed'))

                # Store token for future requests
                self._auth_token = data.get('token')

                return {
                    'success': True,
                    'token': self._auth_token
                }

    def _authenticate_sync(self, username: str, password: str) -> Dict[str, Any]:
        """Synchronous fallback for authenticate"""
        import requests

        auth_url = self._get_auth_endpoint('login')

        response = requests.post(
            auth_url,
            json={'username': username, 'password': password},
            headers={'Content-Type': 'application/json'}
        )

        data = response.json()

        if response.status_code != 200:
            raise Exception(data.get('error', 'Authentication failed'))

        # Store token for future requests
        self._auth_token = data.get('token')

        return {
            'success': True,
            'token': self._auth_token
        }

    async def get_user_robots(self) -> List[Dict[str, Any]]:
        """
        Get list of robots for the authenticated user

        Returns:
            List of robot dictionaries

        Raises:
            Exception: If not authenticated or request fails
        """
        if not self._auth_token:
            raise Exception('Not authenticated. Please call authenticate() first.')

        try:
            import aiohttp
        except ImportError:
            # Fall back to synchronous requests if aiohttp not available
            return self._get_user_robots_sync()

        robots_url = self._get_auth_endpoint('robots')

        async with aiohttp.ClientSession() as session:
            async with session.get(
                robots_url,
                headers={'Authorization': f'Bearer {self._auth_token}'}
            ) as response:
                data = await response.json()

                if response.status != 200:
                    raise Exception(data.get('error', 'Failed to fetch robots'))

                return data

    def _get_user_robots_sync(self) -> List[Dict[str, Any]]:
        """Synchronous fallback for get_user_robots"""
        import requests

        robots_url = self._get_auth_endpoint('robots')

        response = requests.get(
            robots_url,
            headers={'Authorization': f'Bearer {self._auth_token}'}
        )

        data = response.json()

        if response.status_code != 200:
            raise Exception(data.get('error', 'Failed to fetch robots'))

        return data

    def get_auth_token(self) -> Optional[str]:
        """
        Get stored authentication token

        Returns:
            Current auth token or None
        """
        return self._auth_token

    def set_auth_token(self, token: str) -> None:
        """
        Set authentication token directly (e.g., from stored credentials)

        Args:
            token: Authentication token
        """
        self._auth_token = token

    def clear_auth(self) -> None:
        """Clear authentication token"""
        self._auth_token = None

    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self._auth_token is not None

