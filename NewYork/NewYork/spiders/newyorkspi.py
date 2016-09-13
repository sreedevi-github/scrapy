import scrapy
import re
import pycountry
from datetime import datetime
from scrapy.spiders import Spider
from NewYork.items import JobgoItem
from lxml.html.clean import clean_html

class NewYorkSpider(scrapy.Spider):
	name = "nyspi"
	allowed_domains = ['nycityworks.com']
	custom_settings = {
                       'CONCURRENT_REQUESTS_PER_IP' : 8,
                       }
	start_urls = ['http://www.nycityworks.com']


#browse all categories
	def parse(self,response):
		for sel in response.xpath('//div[@id="browse"]/div[@class="inner cf"]/ul/li'):
			
			category = sel.xpath('a/text()')[0].extract() # change here for all categories
			categorypath = sel.xpath('a/@href')[0].extract()
			categoryurl = "http://www.nycityworks.com"+categorypath
		
			request = scrapy.Request(categoryurl,callback=self.parse_page)
			request.meta['categoryurl'] = categoryurl
			#request.meta['category'] = category
			yield request

#parse category page	
	def parse_page(self,response):
	   # category = response.meta['category']	
	    categoryurl = response.meta['categoryurl']
	   	
	    check = response.xpath('//div[@class="pagination"]')  # check if pagination is available on a page - if not its the last
	    	 
	    if ( len(check) > 0 ):
		for jobtag in response.xpath('//ul[@class="jobsList"]/li'):
			newtag = jobtag.xpath('p[@class="age" and @title="Added today"] | div[@class="cf"]/ul[@class="meta"]/li[@class="last" and contains(text(), "1 day ago")]')
			#print newtag	
			#print len(newtag)
			if ( len(newtag) > 0 ):	
				
		 		for sel in newtag.xpath('preceding-sibling::h4/a/@href').extract():
                 			joburl = "http://www.nycityworks.com"+sel
					title = newtag.xpath('preceding-sibling::h4/a/text()')[0].extract()
					
              				yield scrapy.Request(joburl,callback=self.parse_job, meta={'title':title})
	
				
	#Pagination		
				sel = response.xpath('//div[@class="resultsTarget-content"]')
				tmp = str(sel.xpath('div[@class="pagination"]/ul/li/a[@class="nextPageSet"]/@href').extract())
				if ( len(tmp) > 0 ):	
					stmp = tmp.split('/')
					ftmp = stmp[-2]
					url = categoryurl+ftmp
					#print url
					yield scrapy.Request(url,callback=self.parse_page , meta={'categoryurl':categoryurl})
	


	def parse_job(self,response):
		print "Hello in parse jobs"
		title = response.meta['title']
		#print response.meta['category']
		item = JobgoItem()
		item['title'] = title
		#title = response.xpath('//div[@id="detailHeader"]/h1[@itemprop="title"]/text()')[0].extract()
		if item['title']:           	
			sel = response.css("div.details")
								
				
			print "Inside if"
			item['title'] = title
			item['id'] = response.url.split('/')[-3]
			item['idprefix'] = "nycityworks_com_"
			item['url'] = response.url
			item['country'] = 'United States'  # All jobs are in the US
			item['company'] = sel.xpath('div[@class="fieldWrapper"]/span[@class="label" and text()="Employer"]/following-sibling::div[@class="textField"]/span[@itemprop="hiringOrganization"]/span/text()')[0].extract()
			cityreg = map(unicode.strip, sel.xpath('div[@class="fieldWrapper"]/span[@class="label" and contains(text(),"Location")]/following::div[@class="textField"]/text()').extract())
			print "*****************"
			cityreg = cityreg[0]
			
			if "," in cityreg:
				city = str(cityreg).split(',')[-2]
				item['city'] = city.split("'")[-1]
			elif "," not in cityreg:
					item['city'] = str(cityreg)
			else:
				item ['city'] = "New York"				
			item['region'] = "New York"
			item['description'] = clean_html(str(response.xpath('//div[@class="articleBody" and @itemprop="description"]//text()').extract()))
			
				
					
			email = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", item['description'], re.I)
			print email
			if '...@' in str(email):
				pass
			elif email:
				item['email'] = email[0]
			else:
				pass
						
					

			pdate = sel.xpath('div[@class="fieldWrapper"]/span[@class="label" and contains(text(),"Posted")]/following-sibling::div[@class="textField"]/span[@itemprop="datePosted"]/text()')[0].extract()
			item['publish_date'] = datetime.date(datetime.strptime(pdate,"%A, %B %d, %Y"))
			cdate = sel.xpath('div[@class="fieldWrapper"]/span[@class="label" and contains(text(),"Closes")]/following-sibling::div[@class="textField"]/text()')[0].extract()
			item['expire_date'] = datetime.date(datetime.strptime(cdate," %A, %B %d, %Y "))

			yield item
			



