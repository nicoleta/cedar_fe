
import datetime
from django.contrib.auth.models import User, Group
from django.test import TestCase

from cedar_fe.api_common import ApiResourceTestCaseMixin
from campaign.models import Campaign, NativeAd
from campaign.constants import *
from account.models import Advertiser


class CampaignResourceTest(ApiResourceTestCaseMixin, TestCase):
    
    def setUp(self):
        super(CampaignResourceTest, self).setUp()

        # Create a staff user.
        self.staff_username = 'apisuperuser'
        self.staff_password = 'apitestpass'
        self.staff_user = User.objects.create_superuser(self.staff_username, 'apisuperuser@example.com', self.staff_password)

        # Create some advertisers
        self.advertiser_username1, self.advertiser_password1, self.advertiser_user1, self.advertiser1 = self.create_advertiser(1)
        self.advertiser_username2, self.advertiser_password2, self.advertiser_user2, self.advertiser2 = self.create_advertiser(2)


    def create_advertiser(self, index=1, status=Advertiser.STATUS_ACTIVE):
        # Create an advertiser user.
        advertiser_username = 'apiadvertiser%s' % index
        advertiser_password = 'apitestpass'
        advertiser_user = User.objects.create_user(advertiser_username, 'apiadvertiser%s@example.com' % index, advertiser_password)
        group = Group.objects.get(name='advertisers')
        group.user_set.add(advertiser_user)

        advertiser = Advertiser(user=advertiser_user, name='Advertiser Test %s' % index, status=status)
        advertiser.save()

        return advertiser_username, advertiser_password, advertiser_user, advertiser

    def create_campaign(self, advertiser, index=1):
        campaign = Campaign(advertiser=advertiser, name='Random Campaign %s' % index, campaign_type=CAMPAIGN_NATIVE, bid_type=BID_CPM)
        campaign.save()
        return campaign
 

    def test_get_list_unauthenticated(self):
        self.assertHttpForbidden(self.api_client.get('/api/v1/campaign/', format='json'))


    def test_get_list_json(self):
        # create a campaign for advertiser 1
        self.create_campaign(self.advertiser1)

        #staff should get it
        resp = self.api_client.get('/api/v1/campaign/', format='json', authentication=self.create_oauth2(user=self.staff_user))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 1)

        # advertiser1 should get it
        resp = self.api_client.get('/api/v1/campaign/', format='json', authentication=self.create_oauth2(user=self.advertiser_user1))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 1)

        # advertiser1 should NOT get it
        resp = self.api_client.get('/api/v1/campaign/', format='json', authentication=self.create_oauth2(user=self.advertiser_user2))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)


    def test_get_detail_json(self):
        # create a campaign for advertiser 1
        campaign = self.create_campaign(self.advertiser1)

        resp = self.api_client.get('/api/v1/campaign/%s/' % campaign.id, format='json',
                                   authentication=self.create_oauth2(user=self.advertiser_user1))
        self.assertValidJSONResponse(resp)
        resp_obj = self.deserialize(resp)

        # test some keys
        self.assertEqual(resp_obj['id'], campaign.id)
        self.assertEqual(resp_obj['advertiser_id'], self.advertiser1.id)
        self.assertEqual(resp_obj['name'], campaign.name)


    def test_post_unauthenticated(self):
        post_data = {
            'name': 'Campaign POST',
            'campaign_type': CAMPAIGN_NATIVE,
            'bid_type': BID_CPM,
            'advertiser_id': self.advertiser1.id
        }
        self.assertHttpForbidden(self.api_client.post('/api/v1/campaign/', format='json', data=post_data))


    def test_post(self):
        post_data = {
            'name': 'Campaign POST',
            'campaign_type': CAMPAIGN_NATIVE,
            'bid_type': BID_CPM,
            'advertiser_id': self.advertiser1.id
        }
        ids_before = [c.id for c in Campaign.objects.all()]
        post_response = self.api_client.post('/api/v1/campaign/', format='json', data=post_data,
                                             authentication=self.create_oauth2(user=self.advertiser_user1))
        self.assertHttpCreated(post_response)
        ids_after = [c.id for c in Campaign.objects.all()]

        created_id = list(set(ids_after) - set(ids_before))
        self.assertEqual(len(created_id), 1)

        self.assertTrue(post_response['Location'].endswith('/api/v1/campaign/%s/' % created_id[0]))


    def test_put_unauthenticated(self):
         # create a campaign that we'll update
        campaign = self.create_campaign(self.advertiser1)
        put_data = {
            'name': 'Campaign PUT'
        }
        self.assertHttpForbidden(self.api_client.post('/api/v1/campaign/%s/' % campaign.id, format='json', data=put_data))


    def test_put(self):
        # create a campaign that we'll update
        campaign = self.create_campaign(self.advertiser1)
        put_data = {
            'name': 'Campaign PUT'
        }
        self.api_client.put('/api/v1/campaign/%s/' % campaign.id, format='json', data=put_data,
                            authentication=self.create_oauth2(user=self.advertiser_user1))
        updated_campaign = Campaign.objects.get(id=campaign.id)
        self.assertEqual(updated_campaign.name, 'Campaign PUT')
