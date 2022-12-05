from telasi_scraper_v1 import scrape_telasi
from gwp_scraper_v1 import scrape_gwp
def scrape_utilities():
    scrape_gwp()
    scrape_telasi()


scrape_utilities()

# if __name__ == "__main__":
#     scrape_utlities()