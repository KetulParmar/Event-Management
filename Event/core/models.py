from django.db import models

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
    objects = None
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    other_category = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    venue = models.CharField(max_length=255)
    venue_address = models.TextField()
    contact_number = models.CharField(max_length=15)
    social_media = models.URLField(blank=True, null=True)
    max_attendees = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    event_pdf = models.FileField(upload_to='event_pdfs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
