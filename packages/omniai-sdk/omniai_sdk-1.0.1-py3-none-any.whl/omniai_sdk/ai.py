"""
AI API resource
"""

from typing import Dict, Any, Optional, List


class AI:
    """AI-powered features"""

    def __init__(self, client):
        self.client = client

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = 'gpt-4',
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get AI chat completion

        Args:
            messages: Conversation messages
            model: AI model to use
            temperature: Creativity (0-1)
            max_tokens: Maximum tokens (optional)

        Returns:
            AI response

        Example:
            response = client.ai.chat_completion([
                {'role': 'user', 'content': 'Olá, preciso de ajuda'}
            ])
        """
        data = {
            'messages': messages,
            'model': model,
            'temperature': temperature
        }

        if max_tokens:
            data['maxTokens'] = max_tokens

        return self.client.post('/ai/chat', data)

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze text sentiment

        Args:
            text: Text to analyze

        Returns:
            Sentiment analysis (positive, negative, neutral)
        """
        return self.client.post('/ai/sentiment', {'text': text})

    def extract_intent(self, text: str) -> Dict[str, Any]:
        """
        Extract user intent from text

        Args:
            text: User message

        Returns:
            Detected intent and entities
        """
        return self.client.post('/ai/intent', {'text': text})

    def generate_response(
        self,
        context: str,
        user_message: str,
        tone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response suggestion

        Args:
            context: Conversation context
            user_message: User's message
            tone: Response tone (professional, friendly, casual)

        Returns:
            Suggested response
        """
        data = {
            'context': context,
            'userMessage': user_message
        }
        if tone:
            data['tone'] = tone

        return self.client.post('/ai/generate-response', data)
