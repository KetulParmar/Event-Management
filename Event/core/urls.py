from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'core'

urlpatterns = [
    path('Home',views.home1, name='Home'),
    path('Create_user', views.create_event, name='Create_event'),
    path('delete/<int:id>/', views.delete, name="delete_event"),
    path('details/<int:id>/', views.details, name='details'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)