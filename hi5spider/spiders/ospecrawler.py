# -*- coding: utf-8 -*-

import scrapy
import json
from scrapy_splash import SplashRequest
from datetime import datetime
from bs4 import BeautifulSoup

script_detail_page = """
function main(splash)
    assert(splash:go(splash.args.url))
    local get_info = splash:jsfunc([[
    function () {
    var course_detail = document.getElementById('note').innerHTML;
    return course_detail;
    }
    ]])    
    function wait_for(splash, condition)
        while not condition() do
            splash:wait(0.05)
        end
    end

    wait_for(splash, function()
        return splash:evaljs("document.getElementById('note') !== null")
    end)
    return {
        data = get_info(),
        contact_info = splash:evaljs("document.getElementById('contact').innerText"),
        title =  splash:evaljs("document.getElementsByClassName('eventTitle')[0].innerText"),
        event_date = splash:evaljs("document.getElementById('startEndDates').innerText"),
        location = splash:evaljs("document.getElementById('location').innerText")
    }
end
"""

lua_first_page = """
function main(splash)
    assert(splash:go(splash.args.url))  
    function wait_for(splash, condition)
        while not condition() do
            splash:wait(0.05)
        end
    end

    wait_for(splash, function()
        return splash:evaljs("document.getElementById('1') !== null")
    end)
    return {
    html = splash:html()
  }
end
"""
class OspeSpider(scrapy.Spider):
    name = "ospespider"
    def __init__(self, *args, **kwargs):     
        self.root_url = 'https://www.ospe.on.ca/Courses'
    def start_requests(self):
            yield SplashRequest('https://www.ospe.on.ca/Courses', self.parse,
                endpoint='execute',
                args={
                    'lua_source': lua_first_page,
                    'timeout': 90
                }
            )        

    def parse(self, response):
        courses_url = response.xpath('//td/a/@href').extract()
        for url in courses_url:
            print ("url ==>",url)
            current_url = self.root_url+url
            yield SplashRequest(current_url, self.parse_detail,
                endpoint='execute',
                args={
                    'lua_source': script_detail_page,
                    'timeout': 90
                }
            )        

    def parse_detail(self, response):
        #response decoded
        rs = response.data
        print("start detail parsing")
        def date_parser(event_date):
            event_date = event_date.split("-")
            if len(event_date)==2:
                start_date = datetime.strptime(event_date[0].strip(),'%B %d, %Y')
                end_date = datetime.strptime(event_date[1].strip(),'%B %d, %Y')
                return start_date, end_date
            if len(event_date)==1:
                start_date = datetime.strptime(event_date[0].strip(),'%B %d, %Y')
                end_date = None
                return start_date, end_date
            else:
                return None , None

        def link_fixer(soup):
            #fixes the relative path problem of image and 
            root_url = "https://www.ospe.on.ca/"
            for link in soup.find_all(["a","img"]):
                try:
                    link_text = link['href']
                    if link_text.startswith('/'):
                        link['href'] = link['href'].replace(link['href'], root_url+link['href'])
                except:
                    link_text = link['src']
                    if link_text.startswith('/'):
                        link['src'] = link['src'].replace(link['src'], root_url+link['src'])
            return soup  
        event_date = date_parser(rs["event_date"])
        data = {
            "title" : rs["title"],
            "start_date" : event_date[0],
            "end_date" : event_date[1],
            "contact" : rs["contact_info"],
            "location" : rs["location"],
            "description" : link_fixer(BeautifulSoup(rs["data"], "html.parser")),
            "web_link" : response.url,
            "website" : "ospe"
        }
        insert_ospe_course(data)       
        
