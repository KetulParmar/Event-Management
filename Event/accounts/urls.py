from django.urls import path
from . import views
urlpatterns = [
    path('', views.home),
    path('Login', views.login),
    path('Register',views.register),
    path('Organizer',views.organizer),
    path('Attendee',views.attendee),
    path('logout/', views.logout_view, name='logout'),
]