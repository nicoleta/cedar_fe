
from django.db import models


class Geo(models.Model):
    pass


class Device(models.Model):
    # TBD desktop, mobile, tablet + OS?, OS version? browser?
    pass


class Category(models.Model):
    """
    Defines all the IAB codes and their names + GS categories and names
    """
    
    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=128)
    parent = models.ForeignKey("self", related_name="children")







