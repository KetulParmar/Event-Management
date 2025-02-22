from django.db import models
from accounts.models import user_Data
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

    organizer = models.ForeignKey(user_Data, on_delete=models.CASCADE, related_name="events", default=None)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Workshop')
    other_category = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(default=timezone.now)
    start_time = models.TimeField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    end_time = models.TimeField(default=timezone.now)
    venue = models.CharField(max_length=255)
    venue_address = models.TextField()
    contact_number = models.CharField(max_length=15)
    social_media = models.URLField(blank=True, null=True)
    max_attendees = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Uploading files to Cloudinary
    event_pdf = CloudinaryField('pdf', blank=True, null=True, folder="event_pdfs/")
    event_image = CloudinaryField('image', blank=True, null=True, folder="event_images/")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
