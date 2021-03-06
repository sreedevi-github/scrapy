
# -*- coding: utf-8 -*-

import scrapy
#import MySQLdb
import re
from datetime import datetime
from urllib import unquote
from NewYork.items import JobgoItem
from lxml.html.clean import clean_html


class MetroJobbseSpider(scrapy.Spider):
    name = 'metrojobbse'
    allowed_domains = ['metrojobb.se']

    start_urls = ['http://www.metrojobb.se/jobb/s%C3%B6k?pgSize=100'] 
			
    def parse(self, response):
	
        # Send job links to job parser
	for sel in response.xpath('//section[@class="results"]/ol/li[@class="result  js-result"]/a/@href').extract():
		
		if "http" in sel:
			
			pass
		else:
			url = "http://www.metrojobb.se"+sel	  	
			yield scrapy.Request(url, callback=self.parse_job)

        # Send next job page to self
        tmp = response.xpath('//section[@class="pagination"]/div[@class="pagination__main gamma push-half--bottom"]/a[@class="next-page ga-reporter"]/@href')
        if ( len(tmp) > 0 ):
            siteurl = 'http://www.metrojobb.se'
            url =  siteurl + tmp[0].extract()
            yield scrapy.Request(url)

    def parse_job(self,response):
		

        	i = JobgoItem()
       # try:	
        	idtmp1 = response.url.split('-')[0]
		idtmp = idtmp1.split('/')[-1]
		i['id'] = idtmp


		if i['id']:
		
			i['idprefix'] = 'metrojobb_se_'
        		i['url'] = 'http://www.metrojobb.se/jobb/'+i['id']
			
			
			titletmp = map(unicode.strip, response.xpath('//ul[@class="facts__list grid"]/li[@class="facts__item grid__item palm-one-half lap-and-up-one-whole job-ad__sidebar__title"]/text()').extract())
			title = ''.join(titletmp)
			i['title'] = title
			i['country'] = "Sweden"
			city = map(unicode.strip, response.xpath('//ul[@class="facts__list grid"]/li[@class="facts__item grid__item palm-one-half lap-and-up-one-whole job-ad__sidebar__location"]/text()').extract())
			if city:
				i['city'] = ''.join(city)
			else:
				region = map(unicode.strip, response.xpath('//ul[@class="facts__list grid"]/li[@class="facts__item grid__item palm-one-half lap-and-up-one-whole job-ad__sidebar__region"]/text()').extract())
				i['city'] = ''.join(region)
			try:
				logourl = response.xpath('//section[@class="facts push-half--bottom"]/a/img/@src | //section[@class="facts push-half--bottom"]/div/img/@src')[0].extract()
				if logourl:
					i['logourl'] = "http://www.metrojobb.se"+logourl
			except:
				pass
			
			pdatetmp = map(unicode.strip, response.xpath('//ul[@class="facts__list grid"]/li[@class="facts__item grid__item palm-one-half lap-and-up-one-whole job-ad__sidebar__date"]/text()').extract())
			pdate = ''.join(pdatetmp)
			i['publish_date'] = datetime.date(datetime.strptime(pdate,"%Y-%m-%d"))

			company = map(unicode.strip, response.xpath('//ul[@class="facts__list grid"]/li[@class="facts__item grid__item palm-one-half lap-and-up-one-whole job-ad__sidebar__employer"]/text()').extract())
			i['company'] = ''.join(company)

			desc = response.xpath('//section[@class="job-ad__main"]//text()').extract()
			i['description'] = ''.join(desc)

			try:
				email = response.xpath('//ul[@class="facts__list grid"]/li[@class="facts__item grid__item palm-one-half lap-and-up-one-whole job-ad__sidebar__mail"]/a/text()').extract()
				i['email'] = email[0]
			except:
				pass
			
			yield i

		else:
			pass
	
	  
        
        
       		
       # except:
	#	pass	


