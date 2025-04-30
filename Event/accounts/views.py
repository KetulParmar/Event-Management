from core.models import Event
from django.contrib.auth import logout
from .forms import Cap
from .models import *
from accounts.models import user_Data
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
import random
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect

# Home Page
from django.utils import timezone
from django.db.models import Q
def home(request):
    today = timezone.now().date()
    upcoming_events = Event.objects.filter(
        Q(start_date__gte=today) | Q(start_date__lte=today, end_date__gte=today)
    ).order_by('start_date')
    return render(request, 'index.html', {'Data': upcoming_events})



# Login View
@csrf_protect
def login_view(request):
    c1 = Cap(request.POST)
    if request.method == 'POST':
        login_type = request.POST.get('loginType')
        login_input = request.POST.get('loginInput')
        password = request.POST.get('password')

        user = None

        try:
            if login_type == 'email':
                user = user_Data.objects.get(Email=login_input)
            elif login_type == 'phone':
                user = user_Data.objects.get(Phone=login_input)
            elif login_type == 'username':
                user = user_Data.objects.get(username=login_input)

            # Authenticate user
            auth_user = authenticate(request, username=user.username, password=password)

            if auth_user:
                if c1.is_valid():
                    login(request, auth_user)
                else:
                    err = "Incorrect captcha!"
                    return render(request, 'Login.html', context={'err': err})
                request.session['user_id'] = user.id
                print("User ID stored in session:", request.session['user_id'])  # Debugging statement

                if user.User_type.lower() == 'organizer':
                    return redirect(reverse('accounts:Organizer'))
                elif user.User_type.lower() == 'attendee':
                    return redirect(reverse('accounts:Attendee'))
            else:
                return render(request, 'Login.html', {'err': 'Incorrect password!'})

        except user_Data.DoesNotExist:
            return render(request, 'Login.html', {'err': 'Account does not exist!'})

    return render(request, 'Login.html', {'c1': c1})


# Register View
@csrf_protect
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        full_name = request.POST['full_name']
        email = request.POST['email']
        password = request.POST['password']
        re_password = request.POST['re_password']
        phone = request.POST['phone']
        user_type = request.POST['user_type']
        company_name = request.POST['company_name']
        website = request.POST['website']

        if user_Data.objects.filter(username=username).exists():
            return render(request, 'Register.html', {'err': "Username already exists!"})

        if user_Data.objects.filter(Phone=phone).exists():
            return render(request, 'Register.html', {'err': "Phone number already registered!"})

        if password == re_password:
            if len(password) < 8:
                return render(request, 'Register.html', {'err1': "Password too short!"})
            elif len(password) > 20:
                return render(request, 'Register.html', {'err1': "Password too long!"})
            elif len(phone) != 10:
                return render(request, 'Register.html', {'err2': "Phone number must be 10 digits!"})

            user = user_Data(
                username=username,
                Name=full_name,
                Email=email,
                Phone=phone,
                User_type=user_type,
                Company_Name=company_name,
                Website=website
            )
            user.set_password(password)
            user.save()
            return redirect('accounts:Login')

        else:
            return render(request, 'Register.html', {'err3': "Passwords do not match!"})

    return render(request, 'Register.html')


# Organizer Dashboard View
def organizer(request):
    name= request.user.Name
    return render(request, 'accounts/Organizer.html', {'Name':name})

# Attendee Dashboard View
def attendee(request):
    today = timezone.now().date()
    upcoming_events = Event.objects.filter(
        Q(start_date__gte=today) | Q(start_date__lte=today, end_date__gte=today)
    ).order_by('start_date')
    name = request.user.Name
    return render(request, 'accounts/Attendee.html', {'Data': upcoming_events, 'Name': name})


def logout_view(request):
    logout(request)
    return redirect(reverse('accounts:home'))


@login_required
def details(request):
    print(request.user, "1")
    return render(request, 'core/details.html')



@csrf_protect
def forget(request):

    #OTP Sending
    if request.method == 'POST' and request.POST.get('action') == 'send_otp':
        email = request.POST.get('Email', '').strip()
        try:
            user = user_Data.objects.get(Email=email)
            otp = random.randint(1000, 9999)

            # Store in session
            request.session['reset_otp'] = str(otp)
            request.session['reset_user_id'] = user.id
            request.session['reset_email'] = email
            request.session['otp_sent'] = True  # flag to show OTP form


            send_mail(
                'Forgot Password',
                f'Your OTP is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            request.session['otp_sent_message'] = "OTP sent successfully"
            return render(request, 'Forget.html', {'otp_sent': True, 'email': email})

        except user_Data.DoesNotExist:
            return render(request, 'Forget.html', {'error': 'Email not registered!'})

    #OTP Verification
    elif request.method == 'POST' and request.POST.get('action') == 'verify_otp':
        input_otp = request.POST.get('otp')
        session_otp = request.session.get('reset_otp')
        email = request.session.get('reset_email')

        if input_otp == session_otp:
            request.session['otp_verified'] = True
            return render(request, 'Forget.html', {
                'otp_sent': True,
                'show_password_fields': True,
                'email': email
            })
        else:
            return render(request, 'Forget.html', {
                'otp_sent': True,
                'error': 'Invalid OTP!',
                'email': email
            })

    #Password Reset
    elif request.method == 'POST' and request.POST.get('action') == 'reset_password':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        email = request.session.get('reset_email')

        if new_password != confirm_password:
            return render(request, 'Forget.html', {
                'otp_sent': True,
                'show_password_fields': True,
                'error': 'Passwords do not match!',
                'email': email
            })

        try:
            user = user_Data.objects.get(Email=email)
            user.set_password(new_password)
            user.save()

            # Send confirmation email
            send_mail(
                'Password Reset Successful',
                f'Hi {user.Name},\n\nYour password has been successfully changed. It is {new_password}.'
                        f'Do not share with any one',

                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            request.session.flush()
            return redirect('accounts:Login')

        except user_Data.DoesNotExist:
            return render(request, 'Forget.html', {'error': 'User not found!'})

    # On GET or fallback
    context = {}
    if request.session.get('otp_sent'):
        context['otp_sent'] = True
        context['email'] = request.session.get('reset_email')
    if request.session.get('otp_verified'):
        context['show_password_fields'] = True
    if 'otp_sent_message' in request.session:
        context['otp_sent_message'] = request.session.pop('otp_sent_message')

    return render(request, 'Forget.html', context)