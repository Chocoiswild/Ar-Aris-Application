# Scrapes gwp and saves latest outages to a DB
# needs to scrape both planned and unplanned outages,
# so requires slightly different scripts for some steps

import requests
from bs4 import BeautifulSoup
from scraper_helpers import scrape_and_save, Database, Disruption

def latest_disruption_urls(url: str):
    """Extracts the latest disruption URLS"""
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, "html.parser")

    # Extract disruption paths to a list
    disruptions = []
    for path in soup.find('table', class_='table samushaoebi').findAll('a'):
        disruption_url = url + path.get('href')
        disruptions.append(disruption_url)

    return set(disruptions)



def get_planned_gwp_disruptions(url: str):
    """Scrapes a planned disruption URL,returns its text as string in a list"""
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, "html.parser")

    # extract a list of disruption PageElements
    disruptions = soup.find("div", {"class" : lambda L: L and L.endswith('news-details')}).select("p")

    # Extract the disruption announcement
    announcement = soup.select_one("p.media-heading").select_one("span").get_text()

    # extract the text from the paragraphs and join them together
    disruption_text = "\n".join([d.get_text() for d in disruptions[1:-3]])

    # Return a Disruption object from information gathered so far
    # Returned as a list item to work with Scrape and Save function
    return [Disruption(disruption_text.strip(), announcement.strip(), "Water", url)]



def get_unplanned_gwp_disruptions(url: str):
    """Scrapes an unplanned disruption URL, returns a list of unplanned disruption texts"""
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, "html.parser")
    
    # Get the announcement for all disruptions
    announcement = soup.select_one("p.media-heading").get_text()

    # extract a PageElement of only the disruptions, which are found in <div class="initial">
    # selects only the list tags, each <li> contains a separate disruption:
    disruptions = soup.select_one("div.initial").select("li")

    # Return Disruption objects for each separate disruption found
    return [Disruption(d.get_text().strip(), announcement.strip(), "Water", url)
            for d in disruptions]




def scrape_gwp(database: Database, users: list, urls: list):
    """Checks gwp for new planned and unplanned disruptions,
        and saves new disruptions to a database"""
    # Extract disruption urls
    planned_urls = latest_disruption_urls("https://www.gwp.ge/ka/dagegmili")
    unplanned_urls = latest_disruption_urls("https://www.gwp.ge/ka/gadaudebeli")

    # Scrape planned and unplanned URLS and save new disruptions to a DB
    scrape_and_save(database, planned_urls, get_planned_gwp_disruptions, users, urls)
    scrape_and_save(database, unplanned_urls, get_unplanned_gwp_disruptions, users, urls)



if __name__ == "__main__":
    pass