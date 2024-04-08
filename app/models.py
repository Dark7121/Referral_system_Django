from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.core.validators import MinLengthValidator
import uuid
from threading import Thread
import time


class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The EMAIL field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        if password is None:
            raise ValueError('The PASSWORD field must be set')
        elif password.strip() == "":
            raise ValueError('Password cannot be empty')
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    token = models.CharField(max_length=60, blank=True)
    user_id = models.CharField(max_length=10, blank=True, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(blank=False, validators=[MinLengthValidator(8)], max_length=36)
    referral_id = models.CharField(max_length=10, blank=True, unique=True)  #input
    referral_code = models.CharField(max_length=10, blank=True, unique=True) #auto-generated
    points = models.IntegerField(default=0)
    timestamp = models.DateTimeField(blank=True, auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email']
    
    def generate_token(self):
        return str(uuid.uuid4())[:50]
        
    def generate_user_id(self):
        return str(uuid.uuid4())[:8]
    
    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.user_id:
                self.user_id = self.generate_user_id()
            if not self.referral_code:
                self.referral_code = self.generate_referral_code(kwargs.get('validated_data'))
        if not self.token: 
            self.token = self.generate_token()
            self.start_token_refresh_timer()
        super().save(*args, **kwargs)
    
    def generate_referral_code(self, validate_data):
        if self.referral_code:
            return self.referral_code
        return str(uuid.uuid4())[:10].upper()

    def start_token_refresh_timer(self):
        def refresh_token():
            while True:
                time.sleep(180)
                self.token = self.generate_token()
                self.save()

        token_refresh_thread = Thread(target=refresh_token)
        token_refresh_thread.daemon = True
        token_refresh_thread.start()

    def __str__(self):
        return self.email
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',  
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

