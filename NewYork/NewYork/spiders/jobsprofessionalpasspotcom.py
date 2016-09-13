
# -*- coding: utf-8 -*-

import scrapy
#import MySQLdb
import re
from datetime import datetime
from urllib import unquote
from NewYork.items import JobgoItem
from lxml.html.clean import clean_html
from datetime import date

class JobsProfessionalPassportcomSpider(scrapy.Spider):
	name = 'jobsprofessionalpassportcom'
	allowed_domains = ['professionalpassport.com']

   
	start_urls = ['https://jobs.professionalpassport.com/jobboard/cands/jobresults.asp']
	
	def parse(self, response):
		        
		for sel in response.xpath('//form[@id="frmJobResults"]/div[contains(@class,"jobInfo")]/h2/a/@href'):
			urltmp = sel.extract()
			url = "https://jobs.professionalpassport.com"+urltmp	
			yield scrapy.Request(url, callback=self.parse_job)

		# Send next job page to self
        	tmp = response.xpath('//ul[@class="pageNumbers"]/li[@class="next"]/a[@class="pageNavBtn"]/@href')
        	if ( len(tmp) > 0 ):
        		url="https://jobs.professionalpassport.com"+tmp[0].extract()
            		yield scrapy.Request(url)

	def parse_job(self, response):

		print "Hey in jobs........"+response.url
		
	
		i = JobgoItem()

		i['url'] = response.url 

		tmp = response.url.split('/')[-2]
		

		i['id'] = tmp
	
		i['idprefix'] = "jobsprofessionalpassport_com_"

		title = response.xpath('//div[contains(@id,"Job")]/h1/text()')[0].extract()
		i['title'] = title

		emp = response.xpath('//div[contains(@id,"Job")]/div[@id="JobViewFields"]/dl/dd[@id="DDCompanyName"]/a/text()')[0].extract()
		emp = emp.replace("\n","").replace("\t","").replace("\r","")
		i['company'] = emp
	
		i['country'] = "United Kingdom"

		try:

			logourl=response.xpath('//div[@class="jobLogo"]/a/img/@src')[0].extract()
			i['logourl'] = "https://jobs.professionalpassport.com"+logourl

		except:

			pass

		pdate = response.xpath('//div[contains(@id,"Job")]/div[@id="JobViewFields"]/dl/dd[@id="DDPosted"]/text()')[0].extract()

		i['publish_date'] = datetime.date(datetime.strptime(pdate,"%d/%m/%Y"))
		
		try:
			city = response.xpath('//div[contains(@id,"Job")]/div[@id="JobViewFields"]/dl/dd[@id="DDLocation"]/text() | //div[contains(@id,"Job")]/div[@id="JobViewFields"]/dl/dd[@id="DDLocation"]/a/em/text()')[0].extract()
			
			
			if "Unspecified" in city:
				region = response.xpath('//div[contains(@id,"Job")]/div[@id="JobViewFields"]/dl/dd[@id="DDRegion"]/a/em/text()')[0].extract()
				i['city'] = region

			elif '(' in city:
				tmpcity = city.split('(')[0]
				i['city'] = tmpcity	
			else:
				i['city'] = city
		except:
			pass	

		desc = response.xpath('//div[@class="jobDescription"]//p//text()').extract()

		i['description'] =  clean_html(' '.join(desc))

		email = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", i['description'], re.I)

		if email:
			i['email'] =  email[0]
			
		yield i


			
