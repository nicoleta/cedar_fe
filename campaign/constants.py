
#####
# Campaign constants
#####

CAMPAIGN_NATIVE = 1
CAMPAIGN_DISPLAY = 2

# each element in available_ad_types is lowercase(<class>) + s <class> being the related ad model
# E.g.: model NativeAd -> nativeads
CAMPAIGN_TYPES = {
	CAMPAIGN_NATIVE: {'name': 'Native',
					  'available_ad_types': ['nativeads']
					 },
	CAMPAIGN_DISPLAY: {'name': 'Display',
					   'available_ad_types': ['displayads']
					  }
}

# create a constant with all available ad types based on the lists defined above
ALL_AD_TYPES = []
for k, v in CAMPAIGN_TYPES.items():
	ALL_AD_TYPES += [at for at in v['available_ad_types'] if at not in ALL_AD_TYPES]

#####
# Bid constants
#####

BID_CPM = 1
BID_CPC = 2

BID_TYPES = {
	BID_CPM: 'CPM',
	BID_CPC: 'CPC'
}
