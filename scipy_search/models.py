from django.db import models
from django import settings
import urllib2

class Index(models.Model):
    name = models.CharField()
    url = models.CharField()

    def download(self):
        pass
        
