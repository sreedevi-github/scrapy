
# -*- coding: utf-8 -*-
import scrapy
import re
import urlparse
import MySQLdb
from datetime import datetime
from urllib import unquote
from NewYork.items import JobgoItem
from lxml.html.clean import clean_html
from unidecode import unidecode




class MolfiSpider(scrapy.Spider):
	
	name = 'molfi'
    	allowed_domains = ['mol.fi']
	start_urls = ['http://www.mol.fi/tyopaikat/tyopaikkatiedotus/kevyt/hakusivu.htm']

	   	
	def parse(self,response):
		
		link = response.xpath('//div[@class="pageItem"]/a/@href')[0].extract()
		url = response.urljoin(link)
		#url = "http://www.mol.fi/tyopaikat/tyopaikkatiedotus/kevyt/"+link
		print url
		yield scrapy.Request(url, callback=self.parse_options)

	def parse_options(self,response):
		
		region = response.xpath('//select[@id="alueetLista"]/option/@value').extract()
			#region = sel.xpath('@value')[0].extract()
		print region[0]
		
		url = response.urljoin("http://www.mol.fi/tyopaikat/tyopaikkatiedotus/kevyt/hae.htm?lang=fi&tarkempiHaku=true&hakusana=&alueetLista="+region[1]+"&alueetLista="+region[2]+"&alueetLista="+region[3]+"&alueetLista="+region[4]+"&alueetLista="+region[5]+"&alueetLista="+region[6]+"&alueetLista="+region[7]+"&alueetLista="+region[8]+"&alueetLista="+region[9]+"&alueetLista="+region[10]+"&alueetLista="+region[11]+"&alueetLista="+region[12]+"&alueetLista="+region[13]+"&alueetLista="+region[14]+"&alueetLista="+region[15]+"&alueetLista="+region[16]+"&alueetLista="+region[17]+"&alueetLista="+region[18]+"&alueetLista="+region[19]+"&_alueetLista=1&valitutAmmattialat=&_valitutAmmattialat=1&ilmoitettuPvm=1&vuokrapaikka=---")
			
		yield scrapy.Request(url, callback=self.parse_page)

						
			

	
	def parse_page(self,response):
		url = response.url
		print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"+response.url
		#region = response.meta['region']
		for jobhref in response.xpath('//div[@class="hakutulos"]/a/@href').extract():
			#joburl = response.urljoin(jobhref) 
			joburl = "http://www.mol.fi/tyopaikat/tyopaikkatiedotus/kevyt/"+jobhref
			request = scrapy.Request(joburl,callback=self.parse_job)
			yield request

		try:	
			pagehref = response.xpath('//a[contains(text(),"Seuraava")]/@href')[0].extract()
			print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"+pagehref
			if len(pagehref)>0:
				url = urlparse.urljoin(response.url,pagehref)
				yield scrapy.Request(url, callback=self.parse_page)
			else:
				pass
		except:
			pass
			
		
	
	def parse_job(self,response):

#Southern Finland | Western Finland  | Oulu | Aland   | Eastern Finland  || Lapland
		
		i = JobgoItem()
		#region = response.meta['region']
		
		
		try:
			idcheck = response.xpath('//dd/span[@id="ilmoitusnumero"]/text()')[0].extract()
			if idcheck:
				i['id'] = idcheck
				i['idprefix'] = "mol_fi_"
				title = response.xpath('//h3/text()')[0].extract()
				i['country'] = "Finland"
 
				jobtitle = title.split(',')[0]
				i['title'] = jobtitle

				company = title.split(',')[1]          # name of company in different position of title
				if "paikkaa" in company:
					i['company'] = title.split(',')[2]
				else:
					i['company'] = company


				i['url'] = "http://www.mol.fi/tyopaikat/tyopaikkatiedotus/kevyt/tiedot.htm?ilmoitusnumero="+i['id']

				desc = response.xpath('//div[4]//text()').extract()		
				#tmp = " "	
				#for x in desc:			
				#	tmp = tmp + x.encode() 
				i['description'] = ' '.join(desc)

		
		
					# avoiding emails mentioning etunimi.sukunimi or nimi.sukunimi
				try:
			
					info = response.xpath('//dd/span[@id="yhteystiedot"]/a/text()')[0].extract()

					email = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", info, re.I)
					if email:
						if ("etunimi" or "sukunimi")in str(email):
							pass
						else:
							i['email'] = email[0]

					elif (len(email)==0):
						emailcheck = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", i['description'], re.I)
						if emailcheck:
							i['email'] = emailcheck[0]
						else:
							pass
				
					else:
						pass
			
			
				except:
					pass

				try:
					pdate = response.xpath('//dd/span[@id="ilmoituspaivamaarateksti"]/text()')[0].extract()
					i['publish_date'] = datetime.date(datetime.strptime(pdate,"%d.%m.%Y"))
		
					edate = response.xpath('//dd/span[@id="hakuPaattyy"]/text()')[0].extract()
					if "klo" in edate:
						edate = edate.split(' ')[0]
						i['expire_date'] = datetime.date(datetime.strptime(edate,"%d.%m.%Y"))
					else:
						i['expire_date'] = datetime.date(datetime.strptime(edate,"%d.%m.%Y"))			

				except:
					pass
		
			
			
		

		
		
		
				try:
					address = response.xpath('//dd/span[@id="tyopaikanOsoite"]/text()')[0].extract()
					# 02670 Espoo
					space1 = address.count(' ')
					space2 = address.count(',')
					if space1 == 1:
						city = address.split(' ')[-1]
						i['city'] = city
						postcode = address.split(' ')[-2]
						if postcode.isdigit():
							i['postcode'] = postcode
						else:
							pass
			
				# eg Mäkelänkatu 2 A,3krs, 00100 HELSINKI
	

					if (space1 >= 2) and (',' in address):
						tmpaddress = address.split(', ')
						if tmpaddress:
							i['address'] = tmpaddress[0]
						elif not tmpaddress[1].isdigit():
							i['address'] = tmpaddress[0] +' '+ tmpaddress[1]
						newaddress = address.split(', ')[-1]
						spacetmp = newaddress.count(' ')
						if spacetmp == 1:
							city = newaddress.split(' ')[-1]
							i['city'] = city
							postcode = newaddress.split(' ')[-2]
							if postcode.isdigit():
								i['postcode'] = postcode
							else:
								pass
						elif spacetmp == 2:
							city = newaddress.split(' ')[-2] +' ' +newaddress.split(' ')[-1]
							i['city'] = city
							postcode = newaddress.split(' ')[0]	
							if postcode.isdigit():
								i['postcode'] = postcode
							else:
								pass
						
						# eg Turku 20520 TURKU	
	
					elif (space1 >= 2) and (',' not in address):
						newaddress = address.split(' ')
		
						postcode = address.split(' ')[0]
						if postcode.isdigit():
							i['postcode'] = postcode
							i['city'] = newaddress[-2]+' '+newaddress[-1]
						else:
							pass
						
				
					else:
						pass
				
				
	
				except:
					pass
					
		
				yield i	
			else:
				pass
		except:
			pass
		
