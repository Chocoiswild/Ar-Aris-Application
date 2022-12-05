# Scrapes the Telasi electricty website for disruptions and saves new
# ones to a DB.
import requests, sqlite3
from bs4 import BeautifulSoup
from scraper_helpers import disruption_saved, save_to_db

def latest_disruption_urls(url: str):
    """Extracts the latest disruption URLS, 
    returns sorted lists of planned and unplanned URLS"""
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, "html.parser")

    # Extract disruptions to a list
    unplanned_urls = []
    planned_urls = []
    for d in soup.find("nav", class_="power-submenu").findAll("a"):
        # get url, remove duplicate substring from path
        path = d.get("href").replace("ge/power/", "")
        disruption_url = disruption_url = url + path

        # sort disruptions into planned and unplanned
        # არაგეგმური, არაგეგმიური  = unplanned
        if  "არაგეგმიური" in d.text or "არაგეგმური" in d.text:
            unplanned_urls.append(disruption_url)
        else:
            planned_urls.append(disruption_url)
    
    return unplanned_urls, planned_urls



def get_TEL_planned_disruptions(url: str):
    """Returns a list of planned disruptions"""
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, "html.parser")

    # Get the announcement for all disruptions from this URL
    announcement = soup.find("h3").get_text() + ".\n"

    # Extract the disruptions
    disruption_texts = []

    # Skip the last item in soup list as it's filler text
    for d in soup.find("div", class_="field-items").findAll("p")[:-1]:
        text = d.get_text()

        # Paragraphs over a certain length contain outages
        # other paragraphs are empty, or contain unneeded district names
        if len(text) > 50:
            disruption_texts.append(announcement + text)

    return  disruption_texts



def get_TEL_unplanned_disruptions(url: str):
    """Scrapes URL for the unplanned disruption, returns disruption text"""
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, "html.parser")

    # Extract text from page
    disruption = soup.find("div", class_="field-items").get_text()
    
    return disruption



def scrape_TEL_unplanned(urls: list):
    """Scrapes unplanned disruption urls and saves new disruptions to DB"""
    # Iterate over planned urls
    for url in urls:
        # If url is not found in db, scrape url
        if not disruption_saved(url):
            disruption = get_TEL_unplanned_disruptions(url)
            save_to_db(url, disruption)
            print(url)


def scrape_TEL_planned(urls: list):
    """Scrapes planned disruption urls and saves new disruptions to DB"""
    # Iterate over planned urls 
    for url in urls:
        # If URL is not found in db, scrape URL
        if not disruption_saved(url):
            for d in get_TEL_planned_disruptions(url):
                save_to_db(url, d)
                print(url)



def scrape_TEL():
    """Checks Telasi for new disruptions, and saves them to a db"""
    # Extract disruption URLs
    unplanned, planned = latest_disruption_urls("http://www.telasi.ge/ge/power")
    
    # Scrape planned and unplanned URLs and save new disruptions to the db
    scrape_TEL_planned(planned)
    scrape_TEL_unplanned(unplanned)


if __name__ == "__main__":
    scrape_TEL()