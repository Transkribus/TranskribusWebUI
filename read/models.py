

from django.db import models

# Create your models here.
#class Client(models.Model):
#   email = models.EmailField(unique=True, max_length=100)
#   password = models.CharField(max_length=128)

from django.contrib.auth.models import User

class TSData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=100)
    affiliation = models.CharField(max_length=100)

    #Add fields for any user data local to app here
    #thingthatappneedstostoreperuser = models.WhateverField();
