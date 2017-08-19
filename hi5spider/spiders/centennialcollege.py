# -*- coding: utf-8 -*-

import scrapy
import json
from scrapy_splash import SplashRequest
from bs4 import BeautifulSoup

script_first_page = """
function main(splash)
    assert(splash:go(splash.args.url))  
    function wait_for(splash, condition)
        while not condition() do
            splash:wait(0.05)
        end
    end
    wait_for(splash, function()
        return splash:evaljs("document.getElementsByClassName('odd') !== null")
    end)
    return splash:html()
end
"""

class CentinalSpider(scrapy.Spider):
    name = "centinalspider"
    def __init__(self, *args, **kwargs):     
        self.start_url = 'http://db2.centennialcollege.ca/ce/allcourses.php'
        self.root_url = 'http://db2.centennialcollege.ca/ce/'
    def start_requests(self):
        yield SplashRequest(url= self.start_url , 
                callback = self.parse,
                endpoint='execute',
                args={
                    'lua_source': script_first_page,
                    'timeout': 90
                }            
              )
    def clean_text(self,raw_html):
      return BeautifulSoup(raw_html, "html.parser").text   

    def parse(self, response):
      print("prse method called +++++++++")
      courses_url = response.xpath('//*[@id="content"]/table/tr/td[1]/a/@href').extract()
      
      for url in courses_url:
          current_url = self.root_url+url
          yield SplashRequest( url = current_url,
              callback = self.parse_detail
            )
    def parse_detail(self, response):
      print("prse_detail method called +++++++++")
      #response decoded
      title_html = response.xpath('//*[@id="sectionheading"]/h1').extract_first()
      print("title html =====>",title_html)
      title = self.clean_text(title_html)
      print(title)
