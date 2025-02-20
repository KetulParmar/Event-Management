from django.db import models



class user_Data(models.Model):
    USER_TYPE_CHOICES = [
        ('attendee', 'accounts'),
        ('organizer', 'Organizer'),
    ]
    objects = None
    username = models.CharField(max_length=50,default=None, unique=True)
    Name = models.CharField(max_length=50)
    Email = models.EmailField(unique=True)
    Password = models.CharField(max_length=500)
    Phone = models.CharField(max_length=10)
    User_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='attendee')
    #additonal for Organizer
    Company_Name = models.CharField(max_length=20, blank=True, null=True)
    Website = models.CharField(max_length=255, blank=True, null=True)

@property
def is_authenticated(self):
    return True