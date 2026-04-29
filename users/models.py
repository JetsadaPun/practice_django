from django.template import defaultfilters
from django.db import models

from django.contrib.auth.models import User

import uuid

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=10, verbose_name='Phone Number')
    full_name = models.CharField(max_length=150, verbose_name='Full Name')
    token = models.CharField(max_length=100, default = uuid.uuid4, unique = True)
    is_active_status = models.BooleanField(default = True)
    is_deleted_status = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f'{self.user.username} Profile' 
    