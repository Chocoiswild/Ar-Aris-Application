from telasi_scraper_v1 import scrape_telasi
from gwp_scraper_v1 import scrape_gwp
from scraper_helpers import get_urls, get_users
def scrape_utilities():
    # Get users and urls from database here, as it only needs to be done once per runtime
    db_users = get_users()
    db_urls = get_urls()
    scrape_gwp(db_users, db_urls)
    scrape_telasi(db_users, db_urls)


scrape_utilities()

# if __name__ == "__main__":
#     scrape_utlities()