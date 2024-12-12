from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from twilio.rest import Client
import os
import csv
import mimetypes

# Function to test Twilio connection
def test_twilio_connection():
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        # Attempt to fetch account details to verify connection
        client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
        print("Twilio connection successful.")
    except Exception as e:
        print("Twilio connection error:", str(e))



def send_sms(request):
    if request.method == 'POST':
        # Initialize Twilio client
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        except Exception as e:
            return JsonResponse({"status": "error", "message": "Failed to initialize Twilio client."}, status=500)

        # Extract data from the POST request
        phone_numbers = request.POST.get('phone_number', '')
        message_content = request.POST.get('message_content', '')
        link_input = request.POST.get('link_input', '')
        input_option = request.POST.get('inputOption', '')
        country_code = request.POST.get('country', 'US')

        # Handle file upload if chosen
        uploaded_file = request.FILES.get('file_upload')
        file_data = ''
        if input_option == 'upload' and uploaded_file:
            file_type = mimetypes.guess_type(uploaded_file.name)[0]
            if 'csv' in file_type:  # Parse CSV
                try:
                    file_data = 'Uploaded File Content:\n'
                    file_data += '\n'.join([','.join(row) for row in csv.reader(uploaded_file.read().decode('utf-8').splitlines())])
                except Exception as e:
                    return JsonResponse({"status": "error", "message": "Failed to parse CSV file."}, status=400)
            elif 'pdf' in file_type:
                return JsonResponse({"status": "error", "message": "PDF processing is not yet implemented."}, status=400)
            else:
                return JsonResponse({"status": "error", "message": "Unsupported file type."}, status=400)

        # Combine message with link or file data
        if input_option == 'link' and link_input:
            message_content += f"\nLink: {link_input}"
        elif input_option == 'upload' and file_data:
            message_content += f"\n{file_data}"

        # Validate input
        if not phone_numbers or not message_content:
            return JsonResponse({"status": "error", "message": "Phone numbers and message content are required."}, status=400)

        # Format phone numbers with country code
        phone_numbers_list = [number.strip() for number in phone_numbers.split(',') if number.strip()]
        formatted_numbers = []
        for num in phone_numbers_list:
            if num.startswith('+'):
                formatted_numbers.append(num)
            else:
                formatted_numbers.append(f"+{country_code}{num}")

        # Send SMS
        total = len(formatted_numbers)
        sent = 0
        failed = 0
        failed_numbers = []
        for number in formatted_numbers:
            try:
                sms = client.messages.create(
                    body=message_content,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=number
                )
                sent += 1
            except Exception as e:
                failed += 1
                failed_numbers.append(number)

        # Return results
        return JsonResponse({
            "status": "success",
            "total": total,
            "sent": sent,
            "failed": failed,
            "failed_numbers": failed_numbers
        }, status=200)

    return render(request, 'send_sms.html')
