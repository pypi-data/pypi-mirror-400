"""
Analytics API resource
"""

from typing import Dict, Any, Optional


class Analytics:
    """Access analytics and reports"""

    def __init__(self, client):
        self.client = client

    def get_overview(
        self,
        start_date: str,
        end_date: str,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get analytics overview

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            channel: Filter by channel (optional)

        Returns:
            Analytics data
        """
        params = {
            'startDate': start_date,
            'endDate': end_date
        }
        if channel:
            params['channel'] = channel

        return self.client.get('/analytics/overview', params)

    def get_messages_stats(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Get messages statistics"""
        params = {
            'startDate': start_date,
            'endDate': end_date
        }
        return self.client.get('/analytics/messages', params)

    def get_ai_stats(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Get AI usage statistics"""
        params = {
            'startDate': start_date,
            'endDate': end_date
        }
        return self.client.get('/analytics/ai', params)

    def export_report(
        self,
        report_type: str,
        start_date: str,
        end_date: str,
        format: str = 'pdf'
    ) -> Dict[str, Any]:
        """
        Export analytics report

        Args:
            report_type: Report type (overview, messages, ai, satisfaction)
            start_date: Start date
            end_date: End date
            format: Export format (pdf, excel, csv)

        Returns:
            Export URL
        """
        data = {
            'reportType': report_type,
            'startDate': start_date,
            'endDate': end_date,
            'format': format
        }
        return self.client.post('/analytics/export', data)
