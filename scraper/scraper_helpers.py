# Helper functions for the Ar Aris scraper.

import  smtplib, ssl, psycopg2
from deep_translator import GoogleTranslator
from fuzzysearch import find_near_matches
from email.message import EmailMessage
from decouple import config

def get_urls():
    """ Gets all URLS from DB """
    # set the command for searching for matching disruptions
    sql = "SELECT url FROM disruptions"
    urls = []
    con = None
    # Attempt to find matches
    try:
        con = psycopg2.connect(
            host=config('PGHOST', default=''),
            database=config('PGDATABASE', default=''),
            user=config('PGUSER', default=''),
            password=config('PGPASSWORD', default=''),
            port=config('PGPORT', default=''),
            )

        # establish cursor
        c = con.cursor()

        # get all urls
        c.execute(sql)
        url_tuples = c.fetchall()
        for u in url_tuples:
            urls.append(u[0])
        # close connections
        c.close()
        con.close()
        return urls
    # If error, print it
    except(Exception, psycopg2.DatabaseError) as error:
        print('get urls fail')
        print(error)
        if con is not None:
            con.close()

def save_to_db(url: str, disruption_text: str):
    """Saves a disruption to the POSTGRESQL server"""
    print("saving disruption to db")
    # Connection details are kept secret with Decoupler, 
    # kept in .env file and not uploaded to git

    sql = "INSERT INTO disruptions (url, disruption) VALUES (%s, %s)"
    con = None
    try:
        con = psycopg2.connect(
            host=config('PGHOST', default=''),
            database=config('PGDATABASE', default=''),
            user=config('PGUSER', default=''),
            password=config('PGPASSWORD', default=''),
            port=config('PGPORT', default=''),
            )
        c = con.cursor()    
        # enter into db
        c.execute(sql, (url, disruption_text))
        # commit to db
        con.commit()
        # close the cursor
        c.close()
        # close the db

    except(Exception, psycopg2.DatabaseError) as error:
        print('save to db fail')
        print(error)
    finally:
        if con is not None:
            con.close()


def translate_disruption(disruption_text):
    """Translates text piecemeal if over character limit, otherwise just translates"""
    print("translating disruption")
    translator = GoogleTranslator(source='auto', target='english')
    try:
        if len(disruption_text) > 2000:
            # Translation setup for Telasi
            if "ელ.მომარაგების" in disruption_text or "ელექტრო" in disruption_text:
                # Split disruption_text into paragraphs
                paragraphs = disruption_text.split("\n")
                # Create list to store translated paragraphs
                translated_paragraphs = []
                # Iterate over paragraphs
                for p in paragraphs:
                    # Split paragraphs into sentences
                    sentences = p.split(". ")
                    # Translated sentences
                    translated_sentences = translator.translate_batch(sentences)
                    # Join translated sentences together to form translated paragraph
                    translated_p = "".join(translated_sentences)
                    # Add translated paragraph to list
                    translated_paragraphs.append(translated_p)
                # Join translated paragraphs together to form translated disruption_text
                translated_disruption_text = "\n\n".join(translated_paragraphs)

            else:
                # Translation setup for GWP
                text = disruption_text.split(", ")
                chunks = [text[x:x+60] for x in range(0, len(text), 60)] # split list into sublists of 250 words each
                translated_disruption_text = ""
                for chunk in chunks:
                    joined = ", ".join(chunk)
                    
                    translated_disruption_text += (translator.translate(joined))

        else: 
            translated_disruption_text = translator.translate(disruption_text)

        return translated_disruption_text    
    except:
        print(disruption_text)

            

def scrape_and_save(disruption_urls: list, disruption_func, users: list, urls: list):
    """Scrapes disruption urls, translates them, and saves new disruptions to DB"""
    print("Scraping urls...")
    # Get all users from db to prevent doubling up later
    # Iterate over planned urls 
    for url in disruption_urls:
        # If URL is not found in db, scrape URL
        # print(url)
        if url not in urls:
            print("url not yet saved")
            # Iterate over all disruptions found at target URL
            for origin_text in disruption_func(url):
                
                # Translate text to English
                translated_text = translate_disruption(origin_text)

                # Find users affected by disruption
                affected_users = find_affected_users(translated_text, users)

                # Email affected users

                for user in affected_users:
                    email_affected_user(user)

                # Save translated disruption text to database
                save_to_db(url, translated_text)


class User:
    """A class to contain user information """
    def __init__(self, name, email, street, district):
        self.name = name
        self.email = email
        # The full street name, e.g. Smith St.
        self.street = street
        self.district = district
        # Just the name of the street itself, e.g. Smith, not Smith st.
        self.streetname = " ".join(street.split(" ")[:-1])

        

        # To be assigned to user if disruption found
        self.disruption_text = ""

        # A template for generating email text
        self.email_text = "Hi {name},\n\nYour street has been included in a list of streets affected by a utility disruption in Tbilisi.\nPlease see the following announcement for more details:\n\n{disruption_text}\n\n\nIf you believe you have recieved this email in error, or your street is not included in this disruption, please reply to this email."

    def generate_email_text(self):
        return self.email_text.format(name=self.name, disruption_text=self.disruption_text)


def get_users():
    """ Gets a list of all users from the DB """
    # Connect to the user DB
    sql = "SELECT * FROM users"
    con = None
    try:
        con = psycopg2.connect(
            host=config('PGHOST', default=''),
            database=config('PGDATABASE', default=''),
            user=config('PGUSER', default=''),
            password=config('PGPASSWORD', default=''),
            port=config('PGPORT', default=''),
            )
        c = con.cursor()    
        # select all users
        c.execute(sql)
        users = c.fetchall()
        return users
    except(Exception, psycopg2.DatabaseError) as error:
        print('get users fail')
        print(error)
    finally:
        if con is not None:
            con.close()

    


# Iterates over users in DB and emails them if the disruption affects them
def find_affected_users(disruption_text: str, users: list):
    """Iterates over users in DB, returns User objects of affected users."""
    print('finding affected users')
    affected_users = []
    for u in users:
        user_affected = False
        # Users are stored in db as (name, email, street, district)
        user = User(u[1], u[2], u[3], u[4])
        # Use fuzzysearch to find matches to district and streetname in disruption
        # Filter by district due to duplicate street names
        if find_near_matches(user.district, disruption_text, max_l_dist=2):
            # Tbilisi streetnames are a mess, and they're not always written in full in disruptions
            street_parts = user.streetname.split(" ")
            # If the street has two names (e.g. Ivane Machabeli), it is known by second name
            # Filtering by district should avoid any complications filtering like this may turn up
            if len(street_parts) == 2:
                if find_near_matches(street_parts[1], disruption_text, max_l_dist=2):
                    user_affected = True
            # Any other streetname can be searched in full
            elif find_near_matches(user.streetname, disruption_text, max_l_dist=2):
                    user_affected = True

        # if user is affected, set disruption text to User object
        if user_affected == True:
            user.disruption_text = disruption_text
            # Add User to affected user list
            affected_users.append(user)

    return affected_users



def email_affected_user(affected_user: User):
    """ Emails the disruption notification to affected users """
    print('emailing affected users')
    # define settings
    port = 465
    email_sender = config('EMAIL_USER', default='')
    email_password = config('EMAIL_PW', default='')

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        # Login to the server
        server.login(email_sender, email_password)

        # Generate email message
        message = EmailMessage()
        message.set_content(affected_user.generate_email_text())
        message["subject"] = "Your street has a utility disruption!"
        message["from"] = email_sender
        message["to"] = affected_user.email

        # Send email
        server.send_message(message)
        # Cut server connection
        server.close()
    

if __name__ == "__main__":
    print(get_urls())
