"""
Basic usage examples for revhold-python SDK
"""

import os
from revhold import RevHold, RevHoldError


def basic_examples():
    """Demonstrate basic SDK usage."""
    
    # Initialize the client
    revhold = RevHold(
        api_key=os.environ.get('REVHOLD_API_KEY', 'your_api_key_here')
    )

    try:
        # Example 1: Track a single event
        print('Tracking a single event...')
        event_response = revhold.track_event(
            user_id='user_123',
            event_name='document_created',
            event_value=1
        )
        print(f"Event tracked: {event_response}")

        # Example 2: Track multiple events in batch
        print('\nTracking batch events...')
        batch_response = revhold.track_batch([
            {'user_id': 'user_1', 'event_name': 'feature_used'},
            {'user_id': 'user_2', 'event_name': 'document_created'},
            {'user_id': 'user_3', 'event_name': 'export_completed'},
        ])
        print(f"Batch tracked: {batch_response}")

        # Example 3: Ask AI a question
        print('\nAsking AI a question...')
        ai_response = revhold.ask_ai(
            question='Which users are most engaged this week?'
        )
        print(f"AI Answer: {ai_response['answer']}")
        print(f"Confidence: {ai_response['confidence']}")
        print(f"Data Points: {ai_response['dataPoints']}")

        # Example 4: Get recent usage events
        print('\nGetting recent usage...')
        usage = revhold.get_usage(limit=5)
        print(f"Found {usage['total']} events")
        for event in usage['events']:
            print(f"  - {event['eventName']} by {event['userId']}")

    except RevHoldError as e:
        print('RevHold Error:')
        print(f"  Status: {e.status_code}")
        print(f"  Code: {e.error_code}")
        print(f"  Message: {e.message}")

        # Handle specific errors
        if e.is_rate_limit_error:
            print('Rate limit hit - wait before retrying')
        elif e.is_payment_required_error:
            print('Plan limit reached - upgrade your account')
        elif e.is_authentication_error:
            print('Invalid API key')

    except Exception as e:
        print(f'Unexpected error: {e}')

    finally:
        # Clean up
        revhold.close()


def context_manager_example():
    """Demonstrate context manager usage."""
    
    with RevHold(api_key=os.environ.get('REVHOLD_API_KEY', 'your_key')) as revhold:
        try:
            result = revhold.track_event(
                user_id='user_123',
                event_name='feature_used'
            )
            print(f"Event tracked: {result}")
        except RevHoldError as e:
            print(f"Error: {e}")
    # Session automatically closed


if __name__ == '__main__':
    print('=== Basic Examples ===')
    basic_examples()
    
    print('\n=== Context Manager Example ===')
    context_manager_example()

