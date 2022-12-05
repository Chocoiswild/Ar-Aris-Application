import requests
streets = ['Ikalto St.']
api_key = "677a90ba388d487ca1e1d14c2d12a16e"
# text = "ზესტაფონის ქ; შეს; ჩიხი"
found = []
for street in streets:
    street = street + ", Tbilisi"

    url = f"https://api.geoapify.com/v1/geocode/autocomplete?text={street}&type=street&format=json&apiKey={api_key}"
    response = requests.get(url)
    results = response.json()
    try:
        found
        s = {}
        s["search term"] = street
        s["street"] = {results["results"][0]["street"]}
        s["city"] = {results["results"][0]["city"]}
        s["suburb"] = {results["results"][0]["suburb"]}
        found.append(s)
        print(s)
    except:
        s = {}
        s["search term"] = street
        s["not found"] = "true"
        found.append(s)
        print(f"{street} not found")
          
# response = requests.get(url)
# print(response.json())



