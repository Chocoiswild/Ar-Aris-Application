from telasi_scraper_v1 import scrape_telasi
from gwp_scraper_v1 import scrape_gwp
from scraper_helpers import get_urls, get_users
import time, schedule
def scrape_utilities():
    # Get users and urls from database here, as it only needs to be done once per runtime
    print('Starting up webscraper''\n')
    db_users = get_users()
    db_urls = get_urls()
    scrape_gwp(db_users, db_urls)
    scrape_telasi(db_users, db_urls)
    print()
    print('Scraping completed''\n')
    print()

# Run script every hour
schedule.every(1).hours.do(scrape_utilities)


while 1:
    schedule.run_pending()
    n = schedule.idle_seconds()
    if n > 0:
        time.sleep(n)
    schedule.run_pending()


# scrape_utilities()

# if __name__ == "__main__":
#     scrape_utlities()