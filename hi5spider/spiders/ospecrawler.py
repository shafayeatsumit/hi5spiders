# -*- coding: utf-8 -*-

import scrapy
import json
from scrapy_splash import SplashRequest

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

script_first_page = """
function main(splash)
    assert(splash:go(splash.args.url))  
    function wait_for(splash, condition)
        while not condition() do
            splash:wait(0.05)
        end
    end

    wait_for(splash, function()
        return splash:evaljs("document.getElementById('0') !== null")
    end)
    return splash:html()
end
"""
class OspeSpider(scrapy.Spider):
    name = "ospespider"
    def __init__(self, *args, **kwargs):     
        self.root_url = 'https://www.ospe.on.ca/courses'
    def start_requests(self):
        yield SplashRequest(url= self.root_url , 
               callback = self.parse,
               endpoint='execute',
                args={
                    'lua_source': script_first_page,
                    'timeout': 90
                }            
            )

    def parse(self, response):
        
        courses_url = response.xpath('//td/a/@href').extract()
        for url in courses_url:
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
        def link_fixer(soup):
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

        data = {
            "title" : rs["title"],
            "event_date" : rs["event_date"],
            "contact" : rs["contact_info"],
            "location" : rs["location"],
            "description" : link_fixer(rs["data"])
        }
        print(data)