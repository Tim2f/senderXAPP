from celery import shared_task
import requests
from django.conf import settings

@shared_task
def send_sms_task(phone_number, message_content):
    url = 'https://api.talktone.com/send_sms'  # Replace with your actual API endpoint
    headers = {
        'Authorization': f'Bearer {settings.TOP8TONE_API_KEY}',
    }
    data = {
        'to': phone_number,
        'message': message_content,
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        return {'status': response.status_code, 'message': 'SMS sent successfully'}
    except requests.exceptions.RequestException as e:
        # Log error to console or logging system
        print(f"Failed to send SMS to {phone_number}. Error: {e}")
        return {'status': 'failed', 'error': str(e)}
