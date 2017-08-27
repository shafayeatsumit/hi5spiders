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
    name = "testcentennial"
    def __init__(self, *args, **kwargs):     
        self.start_url = 'http://db2.centennialcollege.ca/ce/certdetail.php?CertificateCode=2470'
        self.root_url = 'http://db2.centennialcollege.ca/ce/'
    def start_requests(self):
        yield SplashRequest(url= self.start_url , 
                callback = self.parse_detail,
                endpoint='execute',
                args={
                    'lua_source': script_first_page,
                    'timeout': 90
                }            
              )
    def clean_text(self,raw_html):
      return BeautifulSoup(raw_html, "html.parser").text   

    def link_fixer(self,soup):
        #fixes the relative path problem of image and
        try: 
          for link in soup.find_all("a"):
              link_text = link['href']
              if link_text.startswith('coursedetail.php'):
                  link['href'] = link['href'].replace(link['href'], self.root_url+link['href'])
        except Exception as e:
          print(e)
        return soup  

    def description_parser(self, soup):
      detail = soup.find("table", class_="collapsible course")
      for td in detail.find_all('td',class_='gray'):
        td.string = "<b>%s</b>"%td.string
      result = str(detail).replace('&lt;b&gt;',"<b>").replace('&lt;/b&gt;',"</b>")
      soup_manadatory_course = soup.find('h2',string="Mandatory Courses")
      soup_elective_course = soup.find('h2',string="Elective Courses")
      
      if soup_manadatory_course:
        mandatory_course = str(soup_manadatory_course)
        mandatory_course_table = self.link_fixer(soup_manadatory_course.find_next_sibling('table'))
        result = result + "<br>"  +mandatory_course + str(mandatory_course_table)

      if soup_elective_course:
        elective_course = str(soup_elective_course)
        elective_course_table = self.link_fixer(soup_elective_course.find_next_sibling('table'))
        result = result + "<br>" + elective_course + str(elective_course_table)

      return result.replace("\n","").replace("\r","").replace("\t","")

    def parse_detail(self, response):
      soup = BeautifulSoup(response.body,"html.parser")
      title = soup.find('td',string="Certificate Name").find_next_sibling('td').text
      if soup.find('td',string="Contact E-mail"):
        email =  soup.find('td',string="Contact E-mail").find_next_sibling('td').find('a').text
      else:
        email = "N/A"
      if soup.find('td',string="Contact Telephone"):
        phone = soup.find('td',string="Contact Telephone").find_next_sibling('td').text
      else:
        phone = "N/A"
      detail = self.description_parser(soup)

      data = {
          "title" : title,
          "email" : email,
          "phone" : phone,
          "description" : detail,
          "web_link" : response.url,
          "website" : "centennial"
      }
      print(data)
   
   
  

"""
soup.find('h2',string="Mandatory Courses")
soup.find('h2',string="Elective Courses").find_next_sibling('table')
soup.find('td',string="Contact Telephone").find_next_sibling('td')
soup.find('td',string="Contact Telephone").find_next_sibling('td')
Contact E-mail
soup.find('td',string="Contact E-mail").find_next_sibling('td').find('a').text

soup.find('td',string="Certificate Name").find_next_sibling('td').get_text()

#main description table
soup.find("table", class_="collapsible course")

#finds all <td> inside main description
for i in m.find_all('td',class_='gray'):
  text = i.get_text()
  i.string = i.string("<b>%s</b>",text)
  
soup = BeautifulSoup(response.body,"html.parser")   
"""