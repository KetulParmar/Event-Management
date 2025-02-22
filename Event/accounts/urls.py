from django.urls import path
from . import views
app_name = 'accounts'
urlpatterns = [
    path('', views.home, name='home'),
    path('Login', views.login_view),
    path('Register',views.register),
    path('Organizer',views.organizer, name='Organizer'),
    path('Attendee',views.attendee, name='Attendee'),
    path('logout/', views.logout_view, name='logout'),
    #path('otp', views.otp_verification, name='otp'),
]