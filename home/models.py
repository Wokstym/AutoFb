from django.contrib.auth.models import User
from django.db import models


class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    token = models.CharField(max_length=200)
