from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.template.defaulttags import csrf_token
from django.views.decorators.csrf import csrf_protect
from .models import *

# Create your views here.
def home(request):
    return render(request, 'index.html')

def login(request):
    if request.method == 'POST':
        pass

    return render(request, 'Login.html')

@csrf_protect
def register(request):
    if request.method == 'POST':
        Username = request.POST['username']
        Name = request.POST['full_name']
        Email = request.POST['email']
        Password = request.POST['password']
        Re_Password = request.POST['re_password']
        Phone = request.POST['phone']
        User_Type = request.POST['user_type']
        Company_Name = request.POST['company_name']
        Website = request.POST['website']
        Hash = make_password(Password)
        if user_Data.objects.filter(Username=Username).exists():
            err = "username already exists!!"
            return render(request, 'Register.html', context={'err' : err})
        if Password == Re_Password:
            if len(Password) < 8:
                err = "Too short!!"
                return render(request, 'Register.html', context={'err1': err})
            elif len(Password) > 20:
                err = "Too Long!!"
                return render(request, 'Register.html', context={'err1': err})
            elif len(Phone)!= 10:
                err = "Must of length 10!!"
                return render(request, 'Register.html', context={'err2': err})
            else:
                data = user_Data(Username=Username,Name=Name, Email=Email, Password=Hash, Phone=Phone, User_type=User_Type, Company_Name=Company_Name, Website=Website)
                data.save()
                data2 = User(username=Email, password=Hash)
                data2.save()
                return redirect(login)
        else:
            err1 = "Password does not match!!"
            return render(request, 'Register.html', context={'err3': err1})

    return  render(request,'Register.html')