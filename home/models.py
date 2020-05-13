from django.contrib.auth.models import User
from djongo import models


class BannedWord(models.Model):
    word = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def __str__(self):
        return self.word


# class Post(models.Model):
#     message = models.TextField(max_length=1000)
#     image = models.ImageField()
#     scheduled_date = models.DateTimeField()
#
#     class Meta:
#         abstract = True
#
#     def str(self):
#         return self.message
#

class Page(models.Model):
    page_id = models.CharField(max_length=254)
    token = models.CharField(max_length=254)

    words = models.ArrayField(model_container=BannedWord)
    # posts = models.ArrayField(model_container=Post)

    class Meta:
        abstract = True

    def str(self):
        return self.page_id


class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    pages = models.ArrayField(
        model_container=Page
    )

    objects = models.DjongoManager()
