from django.db import models
from django.conf import settings  # Use settings.AUTH_USER_MODEL for user reference
from django.utils import timezone
from cloudinary.models import CloudinaryField

class Event(models.Model):
    CATEGORY_CHOICES = [
        ('workshop', 'Workshop'),
        ('conference', 'Conference'),
        ('business_conference', 'Business Conference'),
        ('seminar', 'Seminar & Workshop'),
        ('networking', 'Networking Event'),
        ('trade_show', 'Trade Show & Expo'),
        ('agm', 'Annual General Meeting (AGM)'),
        ('team_building', 'Team Building Activity'),
        ('product_launch', 'Product Launch'),
        ('other', 'Other'),
    ]

    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Workshop')
    other_category = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(default=timezone.now)
    start_time = models.TimeField(blank=True, null=True)
    end_date = models.DateField(default=timezone.now)
    end_time = models.TimeField(blank=True, null=True)
    venue = models.CharField(max_length=255)
    venue_address = models.TextField()
    contact_number = models.CharField(max_length=15)
    social_media = models.URLField(blank=True, null=True)
    max_attendees = models.PositiveIntegerField()
    seat_booked = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Uploading files to Cloudinary
    event_pdf = CloudinaryField('pdf', blank=True, null=True, folder="event_pdfs/")
    event_image = CloudinaryField('image', blank=True, null=True, folder="event_images/")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
        ('used', 'Used'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets")
    quantity = models.PositiveIntegerField(default=1)
    booking_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.quantity} tickets)"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)  # 🔹 Added field to store ticket quantity
    razorpay_order_id = models.CharField(max_length=255, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.title} - {self.status} ({self.quantity} tickets)"
