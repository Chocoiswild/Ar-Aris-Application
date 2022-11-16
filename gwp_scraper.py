# Scrapes GWP and saves latest outages to a DB
# needs to scrape both planned and unplanned outages,
# so requires slightly different scripts for some steps

import requests
from bs4 import BeautifulSoup
from scraper_helpers import disruption_saved, save_to_db

def latest_disruption_urls(url: str):
    """Gets the urls of the latest disruptions"""
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
    """Returns a planned disruption in string format"""
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, "html.parser")

    # extract a list of disruption PageElements
    disruptions = soup.find("div", {"class" : lambda L: L and L.endswith('news-details')}).find_all("p")

    # extract the text, ignoring certain unneccesary items
    disruption_texts = [d.get_text() for d in disruptions[1:-3]]
    # joins the disruption texts as it's all just one disruption
    return "\n".join(disruption_texts)



def get_unplanned_gwp_disruptions(url: str):
    """Returns a list of unplanned water outages"""
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, "html.parser")

    # extract a PageElement of only the disruptions, which are found in <div class="initial">
    # selects only the list tags, each <li> contains a separate disruption:
    disruptions = soup.find("div", "initial").find_all("li")

    # store the text from disruptions to a variable
    disruption_texts = [d.get_text() for d in disruptions]
    return disruption_texts



def scrape_unplanned_GWP():
    # get url of latest  unplanned disruption
    unplanned_urls = latest_disruption_urls("https://www.gwp.ge/ka/gadaudebeli")

    # Check if the disruptions have already been saved to the db
    for url in unplanned_urls:
        if not disruption_saved(url):
            # scrape the page for disruptions, save the data
            unplanned_disruptions = get_unplanned_gwp_disruptions(url)
            for d in unplanned_disruptions:
                save_to_db(url, d)
                print(url)



def scrape_planned_GWP():
    # get url of latest planned disruption
    planned_urls = latest_disruption_urls("https://www.gwp.ge/ka/dagegmili")

    # Check if the disruptions have already been saved to the DB
    for url in planned_urls:
        if not disruption_saved(url):
            # scrape the page, save the data
            planned_disruption = get_planned_gwp_disruptions(url)
            save_to_db(url, planned_disruption)
            print(url)


def scrape_GWP():
    """Checks GWP for new planned and unplanned disruptions,
        and saves new disruptions to a database"""
    # Scrape planned and unplanned URLS and save new disruptions to a DB
    scrape_unplanned_GWP()
    scrape_planned_GWP()


if __name__ == "__main__":
    scrape_GWP()

