from core.models import Event
from django.contrib.auth import authenticate, login, logout
from .models import *
from accounts.models import user_Data
from django.contrib.auth.decorators import login_required

# Home Page
from django.utils import timezone
from django.db.models import Q
def home(request):
    today = timezone.now().date()
    # Fetch events that are either:
    # - currently happening (start_date <= today <= end_date)
    # - or will happen in the future (start_date > today)
    upcoming_events = Event.objects.filter(
        Q(start_date__gte=today) | Q(start_date__lte=today, end_date__gte=today)
    ).order_by('start_date')
    print(upcoming_events)
    return render(request, 'index.html', {'Data': upcoming_events})



# Login View
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect


@csrf_protect
def login_view(request):
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
                login(request, auth_user)  # Log in user using Django's session system

                # **Manually store the user_id in the session**
                request.session['user_id'] = user.id
                print("User ID stored in session:", request.session['user_id'])  # Debugging statement

                # Redirect based on user type
                if user.User_type.lower() == 'organizer':
                    return redirect(reverse('accounts:Organizer'))
                elif user.User_type.lower() == 'attendee':
                    return redirect(reverse('accounts:Attendee'))
            else:
                return render(request, 'Login.html', {'err': 'Incorrect password!'})

        except user_Data.DoesNotExist:
            return render(request, 'Login.html', {'err': 'Account does not exist!'})

    return render(request, 'Login.html')


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
            user.set_password(password)  # Hash password before saving
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
    # Get ongoing or upcoming events
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