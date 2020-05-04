from django.contrib.auth.models import User
from djongo import models


class BannedWord(models.Model):
    word = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def __str__(self):
        return self.word

    def get_word(self):
        return self.word


class Page(models.Model):
    page_id = models.CharField(max_length=254)
    token = models.CharField(max_length=254)

    words = models.ArrayField(model_container=BannedWord)

    class Meta:
        abstract = True

    def str(self):
        return self.page_id

    def get_token(self):
        return self.token

    def get_page_id(self):
        return self.page_id

    def get_words(self):
        return self.words


class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    pages = models.ArrayField(
        model_container=Page
    )

    objects = models.DjongoManager()
