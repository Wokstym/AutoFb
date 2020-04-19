from django.contrib.auth.models import User
from djongo import models


class Page(models.Model):
    page_id = models.IntegerField()
    name = models.CharField(max_length=200)

    class Meta:
        abstract = True


# Need to figure out to store nested
class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    # to działało, potem sie samo zjebało, 2 godizny szukałem czemu to spierdolone gówno nie działa i nw
    # pages = models.EmbeddedField(
    #     model_container=Page,
    #     null=True
    # )
    token = models.CharField(max_length=200)
    objects = models.DjongoManager()
