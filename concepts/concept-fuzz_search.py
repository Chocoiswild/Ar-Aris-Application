from fuzzysearch import find_near_matches

text = "Isni district, water supply will be interrupted from 1:15 p.m. to 9:00 p.m. in order to carry out damage restoration works on the water pipeline network along Tsalenjikhi N78: Tsalenjikhi N73-112 (all)."
street = "Tsalenjilfkdfgh"
matches = find_near_matches(street, text, max_l_dist=3)
print(matches)