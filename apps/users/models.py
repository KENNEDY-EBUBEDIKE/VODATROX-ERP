from django.db import models, IntegrityError
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
import os
from datetime import datetime
from pytz import timezone


class UserProfileManager(BaseUserManager):
    def create_user(self, email, username, password=None,
                    first_name=None,
                    surname=None,
                    phone_number=None,
                    appointment=None,
                    ):
        if not email:
            raise ValueError("Please Enter Email")

        if not username:
            raise ValueError("Please Enter Username")

        if not first_name:
            raise ValueError("Please Enter First Name")

        if not surname:
            raise ValueError("Please Enter Surname")

        if not appointment:
            raise ValueError("Please Enter Appointment")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.surname = surname
        user.first_name = first_name
        user.phone_number = phone_number
        user.appointment = appointment
        try:
            user.save(using=self._db)
        except IntegrityError:
            raise IntegrityError('Username or Email already Exists')
        return user

    def create_superuser(self, email, username, password,
                         first_name=None,
                         surname=None,
                         phone_number=None,
                         appointment=None,
                         ):
        user = self.create_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            surname=surname,
            phone_number=phone_number,
            appointment=appointment,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(null=False, unique=True, max_length=255)
    username = models.CharField(null=False, unique=True, max_length=255)
    first_name = models.CharField(null=True, max_length=255, blank=True)
    surname = models.CharField(null=True, blank=True, max_length=255)

    photo = models.ImageField(null=True, upload_to='image/', blank=True)
    appointment = models.CharField(null=True, blank=True, max_length=255)
    phone_number = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserProfileManager()

    def __str__(self):
        return self.username

    def update_profile_photo(self, photo):
        if self.photo:
            try:
                os.remove(self.photo.path)
            except FileNotFoundError:
                pass
        self.photo = photo

    def update_last_login(self):
        self.last_login = datetime.now(tz=timezone('Africa/Lagos'))
        self.save()
