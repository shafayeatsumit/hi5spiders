import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup
from geopy import geocoders
import time
import re

class CineplexJobSpider (CrawlSpider):
    name = "cineplexcrawler"
    allowed_domains = ["careers.cineplex.com"]
    start_urls = [
        'http://careers.cineplex.com/jobs/search?page=1#job-list'
    ]
    rules = (
        # Rule(LinkExtractor(allow=[''], restrict_xpaths=('//*[@class="row job-list__item"]/div/a')),
        # callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=[''], restrict_xpaths=('//a[@class="next_page"]')), 
          callback='parse_start_url', follow=True),
    )
    def parse_start_url(self, response):
        all_jobs = response.xpath('//*[@class="row job-list__item"]/div/a/@href')
        for job in all_jobs:
            url = job.extract()
            yield response.follow(job, self.parse_job)

    def parse_job(self, response):
        def clean_html(soup):
            for i in soup.find_all(['script','span']):
                i.extract()
            for i in soup.find_all('div',class_="job-details__copy-apply"):
                i.extract()

        def get_address(full_address):
            line = re.search(r'City:(.*)',full_address)
            if line:
                address = line.group(1).split(",")
                city = address[0].strip()
                province = address[1].strip()
                return city,province
        soup = BeautifulSoup(response.body, "html.parser")
        title = soup.find('h1')
        title_text = title.get_text()
        address = title.find_next_sibling().get_text()
        city, province = get_address(address)
        address1 = re.search(r'Location:(.*)',address).group(1).strip()
        soup = soup.find_all('div', class_='job-details__copy')[0]
        clean_html(soup)
        soup.find('h1').extract()
        job_description = str(soup).replace("\n","")
        yield {
            'job_title': title_text,
            'province' : province,
            'job_description' : job_description,
            'web_link' : response.url,
            'city' : city,
            'postal_code' : None,
            'address1' : address1
        }        