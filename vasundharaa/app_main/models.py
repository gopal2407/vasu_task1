from django.db import models

from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("User must have email")

        user = self.model(
            email=self.normalize_email(email), **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        user = self.create_user(email=email, password=password, **kwargs)
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(verbose_name="your name", max_length=50, null=True, blank=True)
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    contact_no = models.CharField(verbose_name="contact number", max_length=15)
    organization = models.ForeignKey('Organisation', on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    is_org_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.email}'

    @property
    def hase_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_full_name(self):
        # The user is identified by their email address
        return self.name

    def get_short_name(self):
        # The user is identified by their email address
        return self.name

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_superuser

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.is_superuser


class Organisation(models.Model):
    name = models.CharField(max_length=155, unique=True, null=False, blank=False)
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    is_global = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'
