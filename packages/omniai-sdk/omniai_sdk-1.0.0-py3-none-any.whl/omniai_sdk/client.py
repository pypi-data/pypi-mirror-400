"""
Main client for OmniAI API
"""

import requests
from typing import Dict, Any, Optional, List
from .exceptions import OmniAIError, AuthenticationError, ValidationError, RateLimitError
from .messages import Messages
from .contacts import Contacts
from .campaigns import Campaigns
from .analytics import Analytics
from .ai import AI


class Client:
    """
    OmniAI API Client

    Example:
        client = Client('YOUR_API_KEY')
        message = client.messages.send(
            phone='+5511999999999',
            channel='whatsapp',
            type='text',
            content='Olá! Como posso ajudar?'
        )
    """

    def __init__(self, api_key: str, base_url: str = 'http://localhost:3000/api/v1'):
        """
        Initialize OmniAI client

        Args:
            api_key: Your OmniAI API key
            base_url: API base URL (default: http://localhost:3000/api/v1)
        """
        if not api_key:
            raise ValueError('API key is required')

        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'OmniAI-Python/1.0.0'
        })

        # Initialize resource managers
        self.messages = Messages(self)
        self.contacts = Contacts(self)
        self.campaigns = Campaigns(self)
        self.analytics = Analytics(self)
        self.ai = AI(self)

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to API

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests

        Returns:
            Response data as dictionary

        Raises:
            AuthenticationError: Invalid API key
            ValidationError: Invalid request data
            RateLimitError: Rate limit exceeded
            OmniAIError: Other API errors
        """
        url = f'{self.base_url}/{endpoint.lstrip("/")}'

        try:
            response = self.session.request(method, url, **kwargs)

            if response.status_code == 401:
                raise AuthenticationError('Invalid API key')
            elif response.status_code == 400:
                raise ValidationError(response.json().get('message', 'Validation error'))
            elif response.status_code == 429:
                raise RateLimitError('Rate limit exceeded')
            elif response.status_code >= 400:
                raise OmniAIError(f'API error: {response.status_code}')

            return response.json()

        except requests.exceptions.RequestException as e:
            raise OmniAIError(f'Request failed: {str(e)}')

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request"""
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request"""
        return self._request('POST', endpoint, json=data)

    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make PUT request"""
        return self._request('PUT', endpoint, json=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request"""
        return self._request('DELETE', endpoint)
