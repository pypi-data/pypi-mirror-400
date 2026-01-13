# OmniAI Python SDK

Official Python SDK for the OmniAI API - Multi-channel messaging platform with AI automation.

## Installation

```bash
pip install omniai-sdk
```

## Quick Start

```python
from omniai import Client

# Initialize client
client = Client('YOUR_API_KEY')

# Send a message
message = client.messages.send(
    phone='+5511999999999',
    channel='whatsapp',
    type='text',
    content='Olá! Como posso ajudar?'
)

print(f'Message sent: {message["id"]}')
```

## Features

- **Multi-channel messaging** - WhatsApp, Email, SMS, Telegram
- **Contact management** - Create, update, search contacts
- **Campaign automation** - Schedule and manage marketing campaigns
- **AI-powered features** - Chat completions, sentiment analysis, intent detection
- **Analytics & Reports** - Get insights and export reports
- **Type hints** - Full type annotation support
- **Error handling** - Comprehensive exception classes

## Usage Examples

### Send Messages

```python
# Text message
message = client.messages.send(
    phone='+5511999999999',
    channel='whatsapp',
    type='text',
    content='Hello from OmniAI!'
)

# Media message
message = client.messages.send(
    phone='+5511999999999',
    channel='whatsapp',
    type='image',
    content='Check this image',
    media_url='https://example.com/image.jpg'
)

# Bulk send
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
```

### Manage Contacts

```python
# Create contact
contact = client.contacts.create(
    name='João Silva',
    phone='+5511999999999',
    email='joao@example.com',
    tags=['customer', 'vip']
)

# List contacts
contacts = client.contacts.list(
    page=1,
    limit=50,
    search='João'
)

# Update contact
updated = client.contacts.update(
    contact_id='contact-123',
    tags=['customer', 'vip', 'premium']
)
```

### Create Campaigns

```python
campaign = client.campaigns.create(
    name='Black Friday 2024',
    channel='whatsapp',
    message_template='Aproveite 50% OFF em todos os produtos!',
    target_audience={
        'tags': ['customer'],
        'segment': 'active'
    },
    scheduled_at='2024-11-29T09:00:00Z'
)

# Start campaign
client.campaigns.start(campaign['id'])
```

### AI Features

```python
# Chat completion
response = client.ai.chat_completion([
    {'role': 'user', 'content': 'Preciso de ajuda com meu pedido'}
])

# Sentiment analysis
sentiment = client.ai.analyze_sentiment(
    'Estou muito satisfeito com o atendimento!'
)
print(sentiment['sentiment'])  # 'positive'

# Intent detection
intent = client.ai.extract_intent(
    'Quero cancelar minha assinatura'
)
print(intent['intent'])  # 'cancel_subscription'

# Generate response
suggestion = client.ai.generate_response(
    context='Cliente perguntou sobre prazo de entrega',
    user_message='Quando chega meu pedido?',
    tone='professional'
)
```

### Analytics

```python
# Get overview
analytics = client.analytics.get_overview(
    start_date='2024-01-01',
    end_date='2024-01-31',
    channel='whatsapp'
)

# Export report
export = client.analytics.export_report(
    report_type='messages',
    start_date='2024-01-01',
    end_date='2024-01-31',
    format='pdf'
)
print(export['downloadUrl'])
```

## Error Handling

```python
from omniai import Client, AuthenticationError, ValidationError, RateLimitError

client = Client('YOUR_API_KEY')

try:
    message = client.messages.send(
        phone='+5511999999999',
        channel='whatsapp',
        type='text',
        content='Hello!'
    )
except AuthenticationError:
    print('Invalid API key')
except ValidationError as e:
    print(f'Validation error: {e}')
except RateLimitError:
    print('Rate limit exceeded, please wait')
```

## Configuration

```python
# Custom base URL
client = Client(
    api_key='YOUR_API_KEY',
    base_url='https://api.omniaiassist.com/v1'
)
```

## API Reference

### Messages
- `messages.send(phone, channel, type, content, **kwargs)` - Send message
- `messages.get(message_id)` - Get message by ID
- `messages.list(**kwargs)` - List messages
- `messages.send_bulk(messages)` - Send multiple messages

### Contacts
- `contacts.create(name, phone, **kwargs)` - Create contact
- `contacts.get(contact_id)` - Get contact by ID
- `contacts.list(**kwargs)` - List contacts
- `contacts.update(contact_id, **kwargs)` - Update contact
- `contacts.delete(contact_id)` - Delete contact

### Campaigns
- `campaigns.create(name, channel, message_template, target_audience, **kwargs)` - Create campaign
- `campaigns.get(campaign_id)` - Get campaign
- `campaigns.list(**kwargs)` - List campaigns
- `campaigns.start(campaign_id)` - Start campaign
- `campaigns.pause(campaign_id)` - Pause campaign
- `campaigns.delete(campaign_id)` - Delete campaign

### AI
- `ai.chat_completion(messages, **kwargs)` - Chat completion
- `ai.analyze_sentiment(text)` - Sentiment analysis
- `ai.extract_intent(text)` - Intent detection
- `ai.generate_response(context, user_message, **kwargs)` - Generate response

### Analytics
- `analytics.get_overview(start_date, end_date, **kwargs)` - Get overview
- `analytics.get_messages_stats(start_date, end_date)` - Messages stats
- `analytics.get_ai_stats(start_date, end_date)` - AI stats
- `analytics.export_report(report_type, start_date, end_date, format)` - Export report

## Requirements

- Python 3.7+
- requests >= 2.25.0

## License

MIT License - see LICENSE file for details

## Support

- Documentation: https://docs.omniaiassist.com
- GitHub Issues: https://github.com/omniaiassist/omniai-python-sdk/issues
- Email: support@omniaiassist.com
