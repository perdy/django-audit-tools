import datetime

from django.db import models


class Test(models.Model):
    name = models.CharField(max_length=128)
    time = models.DateTimeField(default=datetime.datetime.now())
    force_time = models.TimeField()