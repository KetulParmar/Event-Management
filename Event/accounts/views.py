from django.views.decorators.csrf import csrf_protect
from core.models import Event
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import render, redirect,  get_object_or_404
from django.urls import reverse
from .models import *
from accounts.models import user_Data
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required

# Home Page
def home(request):
    D = Event.objects.all()
    return render(request, 'index.html', {'Data':D})


# Login View
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

            # Authenticate using Django's system
            auth_user = authenticate(request, username=user.username, password=password)

            if auth_user:
                login(request, auth_user)  # Log in the user using Django's session system

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
            return redirect('accounts:login')

        else:
            return render(request, 'Register.html', {'err3': "Passwords do not match!"})

    return render(request, 'Register.html')


# Organizer Dashboard View
def organizer(request):
    print(request.user)
    return render(request, 'accounts/Organizer.html')

# Attendee Dashboard View
def attendee(request):
    Data = Event.objects.all()
    print(request.user)
    return render(request, 'accounts/Attendee.html',{'Data':Data})

def logout_view(request):
    logout(request)
    return redirect(reverse('accounts:home'))

@login_required
def details(request):
    return render(request, 'core/details.html')