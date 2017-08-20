import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup
from geopy import geocoders
import time

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
        def clean_description(html):
            for  i in soup.find_all('div',class_="job-details__copy-apply"):
                i.extract()
            for  i in soup.find_all('script'):
                i.extract()    
        soup = BeautifulSoup(response.body,"html.parser") 
        title = soup.find('h1')
        address = title.find_next_sibling().get_text()
        province = address.split(",")[-1].strip()
        print(address)        