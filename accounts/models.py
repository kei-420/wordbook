from django.db import models
from django.contrib.auth.models import AbstractUser


class UserManager(AbstractUser):
    class Meta:
        db_table = 'usermanager'

    user_id = models.AutoField(
        primary_key=True,
        unique=True,
    )
    username = models.CharField(
        max_length=255,
        unique=True,
    )
    email = models.EmailField(
        unique=True,
        blank=True,
    )
    password = models.CharField(
        max_length=255,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.username


