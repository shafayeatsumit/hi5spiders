import scrapy
from bs4 import BeautifulSoup
from geopy import geocoders
from hi5spider.insert_db import insert_jobs
import re

class RogersJobSpider (scrapy.Spider):
    name = "crawlrogers"
    url = 'https://jobs.rogers.com/search/?q=&sortColumn=referencedate&sortDirection=desc&startrow='
    start_urls =[] 
    increment = 0
    for i in range(0,15):
        new_url = url+str(increment)
        start_urls.append(new_url)
        increment += 25    
    def __init__(self, *args, **kwargs): 
        self.root_url = "https://jobs.rogers.com"
        self.next_page_xpath = '//*[@id="content"]/div/div[2]/div[2]/div/div/ul//li[@class="active"]//following-sibling::*/a/@href'

    def parse(self, response):
        all_jobs = response.xpath('//*[@id="searchresults"]/tbody/tr/td//a/@href')
        for job in all_jobs:
            yield response.follow(job, self.parse_job)



    
    def parse_job(self, response):
        def extract_with_xpath(query):
            return response.xpath(query).extract_first().strip()
        def province_parsing(address_string):
            provinces = ["AB","BC","MB","NB","NL","NS","NT","NU","ON","PE","QC","SK","YT"]
            province_initial = [i.strip()  for i in address_string.split(",") if i.strip() in provinces]
            if province_initial:
                return province_initial[0]
            else:
                return None      
        job_location_string = extract_with_xpath('//p[@class="jobLocation"]/span/text()')

        def job_description_parsing(response):
            soup = BeautifulSoup(response.body,"html.parser")   
            job = soup.find_all("div", class_="job") 
            job_description = str(job[0]).replace(u'\xa0', u' ').replace('\n', '')
            return job_description

        def cleanhtml(raw_html):
           cleanr = re.compile('<.*?>')
           cleantext = re.sub(cleanr, '', raw_html)
           return cleantext

        def get_address (response):
            result = re.search(r'Work Location:(.*)</div>',response.text)
            try:
                print(response.url)
                #address =  cleanhtml(result.group(1)).split(",")[0].replace("&nbsp;","").strip()
                address_list = cleanhtml(result.group(1)).split(",")
                if len(address_list) >3:
                    del address_list [-2:]
                    address = "".join(address_list).strip()
                else:
                   address =  cleanhtml(result.group(1)).split(",")[0].replace("&nbsp;","").strip()     
                return address
            except Exception as e:
                return None

        data = {
            'job_title': extract_with_xpath('//div[@class="jobTitle"]/h1/text()'),
            'province' : province_parsing(job_location_string),
            'job_description' : job_description_parsing(response),
            'web_link' : response.url,
            'city' : job_location_string.split(",")[0],
            'postal_code' : job_location_string.split(",")[-1],
            'address1' : get_address(response)
        }
        print("address", data['address1'])
        insert_jobs(data)

