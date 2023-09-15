from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from .util import username_validator


class User(AbstractUser):
    first_name = models.CharField(
        max_length=150,
        verbose_name='Firstname'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Lastname'
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Username',
        unique=True,
        validators=[RegexValidator(regex=r'^[\w.@+-]+\Z'), username_validator]
    )
    email = models.EmailField(
        verbose_name='Email',
        unique=True,
        max_length=254
    )

    class Meta:
        ordering = ['date_joined']
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'], name='unique_username_email'
            )
        ]
