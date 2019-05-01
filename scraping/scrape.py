import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

def scrape():
    index_url = "https://www.conservapedia.com/Special:AllPages"
    index_page = requests.get(index_url)
    index_soup = BeautifulSoup(index_page.text, "html.parser")
    #print(index_soup)
    link_sec = index_soup.find(class_="mw-allpages-chunk")
    link_list = link_sec.find_all("a")
    #print(link_list)
    
    f = csv.writer(open("conservapedia.csv", "w"))
    f.writerow(["page_title","page_link","page_contents"])
    site_dict = {}
    for link in link_list:
        page_title = link.contents[0]
        page_link = "https://www.conservapedia.com"+link.get("href")
        site_dict[page_title] = page_link
        
    for k,v in site_dict.items():
        page = requests.get(v)
        page_soup = BeautifulSoup(page.text, "html.parser")
        page_body = page_soup.find(id="content")
        page_content = page_body.find("div", class_="mw-content-ltr")
        text = page_content.get_text()
        f.writerow([k,v,text])
        
    f.close()
    return

scrape()