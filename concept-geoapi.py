import requests
streets = [
        'Amiranashvili Petre St.', 'Baramidze St.', 'Gamkrelidze St.', 'Garikuli St.', 'Gmir Kursantta St.', 'Guramishvili Ave. #35-41', 'Veliscikhi St.', 'Sea district. (Temka) 9th, 10th, 10a, 10th square', 'Tavadze Ferdinandi St.', 'Iremashvili St.', 'Mariam Garikuli St.', 'Maghalashvili St.', 'Nikortsminda St.', 'Sadmeli St.', 
        'Samotosdametsamete St.', 'Tkibuli St.', 'Ureki St. ; Dead end', 'Shatili st. ', 'Tsodniskar St.', 'Khevdzmari Das. (Temka) 4-sq. ', 'Khevdzmari Das. (Temka) 9-sq. 10-kv; 10-a sq; 10-b sq.', 'Khvanchkari St.', 'Dumbadze Ave.', 'Mukhiani Das. 1,2,3,4-a,4-b m/r.', 'Noneshvili i. (Mukhian sister) St.', 'Antonovskaya St.', 'Asatiani Mikheili St.', 'Beritashvili St.', 'Buachidze T. St., Gabashvili Gigo Square; St.', 'Delis St. 1,2,3 St.; dead ends; Square', 'Vazha Pshavela 1-kwt.', 'Vazha Pshavela Ave., 2nd floor', 
        'Vazha Pshavela Ave. #33-51, 26-66', 'Vazha Pshavela Alley', 'Zakariadze St.', 'Zemo Vedzesi Das.', 'Tavadze St.', 'Tamarashvili St. #13_21, 6, 10', 'Ionavakeli St.', 'Kartozia St.', 'Lisi Lake, Partizantha Park', 'Megreladze St.; Add.', 'Nutsubidze st. #1-77, 2-60', 'University st. #2,3,6', 'Kazbegi Ave. #27-57; 18-46', 'Chikovani v. St.', 'Akuri St.', 'Aleksidze Merabi St. Corp. #1, 2, 3, 4', 'Aslanidi St.', 'Bakuriani St.',
        'Bakurtsikhi St.', 'Balanchivadze St.', 'Bakhtrioni St.', 'Bendeliani Z. St.', 'Berbuki St.; Add.', 'Bolkvadze z. St.', 'Bochorishvili Vakhtangi St.', 'Gmirta Medani', 'Dolidze Viktori St.', 
        'Iosebidze St.;1,3,6/3', 'Yoseliani st.', 'Ikaltos st.; mountain Alleys', 'Kodori St.', 
        ]
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



