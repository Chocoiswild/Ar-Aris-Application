import requests
from bs4 import BeautifulSoup
import time
def latest_disruption():
    url = "https://www.gwp.ge/ka/gadaudebeli"
    response = requests.get(url)
    text = response.text
    gwp_data = BeautifulSoup(text, "html.parser")

    #get paths to disruptions
    disruptions = []
    for link in gwp_data.find_all("a"):
        url = link.get("href")
        if "en/gadaudebeli" in url:
            disruptions.append(url)

    #disruption is 4th listed (today, need to check regularly to confirm)
    gwp_url = "https://www.gwp.ge/"
    disruption_url = gwp_url + disruptions[3]
    return disruption_url

def disruption_text():
    url = latest_disruption()
    response = requests.get(url)
    text = response.text
    disruption_data = BeautifulSoup(text, "html.parser")
    print(disruption_data.get_text())

disruption_text()


#test change#