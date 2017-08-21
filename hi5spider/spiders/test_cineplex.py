import requests
from bs4 import BeautifulSoup
import re

url = "http://careers.cineplex.com/jobs/7527173-amusement-cashier-the-rec-room-deerfoot"
r = requests.get(url)
c = r.content


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
soup = BeautifulSoup(c, "html.parser")
title = soup.find('h1')
title_text = title.get_text()
address = title.find_next_sibling().get_text()
city, province = get_address(address)
address1 = re.search(r'Location:(.*)',address).group(1).strip()
soup = soup.find_all('div', class_='job-details__copy')[0]
clean_html(soup)
soup.find('h1').extract()
job_description = str(soup)
job_description = re.sub(r'(</br>)+</div>$',"",job_description)

print(job_description)