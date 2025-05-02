from django.test import Client
from unittest.mock import patch
import pytest
from core.models import Payment, Event
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone


@pytest.fixture
def create_event():
    user = get_user_model().objects.create_user(
        username='test_user',  email='test_user@e456.com',password='password123'
    )
    event = Event.objects.create(
        organizer=user,
        title="Test Event",
        description="Test Event Description",
        category="Seminar",
        start_date="2025-05-10",
        start_time=timezone.now(),
        end_date="2025-05-10",
        end_time=timezone.now(),
        venue="MBIT College",
        contact_number="9856232356",
        max_attendees=100,
        price=500.00,
    )
    return event


@pytest.fixture
def authenticated_client(create_event):
    client = Client()
    client.login(username='test_user', password='password123')
    return client


@pytest.mark.django_db
def test_home_page(client):
    user = get_user_model().objects.create_user(
        username='test_user', email='test_user@e456.com', password='password123'
    )
    event = Event.objects.create(
        organizer=user,
        title="Test Event",
        description="Test Event Description",
        category="Seminar",
        start_date="2025-05-10",
        start_time=timezone.now(),
        end_date="2025-05-10",
        end_time=timezone.now(),
        venue="MBIT College",
        contact_number="9856232356",
        max_attendees=100,
        price=500.00,
    )
    response = client.get('/')
    assert response.status_code == 200
    assert 'Test Event' in response.content.decode()


@pytest.mark.django_db
def test_create_event_view(authenticated_client):
    url = reverse('core:create_event')
    data = {
        'organizer': 'test_user',
        'title': 'New Event',
        'description': 'New Event Description',
        'category': 'workshop',
        'start_date': '2025-05-15',
        'start_time' : timezone.now(),
        'end_date': '2025-05-16',
        'end_time': timezone.now(),
        'venue': 'New Venue',
        'contact_number': '1234567890',
        'max_attendees': 50,
        'price': 1000.00,
    }
    response = authenticated_client.post(url, data)
    assert response.status_code == 302  # Redirect to home page
    assert Event.objects.filter(title="New Event").exists()

@pytest.mark.django_db
@patch('razorpay.Client')
def test_create_order(mock_razorpay_client, authenticated_client, create_event):
    mock_razorpay_client.return_value.order.create.return_value = {"id": "order_id123"}

    url = reverse('core:create_order', args=[create_event.id])
    data = {"quantity": 2}
    response = authenticated_client.post(url, data, content_type='application/json')

    assert response.status_code == 200
    assert response.json().get("order_id") == "order_id123"