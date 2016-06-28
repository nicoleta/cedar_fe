
from django.db import models
from django.contrib.auth.models import User



class UserProfile(models.Model):
    
    user = models.OneToOneField(User, related_name='user_profile')
    address1 = models.CharField(max_length=64, null=True)
    address2 = models.CharField(max_length=64, null=True)
    city = models.CharField(max_length=32, null=True)
    state = models.CharField(max_length=32, null=True)
    country = models.CharField(max_length=2, null=True)
    postal_code = models.CharField(max_length=16, null=True)
    phone = models.CharField(max_length=32, null=True)
    api_token = models.CharField(max_length=64, null=True)
    stripe_id = models.CharField(max_length=128, null=True)


class Advertiser(models.Model):

    # We have this status for when an advertiser needs to be approved.
    STATUS_PENDING = 1
    STATUS_ACTIVE = 2
    STATUS_PAUSED = 3
    STATUS_DELETED = 4

    STATUSES = {
        STATUS_PENDING: 'Pending',
        STATUS_ACTIVE: 'Active',
        STATUS_PAUSED: 'Paused',
        STATUS_DELETED: 'Deleted'
    }

    
    user = models.ForeignKey(User)
    name = models.CharField(max_length=128)
    status = models.IntegerField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class AuthLog(models.Model):
    """
    Keep track of user authentication.
    """
    user = models.ForeignKey(User, null=True)
    username = models.CharField(max_length=75, null=True)
    ip_address = models.GenericIPAddressField(null=True)
    date_used = models.DateTimeField(auto_now=True)
    requested_url = models.CharField(max_length=512)
    message = models.CharField(max_length=512, null=True)
    authenticated = models.BooleanField(default=False)