from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet)
app_name = 'core'

urlpatterns = [
    path('Home',views.home1, name='Home'),
    path('Create_user', views.create_event, name='create_event'),
    path('delete/<int:id>/', views.delete, name="delete_event"),
    path('details/<int:id>/', views.details, name='details'),
    path('ticket1/<int:id>/', views.ticket1, name='ticket1'),
    path("create_order/<int:event_id>/", views.create_order, name="create_order"),
    path("payment_success_page/<int:ticket_id>/", views.payment_success_page, name='payment_success_page'),
    path("payment_success/", views.payment_success, name="payment_success"),
    path('organizer_dashboard', views.organizer_dashboard, name='organizer_dashboard'),
    path("my_ticket/", views.my_ticket, name="my_ticket"),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)