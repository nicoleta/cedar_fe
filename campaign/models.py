
from django.db import models
from django.forms.models import model_to_dict
from datetime import timedelta, datetime, date

from campaign.constants import *
from account.models import Advertiser
from config.models import Category



class Campaign(models.Model):
    """
    Store all campaign's configuration attributes.
    """

    # We have this status for when a campaign needs to be approved before getting ACTIVE.
    STATUS_PENDING = 1
    STATUS_ACTIVE = 2
    # This status is set when user specifically wants to have the campaign inactive.
    # Campaign might still be inactive even having status ACTIVE because of other reasons like caps_reached,
    # hasn't yet started (current time < start_time), it has ended (current_time > end_time), it doesn't have
    # any active Ads etc - but all these conditions are checked before sending the campaign to the bidder.
    STATUS_PAUSED = 3
    STATUS_DELETED = 4

    STATUSES = {
		STATUS_PENDING: 'Pending',
		STATUS_ACTIVE: 'Active',
		STATUS_PAUSED: 'Paused',
        STATUS_DELETED: 'Deleted'
	}

    
    advertiser = models.ForeignKey(Advertiser, related_name='campaigns')
    name = models.CharField(max_length=128)
    # using codes in the tables - see constants their meaning
    campaign_type = models.IntegerField(choices=[(k, v) for k,v in STATUSES.items()])
    status = models.IntegerField(default=STATUS_PENDING)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # how much $ can a campaign spend in a day, 0 means unlimited
    daily_cap = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    # how much $ can a campaign spend in a month, 0 means unlimited
    monthly_cap = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    # how much $ can a campaign spend in total, 0 means unlimited
    total_cap = models.DecimalField(max_digits=14, decimal_places=6, default=0)

    start_date = models.DateField(null=True) 
    end_date = models.DateField(null=True)

    bid_type = models.IntegerField(choices=[(k, v) for k,v in BID_TYPES.items()])
    # bid used as default when the campaign ads don't have one set
    bid = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    # since bid can be overwritten by its ads, set a minimum value an ad can have as bid
    min_bid = models.DecimalField(max_digits=14, decimal_places=6, default=0)

    # how many times an ad is shown per day, per user (0 = unlimited)
    daily_frequency_cap = models.IntegerField(default=0)
    # ad is shown every X minutes per user
    minutes_frequency = models.IntegerField(default=1440)

    # ???????????????
    #spreading = models.CharField(max_length=16, default='spend', choices=SPREADING_CHOICES)

    # ??how deep are we going with campaign locations? UFE has countries, Lyfe goes more in depth with states and cities
    #geos = models.ManyToManyField('config.Geo')

    # targeted platforms??
    # schedule - like adon(hours per selected days) or like lyfe(same hours for all selected days)?
    # keywords - per ad or per campaign?

    def set_status(self, new_status, save=True):
        """
        This method should always be used when changing a campaign status because extra checks will be required
        for different types of statuses

        @param new_status: integer
        @param save: boolean; weather to actually save the instance;

        """
        # add the extra checks here
        self.status = new_status
        if save:
            self.save()

class CampaignCategories(models.Model):
    # TBD
    
    campaign = models.ForeignKey(Campaign, related_name='campaign_categories')
    category = models.ForeignKey(Category)
    # overwrites the campaign level bid; if left null, the campaign's bid will be used
    max_bid = models.DecimalField(max_digits=14, decimal_places=6, null=True)


class CampaignDevices(models.Model):
    # TBD
    
    campaign = models.ForeignKey(Campaign, related_name='campaign_categories')
    device = models.ForeignKey(Device) #?
    # overwrites the campaign level bid; if left null, the campaign's bid will be used
    max_bid = models.DecimalField(max_digits=14, decimal_places=6, null=True)


class AbstractAd(models.Model):
    """
    Parent model storing common Ad configuration
    """

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
    
    campaign = models.ForeignKey(Campaign, related_name='%(class)ss')
    name = models.CharField(max_length=128)
    # using codes in the tables - see constants their meaning
    status = models.IntegerField(default=STATUS_PENDING, choices=[(k, v) for k,v in STATUSES.items()])
    # bid ?

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    url = models.CharField(max_length=256)

    def save(self, *args, **kwargs):
        # the campaign related name for the list of ads is lowercase(<child model>)+s
        # (same as related_name in the campaign field definition above)
        related_name = '%(class)ss' % {'class': self._meta.get_field('campaign').model.__name__.lower()}
        # make sure the campaign can have this type of ads
        if related_name not in CAMPAIGN_TYPES[self.campaign.campaign_type]['available_ad_types']:
            raise Exception("Cannot add %s for a %s campaign type" % (related_name, CAMPAIGN_TYPES[self.campaign.campaign_type]['name']))
        super(AbstractAd, self).save(*args, **kwargs)

    class Meta:
        abstract = True

############################################################################################################
# Native Ads related models

class NativeAd(AbstractAd):
    """
    Configuration for native ads
    """
    title = models.CharField(max_length=128)

    def set_data_assets(self, data_assets_list):
        das = []
        for item in data_assets_list:
            da = NativeAdDataAsset()
            for k in ['asset_type', 'value']:
                setattr(da, k, item[k])
            das.append(da)
        self.data_assets = das
    
    def set_image_assets(self, image_assets_list):
        ias = []
        for item in image_assets_list:
            ia = NativeAdImageAsset()
            for k in ['asset_type', 'filename', 'original_width', 'original_height']:
                setattr(ia, k, item[k])
            ias.append(ia)
        self.image_assets = ias


class NativeAdDataAsset(models.Model):
    """
    Store Data Assets for the native ads.
    """

    # as defined by OpenRTB Data Asset ID
    TYPE_1  = 1
    TYPE_2  = 2
    TYPE_3  = 3
    TYPE_4  = 4
    TYPE_5  = 5
    TYPE_6  = 6
    TYPE_7  = 7
    TYPE_8  = 8
    TYPE_9  = 9
    TYPE_10 = 10
    TYPE_11 = 11
    TYPE_12 = 12
    
    # map the asset types with human readable text and a type that will be used to check the value before
    # storing it in the db. The saved value is always str, but type is checked because of OpenRTB requirements.
    # (these were taken from the IAB OpenRTB specifications)
    DATA_TYPES = {
        TYPE_1:  {"name": "Sponsored", "data_type": str},
        TYPE_2:  {"name": "Description", "data_type": str},
        TYPE_3:  {"name": "Rating", "data_type": int},
        TYPE_4:  {"name": "Likes", "data_type": int},
        TYPE_5:  {"name": "Downloads", "data_type": int},
        TYPE_6:  {"name": "Price", "data_type": float},
        TYPE_7:  {"name": "SalePrice", "data_type": float},
        TYPE_8:  {"name": "Phone", "data_type": str},
        TYPE_9:  {"name": "Address", "data_type": str},
        TYPE_10: {"name": "Description2", "data_type": str},
        TYPE_11: {"name": "DisplayURL", "data_type": str},
        TYPE_12: {"name": "CTAText", "data_type": str}        
    }
    
    ad = models.ForeignKey(NativeAd, related_name="data_assets")
    asset_type = models.IntegerField(choices=[(k, v) for k,v['name'] in DATA_TYPES.items()])
    value = models.CharField(max_length=256)
    
    def to_dict(self):
        return model_to_dict(self, fields=['asset_type', 'value'])
    
    def save(self, *args, **kwargs):
        assert self.asset_type in self.DATA_TYPES
        # try to convert the value to the OpenRTB required type
        # (even though it will still be saved as str, we need to make sure it complies to OpenRTB requirements)
        try:
            self.DATA_TYPES[self.asset_type]["data_type"](self.value)
        except:
            raise Exception("Invalid value type for data type %s (%s). Should be %s" % (self.asset_type,
                                                                        self.DATA_TYPES[self.asset_type]['name'],
                                                                        self.DATA_TYPES[self.asset_type]['data_type']))
        super(NativeAdDataAsset, self).save(*args, **kwargs)


class NativeAdImageAsset(models.Model):
    """
    Store Image Assets for the native ads.
    """

    # as defined by OpenRTB Image Asset ID
    TYPE_1  = 1
    TYPE_2  = 2
    TYPE_3  = 3

    # map the asset types with human readable text
    IMAGE_TYPES = {
        TYPE_1:  "Icon",
        TYPE_2:  "Logo",
        TYPE_3:  "Main"
    }

    ad = models.ForeignKey(NativeAd, related_name="image_assets")
    asset_type = models.IntegerField(choices=[(k, v) for k,v in IMAGE_TYPES.items()])
    filename = models.CharField(max_length=256)
    original_width = models.IntegerField()
    original_height = models.IntegerField()
    
    def to_dict(self):
        return model_to_dict(self, fields=['asset_type', 'filename', 'original_width', 'original_height'])

    def save(self, *args, **kwargs):
        assert self.asset_type in self.IMAGE_TYPES
        super(NativeAdImageAsset, self).save(*args, **kwargs)



############################################################################################################



