from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from twilio.rest import Client
import csv
import mimetypes
from django.contrib  import messages


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('send_sms')
    return render(request, 'landing_page.html')


def signin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, " you  are in ok.")
            
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
            return redirect('send_sms')
        else:
            return render(request, 'landing_page.html', {"error": "Username already exists", "form_type": "signup"})
    return render(request, 'landing_page.html', {"form_type": "signup"})


def logout_view(request):
    logout(request)
    request.session.clear()
    return redirect('landing_page')


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
