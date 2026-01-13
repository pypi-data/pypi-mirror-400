# revhold-python

Official Python SDK for [RevHold](https://www.revhold.io) - AI business assistant for SaaS analytics.

## Installation

```bash
pip install revhold-python
# or
poetry add revhold-python
```

## Quick Start

```python
from revhold import RevHold

revhold = RevHold(api_key='your_api_key_here')

# Track a usage event
revhold.track_event(
    user_id='user_123',
    event_name='document_created',
    event_value=1,
)

# Ask AI a question
insight = revhold.ask_ai(
    question='Which users are most engaged this week?'
)
print(insight['answer'])
```

## API Reference

### Constructor

```python
revhold = RevHold(
    api_key='your_api_key',     # Required: Your RevHold API key
    base_url='...',             # Optional: Override API base URL
    timeout=30,                 # Optional: Request timeout in seconds
)
```

### track_event()

Track a single usage event.

```python
revhold.track_event(
    user_id='user_123',              # Required
    event_name='feature_used',       # Required
    event_value=1,                   # Optional, defaults to 1
    timestamp='2025-01-07T...'       # Optional, defaults to now
)
```

**Returns:** `dict`

```python
{
    'success': True,
    'message': 'Usage event recorded',
    'eventId': 'evt_xyz789'
}
```

### track_batch()

Track multiple events efficiently.

```python
revhold.track_batch([
    {'user_id': 'user_1', 'event_name': 'feature_used'},
    {'user_id': 'user_2', 'event_name': 'document_created'},
    {'user_id': 'user_3', 'event_name': 'export_completed'},
])
```

**Returns:** `dict`

```python
{
    'success': True,
    'message': 'Batch events tracked successfully',
    'count': 3,
    'errors': None  # or list of errors if some failed
}
```

### ask_ai()

Ask the AI a question about your usage data.

```python
result = revhold.ask_ai(
    question='Which users are most engaged this week?'
)

print(result['answer'])       # AI-generated insight
print(result['confidence'])   # 'high' | 'medium' | 'low'
print(result['dataPoints'])   # Number of events analyzed
```

**Returns:** `dict`

```python
{
    'answer': 'Based on your usage data...',
    'confidence': 'high',
    'dataPoints': 127
}
```

### get_usage()

Retrieve recent usage events.

```python
usage = revhold.get_usage(
    limit=10,               # Optional: max 1000
    user_id='user_123'      # Optional: filter by user
)

print(usage['events'])
print(usage['total'])
```

**Returns:** `dict`

```python
{
    'events': [
        {
            'eventId': 'evt_xyz789',
            'userId': 'user_abc123',
            'eventName': 'feature_used',
            'eventValue': 1,
            'timestamp': '2025-01-07T14:30:00Z'
        }
    ],
    'total': 1,
    'limit': 10
}
```

## Error Handling

The SDK raises `RevHoldError` for all API errors:

```python
from revhold import RevHold, RevHoldError

revhold = RevHold(api_key='your_key')

try:
    revhold.track_event(
        user_id='user_123',
        event_name='feature_used'
    )
except RevHoldError as e:
    print(f'Status: {e.status_code}')
    print(f'Code: {e.error_code}')
    print(f'Message: {e.message}')
    
    if e.status_code == 429:
        print('Rate limit - retry after 60s')
    elif e.status_code == 402:
        print('Plan limit reached - upgrade')
```

### Error Properties

- `status_code: int` - HTTP status code (401, 402, 429, 500, etc.)
- `error_code: str` - Machine-readable error code
- `message: str` - Human-readable error message
- `details: dict` - Additional error context

### Error Helper Methods

```python
if e.is_rate_limit_error:
    # Handle rate limiting (429)
    pass

if e.is_payment_required_error:
    # Handle plan limits (402)
    pass

if e.is_authentication_error:
    # Handle invalid API key (401)
    pass

if e.is_network_error:
    # Handle network issues
    pass
```

## Context Manager

Use the SDK as a context manager for automatic cleanup:

```python
with RevHold(api_key='your_key') as revhold:
    revhold.track_event(
        user_id='user_123',
        event_name='feature_used'
    )
# Session automatically closed
```

## Type Hints

The SDK includes full type hints for better IDE support:

```python
from typing import Dict, Any
from revhold import RevHold

revhold = RevHold(api_key='your_key')

# Type hints work automatically
result: Dict[str, Any] = revhold.track_event(
    user_id='user_123',
    event_name='feature_used'
)
```

## Examples

### Track user activity

```python
# When a user creates a document
revhold.track_event(
    user_id=request.user.id,
    event_name='document_created',
    event_value=1
)

# When a user exports data
revhold.track_event(
    user_id=request.user.id,
    event_name='data_exported',
    event_value=1
)
```

### Batch tracking

```python
# Track multiple events efficiently
events = [
    {
        'user_id': user.id,
        'event_name': 'daily_active',
        'event_value': 1
    }
    for user in active_users
]

revhold.track_batch(events)
```

### AI insights

```python
# Get churn insights
churn_analysis = revhold.ask_ai(
    question='Which users are at risk of churning?'
)

# Identify upsell opportunities
upsell_opportunities = revhold.ask_ai(
    question='Which trial users are most likely to upgrade?'
)

# Analyze feature adoption
feature_adoption = revhold.ask_ai(
    question='What features do power users use most?'
)
```

### Environment Variables

```python
import os
from revhold import RevHold

# Load API key from environment
revhold = RevHold(api_key=os.environ['REVHOLD_API_KEY'])
```

## Rate Limits

- **Usage events:** 1,000 requests/minute
- **AI questions:** 10 requests/minute
- **Get usage:** 100 requests/minute

Rate limit info is included in error responses:

```python
try:
    revhold.ask_ai(question='...')
except RevHoldError as e:
    if e.status_code == 429:
        retry_after = e.details.get('retryAfter', 60)
        print(f'Retry after {retry_after} seconds')
```

## Requirements

- Python 3.8 or higher
- `requests` library (automatically installed)

## Development

```bash
# Clone the repository
git clone https://github.com/revhold/python-sdk.git
cd python-sdk

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black revhold/

# Type checking
mypy revhold/
```

## Support

- 📖 [Documentation](https://www.revhold.io/docs)
- 📚 [API Reference](https://www.revhold.io/api-reference)
- 💬 [Contact Support](https://www.revhold.io/contact)

## License

MIT

