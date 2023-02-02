# Scrapes the telasi electricty website for disruptions and saves new
# ones to a DB.
import requests
from bs4 import BeautifulSoup

from scraper_helpers import scrape_and_save, Database

def latest_disruption_urls(url: str):
    """Extracts the latest planned and unplanned disruption URLS"""
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



def get_planned_tel_disruptions(url: str):
    """Returns a list of planned disruptions"""
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, "html.parser")

    # Get the announcement for all disruptions from this URL
    announcement = soup.find("h3").get_text()

    # Create empty list to store disruption texts
    disruption_texts = []

    # extract all paragraphs, these contain disruptions and suburb names (first <p> is always blank)
    paragraphs = soup.find("div", class_="field-items").findAll("p")[:-1]
    
    # Set suburb name variable
    suburb = paragraphs[0].get_text()

    # Loop through disruption paragraphs
    for p in paragraphs:
        # Extract the text from the paragraph
        text = p.get_text()

        # If the paragraph isn't empty, and shorter than 50, it's a suburb name
        if len(text) > 1 and len(text) < 50:
            # So set the new suburb name for following paragraphs
            suburb = text

        # Else if it's greater, it contains the disruption text
        elif len(text) > 50:
            # So create the full disruption text to save to db
            disruption_text = announcement + "\n" + suburb + "\n" + text
            disruption_texts.append(disruption_text)

    return  disruption_texts



def get_unplanned_tel_disruptions(url: str):
    """Scrapes URL for the unplanned disruption, returns disruption text"""
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, "html.parser")

    # Extract text from page
    disruption = [soup.find("div", class_="field-items").get_text()]
    
    return disruption



def scrape_telasi(database: Database, users: list, urls: list):
    """Checks telasi for new disruptions, and saves them to a db"""
    # Extract disruption URLs
    unplanned, planned = latest_disruption_urls("http://www.telasi.ge/ge/power")
    # Scrape planned and unplanned URLs and save new disruptions to the db
    scrape_and_save(database, planned, get_planned_tel_disruptions, users, urls)
    scrape_and_save(database, unplanned, get_unplanned_tel_disruptions, users, urls)


if __name__ == "__main__":
    scrape_telasi()

