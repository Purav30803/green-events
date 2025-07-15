from ast import Pass
from mailbox import Mailbox
from tokenize import Name
from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import User
from Iads import settings



class SignupFields(models.Model):
    name = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=100, null=True)
    number = models.CharField(max_length=10, null=True)
    age = models.IntegerField(null=True)

    def __str__(self):
        return self.name, self.address, self.number, self.age

