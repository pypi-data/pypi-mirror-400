"""
Messages API resource
"""

from typing import Dict, Any, Optional, List


class Messages:
    """Manage messages"""

    def __init__(self, client):
        self.client = client

    def send(
        self,
        phone: str,
        channel: str,
        type: str,
        content: str,
        media_url: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Send a message

        Args:
            phone: Recipient phone number (E.164 format)
            channel: Channel (whatsapp, email, sms, telegram)
            type: Message type (text, image, video, document, audio)
            content: Message content
            media_url: URL for media messages (optional)
            metadata: Additional metadata (optional)

        Returns:
            Message object

        Example:
            message = client.messages.send(
                phone='+5511999999999',
                channel='whatsapp',
                type='text',
                content='Olá! Como posso ajudar?'
            )
        """
        data = {
            'phone': phone,
            'channel': channel,
            'type': type,
            'content': content
        }

        if media_url:
            data['mediaUrl'] = media_url
        if metadata:
            data['metadata'] = metadata

        return self.client.post('/messages', data)

    def get(self, message_id: str) -> Dict[str, Any]:
        """
        Get message by ID

        Args:
            message_id: Message ID

        Returns:
            Message object
        """
        return self.client.get(f'/messages/{message_id}')

    def list(
        self,
        page: int = 1,
        limit: int = 50,
        channel: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List messages

        Args:
            page: Page number
            limit: Results per page
            channel: Filter by channel
            status: Filter by status

        Returns:
            Paginated messages list
        """
        params = {'page': page, 'limit': limit}
        if channel:
            params['channel'] = channel
        if status:
            params['status'] = status

        return self.client.get('/messages', params)

    def send_bulk(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send multiple messages

        Args:
            messages: List of message objects

        Returns:
            Bulk send result

        Example:
            result = client.messages.send_bulk([
                {
                    'phone': '+5511999999999',
                    'channel': 'whatsapp',
                    'type': 'text',
                    'content': 'Message 1'
                },
                {
                    'phone': '+5511888888888',
                    'channel': 'whatsapp',
                    'type': 'text',
                    'content': 'Message 2'
                }
            ])
        """
        return self.client.post('/messages/bulk', {'messages': messages})
