from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from twilio.rest import Client
import csv
import mimetypes
from django.contrib  import messages
import requests


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('send_sms')
    return render(request, 'landing_page.html')




def signin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')  # Fetch the checkbox value

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Set session expiry based on "Remember Me"
            if remember_me:
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
            else:
                request.session.set_expiry(0)  # Expire on browser close

            return redirect('send_sms')
        else:
            return render(request, 'landing_page.html', {"error": "Invalid credentials", "form_type": "signin"})
    return render(request, 'landing_page.html', {"form_type": "signin"})



def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            
            return redirect('signin')
        else:
            return render(request, 'landing_page.html', {"error": "Username already exists", "form_type": "signup"})
    return render(request, 'landing_page.html', {"form_type": "signup"})


def logout_view(request):
    logout(request)
    request.session.clear()
    return redirect('signin')




def send_sms(request):
    if not request.user.is_authenticated:
        return redirect('landing_page')

    if request.method == 'POST':
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        except Exception:
            return JsonResponse({"status": "error", "message": "Failed to initialize Twilio client."}, status=500)

        phone_numbers = request.POST.get('phone_number', '')
        message_content = request.POST.get('message_content', '')
        link_input = request.POST.get('link_input', '')
        input_option = request.POST.get('inputOption', '')
        country_code = request.POST.get('country', 'US')

        uploaded_file = request.FILES.get('file_upload')
        file_data = ''
        if input_option == 'upload' and uploaded_file:
            file_type = mimetypes.guess_type(uploaded_file.name)[0]
            if 'csv' in file_type:
                try:
                    file_data = 'Uploaded File Content:\n'
                    file_data += '\n'.join([','.join(row) for row in csv.reader(uploaded_file.read().decode('utf-8').splitlines())])
                except Exception:
                    return JsonResponse({"status": "error", "message": "Failed to parse CSV file."}, status=400)
            else:
                return JsonResponse({"status": "error", "message": "Unsupported file type."}, status=400)

        if input_option == 'link' and link_input:
            message_content += f"\nLink: {link_input}"
        elif input_option == 'upload' and file_data:
            message_content += f"\n{file_data}"

        if not phone_numbers or not message_content:
            return JsonResponse({"status": "error", "message": "Phone numbers and message content are required."}, status=400)

        phone_numbers_list = [number.strip() for number in phone_numbers.split(',') if number.strip()]
        formatted_numbers = [f"+{country_code}{num}" if not num.startswith('+') else num for num in phone_numbers_list]

        total = len(formatted_numbers)
        sent = 0
        failed = 0
        failed_numbers = []
        for number in formatted_numbers:
            try:
                client.messages.create(
                    body=message_content,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=number
                )
                sent += 1
            except Exception:
                failed += 1
                failed_numbers.append(number)

        return JsonResponse({
            "status": "success",
            "total": total,
            "sent": sent,
            "failed": failed,
            "failed_numbers": failed_numbers
        }, status=200)

    return render(request, 'send_sms.html')


import requests


def send_emails(request):
    if not request.user.is_authenticated:
        return redirect('landing_page')

    if request.method == 'POST':
        recipient_email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message_content = request.POST.get('message_content', '')

        if not recipient_email or not subject or not message_content:
            return JsonResponse({"status": "error", "message": "Email, subject, and message are required."}, status=400)

        # Hardcoded Mailgun credentials and domain
        mailgun_api_key = 'your-mailgun-api-key'  # Replace with your Mailgun API key
        mailgun_domain = 'your-mailgun-domain.com'  # Replace with your Mailgun domain (e.g., mg.yourdomain.com)

        # Sending email using Mailgun API via requests
        try:
            # API endpoint for sending emails through Mailgun
            url = f"https://api.mailgun.net/v3/{mailgun_domain}/messages"
            
            # Mailgun API authentication
            auth = ('api', mailgun_api_key)
            
            # Data for the email
            data = {
                'from': f"Webtrix <postmaster@{mailgun_domain}>",  # Change to your sending email address
                'to': recipient_email,
                'subject': subject,
                'text': message_content,
            }
            
            # Send the request to Mailgun's API
            response = requests.post(url, auth=auth, data=data)

            # Check the response from Mailgun
            if response.status_code == 200:
                return JsonResponse({"status": "success", "message": "Email sent successfully."}, status=200)
            else:
                return JsonResponse({"status": "error", "message": "Failed to send email.", "details": response.text}, status=500)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return render(request, 'send_emails.html')
