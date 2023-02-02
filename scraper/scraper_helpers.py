# Helper functions for the Ar Aris scraper.

import  smtplib, ssl, psycopg2
from deep_translator import GoogleTranslator
from fuzzysearch import find_near_matches
from email.message import EmailMessage
from decouple import config
import hashlib

class User:
    """A class for creating User objects"""
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
        return self.email_text.format(name=self.name, 
                                    disruption_text=self.disruption_text)



class Database():
    """Connects and handles the various SQL queries"""
    def __init__(self):
        # connect to DB
        try:
            self.con = psycopg2.connect(
                host=config('PGHOST', default=''),
                database=config('PGDATABASE', default=''),
                user=config('PGUSER', default=''),
                password=config('PGPASSWORD', default=''),
                port=config('PGPORT', default=''),
                )
        except(Exception, psycopg2.DatabaseError) as error:
            print('failed to connect to database')
            print(error)

    def fetch(self, query, parameters):
        with self.con.cursor() as c:
            c.execute(query, (parameters))
            return c.fetchall()

    def save(self, query, parameters):
        with self.con.cursor() as c:
            c.execute(query, (parameters))
        self.con.commit()
    
    def close_connection(self):
        self.con.close()



def get_users(database: Database):
    """Retrieves a list of all users from the DB"""
    sql = "SELECT * FROM users"
    users = database.fetch(sql, ())
    return users



def get_urls(database: Database):
    """Retrieves and returns a list of dictionaries of URLS 
        and the hashes of the disruptions found at each URL """
    sql = "SELECT url, hash FROM urls"
    urls = []
    results = database.fetch(sql, ())
    # Create dict objects, add them to list
    for u in results:
        url = u[0]
        hash = u[1]
        urls.append({'url': url, 'hash': hash})
    return urls



def get_disruption_hashes(database: Database, url: str):
    """Gets all disruption hashes from the database's disruptions table
        which match the given url"""
    hashes = []
    sql = "SELECT hash FROM disruptions WHERE url LIKE (%s)"
    hash_tuples = database.fetch(sql, (url,))
    # hashes tuples are returned as (hash,)
    for h in hash_tuples:
        hashes.append(h[0])
    return hashes        



def save_disruption(database: Database, url: str, 
                    disruption_text: str, hash: str):
    """Saves a disruption to the POSTGRESQL database"""
    print("saving new disruption to db")
    sql = "INSERT INTO disruptions (url, text, hash) VALUES (%s, %s, %s)"
    database.save(sql, (url, disruption_text, hash))



def save_url(database: Database, url: str, hash: str, url_exists: bool):
    """Saves a url and the hash of its disruptions to the database"""
    # if the url exists, replace the hash with the new one.
    if url_exists:
        print("updating hash")
        sql = "UPDATE urls SET hash=(%s) WHERE url like (%s)"
    # Otherwise create a new DB entry
    else:
        print("saving url to db")
        sql = "INSERT INTO urls (hash, url) VALUES (%s, %s)"
    database.save(sql, (hash, url))



def translate_disruption(disruption_text: str):
    """Translates given text from Georgian to English"""
    print("translating disruption")
    # Initiate the translator object here so it's done just once
    translator = GoogleTranslator(source='auto', target='english')
    # Translator can only handle so many characters at once. 
    if len(disruption_text) > 2000:
        # Telasi and GWP's texts are formatted differently, 
        # so they need to be broken up in different ways for translation.
        # For Telasi
        if "ელ.მომარაგების" in disruption_text or "ელექტრო" in disruption_text:
            # Telasi texts are often long, so break into paragraphs
            # and then translate sentences within paragraphs.
            paragraphs = disruption_text.split("\n")
            translated_paragraphs = []
            for p in paragraphs:
                # Then into sentences, then translate
                sentences = p.split(". ")
                translated_sentences = translator.translate_batch(sentences)
                translated_p = "".join(translated_sentences)
                translated_paragraphs.append(translated_p)
            # Text is joined together at end
            translated_disruption_text = "\n\n".join(translated_paragraphs)

        else:
            # For GWP
            text = disruption_text.split(", ")
            # GWP texts are not as long, and their formatting allows a text to
            # be split into groups of 60 words which are translated.
            chunks = [text[x:x+60] for x in range(0, len(text), 60)] 
            translated_disruption_text = ""
            for chunk in chunks:
                joined = ", ".join(chunk)
                translated_disruption_text += (translator.translate(joined))
    # If the text is short enough it's translated in one go.
    else: 
        translated_disruption_text = translator.translate(disruption_text)

    return translated_disruption_text    



def generate_hash(string: str):
    """A simple function to generate and return hashes from strings"""
    bytestring = bytes(string, 'utf-8')
    m = hashlib.sha256()
    m.update(bytestring)
    
    return m.hexdigest()



def find_affected_users(disruption_text: str, users: list):
    """Iterates over users in DB, returns User objects of affected users."""
    print('finding affected users')
    affected_users = []
    for u in users:
        user_affected = False
        # Users are stored in db as (name, email, street, district)
        user = User(u[1], u[2], u[3], u[4])
        # Use fuzzysearch to find matches to district 
        # and streetname in disruption
        # Filter by district due to duplicate street names
        if find_near_matches(user.district, disruption_text, max_l_dist=2):
            # Tbilisi streetnames are a mess, and they're not 
            # always written in full in disruptions
            street_parts = user.streetname.split(" ")
            # If the street has two names (e.g. Ivane Machabeli), 
            # it is known by second name.
            # Filtering by district should avoid any complications 
            # filtering like this may turn up
            if len(street_parts) == 2:
                if find_near_matches(street_parts[1], disruption_text, 
                                     max_l_dist=2):
                    user_affected = True
            # Any other streetname can be searched in full
            elif find_near_matches(user.streetname, disruption_text, 
                                   max_l_dist=2):
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



def process_disruptions(database: Database, url: str, disruptions: list, 
                        users: list, new_url: bool):
    """Iterates over disruptions. If a new disruption is found, 
        save it to the database and email any affected users."""
    print("processing disruptions")
    for d in disruptions:
        hash = generate_hash(d)
        add_disruption = True

        # If False, the URL exists in the DB and the page has been updated
        if new_url == False:
            # If the hash exists in the DB, the disruption hasn't been changed
            # So it doesn't need to be processed
            if hash in get_disruption_hashes(database, url):
                print("disruption already in db")
                add_disruption = False

        if add_disruption:
            # Translate text to English
            translated_text = translate_disruption(d)
            # Find users affected by disruption
            affected_users = find_affected_users(translated_text, users)
            # Email affected users
            for user in affected_users:
                email_affected_user(user)
            # Save translated disruption text to database
            save_disruption(database, url, translated_text, hash)



def in_list_of_dicts(dicts: list, value: str):
    """Returns true if a given value is found within a list of dictionaries"""
    for d in dicts:
        if value in d.values():
            return True



def scrape_and_save(database: Database, disruption_urls: list, disruption_func,
                    users: list, urls: list):
    """Scrapes disruption urls, translates them, 
        and saves new disruptions to DB"""
    print("Scraping urls...")
    for url in disruption_urls:
        # get all disruptions from URL
        disruptions = disruption_func(url)
        # Generate a hash of outages from URL
        url_hash = generate_hash("".join(disruptions))
        # Is URL already in DB?
        if in_list_of_dicts(urls, url):
            print("url is already in db")

            # If the hash isn't in the urls, the page has been updated
            if not in_list_of_dicts(urls, url_hash):
                print("found new/updated disruptions")
                save_url(database, url, url_hash, True)
                process_disruptions(database, url, disruptions, users, False)
            else:
                print("no new disruptions found")
        else:
            save_url(database, url, url_hash, False)
            print("url is not in db")
            process_disruptions(database, url, disruptions, users, True)
    


if __name__ == "__main__":
    pass

