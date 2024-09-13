# custom_users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ministry_name = models.CharField(max_length=255, blank=True, null=True)

    # Add any other custom fields you need
    
    # Specify unique related_name attributes for groups and user_permissions
    groups = models.ManyToManyField(
        "auth.Group",
        blank=True,
        related_name="custom_users",  # Use a unique related_name
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        blank=True,
        related_name="custom_users_permissions",  # Use a unique related_name
        related_query_name="custom_user_permission",
    )


class MinistryArticle(models.Model):
    ministry_name = models.CharField(max_length=255)
    heading = models.CharField(max_length=255)
    date = models.DateField()
    source = models.URLField()
    sentiment = models.CharField(max_length=255)

    def __str__(self):
        return self.heading


