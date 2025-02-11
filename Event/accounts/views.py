from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password, make_password
from django.views.decorators.csrf import csrf_protect
from .models import *
from django.urls import reverse
from core.models import Event

# Home Page
def home(request):

    return render(request, 'index.html')

# Login View
@csrf_protect
def login(request):
    if request.method == 'POST':
        login_type = request.POST.get('loginType')
        login_input = request.POST.get('loginInput')
        password = request.POST.get('password')
        user = None  # Store the user object
        try:
            if login_type == 'email':
                user = user_Data.objects.get(Email=login_input)
            elif login_type == 'phone':
                user = user_Data.objects.get(Phone=login_input)
            elif login_type == 'username':
                user = user_Data.objects.get(Username=login_input)
            Name = user.Name

            # Authenticate using check_password
            if user and check_password(password, user.Password):
                request.session['user_id'] = user.id  # Store user ID in session

                # Redirect based on user type
                if user.User_type.lower() == 'organizer':
                    url = reverse(organizer)  # Name of the URL pattern
                    return redirect(f"{url}?Name={user.Name}")
                elif user.User_type.lower() == 'attendee':
                    url = reverse(attendee)  # Name of the URL pattern
                    return redirect(f"{url}?Name={user.Name}")
            else:
                err = 'Incorrect password!'
                return render(request, 'Login.html', context={'err': err})
        except user_Data.DoesNotExist:
            err = "Account does not exist!"
            return render(request, 'Login.html', context={'err': err})

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

        # Check if username or phone number already exists
        if user_Data.objects.filter(username=username).exists():
            err = "Username already exists!"
            return render(request, 'Register.html', context={'err': err})

        if user_Data.objects.filter(Phone=phone).exists():
            err = "Phone number already registered!"
            return render(request, 'Register.html', context={'err': err})

        # Validate password and phone number length
        if password == re_password:
            if len(password) < 8:
                err = "Password too short!"
                return render(request, 'Register.html', context={'err1': err})
            elif len(password) > 20:
                err = "Password too long!"
                return render(request, 'Register.html', context={'err1': err})
            elif len(phone) != 10:
                err = "Phone number must be 10 digits!"
                return render(request, 'Register.html', context={'err2': err})
            else:
                hashed_password = make_password(password)
                user = user_Data(
                    username=username,
                    Name=full_name,
                    Email=email,
                    Password=hashed_password,
                    Phone=phone,
                    User_type=user_type,
                    Company_Name=company_name,
                    Website=website
                )
                user.save()
                return redirect(login)  # Redirect to login page
        else:
            err1 = "Passwords do not match!"
            return render(request, 'Register.html', context={'err3': err1})

    return render(request, 'Register.html')

# Organizer Dashboard View
def organizer(request):
    return render(request, 'accounts/Organizer.html')

# Attendee Dashboard View
def attendee(request):
    Data = Event.objects.all()
    return render(request, 'accounts/Attendee.html',{'Data':Data})

def logout_view(request):
    logout(request)
    return redirect(home)