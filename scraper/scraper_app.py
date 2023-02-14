from telasi_scraper_v1 import scrape_telasi
from gwp_scraper_v1 import scrape_gwp
from scraper_helpers import get_urls, get_users, Database
import time, schedule
def scrape_utilities():
    print(20*"*")
    print('Starting up webscraper''\n')
    # Establish connection to database through a Database object
    mydb = Database()
    users = get_users(mydb)
    db_urls = get_urls(mydb)
    print("Scraping GWP")
    scrape_gwp(mydb, users, db_urls)
    print("Scraping Telasi")
    scrape_telasi(mydb, users, db_urls)
    print()
    print('Scraping completed''\n')
    mydb.close_connection()
    print()

# Run script every ten minutes
schedule.every(10).minutes.do(scrape_utilities)


while 1:
    schedule.run_pending()
    n = schedule.idle_seconds()
    if n > 0:
        time.sleep(n)
    schedule.run_pending()


if __name__ == "__main__":
    scrape_utilities()