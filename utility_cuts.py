import requests
from bs4 import BeautifulSoup


def latest_disruption():
    url = "https://www.gwp.ge/ka/gadaudebeli"
    response = requests.get(url)
    text = response.text
    gwp_data = BeautifulSoup(text, "html.parser")

    #get paths to disruptions
    disruptions = []
    for link in gwp_data.find_all("a"):
        url = link.get("href")
        if "ka/gadaudebeli" in url:
            disruptions.append(url)

    #disruption is 4th listed (today, need to check regularly to confirm)
    gwp_url = "https://www.gwp.ge/"
    disruption_url = gwp_url + disruptions[3]

    return disruption_url

#A simple function to save the disruptions to a new file
def save_to_file(disruption_data):
    with open("disruption.txt", "w", encoding="utf-8") as new_file:
        for d in disruption_data:
            new_file.write(d.get_text())

# This gets the disruptions affecting the given street, and saves them to file
def disruptions_by_street(disruption_text, streetname: str):
    disruptions = []
    for d in disruption_text:
        if streetname in d.get_text():
            disruptions.append(d)

    return disruptions
    
    

def get_disruptions():
    url = latest_disruption()
    response = requests.get(url)
    text = response.text
    GWP_soup = BeautifulSoup(text, "html.parser")
    #extract a PageElement of only the disruptions, which are found in <div class="initial">
    disruptions_all = GWP_soup.find("div", "initial")
    #selects only the list tags, each <li> contains a separate disruption:
        #content with <p> tag is the description of the disruption
        #content with <strong> tag contains the streets affected
    disruptions_all_text = disruptions_all.find_all("li")

    return disruptions_all_text
    



def main():
    # Ask the user for the street to check for disruptions
    streetname = "იყალთო"#input("Streetname: ")

    # Get the day's disruptions affecting all streets in Tbilisi
    all_disruptions = get_disruptions()

    # Filter the disruptions by provided streetname
    filtered_disruptions = disruptions_by_street(all_disruptions, streetname)

    if len(filtered_disruptions) == 0:
        print("Huzzah, You may bathe to your heart's content this day")
        # If no disruptions found, end program.
        return
    elif len(filtered_disruptions) == 1:
        print("1 disruption found")
    else:
        print(f"{len(filtered_disruptions)} disruptions found")
    # Saves disruptions to disruptions.txt and announce when done.
    save_to_file(filtered_disruptions)
    print("Disruptions saved to disruptions.txt")


if __name__ == "__main__":
    main()



##### NOTES FOR NEXT TIME #####
# STREETNAME:
# streetname is hardcoded to "იყალთო" (Ikalto) for testing purposes, but it can ask for user input
# maybe take user's streetname input and plug it into ge.translit to get Ge text for searching within disruptions?
# 
# TRANSLATION:
# need to implement a feature to translate the disruption text to English
#
# FURTHER IMPLEMENTATION:
# Build a GUI/simple website to run from
# Turn the program into a bot that runs X times/day and sends you updates

# NOTE - 
