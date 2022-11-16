import requests
from bs4 import BeautifulSoup

# Takes the URL from a page of disruptions and returns the path to the latest disruption
def latest_disruption_path(url: str):
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, "html.parser")
    path = soup.find("tr").find("a").get("href")
    
    return url + path



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
    
    
# Returns a list of unplanned water outages
def get_unplanned__gwp_disruptions():
    url = latest_disruption_path("https://www.gwp.ge/ka/gadaudebeli")
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, "html.parser")
    #extract a PageElement of only the disruptions, which are found in <div class="initial">
    disruptions = soup.find("div", "initial").find_all("li")
    #selects only the list tags, each <li> contains a separate disruption:
        #content with <p> tag is the description of the disruption
        #content with <strong> tag contains the streets affected
    return disruptions

# Returns a list of planned water outages
def get_planned_gwp_disruptions():
    url = latest_disruption_path("https://www.gwp.ge/ka/dagegmili")
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, "html.parser")
    planned_disruptions = soup.find("div", {"class" : lambda L: L and L.endswith('news-details')}).find_all("p")

    return planned_disruptions[:-3]


def main():
    unplanned_gwp_disruptions = get_unplanned__gwp_disruptions()
    planned_gwp_disruptions = get_planned_gwp_disruptions()
    for d in planned_gwp_disruptions:
        print(d.get_text())
    print("UNPLANNED")
    for d in unplanned_gwp_disruptions:
        print(d.get_text())


    # Ask the user for the street to check for disruptions
    streetname = "იყალთო"#input("Streetname: ")

    # Get the day's disruptions affecting all streets in Tbilisi
    # all_disruptions = get_disruptions()

    # Filter the disruptions by provided streetname
    filtered_disruptions = disruptions_by_street(unplanned_gwp_disruptions, streetname)

    if len(filtered_disruptions) == 0:
        print("Huzzah, You may bathe to your heart's content this day")
        # If no disruptions found, end program.
        # return
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
# First line of program check if datetime from header == datetime from last check
# only run program if not