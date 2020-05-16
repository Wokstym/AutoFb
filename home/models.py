from django.contrib.auth.models import User
from djongo import models
from django.db import models as or_mod


class BannedWord(models.Model):
    word = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def __str__(self):
        return self.word


# class Post(models.Model):
#     message = models.TextField(max_length=512)
#     image = models.ImageField()
#     scheduled_date = models.CharField(max_length=20)
#
#     class Meta:
#         abstract = True
#
#     def str(self):
#         return self.message
#

class StatPost(models.Model):
    position = models.IntegerField()
    post_id = models.CharField(max_length=254)
    reactions_nr = models.IntegerField(blank=True)
    shares_nr = models.IntegerField(blank=True)
    comments_nr = models.IntegerField(blank=True)

    class Meta:
        abstract = True

    def str(self):
        return self.post_id


class StatPerson(models.Model):
    position = models.IntegerField()
    name = models.CharField(max_length=254)
    photo_url = models.CharField(max_length=254)
    comments_nr = models.IntegerField()

    class Meta:
        abstract = True

    def str(self):
        return self.position


class Statistics(models.Model):
    top_commenters_refresh_date = models.CharField(max_length=254)
    top_commenters = models.ArrayField(
        model_container=StatPerson
    )

    top_liked_posts_refresh_date = models.CharField(max_length=254)
    top_liked_posts = models.ArrayField(
        model_container=StatPost
    )

    top_commented_posts_refresh_date = models.CharField(max_length=254)
    top_commented_posts = models.ArrayField(
        model_container=StatPost
    )

    top_shared_posts_refresh_date = models.CharField(max_length=254)
    top_shared_posts = models.ArrayField(
        model_container=StatPost
    )

    class Meta:
        abstract = True

    def str(self):
        return self.top_commenters

    def __unicode__(self):
        return self.top_commenters


class Page(models.Model):
    page_id = models.CharField(max_length=254)
    token = models.CharField(max_length=254)

    words = models.ArrayField(model_container=BannedWord)
    # posts = models.ArrayField(model_container=Post)

    statistics = models.EmbeddedField(model_container=Statistics)

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
