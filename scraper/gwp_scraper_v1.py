# Scrapes gwp and saves latest outages to a DB
# needs to scrape both planned and unplanned outages,
# so requires slightly different scripts for some steps

import requests
from bs4 import BeautifulSoup
from scraper_helpers import scrape_and_save

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

    return disruptions



def get_planned_gwp_disruptions(url: str):
    """Scrapes a planned disruption URL,returns its text as string in a list"""
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, "html.parser")

    # extract a list of disruption PageElements
    disruptions = soup.find("div", {"class" : lambda L: L and L.endswith('news-details')}).find_all("p")

    # extract the text, ignoring certain unneccesary items
    disruption_texts = [d.get_text() for d in disruptions[1:-3]]

    # Joins the disruption texts as it's all just one disruption
    # Returns it as a single list item for the scrape_and_save function to work
    return ["\n".join(disruption_texts)]



def get_unplanned_gwp_disruptions(url: str):
    """Scrapes an unplanned disruption URL, returns a list of unplanned disruption texts"""
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, "html.parser")
    
    # Get the announcement for all disruptions
    announcement = soup.find("p", class_="media-heading").get_text()

    # extract a PageElement of only the disruptions, which are found in <div class="initial">
    # selects only the list tags, each <li> contains a separate disruption:
    disruptions = soup.find("div", "initial").find_all("li")

    # store the text from disruptions to a variable
    disruption_texts = [announcement + "\n" + d.get_text() for d in disruptions]
    return disruption_texts



def scrape_gwp():
    """Checks gwp for new planned and unplanned disruptions,
        and saves new disruptions to a database"""
    # Extract disruption urls
    planned_urls = latest_disruption_urls("https://www.gwp.ge/ka/dagegmili")
    unplanned_urls = latest_disruption_urls("https://www.gwp.ge/ka/gadaudebeli")
    # Scrape planned and unplanned URLS and save new disruptions to a DB
    scrape_and_save(planned_urls, get_planned_gwp_disruptions)
    scrape_and_save(unplanned_urls, get_unplanned_gwp_disruptions)


if __name__ == "__main__":
    scrape_gwp()

