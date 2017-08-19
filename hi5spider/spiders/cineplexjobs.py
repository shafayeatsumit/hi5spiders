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
        title = response.xpath('//*[@id="job-details"]//h1/text()').extract_first()
        print(title)        