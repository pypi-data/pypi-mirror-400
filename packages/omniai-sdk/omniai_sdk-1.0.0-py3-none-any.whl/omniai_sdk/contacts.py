"""
Contacts API resource
"""

from typing import Dict, Any, Optional, List


class Contacts:
    """Manage contacts"""

    def __init__(self, client):
        self.client = client

    def create(
        self,
        name: str,
        phone: str,
        email: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create a new contact

        Args:
            name: Contact name
            phone: Phone number
            email: Email address (optional)
            tags: Contact tags (optional)
            metadata: Additional metadata (optional)

        Returns:
            Contact object
        """
        data = {
            'name': name,
            'phone': phone
        }

        if email:
            data['email'] = email
        if tags:
            data['tags'] = tags
        if metadata:
            data['metadata'] = metadata

        return self.client.post('/contacts', data)

    def get(self, contact_id: str) -> Dict[str, Any]:
        """Get contact by ID"""
        return self.client.get(f'/contacts/{contact_id}')

    def list(
        self,
        page: int = 1,
        limit: int = 50,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        List contacts

        Args:
            page: Page number
            limit: Results per page
            search: Search query
            tags: Filter by tags

        Returns:
            Paginated contacts list
        """
        params = {'page': page, 'limit': limit}
        if search:
            params['search'] = search
        if tags:
            params['tags'] = ','.join(tags)

        return self.client.get('/contacts', params)

    def update(
        self,
        contact_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Update contact"""
        data = {}
        if name:
            data['name'] = name
        if email:
            data['email'] = email
        if tags:
            data['tags'] = tags
        if metadata:
            data['metadata'] = metadata

        return self.client.put(f'/contacts/{contact_id}', data)

    def delete(self, contact_id: str) -> Dict[str, Any]:
        """Delete contact"""
        return self.client.delete(f'/contacts/{contact_id}')
