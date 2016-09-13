# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class JobgoItem(scrapy.Item):
    id = scrapy.Field()                 # * External ID of job----------------
    idprefix = scrapy.Field()           # * ID Prefix eg. mol_fi_ for mol.fi-------------
    publish_date = scrapy.Field()       #   Job publishdate - Format: 2016-01-27------------
    expire_date = scrapy.Field()        #   Job expiration date - Format: 2016-01-27
    modify_date = scrapy.Field()        #   Job modification date - Format:  2016-01-27
    company = scrapy.Field()            #   Name of the company-------------
    #category = scrapy.Field()		  category -- Remove after test
    title = scrapy.Field()              # * Title of the job-------------
    description = scrapy.Field()        # * Description of the job----------
    email = scrapy.Field()              #   Email address for applications----------
    logourl = scrapy.Field()            #   Logo url of company in ad.-------------
    url = scrapy.Field()                # * Url of the job ad.------------------
    address = scrapy.Field()            #   eg. Hakakatu 12
    postcode = scrapy.Field()           #   eg. 20540
    country = scrapy.Field()            # * eg. Finland
    city = scrapy.Field()               #   eg. Turku--------------
    region = scrapy.Field()             #   eg. Western Finland---------
    telephone = scrapy.Field()   	#   eg:00358465420799	


