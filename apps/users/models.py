from django.db import models, IntegrityError
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
import os


class UserProfileManager(BaseUserManager):
    def create_user(self, email, username, password=None,
                    first_name=None,
                    surname=None,
                    photo=None):
        if not email:
            raise ValueError("Please Enter Email")

        if not username:
            raise ValueError("Please Enter Username")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.surname = surname
        user.first_name = first_name
        user.photo = photo
        try:
            user.save(using=self._db)
        except IntegrityError:
            raise IntegrityError('Username or Email already Exists')
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email=email, username=username, password=password)
        user.is_super_user = True
        user.is_staff = True
        user.save(using=self._db)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(null=False, unique=True, max_length=255)
    username = models.CharField(null=False, unique=True, max_length=255)
    first_name = models.CharField(null=True, max_length=255, blank=True)
    surname = models.CharField(null=True, blank=True, max_length=255)

    photo = models.ImageField(null=True, upload_to='image/', blank=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    is_active = True
    objects = UserProfileManager()

    def __str__(self):
        return self.email

    def update_profile_photo(self, photo):
        if self.photo:
            os.remove(self.photo.path)
        self.photo = photo
