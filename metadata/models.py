from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class TanitJobsCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "%s" % self.name


class KeeJobsCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "%s" % self.name
