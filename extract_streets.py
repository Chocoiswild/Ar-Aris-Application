"""Used to extract Tbilisi's street names from https://www.getpostalcodes.com/georgia/pplace-tbilisi-tbilisi/"""


from transliterate import get_translit_function
import requests
from bs4 import BeautifulSoup
streets = []
anomalies = []
for i in range(1, 50):
        
    url = "https://www.getpostalcodes.com/georgia/pplace-tbilisi-tbilisi/?page=" + str(i)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}

    soup = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser')

    table = soup.findAll("tbody")[1]
    for row in table.findAll("a"):
        text = row.get_text()
        if "Tbilisi" in text and len(text) > 7:
            streets.append(text)
        # bad way of extracting street names
        # if "street" in text:
        #     split = text.split(" ")
        #     if "street" in text:
        #         streets.append(" ".join(split[0:-2]))
        #     else:
        #         anomalies.append(" ".join(split[0:-1]))
        # else:
        #     anomalies.append(text)
            # elif len(split) == 4:
            #     streets.append(" ".join(split[0:2]))
            # else:
            #     anomalies.append(" ".join(split))
with open("streets.csv", "w") as streets_csv:
    for s in streets[0:11]:

        print(s)
        street = s.split(",")
        streets_csv.write(street[0] + ", ")

# print(streets[0:11])
print(len(streets))
print(len(anomalies))


# translit_ka = get_translit_function("ka")
# for street in streets[0:11]:
#     print(translit_ka(street))