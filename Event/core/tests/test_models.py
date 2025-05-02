import pytest
from django.utils import timezone
from core.models import Event, Ticket
from django.contrib.auth import get_user_model


@pytest.fixture
def create_event():
    user = get_user_model().objects.create_user(
        username='test_user',  email='test_user@e456.com',password='password123'
    )
    event = Event.objects.create(
        organizer=user,
        title="Test Event",
        description="Test Event Description",
        category="workshop",
        start_date=timezone.now().date(),
        start_time=timezone.now(),
        end_time=timezone.now(),
        end_date=timezone.now().date(),
        venue="Test Venue",
        contact_number="1234567890",
        max_attendees=100,
        price=500.00,
    )
    return event

@pytest.mark.django_db
def test_event_creation(create_event):
    event = create_event
    assert event.title == "Test Event"
    assert event.venue == "Test Venue"
    assert event.max_attendees == 100
    assert event.price == 500.00

@pytest.mark.django_db
def test_ticket_creation(create_event):
    user = create_event.organizer
    ticket = Ticket.objects.create(
        user=user,
        event=create_event,
        quantity=2
    )
    assert ticket.quantity == 2
    assert ticket.event == create_event
    assert ticket.user == user
