from gwp_scraper_v1.0 import scrape_gwp
import gwp_scraper_v1.0 
from telasi_scraper_v1.0 import scrape_telasi

def scrape_utlities():
    scrape_GWP()
    scrape_TEL()

if __name__ == "__main__":
    scrape_utlities()