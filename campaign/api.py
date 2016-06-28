
from tastypie.resources import ModelResource, ALL
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.exceptions import BadRequest, ImmediateHttpResponse
from django.core.exceptions import PermissionDenied

from cedar_fe.api_common import ApiAuthorization
from account import auth
from account.models import Advertiser
from campaign.models import Campaign, NativeAd
from campaign.constants import *


def auth_filter_native_ads_list(object_list, user):
    if user.is_superuser or user.is_staff:
        return object_list

    # Account Reps have access to a subset of Advertisers
    if user.groups.filter(name='account_reps').count() > 0:
        # TODO: get list of this account rep's advertisers
        advertisers_ids = []
        return object_list.filter(campaign__advertiser_id__in=advertisers_ids)

    if user.groups.filter(name='advertisers').count() > 0:
        return object_list.filter(campaign__advertiser__user_id=user.id)

    raise PermissionDenied()

class NativeAdResource(ModelResource):
    class Meta:
        queryset = NativeAd.objects.all()
        resource_name = 'nativead'
        authentication = Authentication()
        
        authorization = ApiAuthorization(Campaign, # if user can access Campaign, it can also access Ads
                                        gen_kwargs_func=None,
                                        filter_list_func=auth_filter_native_ads_list,
                                        auth_get_func=auth.user_has_model_access,
                                        auth_post_func=auth.user_has_model_access,
                                        auth_put_func=auth.user_has_model_access,
                                        auth_delete_func=auth.user_has_model_access)
        filtering = {
            'id': ALL,
            'status': ALL,
            'name': ALL,
            'campaign_id' : ALL
        }

    campaign_id = fields.IntegerField(attribute='campaign_id', blank=False, null=False)
    dataassets = fields.DictField(attribute='dataassets', blank=True, null=True)
    imageassets = fields.DictField(attribute='imageassets', blank=True, null=True)


    def hydrate_campaign_id(self, bundle):
        if 'campaign_id' in bundle.data:
            # can't update (PUT) campaign_id
            if bundle.request.method.lower() == 'put':
                del bundle.data['campaign_id']
                return bundle
            # make sure the campaign_id is correct and it exists
            try:
                campaign = Campaign.objects.get(pk=bundle.data['campaign_id'])
                if campaign.campaign_type != CAMPAIGN_NATIVE:
                    raise BadRequest('The provided campaign does not support nativeads')
                bundle.data['campaign_id'] = campaign.id
            except:
                raise BadRequest('Invalid campaign_id.')
        elif bundle.request.method.lower() == 'post':
            raise BadRequest('Missing campaign_id.')
        return bundle
    
    def obj_create(self, bundle, **kwargs):
        request_method = bundle.request.method.lower();
        if request_method == 'put':
            raise BadRequest("Invalid primary key provided.")
        data_assets = bundle.data['dataassets']
        image_assets = bundle.data['imageassets']

        saved_bundle = super(NativeAdResource, self).obj_create(bundle, **kwargs)

        saved_bundle.obj.set_data_assets(data_assets)
        saved_bundle.obj.set_image_assets(image_assets)
        saved_bundle.obj.save()

        return saved_bundle

    def obj_update(self, bundle, **kwargs):
        data_assets = bundle.data['dataassets']
        image_assets = bundle.data['imageassets']

        saved_bundle = super(NativeAdResource, self).obj_update(bundle, **kwargs)

        saved_bundle.obj.set_data_assets(data_assets)
        saved_bundle.obj.set_image_assets(image_assets)
        saved_bundle.obj.save()

        return saved_bundle

    def dispatch(self, request_type, request, **kwargs):

        return super(NativeAdResource, self).dispatch(request_type, request, **kwargs)
    
    
    def dehydrate(self, bundle):
        
        ad = bundle.obj
        bundle.data['dataassets'] = [ds.to_dict() for ds in ad.data_assets.all()]
        bundle.data['imageassets'] = [imgs.to_dict() for imgs in ad.image_assets.all()]

        return super(NativeAdResource, self).dehydrate(bundle)


def auth_filter_campaign_list(object_list, user):
    if user.is_superuser or user.is_staff:
        return object_list

    # Account Reps have access to a subset of Advertisers
    if user.groups.filter(name='account_reps').count() > 0:
        # TODO: get list of this account rep's advertisers
        advertisers_ids = []
        return object_list.filter(advertiser_id__in=advertisers_ids)

    if user.groups.filter(name='advertisers').count() > 0:
        return object_list.filter(advertiser__user_id=user.id)

    raise PermissionDenied()

class CampaignResource(ModelResource):
    class Meta:
        queryset = Campaign.objects.all()
        resource_name = 'campaign'
        authentication = Authentication()
        
        authorization = ApiAuthorization(Campaign,
                                        gen_kwargs_func=None,
                                        filter_list_func=auth_filter_campaign_list,
                                        auth_get_func=auth.user_has_model_access,
                                        auth_post_func=auth.user_has_model_access,
                                        auth_put_func=auth.user_has_model_access,
                                        auth_delete_func=auth.user_has_model_access)
        filtering = {
            'id': ALL,
            'status': ALL,
            'name': ALL,
            'advertiser_id' : ALL,
            'campaign_type' : ALL
        }

    advertiser_id = fields.IntegerField(attribute='advertiser_id', blank=False, null=False)
    # add all possible ads here, they will be removed in the dehydrate based on campaign type
    # NOTE: all ads must be saved separately using the NativeAdResource with the correspondent campaign_id.
    # We could make the NativeAdResource.campaign_id field relate to this CampaignResource so that when a post request
    # is made for a campaign it can also save related nativeads resources.
    # The problem is that related resource objects do not call obj_create/obj_update, only save().
    # In that case, all related operations that we have in those two methods are not performed.
    nativeads = fields.ToManyField(NativeAdResource, 'nativeads', full=True, null=True, blank=True, related_name='campaign')


    def dispatch(self, request_type, request, **kwargs):

        #print 'format in campaign'
        #print self.determine_format(request)
        #print
        return super(CampaignResource, self).dispatch(request_type, request, **kwargs)

    def dehydrate(self, bundle):
        # remove the ads list that are not related to this type of campaign
        campaign_type = bundle.data['campaign_type']
        bundle.data['ads'] = {}
        for ad_type in ALL_AD_TYPES:
            if ad_type in bundle.data:
                if ad_type in CAMPAIGN_TYPES[campaign_type]['available_ad_types']:
                    bundle.data['ads'][ad_type] = bundle.data[ad_type]
            del bundle.data[ad_type]

        return super(CampaignResource, self).dehydrate(bundle)

    def hydrate_advertiser_id(self, bundle):
        if 'advertiser_id' in bundle.data:
            # can't update advertiser_id
            if bundle.request.method.lower() == 'put':
                del bundle.data['advertiser_id']
                return bundle
            # make sure the advertiser_id is correct and it exists
            try:
                bundle.data['advertiser_id'] = Advertiser.objects.get(pk=bundle.data['advertiser_id']).id
            except:
                raise BadRequest('Invalid advertiser_id.')
        elif bundle.request.method.lower() == 'post':
            raise BadRequest('Missing advertiser_id.')
        return bundle


    def obj_create(self, bundle, **kwargs):
        request_method = bundle.request.method.lower();
        if request_method == 'put':
            raise BadRequest("Invalid primary key provided.")

        return super(CampaignResource, self).obj_create(bundle, **kwargs)
