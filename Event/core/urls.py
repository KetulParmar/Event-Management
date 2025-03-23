from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import create_order
app_name = 'core'

urlpatterns = [
    path('Home',views.home1, name='Home'),
    path('Create_user', views.create_event, name='Create_event'),
    path('delete/<int:id>/', views.delete, name="delete_event"),
    path('details/<int:id>/', views.details, name='details'),
    path('ticket1/<int:id>/', views.ticket1, name='ticket1'),
    path("create_order/<int:event_id>/", create_order, name="create_order"),
    path("payment_success_page/<int:ticket_id>/", views.payment_success_page, name='payment_success_page'),
    path("payment_success/", views.payment_success, name="payment_success"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)