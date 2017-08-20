import requests
from bs4 import BeautifulSoup

url = "http://careers.cineplex.com/jobs/7388300-serveurs-et-serveuses-vip-dynamiques-cinema-cineplex-odeon-brossard-et-vip"
r = requests.get(url)
c = r.content


def clean_html(soup):
	for i in soup.find_all(['script','span']):
		i.extract()
	for i in soup.find_all('div',class_="job-details__copy-apply"):
		i.extract()


soup = BeautifulSoup(c, "html.parser")
title = soup.find('h1')
address = title.find_next_sibling().get_text()
province = address.split(",")[-1].strip()


soup = soup.find_all('div', class_='job-details__copy')[0]
clean_html(soup)
soup.find('h1').extract()
job_discreption = str(soup)

