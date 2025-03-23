from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(username=username, Email=email, **extra_fields)
        user.set_password(password)  # Hash password automatically
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


class user_Data(AbstractBaseUser, PermissionsMixin):  # Add PermissionsMixin for superuser functionality
    USER_TYPE_CHOICES = [
        ('attendee', 'Attendee'),
        ('organizer', 'Organizer'),
    ]

    username = models.CharField(max_length=50, unique=True)
    Name = models.CharField(max_length=50)
    Email = models.EmailField(unique=True)
    Phone = models.CharField(max_length=10)
    User_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='attendee')

    # Additional fields for Organizer
    Company_Name = models.CharField(max_length=20, blank=True, null=True)
    Website = models.CharField(max_length=255, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['Email']

    def __str__(self):
        return self.username
