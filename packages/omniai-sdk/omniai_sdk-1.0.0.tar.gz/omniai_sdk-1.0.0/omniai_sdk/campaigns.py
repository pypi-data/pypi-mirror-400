"""
Campaigns API resource
"""

from typing import Dict, Any, Optional, List


class Campaigns:
    """Manage marketing campaigns"""

    def __init__(self, client):
        self.client = client

    def create(
        self,
        name: str,
        channel: str,
        message_template: str,
        target_audience: Dict[str, Any],
        scheduled_at: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new campaign

        Args:
            name: Campaign name
            channel: Channel (whatsapp, email, sms)
            message_template: Message template
            target_audience: Audience criteria
            scheduled_at: Schedule datetime (ISO format, optional)

        Returns:
            Campaign object
        """
        data = {
            'name': name,
            'channel': channel,
            'messageTemplate': message_template,
            'targetAudience': target_audience
        }

        if scheduled_at:
            data['scheduledAt'] = scheduled_at

        return self.client.post('/campaigns', data)

    def get(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign by ID"""
        return self.client.get(f'/campaigns/{campaign_id}')

    def list(
        self,
        page: int = 1,
        limit: int = 50,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """List campaigns"""
        params = {'page': page, 'limit': limit}
        if status:
            params['status'] = status

        return self.client.get('/campaigns', params)

    def start(self, campaign_id: str) -> Dict[str, Any]:
        """Start campaign"""
        return self.client.post(f'/campaigns/{campaign_id}/start')

    def pause(self, campaign_id: str) -> Dict[str, Any]:
        """Pause campaign"""
        return self.client.post(f'/campaigns/{campaign_id}/pause')

    def delete(self, campaign_id: str) -> Dict[str, Any]:
        """Delete campaign"""
        return self.client.delete(f'/campaigns/{campaign_id}')
